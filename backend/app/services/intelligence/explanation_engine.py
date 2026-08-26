from datetime import datetime
from typing import Any

from app.services.intelligence.priority_engine import PriorityEngine


class ExplanationEngine:
    """
    Generates transparent, human-readable explanations
    for RailSync maintenance priority decisions.

    This engine does not calculate a new priority score.
    It explains the score already produced by PriorityEngine.
    """

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _severity_description(severity: float) -> str:
        if severity >= 5:
            return "Very high defect severity"
        if severity >= 4:
            return "High defect severity"
        if severity >= 3:
            return "Moderate defect severity"
        if severity >= 2:
            return "Low defect severity"

        return "Very low defect severity"

    @staticmethod
    def _criticality_description(criticality: float) -> str:
        if criticality >= 90:
            return "Critical infrastructure asset"
        if criticality >= 75:
            return "Highly critical infrastructure asset"
        if criticality >= 50:
            return "Moderately critical infrastructure asset"

        return "Lower criticality asset"

    @staticmethod
    def _safety_description(safety_risk: float) -> str:
        if safety_risk >= 90:
            return "Extremely high safety risk"
        if safety_risk >= 75:
            return "High safety risk"
        if safety_risk >= 50:
            return "Moderate safety risk"

        return "Low safety risk"

    @staticmethod
    def _operational_description(
        operational_impact: float,
    ) -> str:

        if operational_impact >= 90:
            return "Extremely high operational impact"
        if operational_impact >= 75:
            return "High operational impact"
        if operational_impact >= 50:
            return "Moderate operational impact"

        return "Low operational impact"

    @staticmethod
    def _deadline_urgency(deadline: Any) -> float:

        if deadline is None:
            return 0.0

        try:
            if isinstance(deadline, str):
                deadline_date = datetime.strptime(
                    deadline[:10],
                    "%Y-%m-%d",
                ).date()
            else:
                deadline_date = deadline.date()

            today = datetime.now().date()
            days_remaining = (
                deadline_date - today
            ).days

            if days_remaining <= 0:
                return 100.0

            if days_remaining == 1:
                return 90.0

            if days_remaining == 2:
                return 80.0

            if days_remaining <= 4:
                return 65.0

            if days_remaining <= 7:
                return 50.0

            if days_remaining <= 14:
                return 30.0

            return 15.0

        except (
            ValueError,
            TypeError,
            AttributeError,
        ):
            return 0.0

    @staticmethod
    def _urgency_description(
        urgency: Any,
    ) -> str:

        if urgency is None:
            return "No urgency information available"

        value = str(urgency).strip().upper()

        descriptions = {
            "IMMEDIATE": "Immediate action required",
            "HIGH": "High urgency request",
            "MEDIUM": "Moderate urgency request",
            "NORMAL": "Normal urgency request",
            "LOW": "Low urgency request",
        }

        return descriptions.get(
            value,
            f"Urgency classified as {value}",
        )

    @staticmethod
    def _overdue_description(
        overdue_days: float,
    ) -> str:

        if overdue_days <= 0:
            return "Task is not overdue"

        if overdue_days >= 30:
            return f"Severely overdue by {int(overdue_days)} days"

        if overdue_days >= 14:
            return f"Significantly overdue by {int(overdue_days)} days"

        if overdue_days >= 7:
            return f"Overdue by {int(overdue_days)} days"

        return f"Slightly overdue by {int(overdue_days)} days"

    # ========================================================
    # DRIVER DETECTION
    # ========================================================

    @classmethod
    def identify_drivers(
        cls,
        task: dict,
    ) -> list[dict]:

        severity = float(task.get("severity", 0))
        criticality = float(task.get("criticality", 0))
        overdue = float(task.get("overdue_days", 0))
        safety_risk = float(task.get("safety_risk", 0))
        operational_impact = float(
            task.get("operational_impact", 0)
        )

        drivers = [
            {
                "factor": "severity",
                "score": PriorityEngine._normalize(
                    severity,
                    1,
                    5,
                ),
                "description": cls._severity_description(
                    severity
                ),
            },
            {
                "factor": "criticality",
                "score": PriorityEngine._normalize(
                    criticality,
                    1,
                    100,
                ),
                "description": cls._criticality_description(
                    criticality
                ),
            },
            {
                "factor": "overdue",
                "score": PriorityEngine._normalize(
                    overdue,
                    0,
                    30,
                ),
                "description": cls._overdue_description(
                    overdue
                ),
            },
            {
                "factor": "safety_risk",
                "score": PriorityEngine._normalize(
                    safety_risk,
                    1,
                    100,
                ),
                "description": cls._safety_description(
                    safety_risk
                ),
            },
            {
                "factor": "operational_impact",
                "score": PriorityEngine._normalize(
                    operational_impact,
                    1,
                    100,
                ),
                "description": cls._operational_description(
                    operational_impact
                ),
            },
            {
                "factor": "deadline_urgency",
                "score": cls._deadline_urgency(
                    task.get("deadline")
                ),
                "description": (
                    "Deadline requires immediate attention"
                    if cls._deadline_urgency(
                        task.get("deadline")
                    ) >= 80
                    else "Deadline contributes moderate urgency"
                    if cls._deadline_urgency(
                        task.get("deadline")
                    ) >= 50
                    else "Deadline contributes limited urgency"
                ),
            },
        ]

        drivers.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return drivers

    # ========================================================
    # EXPLANATION
    # ========================================================

    @classmethod
    def explain_task(
        cls,
        task: dict,
    ) -> dict:

        score = PriorityEngine.calculate_score(task)
        priority_class = PriorityEngine.classify(score)

        drivers = cls.identify_drivers(task)

        significant_drivers = [
            driver
            for driver in drivers
            if driver["score"] >= 50
        ]

        if not significant_drivers:
            significant_drivers = drivers[:3]

        task_id = task.get(
            "request_id",
            task.get("task_id", "UNKNOWN"),
        )

        explanation = {
            "task_id": task_id,
            "priority_score": score,
            "priority_class": priority_class,
            "drivers": significant_drivers,
            "summary": cls._build_summary(
                task,
                score,
                priority_class,
                significant_drivers,
            ),
        }

        return explanation

    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def _build_summary(
        task: dict,
        score: float,
        priority_class: str,
        drivers: list[dict],
    ) -> str:

        task_id = task.get(
            "request_id",
            task.get("task_id", "UNKNOWN"),
        )

        if not drivers:
            return (
                f"{task_id} has a {priority_class} "
                f"priority with a score of {score:.2f}."
            )

        driver_text = ", ".join(
            driver["description"]
            for driver in drivers[:3]
        )

        return (
            f"{task_id} is classified as "
            f"{priority_class} priority with a "
            f"score of {score:.2f}. "
            f"The main contributing factors are: "
            f"{driver_text}."
        )

    # ========================================================
    # BATCH EXPLANATION
    # ========================================================

    @classmethod
    def explain_tasks(
        cls,
        tasks: list[dict],
    ) -> list[dict]:

        return [
            cls.explain_task(task)
            for task in tasks
        ]