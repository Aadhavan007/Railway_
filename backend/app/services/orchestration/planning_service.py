from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from app.services.intelligence.priority_engine import PriorityEngine
from app.services.intelligence.coordination_engine import (
    CoordinationEngine,
)
from app.services.intelligence.decision_engine import (
    DecisionEngine,
)
from app.services.scheduling.block_matcher import BlockMatcher
from app.services.optimization.optimizer import BlockOptimizer
from app.services.safety.safety_validator import SafetyValidator


@dataclass
class PlanningResult:
    planning_date: str
    corridor_id: str | None
    total_tasks: int
    prioritized_tasks: int
    requests_with_candidates: int
    total_candidates: int
    coordination_opportunities: int
    optimization_status: str
    selected_tasks: list[dict]
    safety_valid: bool
    safety_penalty: float

    # Phase 3
    decisions: list[dict]
    decision_summary: dict


class PlanningService:
    """
    Production orchestration layer for RailSync.

    Current pipeline:

        Department Requests
              ↓
        Planning-date validation
              ↓
        Optional corridor filtering
              ↓
        Priority Engine
              ↓
        Candidate Generation
              ↓
        Candidate Ranking
              ↓
        Coordination Engine
              ↓
        CP-SAT Optimizer
              ↓
        Safety Validator
              ↓
        Decision Engine
              ↓
        Final Planning Result

    The service uses the current locked RailSync
    request schema based on `request_id`.
    """

    REQUEST_DATASET = (
        "railsync_department_requests_420.csv"
    )

    def __init__(
        self,
        data_dir: str = "data",
    ):
        self.data_dir = Path(data_dir)

        self.matcher = BlockMatcher()
        self.coordinator = CoordinationEngine()
        self.optimizer = BlockOptimizer()
        self.validator = SafetyValidator()

        # Phase 3
        self.decision_engine = DecisionEngine()

    # ========================================================
    # REQUEST ID
    # ========================================================

    @staticmethod
    def _get_request_id(
        task: dict,
    ) -> str | None:
        """
        Supports the current request_id schema and
        the legacy task_id schema.
        """

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
    # LOAD REQUESTS
    # ========================================================

    def load_tasks(
        self,
    ) -> list[dict]:
        """
        Load the current locked RailSync
        department request dataset.
        """

        path = (
            self.data_dir
            / self.REQUEST_DATASET
        )

        if not path.exists():
            raise FileNotFoundError(
                f"Maintenance request data not found: "
                f"{path}"
            )

        df = pd.read_csv(
            path
        )

        if df.empty:
            raise ValueError(
                f"{self.REQUEST_DATASET} is empty."
            )

        if (
            "request_id"
            not in df.columns
        ):
            raise ValueError(
                f"{self.REQUEST_DATASET} must contain "
                "`request_id`."
            )

        return df.to_dict(
            orient="records"
        )

    # ========================================================
    # DATE FILTER
    # ========================================================

    @staticmethod
    def filter_by_date(
        tasks: list[dict],
        planning_date: str,
    ) -> list[dict]:
        """
        Validate the planning date without discarding
        requests.

        The locked RailSync request dataset uses
        `deadline_day` as a weekday field rather than
        an absolute calendar deadline.

        Actual scheduling feasibility is determined by
        CandidateGenerator against the real block dates.

        Therefore requests must not be discarded here
        based on an assumed absolute deadline field.
        """

        try:
            pd.to_datetime(
                planning_date,
                format="%Y-%m-%d",
                errors="raise",
            )

        except (
            ValueError,
            TypeError,
        ) as exc:

            raise ValueError(
                "planning_date must use "
                "YYYY-MM-DD format."
            ) from exc

        return list(
            tasks
        )

    # ========================================================
    # CORRIDOR FILTER
    # ========================================================

    @staticmethod
    def filter_by_corridor(
        tasks: list[dict],
        corridor_id: str | None,
    ) -> list[dict]:

        if not corridor_id:
            return tasks

        corridor_id = str(
            corridor_id
        )

        return [
            task
            for task in tasks
            if str(
                task.get(
                    "corridor_id"
                )
            )
            == corridor_id
        ]

    # ========================================================
    # PRIORITY
    # ========================================================

    def prioritize(
        self,
        tasks: list[dict],
    ) -> list[dict]:
        """
        Calculate the transparent priority score
        for every request.
        """

        return [
            PriorityEngine.prioritize_task(
                task
            )
            for task in tasks
        ]

    # ========================================================
    # CANDIDATES + RANKING
    # ========================================================

    def generate_candidates(
        self,
        tasks: list[dict],
    ) -> dict[str, list[dict]]:
        """
        Generate candidates once and rank those same
        candidates.

        Priority scores are explicitly carried into
        every candidate so CoordinationEngine can
        use the actual request priority.
        """

        # ----------------------------------------------------
        # Generate candidates once
        # ----------------------------------------------------

        candidates = (
            self.matcher
            .candidate_generator
            .generate_for_requests(
                tasks
            )
        )

        ranked_candidates = {}

        # ----------------------------------------------------
        # Rank existing candidates
        # ----------------------------------------------------

        for task in tasks:

            request_id = (
                self._get_request_id(
                    task
                )
            )

            if not request_id:
                continue

            existing_candidates = (
                candidates.get(
                    request_id,
                    [],
                )
            )

            ranked = (
                self.matcher.rank_candidates(
                    task,
                    existing_candidates,
                )
            )

            # ------------------------------------------------
            # Carry request priority into every candidate.
            # ------------------------------------------------

            priority_score = float(
                task.get(
                    "priority_score",
                    0.0,
                )
            )

            enriched = []

            for candidate in ranked:

                candidate_result = (
                    candidate.copy()
                )

                candidate_result[
                    "request_id"
                ] = request_id

                candidate_result[
                    "priority_score"
                ] = priority_score

                enriched.append(
                    candidate_result
                )

            ranked_candidates[
                request_id
            ] = enriched

        return ranked_candidates

    # ========================================================
    # OPTIMIZATION
    # ========================================================

    def optimize(
        self,
        tasks: list[dict],
        ranked_candidates: dict[
            str,
            list[dict],
        ],
    ):
        """
        Run the global optimizer using the ranked
        feasible candidates.
        """

        return self.optimizer.optimize(
            tasks,
            ranked_candidates,
        )

    # ========================================================
    # MAIN PIPELINE
    # ========================================================

    def run(
        self,
        planning_date: str,
        corridor_id: str | None = None,
    ) -> PlanningResult:

        # ----------------------------------------------------
        # 1. LOAD
        # ----------------------------------------------------

        all_tasks = self.load_tasks()

        # ----------------------------------------------------
        # 2. PLANNING DATE
        # ----------------------------------------------------

        tasks = self.filter_by_date(
            all_tasks,
            planning_date,
        )

        # ----------------------------------------------------
        # 3. CORRIDOR FILTER
        # ----------------------------------------------------

        tasks = self.filter_by_corridor(
            tasks,
            corridor_id,
        )

        total_tasks = len(
            tasks
        )

        # ----------------------------------------------------
        # 4. PRIORITY
        # ----------------------------------------------------

        tasks = self.prioritize(
            tasks
        )

        # ----------------------------------------------------
        # 5. CANDIDATE GENERATION + RANKING
        # ----------------------------------------------------

        ranked_candidates = (
            self.generate_candidates(
                tasks
            )
        )

        requests_with_candidates = sum(
            bool(candidates)
            for candidates
            in ranked_candidates.values()
        )

        total_candidates = sum(
            len(candidates)
            for candidates
            in ranked_candidates.values()
        )

        # ----------------------------------------------------
        # 6. COORDINATION
        # ----------------------------------------------------

        coordination_opportunities = (
            self.coordinator
            .find_coordination_opportunities(
                ranked_candidates,
                tasks,
            )
        )

        # ----------------------------------------------------
        # 7. OPTIMIZATION
        # ----------------------------------------------------

        optimization_result = (
            self.optimize(
                tasks,
                ranked_candidates,
            )
        )

        # ----------------------------------------------------
        # 8. SAFETY VALIDATION
        # ----------------------------------------------------

        safety_result = (
            self.validator.validate(
                optimization_result.selected_tasks
            )
        )

        # ----------------------------------------------------
        # 9. DECISION / EXPLANATION
        # ----------------------------------------------------

        decisions = (
            self.decision_engine.explain_all(
                tasks=tasks,
                ranked_candidates=ranked_candidates,
                selected_tasks=(
                    optimization_result.selected_tasks
                ),
                safety_result=safety_result,
                coordination_opportunities=(
                    coordination_opportunities
                ),
            )
        )

        decision_summary = (
            self.decision_engine.summarize(
                decisions
            )
        )

        # ----------------------------------------------------
        # 10. FINAL RESULT
        # ----------------------------------------------------

        return PlanningResult(

            planning_date=(
                planning_date
            ),

            corridor_id=(
                corridor_id
            ),

            total_tasks=(
                total_tasks
            ),

            prioritized_tasks=(
                len(tasks)
            ),

            requests_with_candidates=(
                requests_with_candidates
            ),

            total_candidates=(
                total_candidates
            ),

            coordination_opportunities=(
                len(
                    coordination_opportunities
                )
            ),

            optimization_status=(
                optimization_result.status
            ),

            selected_tasks=(
                optimization_result.selected_tasks
            ),

            safety_valid=(
                safety_result.valid
            ),

            safety_penalty=(
                safety_result.penalty
            ),

            decisions=(
                decisions
            ),

            decision_summary=(
                decision_summary
            ),
        )


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    service = PlanningService()

    result = service.run(
        planning_date="2026-08-25"
    )

    print(
        "\n"
        "========================================"
    )

    print(
        "       RAILSYNC AI PLANNING RESULT"
    )

    print(
        "========================================"
    )

    print("\nPLANNING DATE:")
    print(
        result.planning_date
    )

    print("\nCORRIDOR:")
    print(
        result.corridor_id
        or "ALL"
    )

    print("\nTOTAL REQUESTS:")
    print(
        result.total_tasks
    )

    print("\nPRIORITIZED REQUESTS:")
    print(
        result.prioritized_tasks
    )

    print("\nREQUESTS WITH CANDIDATES:")
    print(
        result.requests_with_candidates
    )

    print("\nTOTAL CANDIDATES:")
    print(
        result.total_candidates
    )

    print(
        "\nCOORDINATION OPPORTUNITIES:"
    )

    print(
        result.coordination_opportunities
    )

    print("\nOPTIMIZER STATUS:")
    print(
        result.optimization_status
    )

    print("\nSELECTED TASKS:")
    print(
        len(
            result.selected_tasks
        )
    )

    print("\nSAFETY VALID:")
    print(
        result.safety_valid
    )

    print("\nSAFETY PENALTY:")
    print(
        result.safety_penalty
    )

    # --------------------------------------------------------
    # PHASE 3 DECISION SUMMARY
    # --------------------------------------------------------

    print("\nDECISIONS:")
    print(
        len(
            result.decisions
        )
    )

    print("\nSCHEDULED REQUESTS:")
    print(
        result.decision_summary.get(
            "scheduled_requests",
            0,
        )
    )

    print("\nUNSCHEDULED REQUESTS:")
    print(
        result.decision_summary.get(
            "unscheduled_requests",
            0,
        )
    )

    print("\nSAFETY-VALID SCHEDULED:")
    print(
        result.decision_summary.get(
            "safety_valid_scheduled",
            0,
        )
    )

    print(
        "\n========================================"
    )

    print("FINAL SCHEDULE:")

    print(
        "========================================"
    )

    for task in result.selected_tasks:
        print(task)