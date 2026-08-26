from app.services.orchestration.planning_service import PlanningService


def test_planning_service_runs():
    service = PlanningService()

    result = service.run(
        planning_date="2026-08-25"
    )

    assert result.planning_date == "2026-08-25"
    assert result.total_tasks >= 0
    assert result.prioritized_tasks == result.total_tasks
    assert result.optimization_status in {
        "OPTIMAL",
        "FEASIBLE",
        "UNKNOWN",
        "MODEL_INVALID",
        "INFEASIBLE",
    }


def test_planning_result_has_schedule():
    service = PlanningService()

    result = service.run(
        planning_date="2026-08-25"
    )

    assert isinstance(
        result.selected_tasks,
        list,
    )

    for task in result.selected_tasks:
        assert "task_id" in task
        assert "corridor_id" in task
        assert "block_id" in task
        assert "date" in task
        assert "start_time" in task
        assert "end_time" in task