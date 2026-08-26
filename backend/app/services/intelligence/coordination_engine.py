from collections import defaultdict
from typing import Any


class CoordinationEngine:
    """
    Identifies opportunities to coordinate maintenance requests
    from different departments within the same feasible block.

    Coordination is based on:
    - Same block
    - Same corridor
    - Same subsection
    - Same work area
    - Multiple departments
    - Feasible candidate blocks already generated

    This engine does not modify candidates and does not perform
    global optimization.
    """

    DEPARTMENTS = {
        "Engineering",
        "S&T",
        "Traction",
    }

    def __init__(
        self,
        minimum_departments: int = 2,
        max_tasks_per_department: int = 3,
    ):
        if minimum_departments < 2:
            raise ValueError(
                "minimum_departments must be at least 2."
            )

        if max_tasks_per_department < 1:
            raise ValueError(
                "max_tasks_per_department must be at least 1."
            )

        self.minimum_departments = (
            minimum_departments
        )

        self.max_tasks_per_department = (
            max_tasks_per_department
        )

    # ========================================================
    # GENERIC HELPERS
    # ========================================================

    @staticmethod
    def _get_request_id(
        task: dict,
    ) -> str | None:

        request_id = task.get(
            "request_id"
        )

        if request_id is not None:
            return str(request_id)

        # Backward compatibility
        task_id = task.get(
            "task_id"
        )

        if task_id is not None:
            return str(task_id)

        return None

    @staticmethod
    def _get_department(
        task: dict,
    ) -> str:

        department = task.get(
            "department"
        )

        if department is None:
            return "UNKNOWN"

        return str(
            department
        ).strip()

    @staticmethod
    def _get_corridor(
        item: dict,
    ) -> str | None:

        value = item.get(
            "corridor_id"
        )

        if value is None:
            return None

        return str(
            value
        ).strip()

    @staticmethod
    def _get_subsection(
        item: dict,
    ) -> str | None:

        value = item.get(
            "subsection_id"
        )

        if value is None:
            return None

        return str(
            value
        ).strip()

    @staticmethod
    def _get_work_area(
        item: dict,
    ) -> str | None:

        value = item.get(
            "work_area_id"
        )

        if value is None:
            return None

        return str(
            value
        ).strip()

    @staticmethod
    def _get_priority_score(
        task: dict,
    ) -> float:

        value = task.get(
            "priority_score",
            0,
        )

        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return 0.0

    # ========================================================
    # LOCATION MATCHING
    # ========================================================

    @classmethod
    def _same_location(
        cls,
        first: dict,
        second: dict,
    ) -> bool:
        """
        Checks whether two candidate blocks refer to the
        same physical maintenance location.
        """

        first_corridor = cls._get_corridor(
            first
        )

        second_corridor = cls._get_corridor(
            second
        )

        if (
            first_corridor is None
            or second_corridor is None
            or first_corridor != second_corridor
        ):
            return False

        first_subsection = cls._get_subsection(
            first
        )

        second_subsection = cls._get_subsection(
            second
        )

        if (
            first_subsection
            and second_subsection
            and first_subsection != second_subsection
        ):
            return False

        first_work_area = cls._get_work_area(
            first
        )

        second_work_area = cls._get_work_area(
            second
        )

        if (
            first_work_area
            and second_work_area
            and first_work_area != second_work_area
        ):
            return False

        return True

    # ========================================================
    # BLOCK INDEX
    # ========================================================

    def _build_block_index(
        self,
        task_candidates: dict[str, list[dict]],
        tasks: list[dict],
    ) -> dict[str, list[dict]]:
        """
        Creates an index:

            block_id -> tasks that can use that block

        Each indexed entry contains both the task and its
        candidate block information.
        """

        task_lookup = {}

        for task in tasks:

            request_id = self._get_request_id(
                task
            )

            if request_id:
                task_lookup[
                    request_id
                ] = task

        block_index = defaultdict(list)

        for request_id, candidates in (
            task_candidates.items()
        ):

            request_id = str(
                request_id
            )

            task = task_lookup.get(
                request_id
            )

            if task is None:
                continue

            for candidate in candidates:

                block_id = candidate.get(
                    "block_id"
                )

                if block_id is None:
                    continue

                block_id = str(
                    block_id
                )

                block_index[
                    block_id
                ].append(
                    {
                        "request_id": request_id,
                        "task": task,
                        "candidate": candidate,
                    }
                )

        return dict(
            block_index
        )

    # ========================================================
    # SELECT TASKS FOR BLOCK
    # ========================================================

    def _select_tasks_for_block(
        self,
        entries: list[dict],
    ) -> list[dict]:
        """
        Selects a bounded number of tasks per department
        for a coordination opportunity.

        Highest-priority requests are selected first.
        """

        by_department = defaultdict(list)

        for entry in entries:

            task = entry["task"]

            department = self._get_department(
                task
            )

            by_department[
                department
            ].append(
                entry
            )

        selected = []

        for department, department_entries in (
            by_department.items()
        ):

            department_entries.sort(
                key=lambda entry: (
                    self._get_priority_score(
                        entry["task"]
                    )
                ),
                reverse=True,
            )

            selected.extend(
                department_entries[
                    : self.max_tasks_per_department
                ]
            )

        return selected

    # ========================================================
    # OPPORTUNITY SCORE
    # ========================================================

    @classmethod
    def _opportunity_score(
        cls,
        entries: list[dict],
    ) -> float:
        """
        Calculates a transparent coordination opportunity
        score.

        Score components:

        - Number of departments involved
        - Priority of the involved requests
        - Shared physical location
        """

        departments = {
            cls._get_department(
                entry["task"]
            )
            for entry in entries
        }

        department_score = min(
            40.0,
            len(departments) * 20.0,
        )

        priority_scores = [
            cls._get_priority_score(
                entry["task"]
            )
            for entry in entries
        ]

        if priority_scores:
            average_priority = (
                sum(priority_scores)
                / len(priority_scores)
            )
        else:
            average_priority = 0.0

        priority_score = (
            average_priority * 0.40
        )

        task_count_score = min(
            20.0,
            max(
                0,
                len(entries) - 1,
            ) * 10.0,
        )

        score = (
            department_score
            + priority_score
            + task_count_score
        )

        return round(
            min(score, 100.0),
            2,
        )

    # ========================================================
    # GROUP BY CORRIDOR
    # ========================================================

    @classmethod
    def group_by_corridor(
        cls,
        opportunities: list[dict],
    ) -> dict[str, list[dict]]:
        """
        Groups coordination opportunities by corridor.
        """

        grouped = defaultdict(list)

        for opportunity in opportunities:

            corridor_id = opportunity.get(
                "corridor_id"
            )

            if corridor_id is None:
                continue

            grouped[
                str(corridor_id)
            ].append(
                opportunity
            )

        return dict(
            grouped
        )

    # ========================================================
    # FIND COORDINATION OPPORTUNITIES
    # ========================================================

    def find_coordination_opportunities(
        self,
        task_candidates: dict[str, list[dict]],
        tasks: list[dict],
    ) -> list[dict]:
        """
        Finds blocks that can accommodate maintenance
        requests from multiple departments.

        Parameters
        ----------
        task_candidates:
            Mapping of request_id -> feasible candidates.

        tasks:
            Original maintenance request dictionaries.

        Returns
        -------
        list[dict]
            Coordination opportunities sorted by score.
        """

        block_index = self._build_block_index(
            task_candidates,
            tasks,
        )

        opportunities = []

        for block_id, entries in (
            block_index.items()
        ):

            # ------------------------------------------------
            # NEED MULTIPLE DEPARTMENTS
            # ------------------------------------------------

            departments = {
                self._get_department(
                    entry["task"]
                )
                for entry in entries
            }

            if (
                len(departments)
                < self.minimum_departments
            ):
                continue

            # ------------------------------------------------
            # SELECT BEST TASKS
            # ------------------------------------------------

            selected = (
                self._select_tasks_for_block(
                    entries
                )
            )

            selected_departments = {
                self._get_department(
                    entry["task"]
                )
                for entry in selected
            }

            if (
                len(selected_departments)
                < self.minimum_departments
            ):
                continue

            # ------------------------------------------------
            # USE FIRST CANDIDATE AS BLOCK METADATA
            # ------------------------------------------------

            primary_candidate = selected[0][
                "candidate"
            ]

            # ------------------------------------------------
            # BUILD TASK INFORMATION
            # ------------------------------------------------

            selected_tasks = []

            for entry in selected:

                task = entry["task"]
                candidate = entry["candidate"]

                selected_tasks.append(
                    {
                        "request_id": (
                            self._get_request_id(
                                task
                            )
                        ),
                        "department": (
                            self._get_department(
                                task
                            )
                        ),
                        "priority_score": (
                            self._get_priority_score(
                                task
                            )
                        ),
                        "asset_type": task.get(
                            "asset_type"
                        ),
                        "maintenance_type": task.get(
                            "maintenance_type"
                        ),
                        "subsection_id": (
                            self._get_subsection(
                                task
                            )
                        ),
                        "work_area_id": (
                            self._get_work_area(
                                task
                            )
                        ),
                        "estimated_duration_hours": (
                            task.get(
                                "estimated_duration_hours"
                            )
                        ),
                        "candidate": candidate,
                    }
                )

            # ------------------------------------------------
            # OPPORTUNITY SCORE
            # ------------------------------------------------

            score = self._opportunity_score(
                selected
            )

            # ------------------------------------------------
            # BUILD OPPORTUNITY
            # ------------------------------------------------

            opportunity = {
                "block_id": str(
                    block_id
                ),
                "date": primary_candidate.get(
                    "date"
                ),
                "day": primary_candidate.get(
                    "day"
                ),
                "start_time": primary_candidate.get(
                    "start_time"
                ),
                "end_time": primary_candidate.get(
                    "end_time"
                ),
                "corridor_id": (
                    self._get_corridor(
                        primary_candidate
                    )
                ),
                "subsection_id": (
                    self._get_subsection(
                        primary_candidate
                    )
                ),
                "work_area_id": (
                    self._get_work_area(
                        primary_candidate
                    )
                ),
                "departments": sorted(
                    selected_departments
                ),
                "department_count": len(
                    selected_departments
                ),
                "task_count": len(
                    selected_tasks
                ),
                "tasks": selected_tasks,
                "opportunity_score": score,
            }

            opportunities.append(
                opportunity
            )

        opportunities.sort(
            key=lambda opportunity: (
                opportunity[
                    "opportunity_score"
                ],
                opportunity[
                    "department_count"
                ],
                opportunity[
                    "task_count"
                ],
            ),
            reverse=True,
        )

        return opportunities

    # ========================================================
    # BEST OPPORTUNITIES
    # ========================================================

    @staticmethod
    def best_opportunities(
        opportunities: list[dict],
        limit: int = 20,
    ) -> list[dict]:
        """
        Returns the highest-scoring coordination
        opportunities.
        """

        if limit <= 0:
            return []

        return sorted(
            opportunities,
            key=lambda opportunity: (
                opportunity.get(
                    "opportunity_score",
                    0,
                )
            ),
            reverse=True,
        )[:limit]