import httpx
import logging
import ipaddress
import socket
from urllib.parse import urlparse
from typing import Dict, Any
from uuid import UUID
from datetime import datetime, timezone
from app.models.webhook import WebhookSubscription
from app.core.redis_client import redis_client
from app.core.config import settings

logger = logging.getLogger(__name__)

def is_safe_webhook_url(url: str) -> bool:
    """
    Validate webhook URL to prevent SSRF attacks.

    Security checks:
    - Only allow HTTP/HTTPS protocols
    - Block localhost and private IP ranges
    - Block cloud metadata services (169.254.x.x)
    - Block link-local addresses
    """
    try:
        parsed = urlparse(url)

        # Only allow HTTP/HTTPS
        if parsed.scheme not in ['http', 'https']:
            logger.warning(f"Blocked webhook URL with invalid scheme: {parsed.scheme}")
            return False

        # Get hostname
        hostname = parsed.hostname
        if not hostname:
            logger.warning("Blocked webhook URL without hostname")
            return False

        # Resolve to IP
        try:
            ip = socket.gethostbyname(hostname)
        except socket.gaierror:
            logger.warning(f"Blocked webhook URL with unresolvable hostname: {hostname}")
            return False

        ip_obj = ipaddress.ip_address(ip)

        # Block private/loopback/link-local addresses
        if ip_obj.is_private:
            logger.warning(f"Blocked webhook URL to private IP: {ip}")
            return False

        if ip_obj.is_loopback:
            logger.warning(f"Blocked webhook URL to loopback: {ip}")
            return False

        if ip_obj.is_link_local:
            logger.warning(f"Blocked webhook URL to link-local: {ip}")
            return False

        # Block cloud metadata services
        if ip.startswith('169.254'):
            logger.warning(f"Blocked webhook URL to metadata service: {ip}")
            return False

        # Block multicast
        if ip_obj.is_multicast:
            logger.warning(f"Blocked webhook URL to multicast: {ip}")
            return False

        return True
    except Exception as e:
        logger.error(f"Error validating webhook URL {url}: {str(e)}")
        return False



class WebhookService:
    """Service for dispatching webhook events to developers"""

    @staticmethod
    async def dispatch_event(event_type: str, data: Dict[str, Any], developer_id: UUID):
        """
        Dispatch a webhook event to all subscribed webhooks for a developer.

        Args:
            event_type: Type of event (e.g., "lead.wishlist", "lead.legal_request")
            data: Event data payload
            developer_id: Developer ID to send webhook to
        """
        # Try cache first (TIER 1 CACHING: Webhook subscriptions)
        cache_key = redis_client.make_key("webhooks", "dev", str(developer_id), "active")
        cached_webhooks = await redis_client.get(cache_key)

        if cached_webhooks:
            webhooks = [WebhookSubscription(**w) for w in cached_webhooks]
        else:
            # Cache miss - query database
            webhooks = await WebhookSubscription.find(
                WebhookSubscription.developer_id == developer_id,
                WebhookSubscription.is_active == True
            ).to_list()

            # Cache for 30 minutes
            if webhooks:
                webhooks_dict = [w.model_dump() for w in webhooks]
                await redis_client.set(cache_key, webhooks_dict, 1800)

        # Filter webhooks that subscribe to this event type
        subscribed_webhooks = [
            webhook for webhook in webhooks
            if event_type in webhook.events or "*" in webhook.events
        ]

        if not subscribed_webhooks:
            logger.info(f"No webhooks subscribed to {event_type} for developer {developer_id}")
            return

        # Prepare payload
        payload = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Dispatch to all subscribed webhooks
        async with httpx.AsyncClient(timeout=10.0) as client:
            for webhook in subscribed_webhooks:
                try:
                    # SECURITY: Validate URL to prevent SSRF attacks
                    if not is_safe_webhook_url(str(webhook.url)):
                        logger.error(f"Blocked unsafe webhook URL: {webhook.url}")
                        continue

                    headers = {"Content-Type": "application/json"}
                    if webhook.secret_token:
                        headers["X-Webhook-Secret"] = webhook.secret_token

                    response = await client.post(
                        str(webhook.url),
                        json=payload,
                        headers=headers
                    )

                    if response.status_code >= 200 and response.status_code < 300:
                        logger.info(f"Webhook dispatched successfully to {webhook.url} for event {event_type}")
                    else:
                        logger.warning(
                            f"Webhook dispatch failed to {webhook.url} with status {response.status_code}"
                        )

                except httpx.TimeoutException:
                    logger.error(f"Webhook timeout for {webhook.url}")
                except httpx.RequestError as e:
                    logger.error(f"Webhook request error for {webhook.url}: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error dispatching webhook to {webhook.url}: {str(e)}")
