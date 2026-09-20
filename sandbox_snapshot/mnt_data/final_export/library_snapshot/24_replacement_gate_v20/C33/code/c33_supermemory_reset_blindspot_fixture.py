from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DeleteResponse:
    success: bool
    deletedCount: int
    errors: list[dict]

class FakeRemoteSupermemory:
    """Minimal remote state model matching the documented bulk-delete response."""
    def __init__(self):
        self.docs = {
            "doc-1": "run-A alpha",
            "doc-2": "run-A beta",
            "doc-3": "run-A RESIDUAL-SM-CANARY",
        }

    async def delete_bulk(self, **_kwargs):
        # Model a provider-visible partial failure. The adapter under audit does
        # not inspect this response before clearing its local shadow state.
        self.docs.pop("doc-1", None)
        self.docs.pop("doc-2", None)
        return DeleteResponse(
            success=False,
            deletedCount=2,
            errors=[{"id": "doc-3", "error": "simulated provider delete failure"}],
        )

    async def search(self, query: str):
        q=query.lower()
        return [text for text in self.docs.values() if q in text.lower()]

class AuditedAdapterShape:
    """Control-flow shape of Redis benchmark SupermemoryStore.reset()."""
    def __init__(self, remote: FakeRemoteSupermemory):
        self.remote=remote
        self._documents=list(remote.docs.values())
        self._document_ids=set(remote.docs)
        self.last_delete_response=None

    async def reset(self):
        self.last_delete_response = await self.remote.delete_bulk(container_tags=["benchmark-user"])
        # audited adapter clears these unconditionally and does not inspect response
        self._documents.clear()
        self._document_ids.clear()

    async def list_memories(self):
        return list(self._documents)

async def run():
    remote=FakeRemoteSupermemory()
    adapter=AuditedAdapterShape(remote)
    await adapter.reset()
    local_visible=await adapter.list_memories()
    remote_hits=await remote.search("residual-sm-canary")
    result={
        "evidence_scope":"source-integration falsifier only",
        "provider_response":{
            "success":adapter.last_delete_response.success,
            "deletedCount":adapter.last_delete_response.deletedCount,
            "errors":adapter.last_delete_response.errors,
        },
        "adapter_local_memory_count_after_reset":len(local_visible),
        "remote_memory_count_after_reset":len(remote.docs),
        "remote_canary_retrievable":bool(remote_hits),
        "blindspot":len(local_visible)==0 and bool(remote_hits),
    }
    assert result["provider_response"]["success"] is False
    assert result["adapter_local_memory_count_after_reset"] == 0
    assert result["remote_memory_count_after_reset"] == 1
    assert result["blindspot"] is True
    return result

if __name__ == "__main__":
    import asyncio
    out=asyncio.run(run())
    path=Path(__file__).resolve().parents[1]/"results"/"c33_supermemory_blindspot_fixture.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
