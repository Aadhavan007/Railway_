from typing import Any

from app.services.intelligence.explanation_engine import (
    ExplanationEngine,
)


class DecisionEngine:
    """
    Phase 3 decision layer for RailSync.

    This engine does NOT:
        - calculate priority
        - generate candidates
        - optimize schedules
        - perform safety validation

    Those responsibilities remain with their existing
    engines.

    DecisionEngine combines their outputs into a single,
    human-readable planning decision.

    It supports:
        - scheduled requests
        - unscheduled requests
        - priority explanations
        - selected block information
        - alternative candidates
        - coordination information
        - safety results
    """

    # ========================================================
    # HELPERS
    # ========================================================

    @staticmethod
    def _get_request_id(
        task: dict,
    ) -> str:

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

        return "UNKNOWN"

    @staticmethod
    def _candidate_block_id(
        candidate: dict,
    ) -> str | None:

        block_id = candidate.get(
            "block_id"
        )

        if block_id is None:
            return None

        return str(
            block_id
        )

    @staticmethod
    def _same_candidate_block(
        candidate: dict,
        selected_task: dict,
    ) -> bool:

        candidate_block = (
            candidate.get(
                "block_id"
            )
        )

        selected_block = (
            selected_task.get(
                "block_id"
            )
        )

        if (
            candidate_block is None
            or selected_block is None
        ):
            return False

        return (
            str(candidate_block)
            == str(selected_block)
        )

    # ========================================================
    # PRIORITY EXPLANATION
    # ========================================================

    @classmethod
    def _priority_explanation(
        cls,
        task: dict,
    ) -> dict:

        return (
            ExplanationEngine.explain_task(
                task
            )
        )

    # ========================================================
    # ASSIGNMENT REASONS
    # ========================================================

    @staticmethod
    def _assignment_reasons(
        task: dict,
        selected_task: dict,
        candidates: list[dict],
    ) -> list[str]:

        reasons = []

        # ----------------------------------------------------
        # PRIORITY
        # ----------------------------------------------------

        priority_score = float(
            task.get(
                "priority_score",
                0,
            )
        )

        if priority_score >= 75:
            reasons.append(
                "High maintenance priority"
            )

        elif priority_score >= 50:
            reasons.append(
                "Moderate maintenance priority"
            )

        elif priority_score > 0:
            reasons.append(
                "Request received a valid priority score"
            )

        # ----------------------------------------------------
        # CANDIDATE MATCH
        # ----------------------------------------------------

        match_score = float(
            selected_task.get(
                "match_score",
                0,
            )
        )

        if match_score >= 70:
            reasons.append(
                "Strong block-to-task match"
            )

        elif match_score >= 50:
            reasons.append(
                "Good block-to-task match"
            )

        elif match_score > 0:
            reasons.append(
                "Feasible block match"
            )

        # ----------------------------------------------------
        # DURATION
        # ----------------------------------------------------

        task_duration = float(
            task.get(
                "estimated_duration_hours",
                selected_task.get(
                    "task_duration_hours",
                    0,
                ),
            )
        )

        block_duration = float(
            selected_task.get(
                "block_duration_hours",
                0,
            )
        )

        if (
            block_duration > 0
            and task_duration > 0
        ):

            if block_duration >= task_duration:

                unused = (
                    block_duration
                    - task_duration
                )

                if unused <= 0.5:
                    reasons.append(
                        "Block closely fits the required maintenance duration"
                    )

                else:
                    reasons.append(
                        "Block provides sufficient maintenance duration"
                    )

        # ----------------------------------------------------
        # OPERATIONAL CONDITIONS
        # ----------------------------------------------------

        traffic = str(
            selected_task.get(
                "traffic_level",
                "",
            )
        ).upper()

        if traffic == "LOW":
            reasons.append(
                "Low traffic operational condition"
            )

        elif traffic == "MEDIUM":
            reasons.append(
                "Acceptable traffic operational condition"
            )

        # ----------------------------------------------------
        # SAFETY
        # ----------------------------------------------------

        if selected_task.get(
            "derived_safe_window",
            False,
        ):

            reasons.append(
                "Assignment uses a derived safe maintenance window"
            )

        elif selected_task.get(
            "block_id"
        ):

            reasons.append(
                "Assignment passed scheduling feasibility checks"
            )

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if not reasons:
            reasons.append(
                "Assignment selected by the global optimizer"
            )

        return reasons

    # ========================================================
    # ALTERNATIVES
    # ========================================================

    @staticmethod
    def _alternatives(
        selected_task: dict | None,
        candidates: list[dict],
    ) -> list[dict]:

        alternatives = []

        for candidate in candidates:

            if (
                selected_task
                and DecisionEngine._same_candidate_block(
                    candidate,
                    selected_task,
                )
            ):
                continue

            alternatives.append(
                {
                    "block_id": candidate.get(
                        "block_id"
                    ),
                    "date": candidate.get(
                        "date"
                    ),
                    "day": candidate.get(
                        "day"
                    ),
                    "corridor_id": candidate.get(
                        "corridor_id"
                    ),
                    "subsection_id": candidate.get(
                        "subsection_id"
                    ),
                    "work_area_id": candidate.get(
                        "work_area_id"
                    ),
                    "start_time": candidate.get(
                        "start_time"
                    ),
                    "end_time": candidate.get(
                        "end_time"
                    ),
                    "match_score": float(
                        candidate.get(
                            "match_score",
                            0,
                        )
                    ),
                }
            )

        alternatives.sort(
            key=lambda item: item[
                "match_score"
            ],
            reverse=True,
        )

        return alternatives

    # ========================================================
    # COORDINATION
    # ========================================================

    @classmethod
    def _coordination_for_task(
        cls,
        request_id: str,
        coordination_opportunities: list[dict],
    ) -> list[dict]:

        matches = []

        for opportunity in (
            coordination_opportunities
        ):

            opportunity_tasks = (
                opportunity.get(
                    "tasks",
                    []
                )
            )

            for task in opportunity_tasks:

                candidate_id = (
                    task.get(
                        "request_id",
                        task.get(
                            "task_id"
                        ),
                    )
                )

                if candidate_id is None:
                    continue

                if (
                    str(candidate_id)
                    != str(request_id)
                ):
                    continue

                matches.append(
                    opportunity
                )

                break

        return matches

    # ========================================================
    # SCHEDULED DECISION
    # ========================================================

    @classmethod
    def explain_scheduled(
        cls,
        task: dict,
        selected_task: dict,
        candidates: list[dict],
        safety_result: Any,
        coordination_opportunities: list[dict] | None = None,
    ) -> dict:

        request_id = (
            cls._get_request_id(
                task
            )
        )

        priority_explanation = (
            cls._priority_explanation(
                task
            )
        )

        alternatives = (
            cls._alternatives(
                selected_task,
                candidates,
            )
        )

        reasons = (
            cls._assignment_reasons(
                task,
                selected_task,
                candidates,
            )
        )

        coordination = []

        if coordination_opportunities:
            coordination = (
                cls._coordination_for_task(
                    request_id,
                    coordination_opportunities,
                )
            )

        safety_valid = bool(
            getattr(
                safety_result,
                "valid",
                False,
            )
        )

        safety_penalty = float(
            getattr(
                safety_result,
                "penalty",
                0.0,
            )
        )

        # ----------------------------------------------------
        # FINAL SUMMARY
        # ----------------------------------------------------

        if safety_valid:

            final_summary = (
                f"{request_id} was scheduled successfully "
                f"to block "
                f"{selected_task.get('block_id', 'UNKNOWN')} "
                f"and passed safety validation."
            )

        else:

            final_summary = (
                f"{request_id} was scheduled to block "
                f"{selected_task.get('block_id', 'UNKNOWN')}, "
                f"but the final schedule requires safety review."
            )

        return {
            "request_id": request_id,

            "status": "SCHEDULED",

            "priority": {
                "score": float(
                    priority_explanation.get(
                        "priority_score",
                        task.get(
                            "priority_score",
                            0,
                        ),
                    )
                ),
                "class": priority_explanation.get(
                    "priority_class"
                ),
                "drivers": priority_explanation.get(
                    "drivers",
                    [],
                ),
                "summary": priority_explanation.get(
                    "summary"
                ),
            },

            "assignment": {
                "block_id": selected_task.get(
                    "block_id"
                ),
                "corridor_id": selected_task.get(
                    "corridor_id"
                ),
                "subsection_id": selected_task.get(
                    "subsection_id"
                ),
                "work_area_id": selected_task.get(
                    "work_area_id"
                ),
                "date": selected_task.get(
                    "date"
                ),
                "day": selected_task.get(
                    "day"
                ),
                "start_time": selected_task.get(
                    "start_time"
                ),
                "end_time": selected_task.get(
                    "end_time"
                ),
            },

            "reasons": reasons,

            "alternatives": {
                "count": len(
                    alternatives
                ),
                "items": alternatives,
            },

            "coordination": {
                "count": len(
                    coordination
                ),
                "opportunities": coordination,
            },

            "safety": {
                "valid": safety_valid,
                "penalty": safety_penalty,
            },

            "final_decision": final_summary,
        }

    # ========================================================
    # UNSCHEDULED DECISION
    # ========================================================

    @classmethod
    def explain_unscheduled(
        cls,
        task: dict,
        candidates: list[dict],
        safety_result: Any | None = None,
    ) -> dict:

        request_id = (
            cls._get_request_id(
                task
            )
        )

        priority_explanation = (
            cls._priority_explanation(
                task
            )
        )

        if not candidates:

            reason = (
                "No feasible scheduling candidates "
                "were generated for this request."
            )

        else:

            reason = (
                "Feasible candidates existed, but none "
                "were selected by the global optimizer."
            )

        safety = {
            "valid": True,
            "penalty": 0.0,
        }

        if safety_result is not None:

            safety = {
                "valid": bool(
                    getattr(
                        safety_result,
                        "valid",
                        False,
                    )
                ),
                "penalty": float(
                    getattr(
                        safety_result,
                        "penalty",
                        0.0,
                    )
                ),
            }

        return {
            "request_id": request_id,

            "status": "UNSCHEDULED",

            "priority": {
                "score": float(
                    priority_explanation.get(
                        "priority_score",
                        task.get(
                            "priority_score",
                            0,
                        ),
                    )
                ),
                "class": priority_explanation.get(
                    "priority_class"
                ),
                "drivers": priority_explanation.get(
                    "drivers",
                    [],
                ),
                "summary": priority_explanation.get(
                    "summary"
                ),
            },

            "assignment": None,

            "reasons": [
                reason
            ],

            "alternatives": {
                "count": len(
                    candidates
                ),
                "items": cls._alternatives(
                    None,
                    candidates,
                ),
            },

            "coordination": {
                "count": 0,
                "opportunities": [],
            },

            "safety": safety,

            "final_decision": (
                f"{request_id} remains unscheduled "
                f"and should be considered in a subsequent "
                f"planning cycle."
            ),
        }

    # ========================================================
    # SINGLE DECISION
    # ========================================================

    @classmethod
    def explain(
        cls,
        task: dict,
        selected_task: dict | None,
        candidates: list[dict] | None = None,
        safety_result: Any | None = None,
        coordination_opportunities: list[dict] | None = None,
    ) -> dict:

        candidates = (
            candidates
            or []
        )

        if selected_task is not None:

            return cls.explain_scheduled(
                task=task,
                selected_task=selected_task,
                candidates=candidates,
                safety_result=(
                    safety_result
                    if safety_result is not None
                    else type(
                        "SafetyResult",
                        (),
                        {
                            "valid": True,
                            "penalty": 0.0,
                        },
                    )()
                ),
                coordination_opportunities=(
                    coordination_opportunities
                    or []
                ),
            )

        return cls.explain_unscheduled(
            task=task,
            candidates=candidates,
            safety_result=safety_result,
        )

    # ========================================================
    # BATCH DECISIONS
    # ========================================================

    @classmethod
    def explain_all(
        cls,
        tasks: list[dict],
        ranked_candidates: dict[
            str,
            list[dict],
        ],
        selected_tasks: list[dict],
        safety_result: Any | None = None,
        coordination_opportunities: list[dict] | None = None,
    ) -> list[dict]:
        """
        Generate a decision record for every request.

        This deliberately includes UNSCHEDULED requests too,
        so the frontend can explain the complete planning result.
        """

        selected_by_id = {}

        for selected in selected_tasks:

            request_id = (
                selected.get(
                    "request_id",
                    selected.get(
                        "task_id"
                    ),
                )
            )

            if request_id is None:
                continue

            selected_by_id[
                str(request_id)
            ] = selected

        decisions = []

        for task in tasks:

            request_id = (
                cls._get_request_id(
                    task
                )
            )

            candidates = (
                ranked_candidates.get(
                    request_id,
                    [],
                )
            )

            selected_task = (
                selected_by_id.get(
                    request_id
                )
            )

            decision = cls.explain(
                task=task,
                selected_task=selected_task,
                candidates=candidates,
                safety_result=safety_result,
                coordination_opportunities=(
                    coordination_opportunities
                    or []
                ),
            )

            decisions.append(
                decision
            )

        return decisions

    # ========================================================
    # SUMMARY
    # ========================================================

    @staticmethod
    def summarize(
        decisions: list[dict],
    ) -> dict:

        scheduled = sum(
            decision.get(
                "status"
            ) == "SCHEDULED"
            for decision in decisions
        )

        unscheduled = sum(
            decision.get(
                "status"
            ) == "UNSCHEDULED"
            for decision in decisions
        )

        safety_valid = sum(
            decision.get(
                "safety",
                {},
            ).get(
                "valid",
                False,
            )
            for decision in decisions
            if decision.get(
                "status"
            ) == "SCHEDULED"
        )

        return {
            "total_requests": len(
                decisions
            ),
            "scheduled_requests": scheduled,
            "unscheduled_requests": unscheduled,
            "safety_valid_scheduled": safety_valid,
        }