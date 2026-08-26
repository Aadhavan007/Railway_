import pandas as pd


class TrainConflictChecker:
    """
    Checks whether a proposed maintenance block overlaps
    with scheduled train movements on the same corridor.
    """

    def __init__(
        self,
        timetable_path: str = "data/train_timetable.csv",
    ):
        self.timetable_path = timetable_path
        self.timetable = self._load_timetable()

    def _load_timetable(self) -> pd.DataFrame:
        df = pd.read_csv(self.timetable_path)

        required_columns = {
            "train_no",
            "train_name",
            "train_type",
            "sequence",
            "station_id",
            "arrival",
            "departure",
        }

        missing = required_columns - set(df.columns)

        if missing:
            raise ValueError(
                f"Missing timetable columns: {sorted(missing)}"
            )

        return df

    @staticmethod
    def _minutes(value: str) -> int:
        hour, minute = map(int, value.split(":"))
        return hour * 60 + minute

    @staticmethod
    def _time_overlaps(
        start_a: str,
        end_a: str,
        start_b: str,
        end_b: str,
    ) -> bool:

        start_a = TrainConflictChecker._minutes(start_a)
        end_a = TrainConflictChecker._minutes(end_a)

        start_b = TrainConflictChecker._minutes(start_b)
        end_b = TrainConflictChecker._minutes(end_b)

        # Handle blocks/movements crossing midnight.
        if end_a <= start_a:
            end_a += 24 * 60

        if end_b <= start_b:
            end_b += 24 * 60

        # Check both representations for midnight-crossing intervals.
        return (
            start_a < end_b
            and start_b < end_a
        )

    def check_candidate(
        self,
        candidate: dict,
        corridor_station_map: dict[str, tuple[str, str]],
    ) -> dict:
        """
        Check a single block candidate against train movements.

        corridor_station_map:
            {
                "C01": ("ST01", "ST02"),
                "C02": ("ST02", "ST03"),
                ...
            }
        """

        corridor_id = candidate["corridor_id"]

        if corridor_id not in corridor_station_map:
            return {
                **candidate,
                "train_conflict": False,
                "conflicting_trains": [],
                "conflict_count": 0,
            }

        from_station, to_station = corridor_station_map[
            corridor_id
        ]

        corridor_trains = self._find_corridor_trains(
            from_station,
            to_station,
        )

        conflicts = []

        for _, train in corridor_trains.iterrows():

            arrival = str(train["arrival"])
            departure = str(train["departure"])

            if self._time_overlaps(
                candidate["start_time"],
                candidate["end_time"],
                arrival,
                departure,
            ):
                conflicts.append(
                    {
                        "train_no": int(train["train_no"]),
                        "train_name": train["train_name"],
                        "train_type": train["train_type"],
                        "arrival": arrival,
                        "departure": departure,
                    }
                )

        return {
            **candidate,
            "train_conflict": len(conflicts) > 0,
            "conflicting_trains": conflicts,
            "conflict_count": len(conflicts),
        }

    def _find_corridor_trains(
        self,
        from_station: str,
        to_station: str,
    ) -> pd.DataFrame:
        """
        Find trains that travel between the two stations
        consecutively in the timetable.
        """

        matching = []

        for train_no, group in self.timetable.groupby(
            "train_no"
        ):
            group = group.sort_values("sequence")

            rows = group.to_dict("records")

            for index in range(len(rows) - 1):

                current = rows[index]
                next_stop = rows[index + 1]

                if (
                    current["station_id"] == from_station
                    and next_stop["station_id"] == to_station
                ):
                    matching.append(
                        {
                            "train_no": train_no,
                            "train_name": current["train_name"],
                            "train_type": current["train_type"],
                            "arrival": current["departure"],
                            "departure": next_stop["arrival"],
                        }
                    )

        return pd.DataFrame(matching)

    def check_candidates(
        self,
        candidates: list[dict],
        corridor_station_map: dict[str, tuple[str, str]],
    ) -> list[dict]:

        return [
            self.check_candidate(
                candidate,
                corridor_station_map,
            )
            for candidate in candidates
        ]