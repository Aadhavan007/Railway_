from app.services.intelligence.coordination_engine import CoordinationEngine


def test_coordination_requires_different_departments():
    engine = CoordinationEngine()

    tasks = [
        {
            "task_id": "A",
            "corridor_id": "C01",
            "department": "Engineering",
            "estimated_duration_hours": 1,
        },
        {
            "task_id": "B",
            "corridor_id": "C01",
            "department": "Engineering",
            "estimated_duration_hours": 1,
        },
    ]

    candidates = {
        "A": [
            {
                "block_id": "B1",
                "corridor_id": "C01",
                "date": "2026-08-25",
                "start_time": "10:00",
                "end_time": "12:00",
            }
        ],
        "B": [
            {
                "block_id": "B1",
                "corridor_id": "C01",
                "date": "2026-08-25",
                "start_time": "10:00",
                "end_time": "12:00",
            }
        ],
    }

    result = engine.find_coordination_opportunities(
        candidates,
        tasks,
    )

    assert result == []


def test_coordination_requires_same_corridor():
    engine = CoordinationEngine()

    tasks = [
        {
            "task_id": "A",
            "corridor_id": "C01",
            "department": "Engineering",
            "estimated_duration_hours": 1,
        },
        {
            "task_id": "B",
            "corridor_id": "C02",
            "department": "S&T",
            "estimated_duration_hours": 1,
        },
    ]

    candidates = {
        "A": [
            {
                "block_id": "B1",
                "corridor_id": "C01",
                "date": "2026-08-25",
                "start_time": "10:00",
                "end_time": "12:00",
            }
        ],
        "B": [
            {
                "block_id": "B2",
                "corridor_id": "C02",
                "date": "2026-08-25",
                "start_time": "10:00",
                "end_time": "12:00",
            }
        ],
    }

    result = engine.find_coordination_opportunities(
        candidates,
        tasks,
    )

    assert result == []


def test_coordination_finds_valid_opportunity():
    engine = CoordinationEngine()

    tasks = [
        {
            "task_id": "A",
            "corridor_id": "C01",
            "department": "Engineering",
            "estimated_duration_hours": 1,
        },
        {
            "task_id": "B",
            "corridor_id": "C01",
            "department": "S&T",
            "estimated_duration_hours": 1,
        },
    ]

    candidates = {
        "A": [
            {
                "block_id": "B1",
                "corridor_id": "C01",
                "date": "2026-08-25",
                "start_time": "10:00",
                "end_time": "12:00",
            }
        ],
        "B": [
            {
                "block_id": "B1",
                "corridor_id": "C01",
                "date": "2026-08-25",
                "start_time": "10:00",
                "end_time": "12:00",
            }
        ],
    }

    result = engine.find_coordination_opportunities(
        candidates,
        tasks,
    )

    assert len(result) >= 1

    opportunity = result[0]

    assert opportunity["corridor_id"] == "C01"
    assert set(opportunity["task_ids"]) == {"A", "B"}
    assert opportunity["department_count"] == 2


def test_coordination_rejects_insufficient_overlap():
    engine = CoordinationEngine()

    tasks = [
        {
            "task_id": "A",
            "corridor_id": "C01",
            "department": "Engineering",
            "estimated_duration_hours": 2,
        },
        {
            "task_id": "B",
            "corridor_id": "C01",
            "department": "S&T",
            "estimated_duration_hours": 1,
        },
    ]

    candidates = {
        "A": [
            {
                "block_id": "B1",
                "corridor_id": "C01",
                "date": "2026-08-25",
                "start_time": "10:00",
                "end_time": "11:00",
            }
        ],
        "B": [
            {
                "block_id": "B2",
                "corridor_id": "C01",
                "date": "2026-08-25",
                "start_time": "10:00",
                "end_time": "11:00",
            }
        ],
    }

    result = engine.find_coordination_opportunities(
        candidates,
        tasks,
    )

    assert result == []