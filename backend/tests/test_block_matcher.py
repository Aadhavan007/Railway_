from app.services.scheduling.block_matcher import BlockMatcher


def test_candidates_are_ranked():
    matcher = BlockMatcher()

    task = {
        "task_id": "TEST-001",
        "corridor_id": "C01",
        "estimated_duration_hours": 2.0,
        "deadline": "2026-08-25",
    }

    ranked = matcher.rank_candidates(task)

    assert isinstance(ranked, list)

    if ranked:
        scores = [
            candidate["match_score"]
            for candidate in ranked
        ]

        assert scores == sorted(
            scores,
            reverse=True,
        )


def test_best_candidate_is_top_ranked():
    matcher = BlockMatcher()

    task = {
        "task_id": "TEST-001",
        "corridor_id": "C01",
        "estimated_duration_hours": 2.0,
        "deadline": "2026-08-25",
    }

    ranked = matcher.rank_candidates(task)
    best = matcher.best_candidate(task)

    if ranked:
        assert best == ranked[0]
    else:
        assert best is None