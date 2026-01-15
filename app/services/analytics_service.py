from typing import Any, List, Dict
from uuid import UUID
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from app.models.lead import ProjectLead, LeadStatus
from app.models.visit import VisitBooking

class ProjectAnalyticsService:
    @staticmethod
    async def get_project_dashboard_stats(project_id: UUID) -> Dict[str, Any]:
        """
        Calculate comprehensive analytics for a specific project.
        """
        now = datetime.now(timezone.utc)
        last_30_days = now - timedelta(days=30)
        prev_30_days = now - timedelta(days=60)

        # Get all leads/interactions for this project
        all_interactions = await ProjectLead.find(ProjectLead.project_id == project_id).to_list()
        
        # 1. Basic Stats
        total_views = 0
        current_period_views = 0
        prev_period_views = 0
        
        total_leads = 0
        current_period_leads = 0
        prev_period_leads = 0
        
        total_wishlists = 0
        current_period_wishlists = 0
        prev_period_wishlists = 0

        traffic_map = defaultdict(int)
        
        recent_leads_data = []

        # Weekly/Monthly Stats aggregation
        weekly_stats_map = defaultdict(lambda: {"views": 0, "leads": 0})
        # Last 7 days
        last_7_days_start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Monthly aggregate (last 6 months)
        monthly_stats_map = defaultdict(lambda: {"views": 0, "leads": 0, "wishlists": 0})

        for interaction in all_interactions:
            # Views
            views_list = interaction.viewed_at_history or []
            total_views += len(views_list)
            
            for v_at in views_list:
                # Ensure v_at is timezone aware
                if v_at.tzinfo is None:
                    v_at = v_at.replace(tzinfo=timezone.utc)
                
                if v_at >= last_30_days:
                    current_period_views += 1
                elif v_at >= prev_30_days:
                    prev_period_views += 1
                
                # Weekly aggregation
                if v_at >= last_7_days_start:
                    day_key = v_at.strftime("%a")
                    weekly_stats_map[day_key]["views"] += 1
                
                # Monthly aggregation
                month_key = v_at.strftime("%b")
                monthly_stats_map[month_key]["views"] += 1

            # Leads (Contacted users)
            is_lead = interaction.status in [LeadStatus.CONTACTED, LeadStatus.PURCHASED] or interaction.is_legal_requested or interaction.visit_booked_at
            if is_lead:
                total_leads += 1
                created_at = interaction.created_at.replace(tzinfo=timezone.utc) if interaction.created_at.tzinfo is None else interaction.created_at
                
                if created_at >= last_30_days:
                    current_period_leads += 1
                elif created_at >= prev_30_days:
                    prev_period_leads += 1
                
                # Weekly aggregation (using creation as lead entry point)
                if created_at >= last_7_days_start:
                    day_key = created_at.strftime("%a")
                    weekly_stats_map[day_key]["leads"] += 1
                
                month_key = created_at.strftime("%b")
                monthly_stats_map[month_key]["leads"] += 1

            # Wishlists
            if interaction.is_wishlisted:
                total_wishlists += 1
                w_at = interaction.wishlisted_at
                if w_at:
                    w_at = w_at.replace(tzinfo=timezone.utc) if w_at.tzinfo is None else w_at
                    if w_at >= last_30_days:
                        current_period_wishlists += 1
                    elif w_at >= prev_30_days:
                        prev_period_wishlists += 1
                    
                    month_key = w_at.strftime("%b")
                    monthly_stats_map[month_key]["wishlists"] += 1

            # Traffic Source
            source = interaction.source or "Direct"
            traffic_map[source] += 1

        # Percentage Changes
        def calc_pct_change(current, prev):
            if prev == 0:
                return 0.0 if current == 0 else 100.0
            return round(((current - prev) / prev) * 100, 1)

        # Conversion Rate
        conversion_rate = round((total_leads / total_views * 100), 2) if total_views > 0 else 0.0

        # Weekly Stats payload
        days_order = []
        for i in range(7):
            d = (last_7_days_start + timedelta(days=i))
            days_order.append(d.strftime("%a"))
        
        weekly_stats = [
            {"date": d, "views": weekly_stats_map[d]["views"], "leads": weekly_stats_map[d]["leads"]}
            for d in days_order
        ]

        # Monthly Stats payload (last 6 months)
        months_order = []
        for i in range(5, -1, -1):
            m = (now - timedelta(days=i*30))
            months_order.append(m.strftime("%b"))
        
        monthly_stats = [
            {
                "date": m, 
                "views": monthly_stats_map[m]["views"], 
                "leads": monthly_stats_map[m]["leads"],
                "wishlists": monthly_stats_map[m]["wishlists"]
            }
            for m in months_order
        ]

        # Traffic Breakdown
        total_interactions = len(all_interactions)
        traffic_breakdown = [
            {"name": source, "value": count} # count or percentage? user example shows values like 35, 28.
            for source, count in traffic_map.items()
        ]
        if not traffic_breakdown:
             traffic_breakdown = [{"name": "Direct", "value": 0}]

        # Recent Leads
        # Need user info for recent leads
        from app.models.user import User
        # Sort by creation / update
        sorted_interactions = sorted(
            [i for i in all_interactions if (i.status in [LeadStatus.CONTACTED, LeadStatus.PURCHASED] or i.is_legal_requested or i.visit_booked_at)],
            key=lambda x: x.updated_at,
            reverse=True
        )[:5]
        
        for inter in sorted_interactions:
            user = await User.get(inter.user_id)
            if user:
                recent_leads_data.append({
                    "id": str(inter.id),
                    "name": user.full_name,
                    "phone": user.phone,
                    "email": user.email,
                    "created_at": inter.created_at,
                    "status": inter.status.value
                })

        return {
            "total_views": total_views,
            "views_change_perc": calc_pct_change(current_period_views, prev_period_views),
            "total_leads": total_leads,
            "leads_change_perc": calc_pct_change(current_period_leads, prev_period_leads),
            "total_wishlists": total_wishlists,
            "wishlists_change_perc": calc_pct_change(current_period_wishlists, prev_period_wishlists),
            "conversion_rate": conversion_rate,
            "weekly_stats": weekly_stats,
            "monthly_stats": monthly_stats,
            "traffic_breakdown": traffic_breakdown,
            "recent_leads": recent_leads_data
        }
