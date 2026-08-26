from fastapi import APIRouter, HTTPException

from app.services.orchestration.planning_service import (
    PlanningService,
)

router = APIRouter(
    prefix="/api/tasks",
    tags=["Tasks"],
)


@router.get("/")
def get_tasks(
    corridor_id: str | None = None,
    department: str | None = None,
):
    try:
        service = PlanningService()

        tasks = service.load_tasks()

        if corridor_id:
            tasks = [
                task
                for task in tasks
                if str(
                    task.get("corridor_id")
                )
                == str(corridor_id)
            ]

        if department:
            tasks = [
                task
                for task in tasks
                if str(
                    task.get("department", "")
                ).lower()
                == department.lower()
            ]

        return {
            "count": len(tasks),
            "tasks": tasks,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/{request_id}")
def get_task(
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

        return task

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )