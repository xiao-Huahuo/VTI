from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal
import json

EvidenceKind = Literal["source", "trace", "source+trace"]


@dataclass(frozen=True)
class SurfaceReceipt:
    surface: str
    scope: str
    behaviorally_active: bool
    activity_evidence: EvidenceKind
    clean_predicate: str
    pre: dict[str, Any]
    reset_action: str
    post: dict[str, Any]
    predicate_holds: bool
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ResetReceipt:
    benchmark: str
    benchmark_commit: str
    provider: str
    provider_version: str
    trial_id: str
    surfaces: list[SurfaceReceipt]

    @property
    def behaviorally_complete(self) -> bool:
        active = [s for s in self.surfaces if s.behaviorally_active]
        return bool(active) and all(s.predicate_holds for s in active)

    def to_json(self) -> str:
        payload = asdict(self)
        payload["behaviorally_complete"] = self.behaviorally_complete
        return json.dumps(payload, sort_keys=True, indent=2)
