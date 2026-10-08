# Industrial Knowledge Copilot

# Engineering Report — Hybrid Retrieval V2

**Project:** Industrial Knowledge Copilot

**Milestone:** Qdrant-Backed Hybrid Retrieval, Representation
Improvement, and Constraint Parity

**Report Version:** V2

**Status:** Completed

**Final automated test status:** 90 tests passing

**Indexed corpus size:** 154 chunks / 154 Qdrant points

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`

**Embedding dimension:** 384

**Vector similarity metric:** Cosine similarity

------------------------------------------------------------------------

# 1. Purpose of This Report

This report documents the complete Hybrid Retrieval V2 engineering
milestone for the Industrial Knowledge Copilot.

It intentionally records more than the final implementation. The purpose
is to preserve the engineering reasoning, experiments, failures,
rejected alternatives, benchmark changes, and methodological lessons
that produced the current retrieval architecture.

The milestone began after the first Qdrant integration. At that point,
Qdrant could persist vectors and perform metadata-aware dense retrieval,
but the complete query-routed hybrid retrieval architecture still
required integration and validation.

During this work, several distinct retrieval problems were discovered:

-   the hybrid dense branch needed to use Qdrant rather than the earlier
    in-memory dense implementation,
-   Qdrant results needed to be adapted back into the common retrieval
    result representation,
-   metadata constraints needed to remain compatible with hybrid
    retrieval,
-   one procedural held-out query retrieved the correct document but
    ranked the wrong evidence section above the required procedure,
-   a procedural-intent detector appeared promising but did not solve
    the underlying representation problem,
-   generic Procedure-section score boosting fixed one query but harmed
    another,
-   document titles were available structurally but were missing from
    the actual text presented to the embedding model,
-   the existing held-out benchmark stopped being genuinely held out
    once one of its failures was inspected and used during system
    development,
-   and finally, Qdrant and BM25 were discovered to be searching
    different eligibility universes under hard metadata constraints.

The final V2 architecture resolves these known issues without adding an
LLM or hiding retrieval behavior behind a framework.

This document therefore answers not only:

> What does the retrieval system do now?

but also:

> Why does it work this way, what alternatives were tried, and what
> evidence justified each decision?

------------------------------------------------------------------------

# 2. Where Hybrid Retrieval V2 Fits in the Project

The intended end-to-end system remains:

``` text
Canonical industrial data
        ↓
Generated technical documents
        ↓
Semantic chunking + metadata
        ↓
Embedding representation
        ↓
Vector / lexical indexing
        ↓
Query analysis
        ↓
Retrieval routing
        ↓
Metadata-aware candidate selection
        ↓
Dense / hybrid ranking
        ↓
Evidence selection
        ↓
LLM prompt construction
        ↓
Grounded answer generation
        ↓
Citations
        ↓
API / application
```

Hybrid Retrieval V2 sits specifically in the retrieval and
evidence-selection portion of this architecture.

The milestone deliberately remains pre-LLM.

The engineering principle established earlier still applies:

> Retrieval should be independently understandable, testable, and
> measurable before answer generation is introduced.

An LLM can make a weak retrieval system appear convincing because fluent
generation can conceal poor evidence selection. For that reason, this
project continues to treat retrieval quality as an independently
measurable subsystem.

------------------------------------------------------------------------

# 3. Starting Point Before Hybrid Retrieval V2

Before this milestone, the project already contained:

-   a synthetic industrial knowledge domain,
-   canonical YAML source data,
-   generated operation and maintenance manuals,
-   generated troubleshooting guides,
-   generated standard operating procedures,
-   semantic Markdown chunking,
-   structured chunk metadata,
-   SentenceTransformer embeddings,
-   NumPy dense retrieval,
-   BM25 lexical retrieval,
-   reciprocal rank fusion,
-   query analysis,
-   query routing,
-   exact identifier boosting,
-   retrieval evaluation,
-   Qdrant vector persistence,
-   Qdrant metadata payloads,
-   Qdrant metadata filtering,
-   deterministic point IDs,
-   and Qdrant retrieval tests.

The corpus contained:

``` text
154 chunks
```

The embedding model was:

``` text
sentence-transformers/all-MiniLM-L6-v2
```

with:

``` text
Embedding dimension: 384
Maximum sequence length: 256 tokens
```

Qdrant V1 had already established that the vector database was
infrastructure, not a new retrieval strategy.

That distinction is important:

``` text
Dense / lexical / hybrid = retrieval strategies
Qdrant                   = vector storage and vector-search infrastructure
```

Hybrid Retrieval V2 therefore did not attempt to replace hybrid search
with Qdrant. It integrated Qdrant into the dense branch of the existing
hybrid strategy.

------------------------------------------------------------------------

# 4. Retrieval Evolution Before V2

The project had already progressed through several retrieval baselines.

## 4.1 Dense retrieval baseline

The initial dense semantic benchmark produced:

``` text
Hit@1: 0.640
Hit@3: 0.840
Hit@5: 0.880
MRR:   0.743
```

Dense retrieval was strong at semantic paraphrases but weaker on exact
identifiers and some technical lexical distinctions.

## 4.2 BM25 lexical baseline

BM25 produced:

``` text
Hit@1: 0.520
Hit@3: 0.560
Hit@5: 0.640
MRR:   0.558
```

BM25 was weaker overall but valuable for exact lexical matches such as
identifiers, part numbers, and technical terminology.

## 4.3 Naive reciprocal rank fusion

Combining dense and lexical rankings for every query did not
automatically improve the system:

``` text
Hit@1: 0.640
Hit@3: 0.760
Hit@5: 0.840
MRR:   0.705
```

This was an important early lesson:

> Hybrid retrieval is not automatically better merely because it
> combines two retrieval systems.

Weak lexical rankings can dilute strong semantic rankings when fusion is
applied indiscriminately.

## 4.4 Query-routed hybrid V1

The architecture therefore evolved into query-aware routing.

Normal semantic questions used dense retrieval.

Queries containing exact identifiers or part-oriented intent could use
hybrid retrieval.

Identifier-aware boosting was then applied after fusion.

The routed V1 benchmark reached:

``` text
Hit@1: 0.800
Hit@3: 0.960
Hit@5: 1.000
MRR:   0.883
```

The original 12-query held-out checkpoint produced:

``` text
Hit@1: 0.750
Hit@3: 0.750
Hit@5: 0.833
MRR:   0.771
```

These results established the retrieval strategy that Hybrid V2 would
later migrate onto Qdrant.

------------------------------------------------------------------------

# 5. Qdrant V1 as the Immediate Predecessor

The Qdrant integration introduced persistent vector storage and
metadata-aware filtering.

The collection configuration was conceptually:

``` text
Collection: industrial_knowledge
Vector size: 384
Distance: cosine
Storage: local .qdrant directory
```

Each Qdrant point contained:

-   a deterministic UUID5 point ID,
-   the chunk embedding,
-   the chunk ID,
-   document ID,
-   document type,
-   machine models,
-   section title,
-   heading path,
-   revision,
-   effective date,
-   language,
-   related components,
-   related procedures,
-   part numbers,
-   alarm codes,
-   and `contains_spare_parts`.

The `contains_spare_parts` payload field was derived as:

``` python
bool(chunk.part_numbers)
```

Qdrant V1 dev retrieval produced:

``` text
Hit@1: 0.760
Hit@3: 0.960
Hit@5: 1.000
MRR:   0.848
```

The then-held-out Qdrant evaluation produced:

``` text
Hit@1: 0.750
Hit@3: 0.750
Hit@5: 0.750
MRR:   0.750
```

Failures included heldout-003, heldout-010, and heldout-011.

The important architectural conclusion from Qdrant V1 was:

> Qdrant solved persistence and metadata-aware vector candidate
> selection, but it did not eliminate the need for query routing,
> lexical retrieval, fusion, representation design, or evidence-quality
> evaluation.

------------------------------------------------------------------------

# 6. Main Goal of Hybrid Retrieval V2

The primary V2 goal was to integrate the proven routed hybrid strategy
with the new Qdrant infrastructure.

Before V2, the conceptual mismatch was:

``` text
Standalone dense retrieval
        ↓
      Qdrant

Hybrid retrieval
        ↓
old dense implementation + BM25
```

The desired architecture was:

``` text
User query
    ↓
Query analyzer
    ↓
Router
    ├──────────── dense route ──────────────┐
    │                                       ↓
    │                                    Qdrant
    │                                       ↓
    │                                   top results
    │
    └──────────── hybrid route ─────────────┐
                                            ↓
                               ┌────────────┴────────────┐
                               ↓                         ↓
                            Qdrant                     BM25
                             dense                    lexical
                               ↓                         ↓
                               └────────────┬────────────┘
                                            ↓
                                  reciprocal rank fusion
                                            ↓
                                  identifier boosting
                                            ↓
                                        top results
```

This preserved the retrieval strategy while replacing the dense
infrastructure inside hybrid search.

------------------------------------------------------------------------

# 7. Qdrant-Backed HybridRetriever

The central V2 implementation is:

``` text
src/industrial_copilot/retrieval/hybrid_retriever.py
```

Its responsibility is to combine:

``` text
Qdrant dense retrieval
+
BM25 lexical retrieval
+
reciprocal rank fusion
```

The class receives the corpus chunks, a Qdrant client, a user query, its
query embedding, query analysis, `top_k`, and a larger `candidate_k` for
fusion.

The final class no longer performs dense vector search itself. Instead,
it delegates dense search to the vector-store layer.

This maintains a useful separation:

``` text
retrieval/
    retrieval strategy and domain-aware retrieval logic

vector_store/
    Qdrant infrastructure and vector database interaction
```

------------------------------------------------------------------------

# 8. Why an Adapter Was Needed

The existing fusion code expected dense results in the common retrieval
representation:

``` python
SearchResult(
    chunk=Chunk(...),
    score=...,
)
```

Qdrant retrieval intentionally returned a flatter
infrastructure-oriented object such as:

``` python
QdrantSearchResult(
    chunk_id=...,
    score=...,
)
```

Rather than forcing the Qdrant layer to depend on the full in-memory
chunk object, Hybrid V2 introduced an adapter:

``` text
QdrantSearchResult
        ↓
adapt_qdrant_results(...)
        ↓
SearchResult
```

The hybrid retriever maintains a `chunks_by_id` mapping and resolves
each Qdrant result's `chunk_id` back to the canonical `Chunk`.

This preserved the existing rank-fusion interface while keeping the
vector-store layer decoupled from higher-level retrieval objects.

------------------------------------------------------------------------

# 9. Initial Constraint Translation

Hybrid retrieval also needed to translate analyzed query metadata into
Qdrant filters.

The first V2 implementation introduced a Qdrant-oriented constraint
abstraction inside `hybrid_retriever.py`.

The relevant fields were:

``` text
machine_model
alarm_code
procedure_id
part_number
contains_spare_parts
```

Only unambiguous single identifiers were converted into hard filters.

For example:

``` text
exactly one machine model → machine_model constraint
exactly one alarm code    → alarm_code constraint
exactly one procedure ID  → procedure_id constraint
exactly one part number   → part_number constraint
PARTS_LOOKUP intent       → contains_spare_parts=True
```

This conservative behavior avoided inventing ambiguous AND/OR semantics
for queries containing multiple values.

------------------------------------------------------------------------

# 10. Initial Hybrid Retrieval V2 Evaluation

After migrating the hybrid dense branch to Qdrant, the routed
development benchmark produced:

``` text
Hit@1: 0.840
Hit@3: 0.960
Hit@5: 1.000
MRR:   0.895
```

The 12-query held-out benchmark produced:

``` text
Hit@1: 0.917
Hit@3: 0.917
Hit@5: 0.917
MRR:   0.917
```

Eleven of twelve cases were successful at rank 1.

The remaining failure was `heldout-010`:

``` text
I need the controlled steps for checking and calibrating the hydraulic pressure sensor.
```

This became the most important diagnostic case in the next phase.

------------------------------------------------------------------------

# 11. heldout-010: Initial Failure Analysis

The expected evidence was the `Procedure` section of:

``` text
SOP-MNT-003
Hydraulic Pressure Sensor Verification and Calibration
```

Dense inspection showed approximately:

``` text
Rank  Score   Result
----  ------  ---------------------------------------------------------
1     0.6657  SOP-MNT-003 — Purpose and Scope
2     0.6551  MAN-MX200 — Hydraulic Pressure Sensor
3     0.6191  TSG-MX300 — HX-418
4     0.6179  TSG-MX200 — HX-418
5     0.6105  TSG-MX220 — HX-418
6     0.6096  SOP-MNT-003 — Procedure   ← expected evidence
```

The retriever had already found the correct document.

The failure was not a wrong topic. It was:

``` text
correct topic / document
but wrong evidence section ranked above the required procedure
```

This distinction changed the direction of the investigation.

------------------------------------------------------------------------

# 12. Hypothesis 1 --- Perhaps the Query Should Use Hybrid Retrieval

The query did not contain an alarm code, procedure ID, part number, or
other strong lexical identifier. The router therefore selected dense
retrieval.

One possible hypothesis was:

> Maybe procedural queries should be routed to hybrid search because
> BM25 can recognize words such as "steps", "procedure", "checking", and
> "calibrating".

To test this, the same query was forced through hybrid retrieval.

The expected Procedure chunk remained around rank 6.

Therefore:

``` text
Dense route failure ≠ problem solved by hybrid route
```

The evidence suggested that the problem was not primarily routing.

This prevented an unnecessary expansion of hybrid routing rules.

------------------------------------------------------------------------

# 13. Hypothesis 2 --- Introduce a Procedural Intent

A temporary query intent was explored:

``` text
PROCEDURAL_GUIDANCE
```

The idea was to detect conservative procedural phrases such as requests
for steps, instructions, performing a procedure, checking and
calibrating, or replacing a component.

Tests were created for the temporary detector.

The motivation was reasonable:

``` text
Query asks "how / steps"
        ↓
recognize procedural evidence preference
        ↓
prefer Procedure sections
```

However, recognizing the intent alone did not answer the deeper
question:

> How should a Procedure section be preferred without promoting
> unrelated Procedure sections?

The procedural intent therefore became useful as an experiment but did
not justify a production abstraction by itself.

It was eventually removed because no final production behavior consumed
it.

This avoided keeping dead architecture merely because tests had once
been written for it.

------------------------------------------------------------------------

# 14. Hypothesis 3 --- Boost Every Procedure Section

The next experiment tested a direct evidence-type preference.

Conceptually:

``` text
if query is procedural
and result.section_title == "Procedure":
    add score boost
```

A relatively strong boost around `+0.10` could move the expected
heldout-010 Procedure chunk upward and fix that case.

At first glance, this appeared successful.

However, a second procedural query exposed the problem:

``` text
How do I perform hydraulic system inspection?
```

The desired result belonged to:

``` text
SOP-MNT-001 — Hydraulic System Inspection
```

A generic Procedure-section boost could instead promote the Procedure
section of:

``` text
SOP-MNT-002 — Hydraulic Return Filter Replacement
```

above the correct inspection procedure.

A smaller boost such as `+0.02` still demonstrated the same underlying
weakness.

The issue was structural:

``` text
Procedure evidence type
≠
correct procedure topic
```

A global section-type boost encodes only "this is a procedure", but not
"this is the procedure about the user's requested task".

The experiment was therefore rejected.

This established an important design rule:

> Evidence-type preference must not overpower topical relevance.

------------------------------------------------------------------------

# 15. What the Failed Boost Experiment Revealed

The incorrect procedure promotion suggested that the embedding
representation did not provide enough task-level document context.

Consider:

``` text
Document A: Hydraulic System Inspection
Section: Procedure

Document B: Hydraulic Return Filter Replacement
Section: Procedure
```

If the embedding text exposes only:

``` text
Section: Procedure
<body text>
```

then both chunks share a highly generic heading.

The document title carries critical task semantics. This led to
inspection of the chunk representation itself rather than adding another
ranking heuristic.

------------------------------------------------------------------------

# 16. Important Discovery --- The Title Already Existed Structurally

The chunk model already contained:

``` python
heading_path: list[str]
```

For ordinary document sections, the heading path already included the
document title and section title:

``` python
heading_path = [
    document.title,
    section_title,
]
```

Therefore the system did not lack document-title metadata.

The problem was more subtle:

> The title existed in the chunk structure but was not included in the
> text sent to the embedding model.

This prevented the addition of a redundant `document_title` field to
`Chunk`.

------------------------------------------------------------------------

# 17. Old Embedding Representation

Before the representation change, `_build_embedding_text()` included
contextual information such as machine model and section title but
omitted the document title.

Conceptually:

``` text
Machine models: MX-200, MX-220, MX-300
Section: Procedure

<body text>
```

This representation made the section type explicit but weakened
task-level identity.

For multiple SOP Procedure sections, the embedding model therefore had
less direct context distinguishing inspection, filter replacement, and
sensor calibration procedures.

------------------------------------------------------------------------

# 18. New Embedding Representation

The embedding representation was enriched to include the document title:

``` text
Machine models: ...
Document: Hydraulic System Inspection
Section: Procedure
<body>
```

The implementation changed `_build_embedding_text()` so it accepts the
document title and appends:

``` text
Document: <document title>
```

The chunk creation path passes `document.title` into the embedding-text
builder.

The test protecting heading representation was strengthened to assert an
exact title example such as:

``` text
Document: MX-200 Operation and Maintenance Manual
```

------------------------------------------------------------------------

# 19. Why Representation Was Preferred Over a Ranking Hack

The document-title solution is architecturally stronger than a global
Procedure boost.

A ranking boost says:

``` text
Procedure sections are generally more important for this query.
```

The representation improvement says:

``` text
Every chunk should expose enough semantic context for the embedding model to understand what document/task the section belongs to.
```

The second principle generalizes beyond procedural queries.

Document titles can distinguish maintenance tasks, machine manuals,
troubleshooting topics, calibration procedures, filter procedures,
safety procedures, and future document families.

This change improves the information available to retrieval rather than
compensating afterward for missing information.

------------------------------------------------------------------------

# 20. Qdrant Reindex After Representation Change

Changing `embedding_text` changes the input to the embedding model.
Therefore the stored Qdrant vectors became stale relative to the new
chunk representation.

The corpus was reindexed using:

``` text
python scripts/index_qdrant.py
```

The resulting collection contained:

``` text
154 indexed chunks
384-dimensional vectors
154 stored points
```

Reindexing was mandatory here because:

``` text
old embedding_text
        ↓
old vectors

new embedding_text
        ↓
new vectors required
```

This distinction later became useful when hard-constraint logic changed:
that later change affected only query-time eligibility and did not
require reindexing.

------------------------------------------------------------------------

# 21. Procedural Retrieval After Title Enrichment

After reindexing, several procedural queries were inspected.

The formerly failing heldout query now returned the expected Procedure
evidence at rank 1 with a similarity score around:

``` text
0.7131
```

A calibration-oriented variant returned the expected Procedure chunk at
rank 1 at approximately:

``` text
0.7087
```

A hydraulic return filter replacement query returned its expected
Procedure evidence at rank 1 at approximately:

``` text
0.6965
```

The important adversarial calibration query:

``` text
How do I perform hydraulic system inspection?
```

returned the correct `SOP-MNT-001` Procedure section at rank 1 at
approximately:

``` text
0.6589
```

This was particularly important because it was the query that exposed
the weakness of generic Procedure boosting.

------------------------------------------------------------------------

# 22. Development Benchmark After Title Enrichment

The routed development benchmark after title enrichment produced:

``` text
Hit@1: 0.840
Hit@3: 0.920
Hit@5: 1.000
MRR:   0.891
```

Compared with the initial Hybrid V2 checkpoint:

``` text
Before title enrichment
Hit@1: 0.840
Hit@3: 0.960
Hit@5: 1.000
MRR:   0.895

After title enrichment
Hit@1: 0.840
Hit@3: 0.920
Hit@5: 1.000
MRR:   0.891
```

This was a small aggregate regression in Hit@3 and MRR.

The change was nevertheless retained because it fixed a diagnosed
representation deficiency, corrected multiple procedural examples,
avoided a brittle section-boosting heuristic, preserved Hit@1 and Hit@5,
and produced a more principled representation.

The project deliberately did not continue tuning merely to restore the
previous aggregate number.

------------------------------------------------------------------------

# 23. The `procedure-001` Rank-5 Case

After title enrichment, the dev query:

``` text
Which procedure explains hydraulic return filter replacement?
```

was successful under the benchmark definition but the strict expected
evidence target appeared at rank 5.

This highlighted a benchmark-design nuance:

``` text
correct document/topic
vs.
exact expected evidence section
```

A retrieval system can understand the user's task while ranking a
different section from the same correct document above the benchmark's
strict target.

This case was not used as justification for another post-hoc tuning
rule.

The benchmark definition was also not changed after observing the
result.

------------------------------------------------------------------------

# 24. Held-Out Results After Title Enrichment

After the representation change, all 12 existing held-out queries
returned their expected evidence at rank 1:

``` text
Hit@1: 1.000
Hit@3: 1.000
Hit@5: 1.000
MRR:   1.000
```

This included the formerly failing `heldout-010`.

However, this result requires an important methodological qualification.

------------------------------------------------------------------------

# 25. Why the Existing Held-Out Benchmark Is No Longer Truly Held Out

A benchmark is genuinely held out only while its outcomes have not
influenced system design.

During this milestone:

1.  `heldout-010` failed.
2.  Its ranking was inspected.
3.  Its expected evidence was analyzed.
4.  Alternative retrieval behaviors were tested.
5.  The embedding representation was changed partly in response to the
    failure it exposed.

Therefore the 12-query set can no longer be described as an unbiased
held-out estimate of generalization.

It remains highly useful, but its role has changed to a:

``` text
diagnostic regression benchmark
```

The 1.000 result means the current architecture handles all known cases
in this diagnostic set. It does not prove perfect retrieval
generalization on unseen industrial questions.

------------------------------------------------------------------------

# 26. Architectural Review Before Creating a Fresh Benchmark

After solving the known representation problem, the next planned step
was to create a fresh unseen benchmark.

Before doing so, the retrieval architecture was reviewed for known
structural inconsistencies.

One important issue was identified:

``` text
Qdrant dense branch → metadata constrained
BM25 lexical branch → whole corpus
```

This meant the two branches of hybrid retrieval did not necessarily
operate over the same candidate universe.

This issue was known before creating or executing the new unseen
benchmark. Fixing it first was therefore methodologically legitimate.

------------------------------------------------------------------------

# 27. The Hybrid Candidate-Leakage Problem

Consider:

``` text
Which replacement filter is compatible with MX-300?
```

The analyzer can derive:

``` text
machine_model = MX-300
intent = PARTS_LOOKUP
contains_spare_parts = True
```

Qdrant therefore searches only points satisfying those hard conditions.

But the old BM25 branch still searched all 154 chunks.

A lexically strong MX-200 chunk could therefore appear in the BM25
ranking even though it violated the machine constraint.

Reciprocal rank fusion could then reintroduce that invalid chunk into
the final hybrid results.

Conceptually:

``` text
                  Query constraints
                        ↓
              ┌─────────┴─────────┐
              ↓                   ↓
        Qdrant dense            BM25
        constrained         unconstrained
              ↓                   ↓
          valid set          whole corpus
              └─────────┬─────────┘
                        ↓
                       RRF
                        ↓
          invalid lexical candidate
          can re-enter final ranking
```

The system's hard constraints were therefore not truly hard at the
hybrid level.

------------------------------------------------------------------------

# 28. Test-First Reproduction of Constraint Leakage

Before changing production code, a regression test reproduced the
problem.

The test created:

``` text
Eligible chunk
- machine: MX-300
- part number: HF-300-R10

Ineligible chunk
- machine: MX-200
- lexically strong text mentioning MX-300
```

The fake Qdrant branch returned only the eligible chunk.

The BM25 branch still saw both chunks.

The test asserted that hybrid results must not contain the ineligible
MX-200 chunk.

Initially, the test failed.

That proved the architecture had a real constraint-parity problem rather
than only a theoretical concern.

The regression test became:

``` text
test_hybrid_retriever_excludes_lexical_results_outside_constraints
```

------------------------------------------------------------------------

# 29. Why Filtering After BM25 Top-K Would Be Wrong

A tempting implementation would be:

``` text
BM25 searches entire corpus
        ↓
take top 20
        ↓
remove invalid chunks
```

This is incorrect.

Imagine:

``` text
Ranks 1-20 = invalid under metadata constraint
Rank 21    = best valid chunk
```

If the system first truncates to top 20 and then filters, the valid
rank-21 chunk is permanently lost.

The correct sequence is:

``` text
Determine eligible candidate universe
        ↓
BM25 scores/ranks only eligible chunks
        ↓
select top candidate_k
```

This ensures `top_k` means top K among valid candidates.

------------------------------------------------------------------------

# 30. BM25 Candidate Scoping

`BM25Retriever.search()` was extended with:

``` python
eligible_chunk_ids: set[str] | None = None
```

When no eligible set is supplied, behavior remains unchanged and the
full corpus is searchable.

When an eligible set is supplied, ranking indices are constructed only
for chunks whose IDs are members of that set.

Conceptually:

``` python
eligible_indices = [
    index
    for index, chunk in enumerate(self.chunks)
    if (
        eligible_chunk_ids is None
        or chunk.chunk_id in eligible_chunk_ids
    )
]
```

A dedicated test was added:

``` text
test_bm25_search_respects_eligible_chunk_ids
```

The test initially failed with the old method signature and passed after
candidate scoping was implemented.

------------------------------------------------------------------------

# 31. Why BM25 Does Not Understand Domain Constraints Directly

The BM25 retriever was deliberately kept domain-neutral.

It does not receive arguments such as machine model, alarm code,
procedure ID, or part number.

Instead, higher-level retrieval logic determines eligibility and gives
BM25 only:

``` text
eligible_chunk_ids
```

This separation is intentional.

BM25's responsibility is:

``` text
lexically rank an allowed set of documents
```

It should not need to understand industrial domain semantics or
query-analysis rules.

------------------------------------------------------------------------

# 32. From Qdrant-Specific Constraints to Shared Retrieval Constraints

The original V2 constraint abstraction lived inside
`hybrid_retriever.py` and was named around Qdrant.

Once BM25 needed the same eligibility semantics, that abstraction was no
longer Qdrant-specific.

A new module was created:

``` text
src/industrial_copilot/retrieval/constraints.py
```

It defines:

``` python
@dataclass(frozen=True)
class RetrievalConstraints:
    machine_model: str | None = None
    alarm_code: str | None = None
    procedure_id: str | None = None
    part_number: str | None = None
    contains_spare_parts: bool | None = None
```

and:

``` text
build_retrieval_constraints(...)
chunk_matches_constraints(...)
```

This renamed the concept according to what it actually represents: hard
retrieval eligibility.

------------------------------------------------------------------------

# 33. Constraint Construction Rules

`build_retrieval_constraints()` translates `QueryAnalysis` into hard
eligibility rules.

The current behavior is conservative:

``` text
one machine model → constrain machine model
one alarm code    → constrain alarm code
one procedure ID  → constrain document ID
one part number   → constrain part number
PARTS_LOOKUP      → require contains_spare_parts=True
```

When multiple values of the same identifier type are present, that field
is not automatically converted into a single hard equality constraint.

Future multi-value support should explicitly define whether the intended
logic is OR, AND, or another policy.

------------------------------------------------------------------------

# 34. AND Semantics Across Constraint Types

When multiple different constraints are active, all must be satisfied.

For example:

``` text
machine_model = MX-300
contains_spare_parts = True
```

means:

``` text
machine is MX-300
AND
chunk contains spare-part metadata
```

The in-memory matcher returns `False` as soon as any active condition
fails.

Qdrant applies corresponding conditions through `Filter(must=[...])`,
which also implements AND semantics.

------------------------------------------------------------------------

# 35. Shared Constraint Flow in Final HybridRetriever

The final hybrid search flow is:

``` text
QueryAnalysis
     ↓
build_retrieval_constraints(...)
     ↓
RetrievalConstraints
     ├──────────────────────────────┐
     ↓                              ↓
Qdrant filter values      chunk_matches_constraints(...)
     ↓                              ↓
Qdrant dense search       eligible_chunk_ids
     ↓                              ↓
Dense candidates          BM25 restricted search
     │                              │
     └──────────────┬───────────────┘
                    ↓
          reciprocal rank fusion
                    ↓
              final results
```

Both branches therefore share the same logical constraint source.

------------------------------------------------------------------------

# 36. Constraint Tests Added

A dedicated module was created:

``` text
tests/test_retrieval_constraints.py
```

The focused tests cover:

-   matching the requested machine model,
-   rejecting the wrong machine model,
-   matching an alarm code,
-   matching a procedure by `document_id`,
-   matching a part number,
-   matching `contains_spare_parts` via `bool(chunk.part_numbers)`,
-   requiring all active constraints to match.

Together with the BM25 and hybrid regression tests, these protect both
shared constraint semantics and candidate-scope correctness.

------------------------------------------------------------------------

# 37. Evaluation Harness Migration

After removing the old Qdrant-specific constraint builder from
`hybrid_retriever.py`, both routed evaluation scripts initially failed
with:

``` text
ImportError: cannot import name 'build_qdrant_constraints'
```

The affected scripts were:

``` text
experiments/evaluate_routed_retrieval.py
experiments/evaluate_routed_retrieval_heldout.py
```

A repository search confirmed only these two scripts retained references
to the obsolete API.

The correct fix was not to restore the obsolete function as a
compatibility alias.

Instead, both harnesses were migrated to:

``` python
from industrial_copilot.retrieval.constraints import (
    build_retrieval_constraints,
)
```

Evaluation code is part of reproducibility, so it should execute against
the same current abstractions as production retrieval.

------------------------------------------------------------------------

# 38. Why No Qdrant Reindex Was Needed for Constraint Parity

The shared-constraint fix changed only query-time retrieval logic.

It did not change:

``` text
chunk text
embedding text
embedding model
embedding dimension
Qdrant payload schema
stored vectors
stored points
```

Therefore no reindex was necessary.

Operational rule:

``` text
Change affects embedded representation?
    → re-embed / reindex

Change affects only query-time filtering/ranking?
    → no reindex unless payload/index requirements changed
```

------------------------------------------------------------------------

# 39. Final Automated Regression Test

After shared constraints and evaluation-harness migration, the complete
automated test suite was run.

Result:

``` text
90 passed
```

`git diff --check` also returned no output.

------------------------------------------------------------------------

# 40. Final Development Benchmark

The routed 25-query development benchmark produced:

``` text
Cases: 25
Hit@1: 0.840
Hit@3: 0.920
Hit@5: 1.000
MRR:   0.891
```

Per-category Hit@5 remained 1.000 for alarm, component, condition,
maintenance, paraphrase, parts, procedure, safety, and specification.

Notable individual strict-target ranks included:

``` text
spec-001       rank 3
procedure-001  rank 5
procedure-003  rank 2
component-002  rank 4
```

All 25 cases remained successful within their expected cutoff.

------------------------------------------------------------------------

# 41. Final Diagnostic Benchmark

The 12-query diagnostic benchmark was rerun.

Every case returned expected evidence at rank 1:

``` text
Cases: 12
Hit@1: 1.000
Hit@3: 1.000
Hit@5: 1.000
MRR:   1.000
```

Again, this set is now diagnostic rather than genuinely unseen.

------------------------------------------------------------------------

# 42. Constraint-Parity Fix Caused Zero Benchmark Regression

Immediately before and after shared hard-constraint enforcement:

``` text
Development benchmark
                       Before     After
Hit@1                   0.840      0.840
Hit@3                   0.920      0.920
Hit@5                   1.000      1.000
MRR                     0.891      0.891

Diagnostic benchmark
                       Before     After
Hit@1                   1.000      1.000
Hit@3                   1.000      1.000
Hit@5                   1.000      1.000
MRR                     1.000      1.000
```

This is an ideal outcome for a correctness fix: the architecture became
stricter without degrading known retrieval quality.

------------------------------------------------------------------------

# 43. Complete Metric Progression

## Dense V1

``` text
Hit@1: 0.640
Hit@3: 0.840
Hit@5: 0.880
MRR:   0.743
```

## BM25 V1

``` text
Hit@1: 0.520
Hit@3: 0.560
Hit@5: 0.640
MRR:   0.558
```

## Naive RRF

``` text
Hit@1: 0.640
Hit@3: 0.760
Hit@5: 0.840
MRR:   0.705
```

## Routed Hybrid V1 + Identifier Boosting

``` text
Hit@1: 0.800
Hit@3: 0.960
Hit@5: 1.000
MRR:   0.883
```

## Original Held-Out Checkpoint

``` text
Hit@1: 0.750
Hit@3: 0.750
Hit@5: 0.833
MRR:   0.771
```

## Qdrant Dense Dev

``` text
Hit@1: 0.760
Hit@3: 0.960
Hit@5: 1.000
MRR:   0.848
```

## Qdrant Held-Out Checkpoint

``` text
Hit@1: 0.750
Hit@3: 0.750
Hit@5: 0.750
MRR:   0.750
```

## Initial Hybrid Retrieval V2 Dev

``` text
Hit@1: 0.840
Hit@3: 0.960
Hit@5: 1.000
MRR:   0.895
```

## Initial Hybrid Retrieval V2 Held-Out

``` text
Hit@1: 0.917
Hit@3: 0.917
Hit@5: 0.917
MRR:   0.917
```

## After Document-Title Representation Enrichment

Development:

``` text
Hit@1: 0.840
Hit@3: 0.920
Hit@5: 1.000
MRR:   0.891
```

Diagnostic:

``` text
Hit@1: 1.000
Hit@3: 1.000
Hit@5: 1.000
MRR:   1.000
```

## After Shared Hard-Constraint Enforcement

Development:

``` text
Hit@1: 0.840
Hit@3: 0.920
Hit@5: 1.000
MRR:   0.891
```

Diagnostic:

``` text
Hit@1: 1.000
Hit@3: 1.000
Hit@5: 1.000
MRR:   1.000
```

Final automated test status:

``` text
90 passed
```

------------------------------------------------------------------------

# 44. Final Hybrid Retrieval V2 Architecture

``` text
                              User query
                                  ↓
                           Query Analyzer
                                  ↓
                         QueryAnalysis object
                                  ↓
                    build_retrieval_constraints
                                  ↓
                       RetrievalConstraints
                                  ↓
                              Router
                    ┌─────────────┴─────────────┐
                    │                           │
                DENSE route                 HYBRID route
                    │                           │
                    ↓                           ↓
             Qdrant dense              ┌────────┴─────────┐
             constrained               ↓                  ↓
                    │            Qdrant dense            BM25
                    │            constrained        eligible IDs only
                    │                  ↓                  ↓
                    │             dense results     lexical results
                    │                  └────────┬─────────┘
                    │                           ↓
                    │                 Reciprocal Rank Fusion
                    │                           ↓
                    │                 Exact Identifier Boost
                    │                           ↓
                    └─────────────── final ranked evidence
```

For hybrid queries:

``` text
Qdrant candidate eligibility
=
BM25 candidate eligibility
```

before ranking and fusion.

------------------------------------------------------------------------

# 45. Current Query Analysis and Routing Behavior

The query analyzer extracts structured identifiers such as:

``` text
machine models: MX-###
alarm codes:    HX-### / SF-### / CL-### / EX-###
procedure IDs:  SOP-...
part numbers:   domain part-number patterns
```

Current intent categories remain intentionally small:

``` text
GENERAL
PARTS_LOOKUP
```

The temporary `PROCEDURAL_GUIDANCE` experiment was removed because it
had no justified production consumer.

The router uses hybrid retrieval for strong lexical/identifier cases
such as alarms, procedure identifiers, part identifiers, and parts
lookup intent.

A machine model alone is not sufficient to force hybrid retrieval.

------------------------------------------------------------------------

# 46. Exact Identifier Boosting Remains Separate

After hybrid fusion, exact identifier boosting remains a separate
ranking stage.

It can boost exact matches for alarm codes, procedure IDs, and part
numbers.

Machine model alone is deliberately not treated as the same kind of
exact identifier boost.

An alarm such as `HX-417` identifies a highly specific troubleshooting
entity, whereas `MX-300` is a broad machine scope applying to many
chunks.

------------------------------------------------------------------------

# 47. Chunk Metadata Relevant to V2

The chunk model contains:

``` python
class Chunk(BaseModel):
    chunk_id: str
    text: str
    document_id: str
    document_type: str
    machine_models: list[str]
    section_title: str
    heading_path: list[str]
    revision: str
    effective_date: date
    language: str
    related_components: list[str] = []
    related_procedures: list[str] = []
    part_numbers: list[str] = []
    alarm_codes: list[str] = []
    embedding_text: str
```

This metadata is not created by Qdrant.

The application creates it during document generation/chunking; Qdrant
persists and searches it.

------------------------------------------------------------------------

# 48. Metadata Quality Improvements That Enabled Retrieval

Earlier Qdrant work uncovered metadata issues that remained important to
Hybrid V2, including SOP model scope, alarm-code propagation,
applicable-component inheritance, and correct part-number placement.

SOP chunks inherit applicable components where appropriate.

Actual part numbers are attached only to relevant spare-parts sections
rather than indiscriminately to every SOP chunk.

This matters because `contains_spare_parts` derives from:

``` python
bool(chunk.part_numbers)
```

If part metadata were over-propagated, parts filters would become too
broad.

Hybrid constraint correctness therefore depends on metadata correctness
upstream.

------------------------------------------------------------------------

# 49. Major Rejected Alternatives

## 49.1 Force procedural questions through hybrid search

Rejected because forced hybrid retrieval did not fix heldout-010.

## 49.2 Keep a `PROCEDURAL_GUIDANCE` intent anyway

Rejected because no final production behavior required it.

## 49.3 Globally boost `Procedure` sections

Rejected because it could promote an unrelated procedure above the
topically correct procedure.

## 49.4 Add a duplicate `document_title` field to `Chunk`

Rejected because the document title was already structurally available;
the correct fix was to expose it to `embedding_text`.

## 49.5 Filter BM25 only after selecting global top-K

Rejected because valid constrained candidates below the global cutoff
could be lost.

## 49.6 Teach BM25 about machine models and alarm codes

Rejected because domain constraint logic belongs in higher-level
retrieval orchestration.

## 49.7 Restore `build_qdrant_constraints` as a compatibility alias

Rejected because the evaluation harness should migrate to the new shared
abstraction.

## 49.8 Tune further against the existing held-out set

Rejected because the set had already influenced system design and was no
longer unbiased unseen data.

------------------------------------------------------------------------

# 50. Key Engineering Lessons

## 50.1 Correct-document retrieval is not the same as correct-evidence retrieval

heldout-010 demonstrated that the system can discover the correct SOP
while ranking the wrong section above the evidence required to answer
the question.

## 50.2 Representation can be more important than another reranker

Before adding scoring heuristics, inspect whether embedding input
contains the information needed to distinguish candidates.

## 50.3 Metadata constraints are eligibility rules, not score hints

An explicit machine mismatch should often be excluded, not merely scored
lower.

## 50.4 Hybrid branches must agree on hard constraints

Filtering dense retrieval while lexical retrieval searches the whole
corpus undermines hard constraints.

## 50.5 Filter before top-K

Filtering afterward can silently destroy recall among valid candidates.

## 50.6 A higher benchmark score is not always the best engineering decision

Title enrichment slightly reduced dev Hit@3/MRR but fixed a diagnosed
representation problem in a principled way.

## 50.7 A benchmark changes status once it influences development

The old held-out set remains useful, but must be described as
diagnostic/regression data.

## 50.8 Failed experiments are valuable evidence

Forced hybrid routing and Procedure boosting narrowed the causal
explanation and prevented brittle production changes.

------------------------------------------------------------------------

# 51. Current Known Limitations

## 51.1 Small synthetic corpus

The corpus contains 154 chunks from a controlled fictional industrial
domain.

## 51.2 Limited query-intent taxonomy

Only `GENERAL` and `PARTS_LOOKUP` remain in production.

## 51.3 Single-value hard-constraint mapping

Multi-machine or multi-identifier queries require explicit future
semantics.

## 51.4 Exact evidence-section ambiguity

Some queries identify the correct document/task while ranking a
different section from the same document above a strict expected
section.

## 51.5 No learned reranker

A cross-encoder or other learned reranker has not yet been introduced.
It should be added only if future evaluation demonstrates need.

## 51.6 No LLM answer-generation evaluation yet

The project has not yet measured answer faithfulness, citation
correctness, refusal behavior, context sufficiency, or hallucination
rate.

------------------------------------------------------------------------

# 52. Fresh Unseen Benchmark Protocol

Because the previous held-out set became diagnostic, the next evaluation
must be created carefully.

``` text
1. Freeze the known retrieval architecture.
2. Commit the implementation and tests.
3. Create new benchmark queries independently of retrieval outputs.
4. Define expected documents/evidence before executing retrieval.
5. Verify expected targets against canonical source documents, not retrieval rankings.
6. Freeze the benchmark definitions.
7. Execute the benchmark for the first time.
8. Record the result honestly.
```

The fresh set should cover semantic paraphrases, exact alarms, machine +
alarm constraints, procedural how-to questions, parts lookup, exact part
identifiers, maintenance conditions, safety questions, specification
questions, and multi-constraint cases.

------------------------------------------------------------------------

# 53. What to Do If the Fresh Benchmark Fails

There are two valid paths.

## Path A --- Preserve it as an unbiased measurement

Record the failure and do not tune the current system against that
benchmark.

## Path B --- Use the failure for development

Inspect the failure and improve the system. Once this happens, the
benchmark becomes diagnostic development data and another fresh unseen
set is required for unbiased evaluation.

The rule is:

> Do not repeatedly tune against a benchmark while continuing to call it
> unseen or held out.

------------------------------------------------------------------------

# 54. Relationship to the Future LLM Layer

The retrieval system is now structured to support grounded answer
generation:

``` text
User query
    ↓
Query analysis
    ↓
Routed retrieval
    ↓
Top evidence chunks
    ↓
Prompt/context construction
    ↓
LLM
    ↓
Grounded answer
    ↓
Source citations
```

The current retrieval diagnostics should remain independently executable
after the LLM is introduced.

This allows two separate questions:

``` text
Did retrieval find the right evidence?
```

and:

``` text
Did the LLM use that evidence correctly?
```

------------------------------------------------------------------------

# 55. Recommended Next Engineering Steps

``` text
1. Review final working-tree diff.
2. Run the complete automated test suite.
3. Run git diff --check.
4. Commit and push Hybrid Retrieval V2.
5. Treat that commit as the frozen retrieval architecture.
6. Build the fresh unseen benchmark.
7. Define expected evidence before running it.
8. Execute and record the fresh benchmark once.
9. Decide whether retrieval needs another iteration or is ready for LLM integration.
```

Later milestones can introduce grounded answer generation, citation
construction, answer-quality evaluation, agent/tool workflows, FastAPI
serving, Docker packaging, deployment, monitoring, and observability.

------------------------------------------------------------------------

# 56. Final State of Hybrid Retrieval V2

At the end of this milestone:

-   Qdrant is the persistent dense-vector backend.
-   Hybrid retrieval uses Qdrant rather than the old NumPy dense branch.
-   Qdrant results are adapted into the common retrieval representation.
-   Query analysis produces shared hard retrieval constraints.
-   Dense and lexical hybrid branches use the same logical eligibility
    rules.
-   BM25 candidate filtering occurs before top-K truncation.
-   Hard constraints use AND semantics across active fields.
-   Exact identifier boosting remains a separate post-fusion ranking
    stage.
-   Document titles are included in embedding text.
-   Procedural retrieval has stronger task-level semantic context.
-   A generic Procedure boost was tested and rejected.
-   A temporary procedural intent was tested and removed.
-   The lexical candidate-leakage failure is protected by a regression
    test.
-   Evaluation scripts use the same shared constraint abstraction as
    production retrieval.
-   The complete automated test suite passes.
-   Known development metrics were preserved after the constraint
    correctness fix.
-   The former held-out benchmark is explicitly reclassified as
    diagnostic.
-   The methodology for a genuinely unseen benchmark is defined before
    executing it.

Final regression status:

``` text
Automated tests: 90 passed
```

Final development retrieval status:

``` text
Hit@1: 0.840
Hit@3: 0.920
Hit@5: 1.000
MRR:   0.891
```

Final diagnostic retrieval status:

``` text
Hit@1: 1.000
Hit@3: 1.000
Hit@5: 1.000
MRR:   1.000
```

The most important outcome is not the perfect score on the diagnostic
set.

The more meaningful result is that the retrieval architecture is now
better understood and more internally consistent:

``` text
semantic representation
+
metadata-aware dense retrieval
+
lexical retrieval
+
query-aware routing
+
shared hard constraints
+
rank fusion
+
exact identifier handling
+
reproducible evaluation
```

Each major component exists because a concrete retrieval behavior or
failure justified it.

------------------------------------------------------------------------

# 57. Milestone Summary

Hybrid Retrieval V2 began as a Qdrant migration and evolved into a
deeper retrieval-quality investigation.

The work demonstrated several important RAG engineering principles:

``` text
Infrastructure is not retrieval strategy.

Correct document discovery is not enough; evidence-section quality matters.

Before adding reranking heuristics, inspect the information presented to the embedding model.

Hard metadata constraints must constrain every retrieval branch.

Eligibility must be applied before top-K truncation.

Evaluation code must evolve with production architecture.

A benchmark that influences development is no longer genuinely held out.

Failed experiments should be preserved because they explain why the final design exists.
```

The resulting system is ready for a fresh, genuinely unseen retrieval
benchmark before the project proceeds to grounded LLM answer generation.
