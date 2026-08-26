from fastapi import APIRouter, HTTPException

from app.services.orchestration.planning_service import PlanningService

router = APIRouter(
    prefix="/api/schedules",
    tags=["Schedules"],
)


@router.get("/")
def get_schedule(
    planning_date: str = "2026-08-25",
    corridor_id: str | None = None,
    department: str | None = None,
):
    try:
        result = PlanningService().run(
            planning_date=planning_date,
            corridor_id=corridor_id,
        )

        schedules = result.selected_tasks

        if department:
            schedules = [
                task
                for task in schedules
                if str(
                    task.get("department", "")
                ).lower()
                == department.lower()
            ]

        return {
            "planning_date": result.planning_date,
            "corridor_id": result.corridor_id or "ALL",
            "count": len(schedules),
            "safety_valid": result.safety_valid,
            "schedules": schedules,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get("/{request_id}")
def get_schedule_for_request(
    request_id: str,
    planning_date: str = "2026-08-25",
):
    try:
        result = PlanningService().run(
            planning_date=planning_date,
        )

        matches = [
            task
            for task in result.selected_tasks
            if str(
                task.get("request_id")
            )
            == str(request_id)
        ]

        if not matches:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"{request_id} is not scheduled."
                ),
            )

        return matches[0]

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )