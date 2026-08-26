from typing import Any


class PriorityEngine:
    """
    RailSync Maintenance Priority Engine.

    Produces a transparent priority score from 0-100.

    The model is designed for railway maintenance planning,
    where safety and operational consequences must dominate
    administrative urgency.

    Input dataset:
        department_requests

    Important:
        This engine does NOT change the dataset schema.
    """

    # ========================================================
    # WEIGHTS
    # ========================================================

    # Railway-oriented weighting:
    #
    # Safety is the strongest factor.
    # Criticality and operational impact follow.
    # Actual urgency and overdue status influence scheduling.
    #
    WEIGHTS = {
        "safety_risk": 0.25,
        "criticality": 0.20,
        "operational_impact": 0.20,
        "severity": 0.15,
        "urgency": 0.10,
        "overdue": 0.10,
    }

    # ========================================================
    # URGENCY MAPPING
    # ========================================================

    URGENCY_SCORES = {
        "IMMEDIATE": 100.0,
        "HIGH": 80.0,
        "MEDIUM": 60.0,
        "NORMAL": 40.0,
        "LOW": 20.0,
    }

    # ========================================================
    # NORMALIZATION
    # ========================================================

    @staticmethod
    def _normalize(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:

        if maximum == minimum:
            return 0.0

        value = max(
            minimum,
            min(value, maximum),
        )

        return (
            (value - minimum)
            / (maximum - minimum)
        ) * 100.0

    # ========================================================
    # SAFE NUMERIC CONVERSION
    # ========================================================

    @staticmethod
    def _number(
        value: Any,
        default: float = 0.0,
    ) -> float:

        try:
            if value is None:
                return default

            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            return default

    # ========================================================
    # URGENCY
    # ========================================================

    @classmethod
    def _urgency_score(
        cls,
        urgency: Any,
    ) -> float:

        if urgency is None:
            return 0.0

        value = str(urgency).strip().upper()

        return cls.URGENCY_SCORES.get(
            value,
            0.0,
        )

    # ========================================================
    # OVERDUE SCORE
    # ========================================================

    @classmethod
    def _overdue_score(
        cls,
        overdue_days: Any,
    ) -> float:

        overdue = cls._number(
            overdue_days
        )

        # 30+ overdue days is treated as maximum urgency.
        return cls._normalize(
            overdue,
            0,
            30,
        )

    # ========================================================
    # PRIORITY SCORE
    # ========================================================

    @classmethod
    def calculate_score(
        cls,
        request: dict,
    ) -> float:

        # ----------------------------------------------------
        # SAFETY
        # ----------------------------------------------------

        safety_risk = cls._normalize(
            cls._number(
                request.get("safety_risk")
            ),
            1,
            100,
        )

        # ----------------------------------------------------
        # ASSET / SYSTEM CRITICALITY
        # ----------------------------------------------------

        criticality = cls._normalize(
            cls._number(
                request.get("criticality")
            ),
            1,
            100,
        )

        # ----------------------------------------------------
        # OPERATIONAL IMPACT
        # ----------------------------------------------------

        operational_impact = cls._normalize(
            cls._number(
                request.get(
                    "operational_impact"
                )
            ),
            1,
            100,
        )

        # ----------------------------------------------------
        # DEFECT SEVERITY
        # ----------------------------------------------------

        severity = cls._normalize(
            cls._number(
                request.get("severity")
            ),
            1,
            5,
        )

        # ----------------------------------------------------
        # ACTUAL BUSINESS URGENCY
        # ----------------------------------------------------

        urgency = cls._urgency_score(
            request.get("urgency")
        )

        # ----------------------------------------------------
        # OVERDUE
        # ----------------------------------------------------

        overdue = cls._overdue_score(
            request.get("overdue_days")
        )

        # ----------------------------------------------------
        # FINAL SCORE
        # ----------------------------------------------------

        score = (
            safety_risk
            * cls.WEIGHTS["safety_risk"]

            + criticality
            * cls.WEIGHTS["criticality"]

            + operational_impact
            * cls.WEIGHTS["operational_impact"]

            + severity
            * cls.WEIGHTS["severity"]

            + urgency
            * cls.WEIGHTS["urgency"]

            + overdue
            * cls.WEIGHTS["overdue"]
        )

        return round(
            max(
                0.0,
                min(score, 100.0),
            ),
            2,
        )

    # ========================================================
    # PRIORITY CLASS
    # ========================================================

    @staticmethod
    def classify(
        score: float,
    ) -> str:

        if score >= 75:
            return "Critical"

        if score >= 55:
            return "High"

        if score >= 35:
            return "Medium"

        return "Low"

    # ========================================================
    # SINGLE REQUEST
    # ========================================================

    @classmethod
    def prioritize_task(
        cls,
        request: dict,
    ) -> dict:

        score = cls.calculate_score(
            request
        )

        result = request.copy()

        result["priority_score"] = score

        result["priority_class"] = (
            cls.classify(score)
        )

        return result

    # ========================================================
    # ALL REQUESTS
    # ========================================================

    @classmethod
    def prioritize_tasks(
        cls,
        requests: list[dict],
    ) -> list[dict]:

        prioritized = [
            cls.prioritize_task(request)
            for request in requests
        ]

        prioritized.sort(
            key=lambda request: (
                request["priority_score"],
                cls._number(
                    request.get(
                        "safety_risk"
                    )
                ),
                cls._number(
                    request.get(
                        "criticality"
                    )
                ),
            ),
            reverse=True,
        )

        return prioritized