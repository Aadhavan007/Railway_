from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.orchestration.planning_service import (
    PlanningService,
)

router = APIRouter(
    prefix="/api/approvals",
    tags=["Approvals"],
)


class ApprovalRequest(BaseModel):
    request_id: str
    approved: bool
    approved_by: str | None = None
    comments: str | None = None


@router.post("/")
def submit_approval(
    request: ApprovalRequest,
):
    try:
        result = PlanningService().run(
            planning_date="2026-08-25",
        )

        scheduled = next(
            (
                task
                for task in result.selected_tasks
                if str(
                    task.get("request_id")
                )
                == str(request.request_id)
            ),
            None,
        )

        if scheduled is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Request is not currently "
                    "scheduled."
                ),
            )

        return {
            "request_id": request.request_id,
            "approved": request.approved,
            "approved_by": request.approved_by,
            "comments": request.comments,
            "status": (
                "APPROVED"
                if request.approved
                else "REJECTED"
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )