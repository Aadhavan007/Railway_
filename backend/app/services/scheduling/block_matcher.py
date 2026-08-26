from datetime import date

from app.services.scheduling.candidate_generator import (
    CandidateGenerator,
)


class BlockMatcher:
    """
    Ranks feasible RailSync block candidates.

    Uses only fields that actually exist in the locked
    RailSync datasets.

    Train movement conflict checking is intentionally
    separate from candidate ranking.
    """

    def __init__(
        self,
        candidate_generator: CandidateGenerator | None = None,
    ):

        self.candidate_generator = (
            candidate_generator
            or CandidateGenerator()
        )

    # ========================================================
    # REQUEST ID
    # ========================================================

    @staticmethod
    def _get_request_id(
        task: dict,
    ) -> str | None:

        request_id = task.get(
            "request_id"
        )

        if request_id:
            return str(
                request_id
            )

        task_id = task.get(
            "task_id"
        )

        if task_id:
            return str(
                task_id
            )

        return None

    # ========================================================
    # DAY SCORE
    # ========================================================

    @staticmethod
    def _day_score(
        task: dict,
        candidate: dict,
    ) -> float:

        preferred_day = str(
            task.get(
                "preferred_day",
                "",
            )
        ).strip().lower()

        candidate_day = str(
            candidate.get(
                "day",
                "",
            )
        ).strip().lower()

        if not preferred_day:
            return 5.0

        if preferred_day == candidate_day:
            return 30.0

        return 10.0

    # ========================================================
    # BUFFER SCORE
    # ========================================================

    @staticmethod
    def _buffer_score(
        candidate: dict,
    ) -> float:

        buffer_minutes = float(
            candidate.get(
                "safety_buffer_minutes",
                0,
            )
        )

        if buffer_minutes >= 20:
            return 20.0

        if buffer_minutes >= 15:
            return 15.0

        if buffer_minutes >= 10:
            return 10.0

        return 5.0

    # ========================================================
    # UTILIZATION SCORE
    # ========================================================

    @staticmethod
    def _utilization_score(
        task: dict,
        candidate: dict,
    ) -> float:

        task_duration = float(
            candidate.get(
                "task_duration_hours",
                task.get(
                    "estimated_duration_hours",
                    0,
                ),
            )
        )

        block_duration = float(
            candidate.get(
                "block_duration_hours",
                0,
            )
        )

        unused = max(
            0.0,
            block_duration
            - task_duration,
        )

        if unused <= 0.25:
            return 30.0

        if unused <= 0.5:
            return 25.0

        if unused <= 1.0:
            return 18.0

        if unused <= 2.0:
            return 10.0

        return 5.0

    # ========================================================
    # BLOCK TYPE SCORE
    # ========================================================

    @staticmethod
    def _block_type_score(
        candidate: dict,
    ) -> float:

        block_type = str(
            candidate.get(
                "block_type",
                "",
            )
        ).upper()

        if block_type == "INTEGRATED_BLOCK":
            return 15.0

        if block_type == "CORRIDOR_BLOCK":
            return 12.0

        if block_type == "ROUTINE_BLOCK":
            return 10.0

        return 5.0

    # ========================================================
    # MATCH SCORE
    # ========================================================

    @classmethod
    def score_candidate(
        cls,
        task: dict,
        candidate: dict,
    ) -> float:

        score = (
            cls._day_score(
                task,
                candidate,
            )
            + cls._buffer_score(
                candidate
            )
            + cls._utilization_score(
                task,
                candidate,
            )
            + cls._block_type_score(
                candidate
            )
        )

        # Requests with higher priority should prefer
        # candidates that satisfy their preferred day.
        priority_score = float(
            task.get(
                "priority_score",
                0,
            )
        )

        if (
            priority_score >= 80
            and str(
                task.get(
                    "preferred_day",
                    "",
                )
            ).strip().lower()
            == str(
                candidate.get(
                    "day",
                    "",
                )
            ).strip().lower()
        ):
            score += 10.0

        return round(
            score,
            2,
        )

    # ========================================================
    # RANK CANDIDATES
    # ========================================================

    def rank_candidates(
        self,
        task: dict,
        candidates: list[dict] | None = None,
    ) -> list[dict]:

        if candidates is None:

            candidates = (
                self.candidate_generator
                .generate_candidates(
                    task
                )
            )

        ranked = []

        for candidate in candidates:

            scored = candidate.copy()

            request_id = (
                self._get_request_id(
                    task
                )
            )

            scored[
                "request_id"
            ] = request_id

            if task.get(
                "task_id"
            ):
                scored[
                    "task_id"
                ] = str(
                    task[
                        "task_id"
                    ]
                )

            scored[
                "match_score"
            ] = self.score_candidate(
                task,
                candidate,
            )

            ranked.append(
                scored
            )

        ranked.sort(
            key=lambda item: (
                item[
                    "match_score"
                ]
            ),
            reverse=True,
        )

        return ranked

    # ========================================================
    # RANK ALL
    # ========================================================

    def rank_for_tasks(
        self,
        tasks: list[dict],
    ) -> dict[str, list[dict]]:

        ranked_candidates = {}

        for task in tasks:

            request_id = (
                self._get_request_id(
                    task
                )
            )

            if not request_id:
                continue

            candidates = (
                self.candidate_generator
                .generate_candidates(
                    task
                )
            )

            ranked_candidates[
                request_id
            ] = self.rank_candidates(
                task,
                candidates,
            )

        return ranked_candidates

    # ========================================================
    # CURRENT API
    # ========================================================

    def rank_for_requests(
        self,
        requests: list[dict],
    ) -> dict[str, list[dict]]:

        return self.rank_for_tasks(
            requests
        )

    # ========================================================
    # BEST
    # ========================================================

    def best_candidate(
        self,
        task: dict,
    ) -> dict | None:

        ranked = self.rank_candidates(
            task
        )

        if not ranked:
            return None

        return ranked[0]