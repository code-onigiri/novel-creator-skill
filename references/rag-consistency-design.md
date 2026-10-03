# Long-Form Consistency RAG Plan Evaluation and Design

## Feasibility Conclusion
Conclusion: Feasible, and significantly helpful for "staying on track during long-term writing", but cannot replace gate proofreading.

Why Feasible:
1. Chapter content, character relationships, and plot lines all reside in local files (indexable).
2. Can automatically re-read relevant chapters before writing, reducing setting conflicts caused by forgetting.
3. Combined with existing gate checks (update memory / consistency / style / copyedit), forms a dual insurance of "retrieval upfront + quality backend".

Boundary:
- RAG can only reduce "missed reading" risk, cannot guarantee 100% logical correctness.
- Retrieval result quality depends on index quality and metadata quality.
- Still need /check-consistency and /copyedit for final adjudication.

## Plan Principles (Referencing Retrieval Best Practices)
1. Metadata filtering: filter by character match, chapter number, keyword overlap.
1.1 Two-stage retrieval: coarse-tune candidate pool (low cost) first, then fine-tune Top-K (high precision).
2. Small retrieval set: default Top-K=4, avoid context overload.
3. Incremental index update: update index once after each chapter.
4. Conditional trigger: skip retrieval automatically for light scenarios, retrieve for complex plots.
5. Fragment priority: return key fragments by default, do not re-read entire chapters.
6. Results are explainable: return hit reasons (character overlap, keyword overlap, chapter recency).
7. Reading order is clear: always read `novel_plan.md` + `novel_state.md` first, then read retrieval hit fragments.
8. Query cache: for the same query + same index signature, prioritize reusing results to reduce redundant overhead.

## Implementation Targets
- Index script: `scripts/plot_rag_retriever.py`
- Index file: `00_memory/retrieval/story_index.json`
- Entity mapping: `00_memory/retrieval/entity_chapter_map.json`
- Chapter metadata sidecar: `00_memory/retrieval/chapter_meta/*.meta.json`
- Pre-writing context suggestion: `00_memory/retrieval/next_plot_context.md`

## Recommended Usage
1. Execute /update-plot-index after each chapter is written
2. Execute /plot-retrieval before writing new plot
3. Then enter /writing
4. After writing, continue the gate check chain: /update-memory -> /check-consistency -> /style-calibration -> /copyedit -> /gate-check