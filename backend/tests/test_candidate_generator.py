from app.services.scheduling.candidate_generator import CandidateGenerator


def test_candidate_generator_loads_blocks():
    generator = CandidateGenerator()

    assert len(generator.blocks) > 0


def test_candidate_generation_returns_valid_candidates():
    generator = CandidateGenerator()

    task = {
        "task_id": "TEST-001",
        "corridor_id": "C01",
        "estimated_duration_hours": 2.0,
        "deadline": "2026-08-25",
    }

    candidates = generator.generate_candidates(task)

    assert isinstance(candidates, list)

    for candidate in candidates:
        assert candidate["corridor_id"] == "C01"
        assert candidate["available"] is True
        assert candidate["block_duration_hours"] >= 2.0
        assert candidate["date"] <= "2026-08-25"