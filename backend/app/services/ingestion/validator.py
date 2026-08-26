from datetime import time

import pandas as pd


class DataValidator:
    """
    Validates the locked RailSync datasets.

    This layer validates structure and basic values.
    It does not modify the data.
    """

    DATASET_REQUIRED_COLUMNS = {
        "stations": {
            "station_id",
            "station_name",
            "station_type",
            "control_area",
            "electrification",
            "operational_status",
        },

        "topology": {
            "corridor_id",
            "section_name",
            "subsection_id",
            "work_area_id",
            "from_station",
            "to_station",
            "line_type",
            "electrification",
            "direction",
        },

        "assets": {
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
        },

        "department_requests": {
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
            "severity",
            "criticality",
            "urgency",
            "overdue_days",
            "estimated_duration_hours",
            "safety_risk",
            "operational_impact",
            "request_status",
            "planning_cycle",
            "request_source",
            "deadline_day",
            "controller_status",
            "approval_required",
        },

        "train_movements": {
            "movement_id",
            "day",
            "corridor_id",
            "subsection_id",
            "from_station",
            "to_station",
            "train_no",
            "train_type",
            "entry_time",
            "exit_time",
            "minimum_maintenance_buffer_minutes",
            "line_id",
            "movement_status",
            "direction",
            "movement_source",
        },

        "block_availability": {
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
        },

        "work_requirements": {
            "department",
            "maintenance_type",
            "planning_class",
            "minimum_duration_hours",
            "maximum_duration_hours",
            "project_safety_buffer_minutes",
            "coordination_scope",
            "requires_controller_approval",
        },
    }

    # ========================================================
    # GENERIC VALIDATION
    # ========================================================

    @classmethod
    def _check_columns(
        cls,
        df: pd.DataFrame,
        dataset_name: str,
    ) -> None:

        if df is None:
            raise ValueError(
                f"{dataset_name} data cannot be None."
            )

        if df.empty:
            raise ValueError(
                f"{dataset_name} dataset is empty."
            )

        required = cls.DATASET_REQUIRED_COLUMNS.get(
            dataset_name
        )

        if required is None:
            raise ValueError(
                f"Unknown dataset: {dataset_name}"
            )

        missing = required - set(df.columns)

        if missing:
            raise ValueError(
                f"{dataset_name} is missing required "
                f"columns: {sorted(missing)}"
            )

    @staticmethod
    def _check_missing_values(
        df: pd.DataFrame,
        columns: list[str],
        dataset_name: str,
    ) -> None:

        for column in columns:

            if column not in df.columns:
                continue

            if df[column].isna().any():

                raise ValueError(
                    f"{dataset_name} contains missing "
                    f"{column} values."
                )

    # ========================================================
    # STATIONS
    # ========================================================

    @classmethod
    def validate_stations(
        cls,
        df: pd.DataFrame,
    ) -> bool:

        cls._check_columns(
            df,
            "stations",
        )

        cls._check_missing_values(
            df,
            ["station_id", "station_name"],
            "stations",
        )

        return True

    # ========================================================
    # TOPOLOGY
    # ========================================================

    @classmethod
    def validate_topology(
        cls,
        df: pd.DataFrame,
    ) -> bool:

        cls._check_columns(
            df,
            "topology",
        )

        cls._check_missing_values(
            df,
            [
                "corridor_id",
                "subsection_id",
                "work_area_id",
                "from_station",
                "to_station",
            ],
            "topology",
        )

        return True

    # ========================================================
    # ASSETS
    # ========================================================

    @classmethod
    def validate_assets(
        cls,
        df: pd.DataFrame,
    ) -> bool:

        cls._check_columns(
            df,
            "assets",
        )

        cls._check_missing_values(
            df,
            [
                "asset_id",
                "department",
                "corridor_id",
                "subsection_id",
                "work_area_id",
            ],
            "assets",
        )

        return True

    # ========================================================
    # DEPARTMENT REQUESTS
    # ========================================================

    @classmethod
    def validate_department_requests(
        cls,
        df: pd.DataFrame,
    ) -> bool:

        cls._check_columns(
            df,
            "department_requests",
        )

        cls._check_missing_values(
            df,
            [
                "request_id",
                "department",
                "corridor_id",
                "subsection_id",
                "work_area_id",
                "maintenance_type",
                "estimated_duration_hours",
                "deadline_day",
            ],
            "department_requests",
        )

        # ----------------------------------------------------
        # NUMERIC VALUES
        # ----------------------------------------------------

        numeric_columns = [
            "severity",
            "criticality",
            "overdue_days",
            "estimated_duration_hours",
            "safety_risk",
            "operational_impact",
        ]

        for column in numeric_columns:

            values = pd.to_numeric(
                df[column],
                errors="coerce",
            )

            if values.isna().any():

                raise ValueError(
                    f"department_requests contains "
                    f"invalid numeric values in "
                    f"{column}."
                )

        # ----------------------------------------------------
        # RANGE CHECKS
        # ----------------------------------------------------

        if (
            pd.to_numeric(
                df["severity"],
                errors="coerce",
            ).lt(1).any()
            or
            pd.to_numeric(
                df["severity"],
                errors="coerce",
            ).gt(5).any()
        ):

            raise ValueError(
                "severity must be between 1 and 5."
            )

        if (
            pd.to_numeric(
                df["criticality"],
                errors="coerce",
            ).lt(1).any()
            or
            pd.to_numeric(
                df["criticality"],
                errors="coerce",
            ).gt(100).any()
        ):

            raise ValueError(
                "criticality must be between 1 and 100."
            )

        if (
            pd.to_numeric(
                df["estimated_duration_hours"],
                errors="coerce",
            ).le(0).any()
        ):

            raise ValueError(
                "estimated_duration_hours must be "
                "greater than zero."
            )

        return True

    # ========================================================
    # TRAIN MOVEMENTS
    # ========================================================

    @classmethod
    def validate_train_movements(
        cls,
        df: pd.DataFrame,
    ) -> bool:

        cls._check_columns(
            df,
            "train_movements",
        )

        cls._check_missing_values(
            df,
            [
                "movement_id",
                "day",
                "corridor_id",
                "subsection_id",
                "from_station",
                "to_station",
                "train_no",
                "entry_time",
                "exit_time",
            ],
            "train_movements",
        )

        numeric_columns = [
            "train_no",
            "minimum_maintenance_buffer_minutes",
        ]

        for column in numeric_columns:

            values = pd.to_numeric(
                df[column],
                errors="coerce",
            )

            if values.isna().any():

                raise ValueError(
                    f"train_movements contains invalid "
                    f"values in {column}."
                )

        # ----------------------------------------------------
        # TIME VALUES
        # ----------------------------------------------------

        for column in [
            "entry_time",
            "exit_time",
        ]:

            invalid = df[column].map(
                lambda value: (
                    not isinstance(value, time)
                )
            )

            if invalid.any():

                raise ValueError(
                    f"train_movements contains invalid "
                    f"{column} values."
                )

        return True

    # ========================================================
    # BLOCK AVAILABILITY
    # ========================================================

    @classmethod
    def validate_block_availability(
        cls,
        df: pd.DataFrame,
    ) -> bool:

        cls._check_columns(
            df,
            "block_availability",
        )

        cls._check_missing_values(
            df,
            [
                "block_id",
                "day",
                "corridor_id",
                "subsection_id",
                "work_area_id",
                "start_time",
                "end_time",
            ],
            "block_availability",
        )

        # ----------------------------------------------------
        # BUFFER
        # ----------------------------------------------------

        buffer_values = pd.to_numeric(
            df["safety_buffer_minutes"],
            errors="coerce",
        )

        if buffer_values.isna().any():

            raise ValueError(
                "block_availability contains invalid "
                "safety_buffer_minutes."
            )

        if buffer_values.lt(0).any():

            raise ValueError(
                "safety_buffer_minutes cannot be negative."
            )

        # ----------------------------------------------------
        # TIME VALUES
        # ----------------------------------------------------

        for column in [
            "start_time",
            "end_time",
        ]:

            invalid = df[column].map(
                lambda value: (
                    not isinstance(value, time)
                )
            )

            if invalid.any():

                raise ValueError(
                    f"block_availability contains invalid "
                    f"{column} values."
                )

        return True

    # ========================================================
    # WORK REQUIREMENTS
    # ========================================================

    @classmethod
    def validate_work_requirements(
        cls,
        df: pd.DataFrame,
    ) -> bool:

        cls._check_columns(
            df,
            "work_requirements",
        )

        cls._check_missing_values(
            df,
            [
                "department",
                "maintenance_type",
                "planning_class",
            ],
            "work_requirements",
        )

        numeric_columns = [
            "minimum_duration_hours",
            "maximum_duration_hours",
            "project_safety_buffer_minutes",
        ]

        for column in numeric_columns:

            values = pd.to_numeric(
                df[column],
                errors="coerce",
            )

            if values.isna().any():

                raise ValueError(
                    f"work_requirements contains invalid "
                    f"values in {column}."
                )

        minimum = pd.to_numeric(
            df["minimum_duration_hours"],
            errors="coerce",
        )

        maximum = pd.to_numeric(
            df["maximum_duration_hours"],
            errors="coerce",
        )

        if (minimum <= 0).any():

            raise ValueError(
                "minimum_duration_hours must be "
                "greater than zero."
            )

        if (maximum < minimum).any():

            raise ValueError(
                "maximum_duration_hours cannot be "
                "less than minimum_duration_hours."
            )

        return True

    # ========================================================
    # VALIDATE EVERYTHING
    # ========================================================

    @classmethod
    def validate_all(
        cls,
        datasets: dict[str, pd.DataFrame],
    ) -> bool:

        validators = {
            "stations": cls.validate_stations,
            "topology": cls.validate_topology,
            "assets": cls.validate_assets,
            "department_requests": (
                cls.validate_department_requests
            ),
            "train_movements": (
                cls.validate_train_movements
            ),
            "block_availability": (
                cls.validate_block_availability
            ),
            "work_requirements": (
                cls.validate_work_requirements
            ),
        }

        missing = (
            set(validators)
            - set(datasets)
        )

        if missing:
            raise ValueError(
                f"Missing datasets: {sorted(missing)}"
            )

        for name, validator in validators.items():
            validator(datasets[name])

        return True

    # ========================================================
    # BACKWARD COMPATIBILITY
    # ========================================================

    @classmethod
    def validate_maintenance_tasks(
        cls,
        df: pd.DataFrame,
    ) -> bool:
        """
        Backward-compatible alias for the old API.
        """

        return cls.validate_department_requests(df)