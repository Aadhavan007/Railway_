from fastapi import APIRouter, HTTPException

from app.services.orchestration.planning_service import (
    PlanningService,
)

router = APIRouter(
    prefix="/api/data",
    tags=["Data"],
)


@router.get("/stats")
def data_stats():
    try:
        service = PlanningService()

        tasks = service.load_tasks()

        departments = sorted(
            {
                str(
                    task.get(
                        "department",
                        "UNKNOWN",
                    )
                )
                for task in tasks
            }
        )

        corridors = sorted(
            {
                str(
                    task.get(
                        "corridor_id",
                        "UNKNOWN",
                    )
                )
                for task in tasks
            }
        )

        return {
            "total_requests": len(tasks),
            "departments": departments,
            "department_count": len(
                departments
            ),
            "corridors": corridors,
            "corridor_count": len(
                corridors
            ),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )