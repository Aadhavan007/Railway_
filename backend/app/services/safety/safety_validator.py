from dataclasses import dataclass
from datetime import datetime


@dataclass
class SafetyValidationResult:
    valid: bool
    penalty: float
    violations: list[dict]


class SafetyValidator:
    """
    Deterministic safety validation layer.

    Checks the final optimized maintenance schedule for:
      - overlapping maintenance blocks
      - invalid time windows
      - invalid durations
      - duplicate block assignments

    This layer does not optimize anything.
    It only validates the optimizer's output.
    """

    def __init__(self):
        pass

    @staticmethod
    def _minutes(time_string: str) -> int:
        hour, minute = map(int, time_string.split(":"))
        return hour * 60 + minute

    @classmethod
    def _overlap(cls, task_a: dict, task_b: dict) -> bool:

        if task_a["date"] != task_b["date"]:
            return False

        if task_a["corridor_id"] != task_b["corridor_id"]:
            return False

        start_a = cls._minutes(task_a["start_time"])
        end_a = cls._minutes(task_a["end_time"])

        start_b = cls._minutes(task_b["start_time"])
        end_b = cls._minutes(task_b["end_time"])

        # Handle blocks crossing midnight.
        if end_a <= start_a:
            end_a += 24 * 60

        if end_b <= start_b:
            end_b += 24 * 60

        return (
            start_a < end_b
            and start_b < end_a
        )

    @classmethod
    def _validate_time_window(
        cls,
        task: dict,
    ) -> bool:

        try:
            start = cls._minutes(task["start_time"])
            end = cls._minutes(task["end_time"])

            if start == end:
                return False

            return (
                0 <= start < 24 * 60
                and 0 <= end < 24 * 60
            )

        except (
            KeyError,
            ValueError,
            TypeError,
        ):
            return False

    @classmethod
    def _validate_duration(
        cls,
        task: dict,
    ) -> bool:

        try:
            start = cls._minutes(task["start_time"])
            end = cls._minutes(task["end_time"])

            if end <= start:
                end += 24 * 60

            duration = (
                end - start
            ) / 60

            return duration > 0

        except (
            KeyError,
            ValueError,
            TypeError,
        ):
            return False

    def validate(
        self,
        selected_tasks: list[dict],
    ) -> SafetyValidationResult:

        violations = []

        # --------------------------------------------------
        # CHECK INDIVIDUAL TASKS
        # --------------------------------------------------

        for task in selected_tasks:

            if not self._validate_time_window(task):

                violations.append(
                    {
                        "type": "INVALID_TIME_WINDOW",
                        "task_id": task.get("task_id"),
                        "message": (
                            "Invalid maintenance time window."
                        ),
                    }
                )

            if not self._validate_duration(task):

                violations.append(
                    {
                        "type": "INVALID_DURATION",
                        "task_id": task.get("task_id"),
                        "message": (
                            "Maintenance block has invalid duration."
                        ),
                    }
                )

        # --------------------------------------------------
        # CHECK DUPLICATE BLOCKS
        # --------------------------------------------------

        seen_blocks = {}

        for task in selected_tasks:

            block_id = task.get("block_id")

            if block_id is None:
                continue

            if block_id in seen_blocks:

                previous_task = seen_blocks[block_id]

                violations.append(
                    {
                        "type": "DUPLICATE_BLOCK",
                        "task_id": task.get("task_id"),
                        "conflicting_task_id": previous_task,
                        "block_id": block_id,
                        "message": (
                            "Multiple tasks were assigned "
                            "to the same physical block."
                        ),
                    }
                )

            else:
                seen_blocks[block_id] = task.get(
                    "task_id"
                )

        # --------------------------------------------------
        # CHECK CORRIDOR/TIME OVERLAPS
        # --------------------------------------------------

        for i in range(len(selected_tasks)):

            task_a = selected_tasks[i]

            for j in range(i + 1, len(selected_tasks)):

                task_b = selected_tasks[j]

                if self._overlap(
                    task_a,
                    task_b,
                ):

                    violations.append(
                        {
                            "type": "CORRIDOR_OVERLAP",
                            "task_id": task_a.get(
                                "task_id"
                            ),
                            "conflicting_task_id": (
                                task_b.get("task_id")
                            ),
                            "corridor_id": task_a.get(
                                "corridor_id"
                            ),
                            "message": (
                                "Two maintenance tasks "
                                "overlap on the same corridor."
                            ),
                        }
                    )

        # --------------------------------------------------
        # PENALTY
        # --------------------------------------------------

        penalty = float(
            len(violations) * 10
        )

        return SafetyValidationResult(
            valid=len(violations) == 0,
            penalty=penalty,
            violations=violations,
        )