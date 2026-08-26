from datetime import date, datetime, timedelta, time
from pathlib import Path
from typing import Any

import pandas as pd


class CandidateGenerator:
    """
    Generates feasible scheduling candidates for the locked
    RailSync datasets.

    Locked schemas:

    Requests:
        request_id
        department
        maintenance_type
        preferred_day
        deadline_day
        corridor_id
        subsection_id
        work_area_id
        estimated_duration_hours

    Blocks:
        block_id
        day
        corridor_id
        subsection_id
        work_area_id
        from_station
        to_station
        start_time
        end_time
        available
        block_type
        availability_source
        derived_safe_window
        safety_buffer_minutes

    Train movements are intentionally NOT treated as safe-window
    validation here. The data contract requires train-conflict
    checking and final safety validation as separate stages.

    Supports the legacy task_id API where practical.
    """

    WEEKDAYS = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    def __init__(
        self,
        block_availability_path: str = "data/railsync_weekly_block_availability.csv",
        work_requirements_path: str = (
            "data/railsync_work_requirements.csv"
        ),
        planning_date: str | date | None = None,
    ):
        self.block_availability_path = (
            block_availability_path
        )

        self.work_requirements_path = (
            work_requirements_path
        )

        self.planning_date = self._parse_planning_date(
            planning_date
        )

        self.blocks = self._load_blocks()

        self.work_requirements = (
            self._load_work_requirements()
        )

        self.blocks_by_corridor = (
            self._index_blocks()
        )

    # ========================================================
    # DATE / DAY HELPERS
    # ========================================================

    @classmethod
    def _parse_planning_date(
        cls,
        value: str | date | None,
    ) -> date:

        if value is None:
            return datetime.now().date()

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        text = str(value).strip()

        return datetime.strptime(
            text[:10],
            "%Y-%m-%d",
        ).date()

    @classmethod
    def _day_index(
        cls,
        day: Any,
    ) -> int | None:

        if day is None:
            return None

        value = str(day).strip().lower()

        for index, weekday in enumerate(
            cls.WEEKDAYS
        ):
            if weekday.lower() == value:
                return index

        return None

    @classmethod
    def _day_name(
        cls,
        day_index: int,
    ) -> str:

        return cls.WEEKDAYS[
            day_index % 7
        ]

    @classmethod
    def _next_date_for_day(
        cls,
        planning_date: date,
        day_name: str,
    ) -> date | None:

        target_index = cls._day_index(
            day_name
        )

        if target_index is None:
            return None

        current_index = planning_date.weekday()

        offset = (
            target_index
            - current_index
        ) % 7

        return planning_date + timedelta(
            days=offset
        )

    @classmethod
    def _within_planning_horizon(
        cls,
        planning_date: date,
        candidate_date: date,
    ) -> bool:

        return (
            planning_date
            <= candidate_date
            <= planning_date + timedelta(days=6)
        )

    # ========================================================
    # LOAD BLOCKS
    # ========================================================

    def _load_blocks(self) -> pd.DataFrame:

        path = Path(
            self.block_availability_path
        )

        if not path.exists():
            raise FileNotFoundError(
                "Block availability dataset not found: "
                f"{path}"
            )

        df = pd.read_csv(path)

        required_columns = {
            "block_id",
            "day",
            "corridor_id",
            "subsection_id",
            "work_area_id",
            "from_station",
            "to_station",
            "start_time",
            "end_time",
            "available",
            "block_type",
            "availability_source",
            "derived_safe_window",
            "safety_buffer_minutes",
        }

        missing = (
            required_columns
            - set(df.columns)
        )

        if missing:
            raise ValueError(
                "Missing block availability columns: "
                f"{sorted(missing)}"
            )

        # ----------------------------------------------------
        # NORMALIZE DAY
        # ----------------------------------------------------

        df["day"] = (
            df["day"]
            .astype("string")
            .str.strip()
        )

        invalid_days = (
            ~df["day"]
            .str.lower()
            .isin(
                [
                    value.lower()
                    for value in self.WEEKDAYS
                ]
            )
        )

        if invalid_days.any():
            raise ValueError(
                "Block availability contains invalid "
                "day values."
            )

        # ----------------------------------------------------
        # NORMALIZE TIME
        # ----------------------------------------------------

        for column in [
            "start_time",
            "end_time",
        ]:

            parsed = pd.to_datetime(
                df[column]
                .astype(str)
                .str.strip(),
                format="%H:%M",
                errors="coerce",
            )

            if parsed.isna().any():

                parsed = pd.to_datetime(
                    df[column]
                    .astype(str)
                    .str.strip(),
                    format="%H:%M:%S",
                    errors="coerce",
                )

            if parsed.isna().any():
                raise ValueError(
                    "Block availability contains invalid "
                    f"{column} values."
                )

            df[column] = parsed.dt.time

        # ----------------------------------------------------
        # AVAILABLE
        # ----------------------------------------------------

        df["available"] = (
            df["available"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(
                {
                    "true": True,
                    "false": False,
                    "1": True,
                    "0": False,
                    "yes": True,
                    "no": False,
                    "y": True,
                    "n": False,
                }
            )
            .fillna(False)
            .astype(bool)
        )

        # ----------------------------------------------------
        # SAFETY BUFFER
        # ----------------------------------------------------

        df["safety_buffer_minutes"] = (
            pd.to_numeric(
                df["safety_buffer_minutes"],
                errors="coerce",
            )
        )

        if df[
            "safety_buffer_minutes"
        ].isna().any():

            raise ValueError(
                "Block availability contains invalid "
                "safety_buffer_minutes."
            )

        if (
            df["safety_buffer_minutes"]
            < 0
        ).any():

            raise ValueError(
                "safety_buffer_minutes cannot "
                "be negative."
            )

        # ----------------------------------------------------
        # NORMALIZE BOOLEAN SAFE-WINDOW FLAG
        # ----------------------------------------------------

        df["derived_safe_window"] = (
            df["derived_safe_window"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(
                {
                    "true": True,
                    "false": False,
                    "1": True,
                    "0": False,
                    "yes": True,
                    "no": False,
                    "y": True,
                    "n": False,
                }
            )
            .fillna(False)
            .astype(bool)
        )

        return df

    # ========================================================
    # LOAD WORK REQUIREMENTS
    # ========================================================

    def _load_work_requirements(
        self,
    ) -> dict[tuple[str, str], dict]:

        path = Path(
            self.work_requirements_path
        )

        if not path.exists():
            raise FileNotFoundError(
                "Work requirements dataset not found: "
                f"{path}"
            )

        df = pd.read_csv(path)

        required_columns = {
            "department",
            "maintenance_type",
            "planning_class",
            "minimum_duration_hours",
            "maximum_duration_hours",
            "project_safety_buffer_minutes",
            "coordination_scope",
            "requires_controller_approval",
        }

        missing = (
            required_columns
            - set(df.columns)
        )

        if missing:
            raise ValueError(
                "Missing work requirements columns: "
                f"{sorted(missing)}"
            )

        requirements = {}

        for _, row in df.iterrows():

            department = str(
                row["department"]
            ).strip()

            maintenance_type = str(
                row["maintenance_type"]
            ).strip()

            minimum = float(
                row["minimum_duration_hours"]
            )

            maximum = float(
                row["maximum_duration_hours"]
            )

            project_buffer = float(
                row[
                    "project_safety_buffer_minutes"
                ]
            )

            requirements[
                (
                    department,
                    maintenance_type,
                )
            ] = {
                "department": department,
                "maintenance_type":
                    maintenance_type,
                "planning_class": str(
                    row["planning_class"]
                ).strip(),
                "minimum_duration_hours":
                    minimum,
                "maximum_duration_hours":
                    maximum,
                "project_safety_buffer_minutes":
                    project_buffer,
                "coordination_scope": str(
                    row["coordination_scope"]
                ).strip(),
                "requires_controller_approval":
                    str(
                        row[
                            "requires_controller_approval"
                        ]
                    ).strip().lower()
                    in {
                        "true",
                        "1",
                        "yes",
                        "y",
                    },
            }

        return requirements

    # ========================================================
    # INDEX BLOCKS
    # ========================================================

    def _index_blocks(
        self,
    ) -> dict[str, list[dict]]:

        index: dict[
            str,
            list[dict],
        ] = {}

        for corridor_id, group in (
            self.blocks.groupby(
                "corridor_id"
            )
        ):

            index[
                str(corridor_id)
            ] = group.to_dict(
                orient="records"
            )

        return index

    # ========================================================
    # GENERIC HELPERS
    # ========================================================

    @staticmethod
    def _duration_hours(
        start: time,
        end: time,
    ) -> float:

        start_minutes = (
            start.hour * 60
            + start.minute
        )

        end_minutes = (
            end.hour * 60
            + end.minute
        )

        if end_minutes <= start_minutes:
            end_minutes += 24 * 60

        return (
            end_minutes
            - start_minutes
        ) / 60

    @staticmethod
    def _parse_date(
        value: Any,
    ) -> date:

        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, date):
            return value

        if value is None:
            raise ValueError(
                "Date is missing."
            )

        text = str(
            value
        ).strip()

        return datetime.strptime(
            text[:10],
            "%Y-%m-%d",
        ).date()

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
    # REQUEST DAY WINDOW
    # ========================================================

    def _request_day_dates(
        self,
        task: dict,
    ) -> tuple[date, date] | None:

        preferred_day = task.get(
            "preferred_day"
        )

        deadline_day = task.get(
            "deadline_day"
        )

        preferred_date = (
            self._next_date_for_day(
                self.planning_date,
                str(preferred_day),
            )
            if preferred_day
            else self.planning_date
        )

        deadline_date = (
            self._next_date_for_day(
                self.planning_date,
                str(deadline_day),
            )
            if deadline_day
            else (
                self.planning_date
                + timedelta(days=6)
            )
        )

        if (
            preferred_date is None
            or deadline_date is None
        ):
            return None

        # If the preferred day falls after the deadline
        # in this seven-day horizon, the request can still
        # be considered from the planning-cycle start.
        if preferred_date > deadline_date:
            preferred_date = (
                self.planning_date
            )

        return (
            preferred_date,
            deadline_date,
        )

    # ========================================================
    # REQUIREMENT LOOKUP
    # ========================================================

    def _get_requirement(
        self,
        task: dict,
    ) -> dict | None:

        department = str(
            task.get(
                "department",
                "",
            )
        ).strip()

        maintenance_type = str(
            task.get(
                "maintenance_type",
                "",
            )
        ).strip()

        return self.work_requirements.get(
            (
                department,
                maintenance_type,
            )
        )

    # ========================================================
    # GENERATE CANDIDATES
    # ========================================================

    def generate_candidates(
        self,
        task: dict,
    ) -> list[dict]:

        corridor_id = task.get(
            "corridor_id"
        )

        if not corridor_id:
            return []

        corridor_id = str(
            corridor_id
        ).strip()

        # ----------------------------------------------------
        # TASK DURATION
        # ----------------------------------------------------

        try:
            duration = float(
                task.get(
                    "estimated_duration_hours",
                    0,
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            return []

        if duration <= 0:
            return []

        # ----------------------------------------------------
        # WORK REQUIREMENT
        # ----------------------------------------------------

        requirement = self._get_requirement(
            task
        )

        if requirement is not None:

            if (
                duration
                < requirement[
                    "minimum_duration_hours"
                ]
            ):
                return []

            if (
                duration
                > requirement[
                    "maximum_duration_hours"
                ]
            ):
                return []

        # ----------------------------------------------------
        # DAY WINDOW
        # ----------------------------------------------------

        day_dates = (
            self._request_day_dates(
                task
            )
        )

        if day_dates is None:
            return []

        earliest_date, latest_date = (
            day_dates
        )

        # ----------------------------------------------------
        # LOCATION
        # ----------------------------------------------------

        subsection_id = task.get(
            "subsection_id"
        )

        work_area_id = task.get(
            "work_area_id"
        )

        corridor_blocks = (
            self.blocks_by_corridor.get(
                corridor_id,
                [],
            )
        )

        results = []

        # ----------------------------------------------------
        # CHECK BLOCKS
        # ----------------------------------------------------

        for block in corridor_blocks:

            if not block.get(
                "available",
                False,
            ):
                continue

            block_day = str(
                block["day"]
            ).strip()

            block_date = (
                self._next_date_for_day(
                    self.planning_date,
                    block_day,
                )
            )

            if block_date is None:
                continue

            if not self._within_planning_horizon(
                self.planning_date,
                block_date,
            ):
                continue

            if (
                block_date
                < earliest_date
                or block_date
                > latest_date
            ):
                continue

            # ------------------------------------------------
            # SUBSECTION
            # ------------------------------------------------

            if (
                subsection_id
                and str(
                    block["subsection_id"]
                )
                != str(
                    subsection_id
                )
            ):
                continue

            # ------------------------------------------------
            # WORK AREA
            # ------------------------------------------------

            if (
                work_area_id
                and str(
                    block["work_area_id"]
                )
                != str(
                    work_area_id
                )
            ):
                continue

            # ------------------------------------------------
            # DURATION
            # ------------------------------------------------

            block_duration = (
                self._duration_hours(
                    block["start_time"],
                    block["end_time"],
                )
            )

            if (
                block_duration
                < duration
            ):
                continue

            # ------------------------------------------------
            # PROJECT SAFETY BUFFER
            # ------------------------------------------------

            block_buffer = float(
                block[
                    "safety_buffer_minutes"
                ]
            )

            requirement_buffer = (
                float(
                    requirement[
                        "project_safety_buffer_minutes"
                    ]
                )
                if requirement is not None
                else 0.0
            )

            safety_buffer = max(
                block_buffer,
                requirement_buffer,
            )

            # ------------------------------------------------
            # RESULT
            # ------------------------------------------------

            results.append(
                {
                    "request_id": (
                        self._get_request_id(
                            task
                        )
                    ),

                    "block_id": str(
                        block["block_id"]
                    ),

                    "day": block_day,

                    # Concrete date is derived from
                    # the supplied planning date.
                    "date": block_date.isoformat(),

                    "corridor_id": corridor_id,

                    "subsection_id": str(
                        block[
                            "subsection_id"
                        ]
                    ),

                    "work_area_id": str(
                        block[
                            "work_area_id"
                        ]
                    ),

                    "from_station": str(
                        block[
                            "from_station"
                        ]
                    ),

                    "to_station": str(
                        block[
                            "to_station"
                        ]
                    ),

                    "start_time": (
                        block[
                            "start_time"
                        ].strftime("%H:%M")
                    ),

                    "end_time": (
                        block[
                            "end_time"
                        ].strftime("%H:%M")
                    ),

                    "available": True,

                    "block_type": str(
                        block[
                            "block_type"
                        ]
                    ),

                    "availability_source": str(
                        block[
                            "availability_source"
                        ]
                    ),

                    # This is informational only.
                    # It is NOT treated as proof of safety.
                    "derived_safe_window": bool(
                        block[
                            "derived_safe_window"
                        ]
                    ),

                    "safety_buffer_minutes": (
                        safety_buffer
                    ),

                    "block_duration_hours": (
                        block_duration
                    ),

                    "task_duration_hours": (
                        duration
                    ),
                }
            )

        return results

    # ========================================================
    # ALL TASKS
    # ========================================================

    def generate_for_tasks(
        self,
        tasks: list[dict],
    ) -> dict[str, list[dict]]:

        candidates = {}

        for task in tasks:

            request_id = (
                self._get_request_id(
                    task
                )
            )

            if not request_id:
                continue

            candidates[
                request_id
            ] = self.generate_candidates(
                task
            )

        return candidates

    # ========================================================
    # CURRENT API
    # ========================================================

    def generate_for_requests(
        self,
        requests: list[dict],
    ) -> dict[str, list[dict]]:

        return self.generate_for_tasks(
            requests
        )