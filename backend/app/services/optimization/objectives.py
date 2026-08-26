class OptimizationObjectives:
    """
    Calculates the value of assigning a maintenance task
    to a particular block.

    Higher objective value = better assignment.
    """

    # ========================================================
    # PRIORITY
    # ========================================================

    @staticmethod
    def priority_value(
        task: dict,
    ) -> int:
        """
        Higher-priority maintenance should be favored.
        """

        try:

            priority_score = float(
                task.get(
                    "priority_score",
                    0,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            priority_score = 0.0

        return int(
            round(
                priority_score * 10
            )
        )

    # ========================================================
    # BLOCK QUALITY
    # ========================================================

    @staticmethod
    def block_quality(
        candidate: dict,
    ) -> int:
        """
        Reward a good task → block match.
        """

        try:

            match_score = float(
                candidate.get(
                    "match_score",
                    0,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            match_score = 0.0

        return int(
            round(
                match_score * 5
            )
        )

    # ========================================================
    # DISRUPTION COST
    # ========================================================

    @staticmethod
    def disruption_cost(
        candidate: dict,
    ) -> int:
        """
        Penalize expected operational disruption.

        If operational data is not present in the current
        dataset, safe defaults are used.
        """

        try:

            train_count = int(
                candidate.get(
                    "expected_train_count",
                    0,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            train_count = 0

        traffic = str(
            candidate.get(
                "traffic_level",
                "MEDIUM",
            )
        ).upper()

        traffic_penalty = {
            "LOW": 0,
            "MEDIUM": 10,
            "HIGH": 25,
        }.get(
            traffic,
            15,
        )

        return (
            train_count * 5
            + traffic_penalty
        )

    # ========================================================
    # FINAL ASSIGNMENT VALUE
    # ========================================================

    @classmethod
    def assignment_value(
        cls,
        task: dict,
        candidate: dict,
    ) -> int:
        """
        Final objective value for one
        task → block assignment.

        Higher = better.
        """

        priority = (
            cls.priority_value(
                task
            )
        )

        block_quality = (
            cls.block_quality(
                candidate
            )
        )

        disruption = (
            cls.disruption_cost(
                candidate
            )
        )

        return (
            priority
            + block_quality
            - disruption
        )