from amb_public_state_audit_v33 import exact_overall, counterfactual_score, same_id_reuse, trace_substring_match


def test_exact_weighting():
    cats = [
        {"category": "factual-recall", "score": 100, "details": []},
        {"category": "semantic-search", "score": 0, "details": []},
    ]
    # normalized over the included weights: 0.15/(0.15+0.20)
    assert round(exact_overall(cats), 6) == round(100 * 0.15 / 0.35, 6)


def test_trace_flip():
    result = {
        "categories": [
            {
                "category": "selective-forgetting",
                "score": 50,
                "passed": 1,
                "total": 2,
                "details": [
                    {"queryId": "q1", "score": 0, "passed": False},
                    {"queryId": "q2", "score": 1, "passed": True},
                ],
            }
        ]
    }
    cf = counterfactual_score(result, {"q1"}, to_score=1)
    assert cf["categories"][0]["passed"] == 2
    assert cf["categories"][0]["score"] == 100


def test_cross_test_uuid_reuse():
    result = {
        "categories": [
            {"category": "factual-recall", "details": [
                {"testId": "a", "queryId": "qa", "passed": False, "topResults": [{"id": "x", "content": "old"}]},
                {"testId": "b", "queryId": "qb", "passed": True, "topResults": [{"id": "x", "content": "old"}]},
            ]}
        ]
    }
    r = same_id_reuse(result)
    assert r["queries_with_prior_test_id"] == 1
    assert r["queries_all_top_results_prior_test_ids"] == 1
    assert r["passing_queries_all_top_results_prior_test_ids"] == 1
    assert r["unique_reused_ids"] == 1


def test_frozen_substring_semantics():
    row = {"topResults": [{"content": "amb-user-1774992130225 environment"}]}
    r = trace_substring_match(row, ["4"])
    assert r["passes"] is True
