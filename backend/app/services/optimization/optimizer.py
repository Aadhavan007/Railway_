from dataclasses import dataclass

from ortools.sat.python import cp_model

from app.services.optimization.constraints import (
    OptimizationConstraints,
)

from app.services.optimization.objectives import (
    OptimizationObjectives,
)


@dataclass
class OptimizationResult:
    selected_tasks: list[dict]
    total_tasks: int
    total_selected: int
    objective_value: float
    status: str


class BlockOptimizer:
    """
    CP-SAT optimizer for RailSync maintenance scheduling.

    Current request schema:
        request_id

    Legacy compatibility:
        task_id

    Hard constraints:
        - A request may be scheduled at most once.
        - A physical block may be assigned at most once.
        - Two maintenance tasks cannot overlap on the
          same corridor on the same date.

    Objective:
        Maximize maintenance priority and block quality
        while minimizing operational disruption.
    """

    def __init__(self):

        self.model = (
            cp_model.CpModel()
        )

        self.constraints = (
            OptimizationConstraints()
        )

        self.objectives = (
            OptimizationObjectives()
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
    # TIME HELPERS
    # ========================================================

    @staticmethod
    def _minutes(
        value,
    ) -> int:

        if value is None:
            return 0

        text = str(
            value
        ).strip()

        if not text:
            return 0

        parts = text.split(":")

        hour = int(
            parts[0]
        )

        minute = int(
            parts[1]
        )

        return (
            hour * 60
            + minute
        )

    @classmethod
    def _time_interval(
        cls,
        candidate: dict,
    ) -> tuple[int, int]:

        start = cls._minutes(
            candidate.get(
                "start_time"
            )
        )

        end = cls._minutes(
            candidate.get(
                "end_time"
            )
        )

        # Handle midnight crossing.
        if end <= start:
            end += 24 * 60

        return (
            start,
            end,
        )

    @classmethod
    def _candidate_intervals_overlap(
        cls,
        first: dict,
        second: dict,
    ) -> bool:
        """
        Return True when two candidates occupy overlapping
        maintenance time on the same corridor and date.
        """

        first_date = str(
            first.get(
                "date",
                "",
            )
        )[:10]

        second_date = str(
            second.get(
                "date",
                "",
            )
        )[:10]

        first_corridor = str(
            first.get(
                "corridor_id",
                "",
            )
        )

        second_corridor = str(
            second.get(
                "corridor_id",
                "",
            )
        )

        # Different dates cannot conflict.
        if first_date != second_date:
            return False

        # Different corridors cannot conflict under this
        # corridor-level constraint.
        if first_corridor != second_corridor:
            return False

        first_start, first_end = (
            cls._time_interval(
                first
            )
        )

        second_start, second_end = (
            cls._time_interval(
                second
            )
        )

        return (
            first_start < second_end
            and second_start < first_end
        )

    # ========================================================
    # OPTIMIZE
    # ========================================================

    def optimize(
        self,
        tasks: list[dict],
        ranked_candidates: dict[
            str,
            list[dict],
        ],
    ) -> OptimizationResult:

        # ----------------------------------------------------
        # RESET MODEL
        # ----------------------------------------------------

        self.model = (
            cp_model.CpModel()
        )

        variables = {}

        candidate_data = {}

        # ----------------------------------------------------
        # TASK LOOKUP
        # ----------------------------------------------------

        task_lookup = {}

        for task in tasks:

            request_id = (
                self._get_request_id(
                    task
                )
            )

            if request_id:

                task_lookup[
                    request_id
                ] = task

        # ----------------------------------------------------
        # CREATE DECISION VARIABLES
        # ----------------------------------------------------

        for task in tasks:

            request_id = (
                self._get_request_id(
                    task
                )
            )

            if not request_id:
                continue

            candidates = (
                ranked_candidates.get(
                    request_id,
                    [],
                )
            )

            for index, candidate in enumerate(
                candidates
            ):

                # --------------------------------------------
                # HARD CANDIDATE VALIDATION
                # --------------------------------------------

                if not (
                    self.constraints
                    .candidate_is_valid(
                        task,
                        candidate,
                    )
                ):
                    continue

                variable_name = (
                    f"x_{request_id}_{index}"
                )

                variable = (
                    self.model.NewBoolVar(
                        variable_name
                    )
                )

                variables[
                    (
                        request_id,
                        index,
                    )
                ] = variable

                candidate_data[
                    (
                        request_id,
                        index,
                    )
                ] = candidate

        # ----------------------------------------------------
        # CONSTRAINT 1
        # ONE ASSIGNMENT PER REQUEST
        # ----------------------------------------------------

        for request_id in task_lookup:

            request_variables = [
                variable
                for (
                    candidate_request_id,
                    _,
                ), variable
                in variables.items()
                if (
                    candidate_request_id
                    == request_id
                )
            ]

            if request_variables:

                self.model.Add(
                    sum(
                        request_variables
                    )
                    <= 1
                )

        # ----------------------------------------------------
        # CONSTRAINT 2
        # ONE ASSIGNMENT PER PHYSICAL BLOCK
        # ----------------------------------------------------

        block_variables = {}

        for key, variable in (
            variables.items()
        ):

            candidate = (
                candidate_data[key]
            )

            block_id = str(
                candidate.get(
                    "block_id"
                )
            )

            block_variables.setdefault(
                block_id,
                [],
            ).append(
                variable
            )

        for (
            block_id,
            block_vars,
        ) in block_variables.items():

            self.model.Add(
                sum(
                    block_vars
                )
                <= 1
            )

        # ----------------------------------------------------
        # CONSTRAINT 3
        # NO SAME-CORRIDOR TIME OVERLAP
        # ----------------------------------------------------
        #
        # Two different blocks may exist on the same
        # corridor. That does NOT mean they can both be
        # used simultaneously.
        #
        # If two candidate intervals overlap on the same
        # corridor and date, they cannot both be selected.
        #

        variable_items = list(
            variables.items()
        )

        for first_index in range(
            len(variable_items)
        ):

            first_key, first_variable = (
                variable_items[
                    first_index
                ]
            )

            first_candidate = (
                candidate_data[
                    first_key
                ]
            )

            for second_index in range(
                first_index + 1,
                len(variable_items),
            ):

                second_key, second_variable = (
                    variable_items[
                        second_index
                    ]
                )

                # Same request is already protected by
                # Constraint 1.
                if (
                    first_key[0]
                    == second_key[0]
                ):
                    continue

                second_candidate = (
                    candidate_data[
                        second_key
                    ]
                )

                if not (
                    self
                    ._candidate_intervals_overlap(
                        first_candidate,
                        second_candidate,
                    )
                ):
                    continue

                # Both assignments cannot be selected.
                self.model.Add(
                    first_variable
                    + second_variable
                    <= 1
                )

        # ----------------------------------------------------
        # OBJECTIVE
        # ----------------------------------------------------

        objective_terms = []

        for (
            key,
            variable,
        ) in variables.items():

            request_id, _ = key

            task = task_lookup.get(
                request_id
            )

            if task is None:
                continue

            candidate = (
                candidate_data[key]
            )

            assignment_value = (
                self.objectives
                .assignment_value(
                    task,
                    candidate,
                )
            )

            objective_terms.append(
                variable
                * assignment_value
            )

        if objective_terms:

            self.model.Maximize(
                sum(
                    objective_terms
                )
            )

        # ----------------------------------------------------
        # SOLVE
        # ----------------------------------------------------

        solver = (
            cp_model.CpSolver()
        )

        solver.parameters.max_time_in_seconds = 10

        status = solver.Solve(
            self.model
        )

        status_name = (
            solver.StatusName(
                status
            )
        )

        # ----------------------------------------------------
        # EXTRACT SOLUTION
        # ----------------------------------------------------

        selected_tasks = []

        if status in (
            cp_model.OPTIMAL,
            cp_model.FEASIBLE,
        ):

            for (
                key,
                variable,
            ) in variables.items():

                if (
                    solver.Value(
                        variable
                    )
                    != 1
                ):
                    continue

                request_id, _ = key

                task = task_lookup.get(
                    request_id
                )

                if task is None:
                    continue

                candidate = (
                    candidate_data[key]
                )

                # --------------------------------------------
                # OPTIONAL OPERATIONAL DATA
                # --------------------------------------------

                traffic_level = str(
                    candidate.get(
                        "traffic_level",
                        "UNKNOWN",
                    )
                )

                try:

                    expected_train_count = int(
                        candidate.get(
                            "expected_train_count",
                            0,
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    expected_train_count = 0

                try:

                    safety_buffer_minutes = float(
                        candidate.get(
                            "safety_buffer_minutes",
                            0,
                        )
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    safety_buffer_minutes = 0.0

                # --------------------------------------------
                # FINAL SCHEDULE RECORD
                # --------------------------------------------

                selected_tasks.append(
                    {
                        # Identity
                        "request_id": request_id,
                        "task_id": request_id,

                        # Maintenance
                        "department": task.get(
                            "department"
                        ),

                        "asset_type": task.get(
                            "asset_type"
                        ),

                        "maintenance_type": task.get(
                            "maintenance_type"
                        ),

                        # Location
                        "corridor_id": candidate.get(
                            "corridor_id"
                        ),

                        "subsection_id": candidate.get(
                            "subsection_id"
                        ),

                        "work_area_id": candidate.get(
                            "work_area_id"
                        ),

                        "from_station": candidate.get(
                            "from_station"
                        ),

                        "to_station": candidate.get(
                            "to_station"
                        ),

                        # Block
                        "block_id": candidate.get(
                            "block_id"
                        ),

                        "block_type": candidate.get(
                            "block_type"
                        ),

                        "availability_source": candidate.get(
                            "availability_source"
                        ),

                        # Timing
                        "day": candidate.get(
                            "day"
                        ),

                        "date": candidate.get(
                            "date"
                        ),

                        "start_time": candidate.get(
                            "start_time"
                        ),

                        "end_time": candidate.get(
                            "end_time"
                        ),

                        # Safety
                        "derived_safe_window": bool(
                            candidate.get(
                                "derived_safe_window",
                                False,
                            )
                        ),

                        "safety_buffer_minutes": (
                            safety_buffer_minutes
                        ),

                        # Scores
                        "priority_score": float(
                            task.get(
                                "priority_score",
                                0,
                            )
                        ),

                        "match_score": float(
                            candidate.get(
                                "match_score",
                                0,
                            )
                        ),

                        # Operational
                        "traffic_level": (
                            traffic_level
                        ),

                        "expected_train_count": (
                            expected_train_count
                        ),
                    }
                )

        # ----------------------------------------------------
        # OBJECTIVE VALUE
        # ----------------------------------------------------

        objective_value = 0.0

        if status in (
            cp_model.OPTIMAL,
            cp_model.FEASIBLE,
        ):

            objective_value = (
                solver.ObjectiveValue()
            )

        # ----------------------------------------------------
        # RESULT
        # ----------------------------------------------------

        return OptimizationResult(

            selected_tasks=(
                selected_tasks
            ),

            total_tasks=len(
                tasks
            ),

            total_selected=len(
                selected_tasks
            ),

            objective_value=(
                objective_value
            ),

            status=status_name,
        )