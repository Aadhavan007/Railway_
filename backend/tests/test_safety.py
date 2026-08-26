from app.services.safety.safety_validator import SafetyValidator


def test_safe_schedule_is_valid():
    validator = SafetyValidator()

    schedule = [
        {
            "task_id": "A",
            "corridor_id": "C01",
            "block_id": "B1",
            "date": "2026-08-25",
            "start_time": "10:00",
            "end_time": "12:00",
        }
    ]

    result = validator.validate(schedule)

    assert result.valid is True
    assert result.penalty == 0
    assert result.violations == []


def test_overlapping_corridor_is_invalid():
    validator = SafetyValidator()

    schedule = [
        {
            "task_id": "A",
            "corridor_id": "C01",
            "block_id": "B1",
            "date": "2026-08-25",
            "start_time": "10:00",
            "end_time": "12:00",
        },
        {
            "task_id": "B",
            "corridor_id": "C01",
            "block_id": "B2",
            "date": "2026-08-25",
            "start_time": "11:00",
            "end_time": "13:00",
        },
    ]

    result = validator.validate(schedule)

    assert result.valid is False
    assert result.penalty > 0
    assert len(result.violations) > 0

    assert any(
        violation["type"] == "CORRIDOR_OVERLAP"
        for violation in result.violations
    )


def test_different_corridors_can_overlap():
    validator = SafetyValidator()

    schedule = [
        {
            "task_id": "A",
            "corridor_id": "C01",
            "block_id": "B1",
            "date": "2026-08-25",
            "start_time": "10:00",
            "end_time": "12:00",
        },
        {
            "task_id": "B",
            "corridor_id": "C02",
            "block_id": "B2",
            "date": "2026-08-25",
            "start_time": "11:00",
            "end_time": "13:00",
        },
    ]

    result = validator.validate(schedule)

    assert result.valid is True
    assert result.penalty == 0