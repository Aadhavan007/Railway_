from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.orchestration.planning_service import (
    PlanningService,
)

router = APIRouter(
    prefix="/api/emergency",
    tags=["Emergency"],
)


class EmergencyRequest(BaseModel):
    request_id: str
    reason: str
    severity: str = "HIGH"


@router.post("/evaluate")
def evaluate_emergency(
    request: EmergencyRequest,
):
    try:
        service = PlanningService()

        tasks = service.load_tasks()

        task = next(
            (
                task
                for task in tasks
                if str(
                    task.get("request_id")
                )
                == str(request.request_id)
            ),
            None,
        )

        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Request not found.",
            )

        return {
            "request_id": request.request_id,
            "emergency": True,
            "severity": request.severity,
            "reason": request.reason,
            "message": (
                "Emergency request identified. "
                "Replanning should be triggered."
            ),
            "request": task,
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )