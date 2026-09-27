# C33 literature lineage across versions

Date: 2026-09-27. Scope: continuity of the **literature and novelty argument** across historical versions; experimental outcomes are outside this audit. This is not a full-text systematic review.

## Short answer

The **main intellectual line does connect**: early reset concerns were narrowed by the V32 novelty red-team; `IDEA.md` now avoids claiming the first reset failure or first cross-unit separation, and positions VTI as a memory-benchmark-specific interventional audit with stochastic calibration and evaluation consequences. However, the **citation chain is not yet publication-ready**. Some early V32 prior art did not carry into the current IDEA text, the V57 statistical method lacks its foundational citations, and papers posted in July–September 2026 require a fresh overlap analysis.

## Version-to-literature crosswalk

| Research stage | Literature position established | Continuity today | Required repair |
| --- | --- | --- | --- |
| V28–V31 reset/state-surface framing | Reset completeness and state receipts as a practical issue. | Preserved as background and motivation; not claimed as first discovery in the current IDEA. | Separate original implementation observations from already public Mem0 defects. |
| V32 novelty red-team | [Agentic Benchmark Checklist](https://arxiv.org/abs/2507.02825), [Cross-Unit Separation](https://arxiv.org/abs/2608.14940), [MemSecBench](https://arxiv.org/abs/2607.27080) and other sources ruled out generic “reset must be verified” novelty. | Current `IDEA.md` explicitly retains the Cross-Unit Separation boundary, but **does not name Agentic Benchmark Checklist or MemSecBench**. | Carry both into the paper's Related Work / claim ledger; maintain the V32 limitation that matched branching and backend receipts alone are not novel. |
| V37–V39 public-artifact forensics | Prior public system and benchmark claims were inspected in historical source-provenance records. | Historical records exist under `history/`; there is no consolidated bibliography/claim table connecting them to current contributions. | Extract exact artifact versions, URLs, dates and claim limits into a current source ledger. |
| V42–V55 Mem0/Redis/MemArena line | Real integration evidence motivates memory-specific benchmark trial isolation, distinct from generic agent-evaluation hygiene. | Current `IDEA.md` correctly cites the danger of known Mem0 reset issues, [MemDelta](https://arxiv.org/abs/2606.29914), [ForgetEval](https://arxiv.org/abs/2606.15903) and [Automated Benchmark Auditing](https://arxiv.org/abs/2605.26079). | Tie each paper claim to a primary reference and avoid universalizing platform-specific Mem0 issues; the Qdrant issue's own correction is explicit. |
| V56 LangMem-Local | Independent provider raises a stochastic clean-control problem. | Method motivation flows naturally from IDEA's stochastic-null discussion. | Do not treat V56 as a cross-backend isolation result or cite the LangMem package as proof of causal generality. |
| V57 proposed randomization/statistics | Fisher sharp-null testing, energy distance and 2-of-3 partial conjunction are proposed as established tools applied to this audit. | Statistical code and synthetic tests exist, but current IDEA/active docs do **not cite the foundational methods**. | Add [Fisher randomization / sharp-null validity](https://www.tandfonline.com/doi/full/10.1080/01621459.2020.1750415), [energy statistics](https://www.sciencedirect.com/science/article/pii/S0378375813000633), and [Benjamini–Heller partial conjunction](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1541-0420.2007.00984.x). Claim novelty for the **experimental application/contract**, not these statistical formulas. |

## Newly adjacent papers not integrated into IDEA

- [A-TMA](https://arxiv.org/abs/2607.01935): explicitly separates memory-bank, retrieval and answer failures. It challenges any claim that VTI first discovered this endpoint hierarchy; VTI must emphasize **trial-boundary predecessor intervention**.
- [Scope Before You Persist](https://arxiv.org/abs/2609.29144) (submitted 2026-09-24): scope-matched certification and cross-family persistent-skill interference. Different unit of analysis, but its scope/certification framing is close enough to require full-text claim mapping before an A-level novelty claim.
- [DolphinBench](https://arxiv.org/abs/2609.24971): task-level memory evaluation with cost/latency; relevant to explaining why downstream consequences matter. Not a direct trial-isolation study based on the checked abstract.
- Historical V32 unresolved: **Stopping Is Not Containing** was noted by title but full text was not located. It should not be described substantively until acquired and inspected.

## Cross-version wording conflicts to avoid in the paper

1. Early docs sometimes treat a native isolation “PASS” as a safe backend. The current V57 proposal correctly says **nonsignificance is not an isolation certificate**. Preserve old labels as historical protocol outputs, but use the newer claim boundary in paper prose.
2. The user's original `IDEA.md` has a dated status paragraph saying V55 has 0/12 outcomes; that is historical drafting context. Cite `CURRENT_STATE.json` and terminal receipts for current status, and preserve the original idea text.
3. “Cross-trial memory” in agent-learning papers can mean **intentionally beneficial memory across attempts**. C33 studies **unintended dependence between benchmark evaluation units**. Define the term each time so unrelated prior work is not misclassified.

## Publication-readiness action

**2026-09-27 update:** a 20-entry DOI-registry-backed starter `docs/literature/references.bib` and current claim-to-citation matrix `docs/literature/RELATED_WORK_CURRENT.md` now exist. Cross-Unit Separation, A-TMA and Scope Before You Persist have targeted primary full-text comparisons. Before submission, normalize conference/venue metadata, finish full-text checks on remaining papers and repeat a recent-literature search. The version trail now has an active citation bridge, but final Related Work is **not yet closed**.
