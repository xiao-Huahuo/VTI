from dataclasses import dataclass, field
import json

@dataclass
class Store:
    rows: list[str] = field(default_factory=list)
    cleared: int = 0

    def add(self, value: str):
        self.rows.append(value)

    def clear(self):
        self.rows.clear()
        self.cleared += 1

    def count(self):
        return len(self.rows)


def memora_partial_retry():
    store = Store()
    # Source-grounded abstraction: one session succeeds, one fails but is caught,
    # then another succeeds. The question-level function returns normally.
    store.add("session-1")
    # session-2 failure is logged and continued
    store.add("session-3")
    first_attempt_partial = list(store.rows)

    # Documented --skip-existing predicate: collection.count() > 0.
    skip_on_retry = store.count() > 0
    if not skip_on_retry:
        store.add("session-2")

    # Search uses the same stable question_<question_id> scope.
    consumed = list(store.rows)
    return {
        "first_attempt_partial": first_attempt_partial,
        "skip_on_retry": skip_on_retry,
        "consumed_after_retry": consumed,
        "complete_sessions_expected": 3,
        "sessions_present": len(consumed),
    }


def memora_direct_force_rebuild():
    store = Store(["stale-old-run"])
    force_rebuild = True

    # Mirrors: if not (force_rebuild or skip_existing): client.clear()
    if not force_rebuild:
        store.clear()

    store.add("new-run")
    return {
        "clear_calls": store.cleared,
        "rows_after_direct_force_rebuild": list(store.rows),
        "stale_survived": "stale-old-run" in store.rows,
    }


def lightmem_partial_resume():
    persistent_backend = Store()
    snapshot_exists = False

    # Interrupted first construction after early persistent writes.
    persistent_backend.add("message-1")
    persistent_backend.add("message-2")

    # MemZero load_memory fallback: any backend memory => loaded.
    has_any = persistent_backend.count() > 0
    load_memory = snapshot_exists or has_any

    construction_skipped = load_memory
    if not construction_skipped:
        persistent_backend.add("message-3")

    # Search uses the same load predicate and persistent scope.
    search_loads = persistent_backend.count() > 0
    return {
        "snapshot_exists": snapshot_exists,
        "backend_has_any": has_any,
        "construction_skipped": construction_skipped,
        "search_loads": search_loads,
        "messages_present": list(persistent_backend.rows),
        "expected_messages": 3,
    }


def lightmem_rerun():
    persistent_backend = Store(["old-state"])
    rerun = True

    # --rerun bypasses load_memory guard; audited wrapper does not reset/delete.
    if not rerun and persistent_backend.count() > 0:
        return {"skipped": True}
    persistent_backend.add("new-state")
    return {
        "skipped": False,
        "rows_after_rerun": list(persistent_backend.rows),
        "old_state_survived": "old-state" in persistent_backend.rows,
    }


def ironcurtain_negative_control():
    temp_db = Store()
    checkpoint = set()
    qid = "q1"
    try:
        temp_db.add("partial-turn")
        raise RuntimeError("simulated mid-question failure")
    except RuntimeError:
        pass
    finally:
        temp_db.clear()

    completed = qid in checkpoint
    return {
        "db_rows_after_failure": list(temp_db.rows),
        "checkpoint_contains_question": completed,
        "resume_reruns": not completed,
    }


if __name__ == "__main__":
    print(json.dumps({
        "memora_partial_retry": memora_partial_retry(),
        "memora_direct_force_rebuild": memora_direct_force_rebuild(),
        "lightmem_partial_resume": lightmem_partial_resume(),
        "lightmem_rerun": lightmem_rerun(),
        "ironcurtain_negative_control": ironcurtain_negative_control(),
    }, indent=2))
