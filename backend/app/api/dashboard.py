from fastapi import APIRouter, HTTPException

from app.services.orchestration.planning_service import PlanningService

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)


@router.get("/summary")
def dashboard_summary(
    planning_date: str = "2026-08-25",
    corridor_id: str | None = None,
):
    try:
        result = PlanningService().run(
            planning_date=planning_date,
            corridor_id=corridor_id,
        )

        summary = result.decision_summary

        return {
            "planning_date": result.planning_date,
            "corridor_id": result.corridor_id or "ALL",
            "total_requests": result.total_tasks,
            "prioritized_requests": result.prioritized_tasks,
            "requests_with_candidates": (
                result.requests_with_candidates
            ),
            "total_candidates": result.total_candidates,
            "coordination_opportunities": (
                result.coordination_opportunities
            ),
            "scheduled_requests": summary.get(
                "scheduled_requests",
                len(result.selected_tasks),
            ),
            "unscheduled_requests": summary.get(
                "unscheduled_requests",
                0,
            ),
            "optimizer_status": (
                result.optimization_status
            ),
            "safety_valid": result.safety_valid,
            "safety_penalty": result.safety_penalty,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )