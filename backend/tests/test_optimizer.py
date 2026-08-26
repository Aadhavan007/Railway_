from app.services.optimization.optimizer import BlockOptimizer


def test_optimizer_selects_valid_candidate():
    tasks = [
        {
            "task_id": "A",
            "priority_score": 90,
        }
    ]

    candidates = {
        "A": [
            {
                "block_id": "B1",
                "corridor_id": "C01",
                "date": "2026-08-25",
                "start_time": "10:00",
                "end_time": "12:00",
                "traffic_level": "LOW",
                "expected_train_count": 0,
                "match_score": 80,
            }
        ]
    }

    optimizer = BlockOptimizer()

    result = optimizer.optimize(
        tasks,
        candidates,
    )

    assert result.status in {
        "OPTIMAL",
        "FEASIBLE",
    }

    assert result.total_tasks == 1
    assert result.total_selected == 1

    selected = result.selected_tasks[0]

    assert selected["task_id"] == "A"
    assert selected["block_id"] == "B1"


def test_optimizer_does_not_select_same_task_twice():
    tasks = [
        {
            "task_id": "A",
            "priority_score": 90,
        }
    ]

    candidates = {
        "A": [
            {
                "block_id": "B1",
                "corridor_id": "C01",
                "date": "2026-08-25",
                "start_time": "10:00",
                "end_time": "12:00",
                "traffic_level": "LOW",
                "expected_train_count": 0,
                "match_score": 80,
            },
            {
                "block_id": "B2",
                "corridor_id": "C01",
                "date": "2026-08-25",
                "start_time": "12:00",
                "end_time": "14:00",
                "traffic_level": "LOW",
                "expected_train_count": 0,
                "match_score": 70,
            },
        ]
    }

    optimizer = BlockOptimizer()

    result = optimizer.optimize(
        tasks,
        candidates,
    )

    assert result.total_selected <= 1


def test_optimizer_does_not_share_same_block():
    tasks = [
        {
            "task_id": "A",
            "priority_score": 90,
        },
        {
            "task_id": "B",
            "priority_score": 80,
        },
    ]

    shared_candidate = {
        "block_id": "B1",
        "corridor_id": "C01",
        "date": "2026-08-25",
        "start_time": "10:00",
        "end_time": "12:00",
        "traffic_level": "LOW",
        "expected_train_count": 0,
        "match_score": 80,
    }

    candidates = {
        "A": [shared_candidate],
        "B": [shared_candidate.copy()],
    }

    optimizer = BlockOptimizer()

    result = optimizer.optimize(
        tasks,
        candidates,
    )

    assert result.total_selected <= 1