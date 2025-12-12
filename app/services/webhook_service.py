import httpx
import logging
from typing import Dict, Any
from uuid import UUID
from datetime import datetime
from app.models.webhook import WebhookSubscription

logger = logging.getLogger(__name__)

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
        # Find all active webhooks for this developer that subscribe to this event
        webhooks = await WebhookSubscription.find(
            WebhookSubscription.developer_id == developer_id,
            WebhookSubscription.is_active == True
        ).to_list()

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
            "timestamp": datetime.utcnow().isoformat()
        }

        # Dispatch to all subscribed webhooks
        async with httpx.AsyncClient(timeout=10.0) as client:
            for webhook in subscribed_webhooks:
                try:
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
