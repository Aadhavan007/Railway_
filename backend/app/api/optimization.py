from fastapi import APIRouter, HTTPException

from app.services.orchestration.planning_service import PlanningService

router = APIRouter(
    prefix="/api/optimization",
    tags=["Optimization"],
)


@router.post("/run")
def run_optimization(
    planning_date: str = "2026-08-25",
    corridor_id: str | None = None,
):
    try:
        result = PlanningService().run(
            planning_date=planning_date,
            corridor_id=corridor_id,
        )

        return {
            "planning_date": result.planning_date,
            "corridor_id": result.corridor_id or "ALL",
            "status": result.optimization_status,
            "selected_tasks": result.selected_tasks,
            "selected_count": len(
                result.selected_tasks
            ),
            "safety_valid": result.safety_valid,
            "safety_penalty": result.safety_penalty,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )