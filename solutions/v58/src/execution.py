"""Prospective execution conditions; old batches are never mixed with these results."""
from audit_freeze import src_and_project, sha

OUTPUT_LIMIT = 8192
SRC, PROJECT = src_and_project()
EXECUTION_AMENDMENT = PROJECT / "study_freeze/V58_EXECUTION_AMENDMENT_20261001.json"
EXPECTED_SHA256 = "a18e512be5a45a815b495ac1237c5d5a6ad94eb8df32346d136f1f66c4f48751"

def verify_execution():
    if sha(EXECUTION_AMENDMENT) != EXPECTED_SHA256:
        raise RuntimeError("Execution amendment identity drift")
    return EXPECTED_SHA256
