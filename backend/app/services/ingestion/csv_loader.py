from pathlib import Path

import pandas as pd


class CSVLoader:
    """
    Loads the locked RailSync datasets.

    This class is responsible only for reading CSV files.
    Validation, normalization, and database insertion are
    handled by separate layers.
    """

    BASE_DIR = Path(__file__).resolve().parents[3]
    DATA_DIR = BASE_DIR / "data"

    DATASETS = {
        "stations": "railsync_station_master.csv",
        "topology": "railsync_railway_topology.csv",
        "assets": "railsync_asset_master.csv",
        "department_requests": (
            "railsync_department_requests_420.csv"
        ),
        "train_movements": (
            "railsync_train_movements_7day.csv"
        ),
        "block_availability": (
            "railsync_weekly_block_availability.csv"
        ),
        "work_requirements": (
            "railsync_work_requirements.csv"
        ),
    }

    @classmethod
    def load(
        cls,
        path: str | Path,
    ) -> pd.DataFrame:
        """
        Load one CSV dataset.
        """

        path = Path(path)

        if not path.is_absolute():
            path = cls.BASE_DIR / path

        if not path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {path}"
            )

        if path.suffix.lower() != ".csv":
            raise ValueError(
                f"Expected a CSV file, got: {path.suffix}"
            )

        df = pd.read_csv(path)

        if df.empty:
            raise ValueError(
                f"CSV file is empty: {path}"
            )

        return df

    # ========================================================
    # LOCKED DATASETS
    # ========================================================

    @classmethod
    def load_stations(cls) -> pd.DataFrame:
        return cls.load(
            cls.DATA_DIR
            / cls.DATASETS["stations"]
        )

    @classmethod
    def load_topology(cls) -> pd.DataFrame:
        return cls.load(
            cls.DATA_DIR
            / cls.DATASETS["topology"]
        )

    @classmethod
    def load_assets(cls) -> pd.DataFrame:
        return cls.load(
            cls.DATA_DIR
            / cls.DATASETS["assets"]
        )

    @classmethod
    def load_department_requests(
        cls,
    ) -> pd.DataFrame:
        return cls.load(
            cls.DATA_DIR
            / cls.DATASETS["department_requests"]
        )

    @classmethod
    def load_train_movements(
        cls,
    ) -> pd.DataFrame:
        return cls.load(
            cls.DATA_DIR
            / cls.DATASETS["train_movements"]
        )

    @classmethod
    def load_block_availability(
        cls,
    ) -> pd.DataFrame:
        return cls.load(
            cls.DATA_DIR
            / cls.DATASETS["block_availability"]
        )

    @classmethod
    def load_work_requirements(
        cls,
    ) -> pd.DataFrame:
        return cls.load(
            cls.DATA_DIR
            / cls.DATASETS["work_requirements"]
        )

    # ========================================================
    # LOAD EVERYTHING
    # ========================================================

    @classmethod
    def load_all(cls) -> dict[str, pd.DataFrame]:
        """
        Load all seven locked RailSync datasets.

        Returns:
            {
                "stations": DataFrame,
                "topology": DataFrame,
                "assets": DataFrame,
                "department_requests": DataFrame,
                "train_movements": DataFrame,
                "block_availability": DataFrame,
                "work_requirements": DataFrame,
            }
        """

        return {
            "stations": cls.load_stations(),
            "topology": cls.load_topology(),
            "assets": cls.load_assets(),
            "department_requests": (
                cls.load_department_requests()
            ),
            "train_movements": (
                cls.load_train_movements()
            ),
            "block_availability": (
                cls.load_block_availability()
            ),
            "work_requirements": (
                cls.load_work_requirements()
            ),
        }