from tests.conftest import auth_header


def test_ai_risk_scoring_calculation_and_explainability(client, seed_test_context):
    admin = seed_test_context["admin"]
    mine_a = seed_test_context["mine_a"]

    res = client.get(f"/api/v1/mines/{mine_a.id}/risk-assessment?recalculate=true", headers=auth_header(admin))
    assert res.status_code == 200
    data = res.json()

    assert data["mine_id"] == mine_a.id
    assert 0.0 <= data["score"] <= 100.0
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    # Verify explainability factors
    factors = data["factors_breakdown"]
    required_factors = [
        "unresolved_hazards",
        "overdue_corrective_actions",
        "compliance_violations",
        "violation_recurrence",
        "inspection_failures",
    ]
    for rf in required_factors:
        assert rf in factors
        detail = factors[rf]
        assert "raw_score" in detail
        assert "weight" in detail
        assert "weighted_score" in detail
        assert "explanation" in detail

    # Verify weights sum up to 1.0
    total_weight = sum(f["weight"] for f in factors.values())
    assert abs(total_weight - 1.0) < 0.001

    # Verify prescriptive recommendations
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) >= 1
