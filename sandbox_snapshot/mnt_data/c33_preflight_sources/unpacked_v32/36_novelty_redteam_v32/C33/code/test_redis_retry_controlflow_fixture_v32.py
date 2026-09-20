from __future__ import annotations

import asyncio
import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("redis_retry_controlflow_fixture_v32.py")
spec = importlib.util.spec_from_file_location("fixture", SCRIPT)
fixture = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = fixture
spec.loader.exec_module(fixture)


def test_user_scope_is_stable_for_resume():
    assert fixture.user_id_for("same", 3) == fixture.user_id_for("same", 3)
    assert fixture.user_id_for("same", 3) != fixture.user_id_for("other", 3)


def test_scope_escaping_matches_frozen_mem0_shape():
    assert fixture.session_scope("a&b=c%") == "user_id=a%26b%3Dc%25"


def test_mid_ingest_retry_reuses_sidecar_after_vector_reset():
    result = asyncio.run(fixture.mid_ingest_retry_case())
    assert result["trigger_reached"] is True
    assert len(result["attempt_starts"]) == 2
    assert result["attempt_starts"][1]["message_count_after_reset"] > 0
    assert result["attempt_starts"][1]["vector_count_after_reset"] == 0
    assert result["attempt2_first_add_last_k"] > 0


def test_crash_resume_reuses_same_user_scope():
    result = asyncio.run(fixture.crash_resume_case())
    assert result["trigger_reached"] is True
    assert result["user_id_equal"] is True
    assert result["after_resume_native_reset_message_count"] > 0
    assert result["after_resume_native_reset_vector_count"] == 0
    assert result["resumed_first_add_last_k"] > 0
    assert result["clean_first_add_last_k"] == 0


def test_full_fixture_has_no_downstream_claim():
    result = asyncio.run(fixture.run())
    assert result["all_routes_trigger"] is True
    assert result["downstream_llm_effect"] == "UNVERIFIED"
