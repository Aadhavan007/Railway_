import pandas as pd


class DataCleaner:
    """Cleans raw RailSync CSV data without changing its schema."""

    @staticmethod
    def clean(df: pd.DataFrame) -> pd.DataFrame:
        if df is None:
            raise ValueError("DataFrame cannot be None")

        if df.empty:
            raise ValueError("DataFrame is empty")

        result = df.copy()

        # Remove completely empty rows.
        result = result.dropna(how="all")

        # Normalize column names.
        result.columns = [
            str(column).strip()
            for column in result.columns
        ]

        # Strip surrounding whitespace from string fields.
        for column in result.select_dtypes(
            include=["object"]
        ).columns:
            result[column] = result[column].map(
                lambda value:
                value.strip()
                if isinstance(value, str)
                else value
            )

        return result.reset_index(drop=True)

    @staticmethod
    def remove_duplicate_rows(
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        return df.drop_duplicates().reset_index(
            drop=True
        )