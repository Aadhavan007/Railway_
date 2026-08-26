class OptimizationConstraints:
    """
    Central definition of hard and soft scheduling constraints.

    Hard constraints:
        - A task can be scheduled at most once.
        - A physical block can be assigned at most once.
        - Candidate feasibility must already be established
          by CandidateGenerator.
        - A candidate must fit within the task duration.
        - If an absolute deadline exists, the candidate must
          not occur after that deadline.

    Soft constraints:
        - Train movements.
        - Traffic level.
        - Poor block utilization.
    """

    TRAFFIC_PENALTY = {
        "LOW": 0,
        "MEDIUM": 10,
        "HIGH": 25,
    }

    # ========================================================
    # TASK VALIDATION
    # ========================================================

    @staticmethod
    def task_is_valid(
        task: dict,
    ) -> bool:
        """
        Basic task validation.

        Supports:
            request_id -> current schema
            task_id    -> legacy schema
        """

        request_id = (
            task.get("request_id")
            or task.get("task_id")
        )

        required_values = [
            request_id,
            task.get("corridor_id"),
            task.get(
                "estimated_duration_hours"
            ),
        ]

        return all(
            value is not None
            for value in required_values
        )

    # ========================================================
    # CANDIDATE VALIDATION
    # ========================================================

    @staticmethod
    def candidate_is_valid(
        task: dict,
        candidate: dict,
    ) -> bool:
        """
        Validate a candidate before it enters CP-SAT.

        CandidateGenerator is the authoritative source for
        basic block feasibility, so this method does NOT
        require an `available` field to exist in the candidate.

        This is important because the current RailSync
        candidate schema may omit that field after ranking.
        """

        # ----------------------------------------------------
        # BLOCK ID
        # ----------------------------------------------------

        if not candidate.get(
            "block_id"
        ):
            return False

        # ----------------------------------------------------
        # CANDIDATE DATE
        # ----------------------------------------------------

        if not candidate.get(
            "date"
        ):
            return False

        # ----------------------------------------------------
        # BLOCK DURATION
        # ----------------------------------------------------

        try:

            block_duration = float(
                candidate.get(
                    "block_duration_hours",
                    0,
                )
            )

            task_duration = float(
                task.get(
                    "estimated_duration_hours",
                    candidate.get(
                        "task_duration_hours",
                        0,
                    ),
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            return False

        if block_duration <= 0:
            return False

        if task_duration <= 0:
            return False

        if block_duration < task_duration:
            return False

        # ----------------------------------------------------
        # OPTIONAL DEADLINE
        # ----------------------------------------------------

        deadline = task.get(
            "deadline"
        )

        if deadline is not None:

            candidate_date = str(
                candidate.get(
                    "date",
                    "",
                )
            )[:10]

            deadline_date = str(
                deadline
            )[:10]

            if (
                candidate_date
                and deadline_date
                and candidate_date
                > deadline_date
            ):
                return False

        return True

    # ========================================================
    # CANDIDATE PENALTY
    # ========================================================

    @classmethod
    def candidate_penalty(
        cls,
        candidate: dict,
    ) -> int:
        """
        Calculate operational disruption penalty.

        Missing train/traffic information is treated as
        unavailable rather than inventing operational data.
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

        traffic_penalty = (
            cls.TRAFFIC_PENALTY.get(
                traffic,
                15,
            )
        )

        train_penalty = (
            train_count * 5
        )

        return (
            traffic_penalty
            + train_penalty
        )

    # ========================================================
    # UTILIZATION PENALTY
    # ========================================================

    @staticmethod
    def utilization_penalty(
        candidate: dict,
    ) -> int:
        """
        Penalize unused block capacity.
        """

        try:

            block_duration = float(
                candidate.get(
                    "block_duration_hours",
                    0,
                )
            )

            task_duration = float(
                candidate.get(
                    "task_duration_hours",
                    0,
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0

        unused = max(
            0,
            block_duration
            - task_duration,
        )

        return int(
            round(
                unused * 10
            )
        )

    # ========================================================
    # TOTAL PENALTY
    # ========================================================

    @classmethod
    def total_penalty(
        cls,
        candidate: dict,
    ) -> int:

        return (
            cls.candidate_penalty(
                candidate
            )
            + cls.utilization_penalty(
                candidate
            )
        )