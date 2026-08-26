from datetime import time

import pandas as pd


class DataNormalizer:
    """
    Normalizes the locked RailSync datasets.

    This layer changes data types and whitespace only.
    It does not rename columns or change the dataset schema.
    """

    # ========================================================
    # GENERIC HELPERS
    # ========================================================

    @staticmethod
    def _numeric(
        df: pd.DataFrame,
        columns: list[str],
    ) -> pd.DataFrame:

        result = df.copy()

        for column in columns:
            if column in result.columns:
                result[column] = pd.to_numeric(
                    result[column],
                    errors="coerce",
                )

        return result

    @staticmethod
    def _string(
        df: pd.DataFrame,
        columns: list[str],
    ) -> pd.DataFrame:

        result = df.copy()

        for column in columns:
            if column in result.columns:
                result[column] = (
                    result[column]
                    .astype("string")
                    .str.strip()
                )

        return result

    @staticmethod
    def _boolean(
        df: pd.DataFrame,
        columns: list[str],
    ) -> pd.DataFrame:

        result = df.copy()

        for column in columns:

            if column not in result.columns:
                continue

            result[column] = (
                result[column]
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

        return result

    @staticmethod
    def _time(
        df: pd.DataFrame,
        columns: list[str],
    ) -> pd.DataFrame:

        result = df.copy()

        for column in columns:

            if column not in result.columns:
                continue

            parsed = pd.to_datetime(
                result[column],
                format="%H:%M",
                errors="coerce",
            )

            # IMPORTANT:
            # SQLAlchemy Time columns require Python
            # datetime.time objects, not strings.
            result[column] = parsed.map(
                lambda value: (
                    value.time()
                    if pd.notna(value)
                    else None
                )
            )

        return result

    # ========================================================
    # STATIONS
    # ========================================================

    @classmethod
    def normalize_stations(
        cls,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        result = df.copy()

        result = cls._string(
            result,
            [
                "station_id",
                "station_name",
                "station_type",
                "control_area",
                "electrification",
                "operational_status",
            ],
        )

        return result

    # ========================================================
    # RAILWAY TOPOLOGY
    # ========================================================

    @classmethod
    def normalize_topology(
        cls,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        result = df.copy()

        result = cls._string(
            result,
            [
                "corridor_id",
                "section_name",
                "subsection_id",
                "work_area_id",
                "from_station",
                "to_station",
                "line_type",
                "electrification",
                "direction",
            ],
        )

        return result

    # ========================================================
    # ASSETS
    # ========================================================

    @classmethod
    def normalize_assets(
        cls,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        result = df.copy()

        result = cls._string(
            result,
            [
                "asset_id",
                "department",
                "asset_type",
                "component_type",
                "corridor_id",
                "subsection_id",
                "work_area_id",
                "from_station",
                "to_station",
                "asset_status",
                "criticality_class",
                "typical_issue",
            ],
        )

        return result

    # ========================================================
    # DEPARTMENT REQUESTS
    # ========================================================

    @classmethod
    def normalize_department_requests(
        cls,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        result = df.copy()

        result = cls._numeric(
            result,
            [
                "severity",
                "criticality",
                "overdue_days",
                "estimated_duration_hours",
                "safety_risk",
                "operational_impact",
            ],
        )

        result = cls._boolean(
            result,
            [
                "approval_required",
            ],
        )

        result = cls._string(
            result,
            [
                "request_id",
                "department",
                "planning_type",
                "preferred_day",
                "corridor_id",
                "subsection_id",
                "work_area_id",
                "from_station",
                "to_station",
                "asset_id",
                "asset_type",
                "maintenance_type",
                "issue",
                "urgency",
                "request_status",
                "planning_cycle",
                "request_source",
                "deadline_day",
                "controller_status",
            ],
        )

        return result

    # ========================================================
    # TRAIN MOVEMENTS
    # ========================================================

    @classmethod
    def normalize_train_movements(
        cls,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        result = df.copy()

        result = cls._numeric(
            result,
            [
                "train_no",
                "minimum_maintenance_buffer_minutes",
            ],
        )

        result = cls._time(
            result,
            [
                "entry_time",
                "exit_time",
            ],
        )

        result = cls._string(
            result,
            [
                "movement_id",
                "day",
                "corridor_id",
                "subsection_id",
                "from_station",
                "to_station",
                "train_type",
                "line_id",
                "movement_status",
                "direction",
                "movement_source",
            ],
        )

        return result

    # ========================================================
    # BLOCK AVAILABILITY
    # ========================================================

    @classmethod
    def normalize_block_availability(
        cls,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        result = df.copy()

        result = cls._numeric(
            result,
            [
                "safety_buffer_minutes",
            ],
        )

        result = cls._boolean(
            result,
            [
                "available",
                "derived_safe_window",
            ],
        )

        result = cls._time(
            result,
            [
                "start_time",
                "end_time",
            ],
        )

        result = cls._string(
            result,
            [
                "block_id",
                "day",
                "corridor_id",
                "subsection_id",
                "work_area_id",
                "from_station",
                "to_station",
                "block_type",
                "availability_source",
            ],
        )

        return result

    # ========================================================
    # WORK REQUIREMENTS
    # ========================================================

    @classmethod
    def normalize_work_requirements(
        cls,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        result = df.copy()

        result = cls._numeric(
            result,
            [
                "minimum_duration_hours",
                "maximum_duration_hours",
                "project_safety_buffer_minutes",
            ],
        )

        result = cls._boolean(
            result,
            [
                "requires_controller_approval",
            ],
        )

        result = cls._string(
            result,
            [
                "department",
                "maintenance_type",
                "planning_class",
                "coordination_scope",
            ],
        )

        return result

    # ========================================================
    # NORMALIZE ALL DATASETS
    # ========================================================

    @classmethod
    def normalize_all(
        cls,
        datasets: dict[str, pd.DataFrame],
    ) -> dict[str, pd.DataFrame]:

        required = {
            "stations",
            "topology",
            "assets",
            "department_requests",
            "train_movements",
            "block_availability",
            "work_requirements",
        }

        missing = required - set(datasets)

        if missing:
            raise ValueError(
                f"Missing datasets: {sorted(missing)}"
            )

        return {
            "stations": cls.normalize_stations(
                datasets["stations"]
            ),

            "topology": cls.normalize_topology(
                datasets["topology"]
            ),

            "assets": cls.normalize_assets(
                datasets["assets"]
            ),

            "department_requests": (
                cls.normalize_department_requests(
                    datasets["department_requests"]
                )
            ),

            "train_movements": (
                cls.normalize_train_movements(
                    datasets["train_movements"]
                )
            ),

            "block_availability": (
                cls.normalize_block_availability(
                    datasets["block_availability"]
                )
            ),

            "work_requirements": (
                cls.normalize_work_requirements(
                    datasets["work_requirements"]
                )
            ),
        }

    # ========================================================
    # BACKWARD-COMPATIBLE METHOD
    # ========================================================

    @classmethod
    def normalize_maintenance_tasks(
        cls,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Backward-compatible alias.

        The old project called the request dataset
        'maintenance_tasks'. The locked dataset now calls it
        'department_requests'.
        """

        return cls.normalize_department_requests(df)