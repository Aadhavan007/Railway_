from fastapi import APIRouter, HTTPException

from app.services.intelligence.priority_engine import (
    PriorityEngine,
)
from app.services.orchestration.planning_service import (
    PlanningService,
)

router = APIRouter(
    prefix="/api/priorities",
    tags=["Priorities"],
)


@router.get("/")
def get_priorities(
    planning_date: str = "2026-08-25",
    corridor_id: str | None = None,
):
    try:
        service = PlanningService()

        tasks = service.load_tasks()

        tasks = service.filter_by_date(
            tasks,
            planning_date,
        )

        tasks = service.filter_by_corridor(
            tasks,
            corridor_id,
        )

        prioritized = [
            PriorityEngine.prioritize_task(task)
            for task in tasks
        ]

        prioritized.sort(
            key=lambda task: float(
                task.get(
                    "priority_score",
                    0,
                )
            ),
            reverse=True,
        )

        return {
            "planning_date": planning_date,
            "corridor_id": corridor_id or "ALL",
            "count": len(prioritized),
            "requests": prioritized,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/{request_id}")
def get_priority(
    request_id: str,
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
                == str(request_id)
            ),
            None,
        )

        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Request not found.",
            )

        return PriorityEngine.prioritize_task(
            task
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )