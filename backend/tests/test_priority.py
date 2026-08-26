from app.services.intelligence.priority_engine import PriorityEngine


def test_priority_engine_returns_priority_score():
    task = {
        "task_id": "TEST-001",
        "severity": 3,
        "criticality": 100,
        "overdue_days": 10,
        "safety_risk": 80,
        "operational_impact": 80,
    }

    result = PriorityEngine.prioritize_task(task)

    assert "priority_score" in result
    assert isinstance(result["priority_score"], (int, float))


def test_priority_engine_returns_priority_class():
    task = {
        "task_id": "TEST-002",
        "severity": 3,
        "criticality": 100,
        "overdue_days": 10,
        "safety_risk": 80,
        "operational_impact": 80,
    }

    result = PriorityEngine.prioritize_task(task)

    assert "priority_class" in result
    assert result["priority_class"] in {
        "Critical",
        "High",
        "Medium",
        "Low",
    }


def test_priority_score_is_not_negative():
    task = {
        "task_id": "TEST-003",
        "severity": 1,
        "criticality": 1,
        "overdue_days": 0,
        "safety_risk": 0,
        "operational_impact": 0,
    }

    result = PriorityEngine.prioritize_task(task)

    assert result["priority_score"] >= 0