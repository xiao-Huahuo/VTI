from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PAGE_LIMIT = 100
N_OLD = 150
N_NEW = 12
N_PROBES = 20
N_TRIALS = N_OLD + 1

@dataclass(frozen=True)
class Memory:
    id: str
    text: str
    run: str

class Mem0LikeStore:
    """Source-integration fixture for mem0<=2.0.14 delete_all semantics.

    The reset path intentionally mirrors the audited contract:
      memories = vector_store.list(filters=filters)[0]
      for memory in memories: delete(memory.id)
      return success

    The backing list() defaults to top_k=100, matching qdrant in mem0 2.0.11.
    This fixture is implementation/feasibility evidence only.
    """

    def __init__(self, memories: Iterable[Memory] = ()):  # stable insertion order
        self._memories = list(memories)

    def add(self, memory: Memory) -> None:
        self._memories.append(memory)

    def list(self, *, top_k: int = PAGE_LIMIT) -> list[Memory]:
        return list(self._memories[:top_k])

    def get_all(self) -> list[Memory]:
        return list(self._memories)

    def delete(self, memory_id: str) -> None:
        self._memories = [m for m in self._memories if m.id != memory_id]

    def flawed_reset(self) -> dict:
        first_page = self.list()  # no explicit top_k, therefore 100
        for memory in first_page:
            self.delete(memory.id)
        return {"message": "Memories deleted successfully!"}

    def attested_reset(self) -> dict:
        rounds = 0
        while True:
            page = self.list()
            if not page:
                break
            for memory in page:
                self.delete(memory.id)
            rounds += 1
            if rounds > 100:
                raise RuntimeError("reset failed to converge")
        assert not self.get_all()
        return {"message": "Memories deleted successfully!", "verified_empty": True}

    def search(self, token: str, *, top_k: int = 5) -> list[Memory]:
        token = token.lower()
        exact = [m for m in self._memories if token in m.text.lower()]
        others = [m for m in self._memories if m not in exact]
        return (exact + others)[:top_k]


def old_memory(i: int) -> Memory:
    # The last 50 are deliberately probe-addressable residual candidates.
    marker = f"legacy-secret-{i}" if i >= PAGE_LIMIT else f"old-fact-{i}"
    return Memory(id=f"old-{i:03d}", text=f"Historical run memory {marker}", run="run-A")


def new_memory(i: int) -> Memory:
    return Memory(id=f"new-{i:03d}", text=f"Current run neutral memory {i}", run="run-B")


def run_one(*, attested: bool) -> dict:
    store = Mem0LikeStore(old_memory(i) for i in range(N_OLD))
    before = len(store.get_all())
    reset_result = store.attested_reset() if attested else store.flawed_reset()
    after_reset = len(store.get_all())
    residual_old = sum(m.run == "run-A" for m in store.get_all())

    for i in range(N_NEW):
        store.add(new_memory(i))

    hits = []
    for offset in range(N_PROBES):
        idx = PAGE_LIMIT + offset
        token = f"legacy-secret-{idx}"
        results = store.search(token, top_k=5)
        old_hit = next((m for m in results if m.run == "run-A" and token in m.text), None)
        hits.append({
            "probe": token,
            "residual_hit": old_hit is not None,
            "top_ids": [m.id for m in results],
        })

    return {
        "attested": attested,
        "before_reset": before,
        "reset_result": reset_result,
        "after_reset": after_reset,
        "residual_old": residual_old,
        "new_memories": N_NEW,
        "probe_count": N_PROBES,
        "contaminated_probes": sum(int(h["residual_hit"]) for h in hits),
        "contamination_rate": sum(int(h["residual_hit"]) for h in hits) / N_PROBES,
        "hits": hits,
    }


def position_sweep() -> dict:
    # Vary the stale target's list position to show the boundary induced by the
    # provider page limit. This is deterministic mechanism validation, not a
    # population estimate.
    contaminated = 0
    rows = []
    for pos in range(N_TRIALS):
        memories = [Memory(id=f"m-{i:03d}", text=f"memory-{i}", run="run-A") for i in range(N_OLD)]
        target = Memory(id="target", text="residual-canary", run="run-A")
        insert_at = pos
        memories.insert(insert_at, target)
        store = Mem0LikeStore(memories)
        store.flawed_reset()
        survived = any(m.id == "target" for m in store.get_all())
        contaminated += int(survived)
        rows.append({"insert_position": insert_at, "survived": survived})
    return {
        "trials": N_TRIALS,
        "survived": contaminated,
        "survival_rate_over_position_sweep": contaminated / N_TRIALS,
        "interpretation": "mechanism sweep over list position only; not a real-world frequency estimate",
        "rows": rows,
    }


def main() -> None:
    flawed = run_one(attested=False)
    attested = run_one(attested=True)
    sweep = position_sweep()
    assert flawed["after_reset"] == 50
    assert flawed["contaminated_probes"] == N_PROBES
    assert attested["after_reset"] == 0
    assert attested["contaminated_probes"] == 0
    output = {
        "evidence_scope": "source-integration implementation fixture only",
        "source_contract": {
            "mem0_version": "2.0.11 behavior: delete_all calls vector_store.list(filters=filters) without top_k",
            "qdrant_default_top_k": 100,
            "benchmark_reset_contract": "provider.reset(namespace) assumes deletion is complete before ingest",
        },
        "flawed_reset": flawed,
        "attested_reset": attested,
        "position_sweep": sweep,
    }
    out = Path(__file__).resolve().parents[1] / "results" / "c33_reset_fixture.json"
    out.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({
        "flawed_after_reset": flawed["after_reset"],
        "flawed_contaminated_probes": flawed["contaminated_probes"],
        "attested_after_reset": attested["after_reset"],
        "attested_contaminated_probes": attested["contaminated_probes"],
        "position_sweep_survival_rate": sweep["survival_rate_over_position_sweep"],
    }, indent=2))

if __name__ == "__main__":
    main()
