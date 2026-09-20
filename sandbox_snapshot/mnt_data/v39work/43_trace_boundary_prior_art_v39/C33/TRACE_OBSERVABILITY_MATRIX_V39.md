# Trace Observability Matrix V39

| Lifecycle / memory event | Construction graph | Search graph | First-class MemTrace error label | C33 relevance |
|---|---|---|---|---|
| Per-user provider path selection | Outside graph | Outside graph | No | High |
| Provider instantiation/open existing store | Outside graph | Outside graph | No | High |
| Resume/load predicate | Outside graph | Outside graph | No | High |
| Early skip on accepted saved state | Outside graph; can return before graph | N/A | No | High |
| Reset / fresh-start attestation | No reset event in audited rerun path | N/A | No | High |
| Message extraction/update operations | Inside graph | N/A | Extraction / Update / Deletion | Medium |
| Final flush | Inside construction graph | N/A | No dedicated lifecycle label | Medium |
| Completion marker `save_memory()` | Outside graph | N/A | No | High |
| Provider cleanup | Outside graph | Outside graph | No | High |
| Retrieval operation | Imported graph + traced search | Inside graph | Retrieval | Medium |
| Final response | Later evaluation trace | Imported/extended graph | Response | Medium |
| Pre-run provider-state fingerprint | Not recorded | Not recorded | No | High |
| `rerun` provenance flag | Not recorded in construction graph metadata | Not recorded | No | High |
