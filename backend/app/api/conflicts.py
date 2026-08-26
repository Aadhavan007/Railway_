from fastapi import APIRouter, HTTPException

from app.services.orchestration.planning_service import (
    PlanningService,
)

router = APIRouter(
    prefix="/api/conflicts",
    tags=["Conflicts"],
)


@router.get("/")
def get_conflicts(
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
            "safety_valid": result.safety_valid,
            "safety_penalty": result.safety_penalty,
            "message": (
                "No safety conflicts detected."
                if result.safety_valid
                else "Safety conflicts detected."
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )