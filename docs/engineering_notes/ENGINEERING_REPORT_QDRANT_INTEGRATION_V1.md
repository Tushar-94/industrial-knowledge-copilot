# Industrial Knowledge Copilot

# Engineering Report — Qdrant Integration V1

**Project:** Industrial Knowledge Copilot  

**Milestone:** Persistent, Metadata-Aware Vector Retrieval with Qdrant  

**Report Version:** V1  

**Status:** Completed  

**Final automated test status:** 78 tests passing  

**Indexed corpus size:** 154 chunks / 154 Qdrant points  

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`  

**Embedding dimension:** 384  

**Vector similarity metric:** Cosine similarity  

---

# 1. Purpose of This Report

This document records the complete engineering journey of integrating Qdrant into the Industrial Knowledge Copilot.

It is intentionally more detailed than a normal project README or changelog.

The goal is to preserve enough context that a developer — including the original author returning months later — can understand:
- what the system looked like before Qdrant,
- why Qdrant was introduced,
- where Qdrant fits in the architecture,
- what files were created,
- what each file is responsible for,
- how chunks become Qdrant points,
- what metadata is stored,
- why metadata matters,
- what retrieval problems were discovered,
- what experiments were performed,
- what failed,
- how failures were diagnosed,
- what architectural decisions were made,
- why those decisions were made,
- what tests protect those decisions,
- what Qdrant solved,
- what Qdrant did not solve,
- and what the next retrieval architecture should look like.

This is therefore both an **engineering report** and a **learning reference**.

---

# 2. Where This Milestone Fits in the Project

The Industrial Knowledge Copilot is being built incrementally.

The high-level intended system is:

```text
Industrial knowledge sources
        ↓
Canonical structured data
        ↓
Generated technical documents
        ↓
Document chunking
        ↓
Metadata enrichment
        ↓
Embeddings
        ↓
Retrieval
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

At the start of this milestone, the project had already implemented:
- a synthetic industrial domain,
- canonical YAML data,
- domain validation,
- generated manuals,
- generated troubleshooting guides,
- generated SOPs,
- semantic chunking,
- embeddings,
- NumPy-based dense retrieval,
- BM25 lexical retrieval,
- hybrid retrieval,
- query analysis,
- retrieval routing,
- identifier boosting,
- retrieval evaluation.

However, vectors were still primarily being handled as experimental in-memory data.

The purpose of this milestone was to introduce a real vector-store layer without prematurely adding an LLM.

---

# 3. Important Architectural Principle

A central principle throughout this project is:

> Do not add the LLM until retrieval is understandable, measurable, and reasonably reliable.

It would have been possible to start with a framework that automatically performs:

```text
documents → embeddings → vector database → LLM
```

However, that would hide many important engineering decisions.

Instead, retrieval was built from first principles so that we could independently understand:
- chunk quality,
- embedding behavior,
- lexical retrieval,
- semantic retrieval,
- exact identifier handling,
- metadata constraints,
- rank fusion,
- evaluation,
- and failure modes.

Qdrant was therefore introduced as an infrastructure improvement to the retrieval system — not as a shortcut around retrieval engineering.

---

# 4. Starting Point Before Qdrant

Before Qdrant, the system already supported dense semantic retrieval.

A user query was embedded using the same embedding model used for corpus chunks.

Conceptually:

```text
User query
   ↓
Embedding model
   ↓
Query vector
   ↓
Compare against all chunk vectors
   ↓
Cosine similarity
   ↓
Sort
   ↓
Top-K chunks
```

The original dense implementation used NumPy for vector similarity.

This was valuable because it made the mechanics of semantic retrieval transparent.

We could directly understand:

```text
query vector
vs.
document chunk vectors
```

without introducing database behavior at the same time.

---

# 5. Original Dense Retrieval Results

The dense retrieval development benchmark produced:

| Metric | Dense Retrieval |
|---|---:|
| Hit@1 | 0.640 |
| Hit@3 | 0.840 |
| Hit@5 | 0.880 |
| MRR | 0.743 |

Dense retrieval performed well on semantic questions.

For example, it handled paraphrases such as maintenance questions where the exact wording of the source document did not appear in the user query.

However, it struggled with some exact industrial identifiers.

Examples include:

```text
HX-417

MX-300

HF-300-R10

SOP-MNT-002
```

An embedding model understands semantic similarity, but exact identifiers often require stronger lexical or structured handling.

---

# 6. Why BM25 Was Added Before Qdrant

BM25 lexical retrieval was implemented to test the opposite retrieval behavior.

Dense retrieval asks approximately:

> Which chunks mean something similar to this query?

BM25 asks approximately:

> Which chunks contain terms that strongly match this query?

This makes BM25 particularly useful for:
- alarm codes,
- part numbers,
- procedure IDs,
- technical identifiers,
- rare exact terms.

The lexical benchmark showed that BM25 could outperform dense retrieval for exact identifiers but was weaker for semantic paraphrases.

This demonstrated that neither retrieval method was universally best.

---

# 7. Routed Hybrid Retrieval

The project then combined:
- query analysis,
- dense retrieval,
- BM25,
- retrieval routing,
- reciprocal-rank fusion,
- identifier boosting.

The routed hybrid development benchmark reached:

| Metric | Routed Hybrid |
|---|---:|
| Hit@1 | 0.800 |
| Hit@3 | 0.960 |
| Hit@5 | 1.000 |
| MRR | 0.883 |

This became the strongest retrieval baseline before Qdrant.

An important consequence is:

> Qdrant was never introduced because BM25 or hybrid retrieval had failed.

Qdrant was introduced because the project needed a persistent and metadata-aware vector infrastructure.

---

# 8. Why the In-Memory Dense Retriever Was No Longer Enough

NumPy retrieval was ideal for learning and experimentation.

It was not the architecture we wanted for a production-style RAG system.

Important missing capabilities included:
- persistent vector storage,
- database-backed indexing,
- metadata payload storage,
- metadata filtering,
- deterministic updates,
- separation of indexing and querying,
- a realistic path toward deployment,
- scalable retrieval infrastructure.

This created the need for a vector database.

---

# 9. What a Vector Database Does

A vector database stores numerical vectors and allows similarity search over them.

For this project, a chunk might conceptually become:

```text
Chunk
├── text
├── embedding vector
└── metadata
```

The embedding might look conceptually like:

```text
[0.018, -0.044, 0.102, ..., 0.031]
```

In this project, every embedding has:

```text
384 dimensions
```

The vector database stores that vector together with structured metadata.

A search then becomes:

```text
Query
  ↓
Query embedding
  ↓
Vector database
  ↓
Similarity search
  ↓
Metadata constraints
  ↓
Top matching points
```

---

# 10. What Qdrant Does Not Do

This distinction is extremely important.

Qdrant does **not** automatically know:
- what `MX-300` means,
- what `HX-417` means,
- which chunk belongs to which machine,
- which SOP contains spare parts,
- which alarm relates to which procedure,
- which chunk contains part numbers,
- what the user's intent is.

The application must create this metadata.

Qdrant's responsibility is primarily to:
- store vectors,
- store payload metadata,
- perform vector similarity search,
- apply payload filters,
- return matching points.

Therefore:

```text
Domain understanding ≠ Qdrant
```

Instead:

```text
Our application creates domain metadata
                    ↓
Qdrant stores and filters that metadata
```

This became one of the most important lessons of this milestone.

---

# 11. Why Qdrant Was Selected

Qdrant was chosen as the vector-store technology for this project because it provides the capabilities needed for a production-oriented RAG architecture:
- vector similarity search,
- payload metadata,
- payload filtering,
- persistent storage,
- Python client support,
- local development support,
- a path toward server/cloud deployment.

For the current milestone, Qdrant runs locally.

This allows the retrieval architecture to be developed without introducing deployment complexity too early.

---

# 12. Local Qdrant Instead of Remote Qdrant

The first integration uses Qdrant's local persistent client:

```python
QdrantClient(path=...)
```

This was intentional.

At this stage, the engineering question was:

> Can we design the vector-store architecture correctly?

It was not yet:

> Can we deploy a distributed Qdrant service?

Keeping Qdrant local allowed us to focus on:
- collection design,
- point design,
- indexing,
- payload metadata,
- filtering,
- retrieval behavior,
- tests.

Deployment can later replace the local client configuration without requiring the entire retrieval architecture to be redesigned.

---

# 13. Repository Locations

The Qdrant implementation lives primarily under:

```text
src/industrial_copilot/vector_store/
```

Current files:

```text
src/industrial_copilot/vector_store/
├── __init__.py
├── config.py
├── client.py
├── indexer.py
├── retriever.py
└── query_service.py
```

The retrieval-domain logic used by Qdrant remains under:

```text
src/industrial_copilot/retrieval/
```

Relevant files include:

```text
src/industrial_copilot/retrieval/
├── models.py
├── corpus.py
├── query_analyzer.py
├── embedder.py
├── markdown_chunker.py
├── router.py
├── identifier_boost.py
└── ...
```

This separation is deliberate.

The retrieval package understands retrieval-domain concepts.

The vector-store package understands Qdrant persistence and querying.

---

# 14. Experiment Files

Qdrant was integrated incrementally through small experiments rather than through one large implementation.

Relevant experiment files include:

```text
experiments/qdrant_collection_lab.py

experiments/qdrant_point_lab.py

experiments/qdrant_search_lab.py

experiments/compare_numpy_qdrant.py

experiments/qdrant_filter_lab.py

experiments/qdrant_query_service_lab.py

experiments/qdrant_alarm_point_lab.py

experiments/evaluate_qdrant_retrieval.py
```

These files served different learning and validation purposes.

This experimental style allowed one question to be answered at a time.

For example:

```text
Can we create a collection?
        ↓
Can we store a point?
        ↓
Can we index the corpus?
        ↓
Can Qdrant reproduce NumPy search?
        ↓
Can we filter by machine?
        ↓
Can we filter by alarm?
        ↓
Can query analysis automatically drive filters?
```

This reduced the risk of debugging multiple architectural layers simultaneously.

---

# 15. Production Indexing Script

The indexing entry point is:

```text
scripts/index_qdrant.py
```

This script builds the retrieval corpus, embeds the chunks, and persists them to Qdrant.

The successful final indexing run reported:
```text
Qdrant indexing complete

============================================================

Chunks indexed: 154

Embedding dimension: 384

Stored points: 154
```

This establishes the important invariant:

```text
154 retrieval chunks = 154 Qdrant points
```

---

# 16. `config.py`

Location:

```text
src/industrial_copilot/vector_store/config.py
```

Current configuration:

```python
COLLECTION_NAME = "industrial_knowledge"
EMBEDDING_DIMENSION = 384
QDRANT_STORAGE_PATH = (
    Path(__file__).resolve().parents[3]
    / ".qdrant"
)
```

This file centralizes vector-store configuration.

The collection name is:

```text
industrial_knowledge
```

The embedding dimension is:

```text
384
```

This must match the embedding model.

The local database is stored at:

```text
.qdrant/
```

at the repository root.

---

# 17. Why `.qdrant/` Is Not Source Code

The `.qdrant/` directory is generated runtime state.

It can be recreated by:
1. loading canonical data,
2. generating/building the corpus,
3. generating embeddings,
4. indexing those embeddings.

Therefore it should not be treated as source code.

The repository's source of truth remains the canonical domain data and application code.

Conceptually:

```text
Canonical data + code
        ↓
Generated documents
        ↓
Chunks
        ↓
Embeddings
        ↓
.qdrant/
```

This is why `.qdrant/` belongs in `.gitignore`.

---

# 18. `client.py`

Location:

```text
src/industrial_copilot/vector_store/client.py
```

This file owns Qdrant client creation and collection initialization.

The function:

```python
create_qdrant_client()
```

creates the storage directory and returns:

```python
QdrantClient(
    path=str(QDRANT_STORAGE_PATH)
)
```

The second function:

```python
ensure_collection()
```

checks whether the collection already exists.

If it does not, the function creates it with:

```python
VectorParams(
    size=EMBEDDING_DIMENSION,
    distance=Distance.COSINE,
)
```

This means the collection expects:

```text
384-dimensional vectors + cosine similarity
```

---

# 19. Why Collection Creation Is Idempotent

The code first checks:

```python
client.collection_exists(...)
```

and returns if the collection already exists.

This matters because initialization should be safe to run repeatedly.

We do not want normal application startup to destroy or recreate the collection every time.

This is part of making the system reproducible and predictable.

---

# 20. `indexer.py`

Location:

```text
src/industrial_copilot/vector_store/indexer.py
```

This file owns the transformation:

```text
Chunk + embedding
        ↓
Qdrant PointStruct
```

A Qdrant point consists conceptually of:

```text
Point
├── ID
├── vector
└── payload
```

The indexer therefore has three important responsibilities:
1. create stable point IDs,
2. convert chunk metadata into payloads,
3. pair each chunk with its embedding.

---

# 21. Deterministic Qdrant Point IDs

Human-readable chunk IDs look like:

```text
TSG-MX200-001::hx-417-hydraulic-pressure-below-operating-threshold::004
```

Qdrant point IDs use supported point identifier formats such as UUIDs.

Instead of generating random UUIDs, the project generates deterministic UUID5 identifiers:

```python
uuid5(
    NAMESPACE_URL,
    chunk_id,
)
```

This means:

```text
same chunk_id
     ↓
same UUID
```

every time.

---

# 22. Why Deterministic IDs Matter

Suppose indexing generated random IDs.

Running indexing twice could conceptually produce:

```text
Run 1:
chunk A → UUID 123

Run 2:
chunk A → UUID 987
```

The database could then contain duplicate logical chunks.

With deterministic UUID5:

```text
Run 1:
chunk A → UUID X

Run 2:
chunk A → UUID X
```

Qdrant's upsert can update the same logical point.

This gives us idempotent indexing behavior.

That is a much stronger production design than random point creation.

---

# 23. Chunk-to-Point Payload

The `_chunk_payload()` function currently stores:

```text
chunk_id

document_id

document_type

machine_models

section_title

heading_path

revision

effective_date

language

text

embedding_text

related_components

related_procedures

part_numbers

contains_spare_parts

alarm_codes
```

This payload is one of the most important architectural components of the retrieval system.

---

# 24. Vector vs Payload

The vector and payload serve different purposes.

The vector represents semantic meaning.

The payload represents structured facts about the source.

For example:

```text
vector
    ↓
"this chunk is semantically similar to hydraulic pressure"


payload
    ↓
document_id = TSG-MX200-001
machine_models = ["MX-200"]
alarm_codes = ["HX-417"]
section_title = HX-417 — Hydraulic Pressure Below Operating Threshold
```

Semantic search and structured filtering can therefore work together.

---

# 25. `contains_spare_parts`

One payload field is not directly stored on the `Chunk` model:

```text
contains_spare_parts
```

It is derived during indexing:

```python
"contains_spare_parts": bool(chunk.part_numbers)
```

Therefore:

```text
part_numbers = []
→ contains_spare_parts = False
```

and:

```text
part_numbers = ["HF-300-R10"]
→ contains_spare_parts = True
```

This creates a simple filterable property for parts queries.

---

# 26. Why Store a Boolean If We Already Have `part_numbers`?

The list answers:

> Which part numbers appear in this chunk?

The Boolean answers:

> Is this a spare-parts evidence chunk?

These are different retrieval questions.

For a generic procurement query, the user may not know the part number.

Example:

```text
What filter element should we buy for MX-300?
```

We cannot filter by a specific part number because the user is asking us to discover it.

But we can filter:

```text
contains_spare_parts = True
```

This narrows retrieval to evidence capable of answering the question.

---

# 27. `build_points()`

The indexer verifies:

```python
if len(chunks) != len(embeddings):
    raise ValueError(...)
```

This protects against a serious alignment error.

The system assumes:

```text
chunks[0] ↔ embeddings[0]
chunks[1] ↔ embeddings[1]
...
```

If the lengths differ, indexing must stop.

Silently continuing could associate the wrong vector with the wrong text.

---

# 28. `zip(..., strict=True)`

The implementation also uses:

```python
zip(
    chunks,
    embeddings,
    strict=True,
)
```

This provides an additional safeguard against mismatched sequences.

This is a good example of defensive engineering around data alignment.

---

# 29. Qdrant Upsert

Points are persisted with:

```python
client.upsert(
    collection_name=COLLECTION_NAME,
    points=points,
    wait=True,
)
```

`upsert` means conceptually:

```text
if point does not exist:
    insert it

if point ID already exists:
    update it
```

Combined with deterministic UUIDs, this makes re-indexing safe and repeatable.

---

# 30. `retriever.py`

Location:

```text
src/industrial_copilot/vector_store/retriever.py
```

This file owns low-level Qdrant search.

It does **not** decide what a user means.

Instead, it accepts already-decided constraints such as:

```text
machine_model

alarm_code

contains_spare_parts
```

and translates them into Qdrant filters.

This responsibility boundary is important.

---

# 31. `QdrantSearchResult`

Qdrant's raw point response is converted into the application-specific dataclass:

```python
QdrantSearchResult
```

It exposes:

```text
point_id

score

chunk_id

document_id

document_type

machine_models

section_title

heading_path

revision

effective_date

language

text
```

This prevents higher application layers from depending directly on Qdrant's raw response object.

---

# 32. Machine-Model Filter

When a machine model is provided:

```python
FieldCondition(
    key="machine_models",
    match=MatchValue(
        value=machine_model
    ),
)
```

is added.

Because `machine_models` is stored as an array payload, Qdrant can match a requested model against values contained in that array.

Example:

```text
machine_models:
["MX-200", "MX-220", "MX-300"]
```

can match:

```text
MX-220
```

---

# 33. Alarm-Code Filter

Alarm filtering uses the same principle:

```python
FieldCondition(
    key="alarm_codes",
    match=MatchValue(
        value=alarm_code
    ),
)
```

For:

```text
HX-417
```

Qdrant can restrict candidates to chunks explicitly carrying:

```text
alarm_codes = ["HX-417"]
```

---

# 34. Spare-Parts Filter

Parts lookup uses:

```python
FieldCondition(
    key="contains_spare_parts",
    match=MatchValue(
        value=True
    ),
)
```

This restricts the candidate set to spare-parts evidence chunks.

---

# 35. Combining Filters

Conditions are combined using:

```python
Filter(must=conditions)
```

The important word is:

```text
must
```

This means all supplied constraints must hold.

For a query like:

```text
What does HX-417 mean on MX-200?
```

the application can apply:

```text
machine_models contains MX-200

AND

alarm_codes contains HX-417
```

before semantic ranking.

---

# 36. Metadata Filtering Before Semantic Ranking

This changes the retrieval problem.

Without filters:

```text
Compare query against all 154 chunks
```

With filters:

```text
First find chunks satisfying structured constraints
                         ↓
Then rank those candidates semantically
```

This is especially useful for industrial identifiers.

The embedding model no longer has to infer every exact constraint.

---

# 37. `query_service.py`

Location:

```text
src/industrial_copilot/vector_store/query_service.py
```

This is the high-level interface between user queries and Qdrant retrieval.

Its job is to coordinate:

```text
query analysis
+
query embedding
+
metadata constraints
+
Qdrant search
```

The function is:

```python
retrieve_query(...)
```

---

# 38. Query-Service Flow

The current flow is:

```text
User query
   ↓
analyze_query()
   ↓
Extract identifiers + intent
   ↓
Choose safe metadata constraints
   ↓
Embed original query
   ↓
search_qdrant()
   ↓
Qdrant payload filtering
   ↓
Dense similarity ranking
   ↓
QdrantSearchResult[]
```

This is now the main metadata-aware Qdrant retrieval path.

---

# 39. Why Only One Machine Model Is Automatically Filtered

The code contains:

```python
if len(analysis.machine_models) == 1:
    machine_model = analysis.machine_models[0]
```

This is deliberately conservative.

If a user asks:

```text
Compare MX-200 and MX-300
```
filtering to one model would be wrong.

Therefore automatic model filtering currently happens only when the query contains exactly one model.

---

# 40. Why Only One Alarm Code Is Automatically Filtered

The same principle applies to alarms:

```python
if len(analysis.alarm_codes) == 1:
    alarm_code = analysis.alarm_codes[0]
```

A query comparing several alarms should not accidentally be reduced to one.

Again, the query service prefers safe deterministic behavior over aggressive assumptions.

---

# 41. Retrieval Responsibility Boundaries

The current architecture deliberately separates responsibilities.

## `query_analyzer.py`

Answers:

> What structured information is present in the query?

Examples:

```text
MX-300

HX-417

SOP-MNT-002

HF-300-R10

PARTS_LOOKUP
```

## `query_service.py`

Answers:

> Which of those signals should become retrieval constraints?

## `retriever.py`

Answers:

> How are those constraints represented in Qdrant?

## `indexer.py`

Answers:

> How are chunks and their metadata represented as Qdrant points?

## `corpus.py`

Answers:

> What domain relationships should each chunk actually carry?

This separation became increasingly important as retrieval logic grew.

---

# 42. Dense Search Parity Experiment

Before relying on Qdrant, we needed to verify that moving vectors into the database did not unexpectedly change dense retrieval.

Experiment:

```text
experiments/compare_numpy_qdrant.py
```

A representative query was:

```text
How often should the hydraulic pump on MX-200 be inspected?
```

The NumPy dense retriever and Qdrant returned the same top-five ordering with matching similarity behavior.

Representative top results included:

```text
MAN-MX200 schedule pump

MAN-MX200 pump

MAN-MX220 schedule pump

MAN-MX300 schedule pump

MAN-MX300 pump
```

This established dense retrieval parity.

The important conclusion was:

> Qdrant storage itself was not changing our embedding model's semantic ranking.

That gave us confidence to investigate filtering separately.

---

# 43. Machine-Model Contamination Problem

The parity experiment also exposed an existing dense retrieval problem.

For an MX-200 query, unfiltered dense retrieval included:

```text
MX-220

MX-300
```

results.

This is understandable semantically.

The manuals contain similar hydraulic-pump language.

The embedding model sees those chunks as highly similar.

But from the user's perspective:

```text
MX-200 requested
```

should usually mean:

```text
prefer/filter MX-200-compatible evidence
```

---

# 44. Machine Filtering Experiment

The query:

```text
How often should hydraulic pump on MX-200 be inspected?
```

was tested without and with metadata filtering.

Unrestricted retrieval produced approximately:

```text
1. MAN-MX200 schedule pump
2. MAN-MX200 pump
3. MAN-MX220 schedule pump
4. MAN-MX300 schedule pump
5. MAN-MX300 pump
```

After applying:

```text
machine_model = MX-200
```

results became MX-200-compatible evidence only.

The highest correct evidence remained unchanged.

This demonstrated that metadata filtering could remove cross-model contamination without sacrificing the best result.

---

# 45. Why Machine Filtering Is Better Than Encoding the Model Only in Text

The embedding text already contains model context.

However, embeddings represent similarity, not strict logical constraints.

These are different statements:

```text
"This chunk is semantically related to MX-200 hydraulic pumps."
```

and:

```text
"This chunk must be applicable to MX-200."
```

The first is semantic.

The second is structured.

Therefore the architecture uses:

```text
embedding
for semantic relevance

metadata
for exact applicability
```

---

# 46. SOP Machine-Scope Metadata Bug

While testing model filtering, an important metadata inconsistency was discovered.

SOP procedure definitions correctly declared applicable models:

```text
MX-200

MX-220

MX-300
```

However, corresponding SOP document definitions had:

```text
model_ids: []
```

This created a subtle inconsistency.

---

# 47. Why the SOP Documents Looked Correct Anyway

The generated SOP Markdown looked correct because the SOP generator used procedure-domain data.

But chunk metadata came from the document definition.

Therefore:

```text
Generated Markdown
→ correct models
```

while:

```text
Chunk metadata
→ missing models
```

This is a dangerous class of bug because the human-readable document can appear correct while machine-readable retrieval metadata is wrong.

---

# 48. SOP Scope Fix

The SOP document definitions were corrected to include:

```yaml
model_ids:
  - MX-200
  - MX-220
  - MX-300
```

for the appropriate SOP documents.

But simply correcting the data was not enough.

Without validation, the same inconsistency could return later.

---

# 49. New Domain Validation Invariant

A relationship invariant was added:

> For SOP documents, the document's machine-model scope must match the associated procedure's applicable-model scope.

A regression test was added:

```text
test_sop_document_model_scope_must_match_procedure
```

This turns an accidental convention into an enforced domain rule.

That is a significant engineering improvement.

---

# 50. Lesson from the SOP Bug

The lesson was:

> If two canonical entities represent the same business relationship, their consistency should be validated automatically.

Otherwise different pipeline stages can read different sources and silently disagree.

This is especially important in RAG systems because retrieval correctness depends heavily on metadata correctness.

---

# 51. Alarm Retrieval Problem

Dense retrieval also struggled with exact alarm questions.

Example:

```text
What does alarm HX-417 mean?
```

Before structured alarm filtering, generic sections such as:

```text
Alarm Response Principles
```

could rank above the actual:

```text
HX-417 — Hydraulic Pressure Below Operating Threshold
```

section.

The problem was not that HX-417 was absent from the source.

The problem was that the chunk did not expose the alarm as structured metadata.

---

# 52. Alarm Chunk Inspection

Inspection showed a chunk like:

```text
chunk_id:
TSG-MX200-001::hx-417-hydraulic-pressure-below-operating-threshold::004

section_title:
HX-417 — Hydraulic Pressure Below Operating Threshold

machine_models:
['MX-200']

alarm_codes:
[]

related_procedures:
[]

related_components:
[]
```

The heading clearly contained `HX-417`.

But:

```text
alarm_codes = []
```

meant Qdrant could not perform an exact alarm filter.

---

# 53. Where Should Alarm Metadata Be Added?

There were two possible locations:

```text
markdown_chunker.py
```

or:

```text
corpus.py
```

The decision was to keep the Markdown chunker generic.

The Markdown chunker should understand:
- headings,
- sections,
- tables,
- chunk boundaries,
- document metadata.

It should not need to understand the entire industrial domain repository.

---

# 54. Why Enrichment Belongs in `corpus.py`

`corpus.py` already receives:

```python
repository: CanonicalRepository
```

This means it can validate domain relationships.

The corpus layer can therefore distinguish:

```text
"this text looks like an alarm code"
```

from:

```text
"this is a valid canonical alarm in our domain"
```

That is stronger than raw regex extraction.

Therefore domain enrichment belongs in the corpus-building layer.

---

# 55. Alarm-Code Detection

The corpus currently uses:

```python
ALARM_CODE_PATTERN = re.compile(
    r"\b[A-Z]{2}-\d{3}\b"
)
```

Candidate text combines:

```text
section title + chunk text
```

Detected codes are then checked against:

```text
repository.alarms.alarms
```

Only known canonical alarms are attached.

---

# 56. Canonical Validation of Detected Alarms

This logic is important:

```python
alarm = alarms_by_code.get(alarm_code)
if alarm is None:
    continue
```

A regex match alone does not make something canonical domain knowledge.

The repository remains the authority.

This prevents arbitrary code-shaped text from automatically becoming trusted alarm metadata.

---

# 57. Related Procedure Enrichment

Once a canonical alarm is found, the chunk also inherits:

```python
alarm.related_procedure_ids
```

For HX-417, the enriched metadata became:

```text
alarm_codes:
['HX-417']

related_procedures:
['SOP-MNT-001', 'SOP-OPS-002']
```

This creates useful structured relationships for future retrieval and agentic workflows.

---

# 58. Why We Did Not Fabricate `related_components`

The alarm definition did not provide an explicit component relationship that justified automatically populating:

```text
related_components
```

Therefore we deliberately left it empty.

This reflects another project principle:

> Empty-but-correct metadata is better than populated-but-invented metadata.

RAG systems can become unreliable if developers infer relationships that the source of truth does not actually define.

---

# 59. Persisted Alarm Metadata

After enrichment and re-indexing, Qdrant stored alarm metadata correctly.

An inspected point contained:

```text
document_id:
TSG-MX300-001

section_title:
HX-417 — Hydraulic Pressure Below Operating Threshold

alarm_codes:
['HX-417']

related_procedures:
['SOP-MNT-001', 'SOP-OPS-002']

related_components:
[]
```

This confirmed that the full chain worked:

```text
canonical alarm
      ↓
corpus enrichment
      ↓
Chunk metadata
      ↓
Qdrant payload
```

---

# 60. Alarm Filtering Result

After alarm filtering, the query:

```text
What does alarm HX-417 mean?
```

returned only specific HX-417 evidence:

```text
1. TSG-MX220-001 | HX-417 ...
2. TSG-MX200-001 | HX-417 ...
3. TSG-MX300-001 | HX-417 ...
```

The generic alarm-response section disappeared.

This was a major retrieval improvement.

---

# 61. Why the Alarm Cosine Scores Became Lower

After filtering, scores were around:

```text
0.36
```

This initially looks worse than a larger similarity score.

But the interpretation is different.

Before filtering, Qdrant asked:

> Which chunks across the whole corpus are most semantically similar?

After filtering, it asks:

> Among chunks known to represent HX-417, which are most semantically similar?

The structured filter has already established correctness of the identifier.

Cosine similarity only needs to rank the valid candidate set.

Therefore a lower absolute cosine score is not necessarily a worse retrieval result.

---

# 62. First Metadata-Aware Qdrant Benchmark

The development benchmark contained 25 retrieval cases.

The first metadata-aware Qdrant evaluation produced:

```text
Hit@1 = 0.760
Hit@3 = 0.960
Hit@5 = 1.000
MRR   = 0.848
```

All 25 cases were found within the top five.

---

# 63. Retriever Comparison

| Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---:|---:|---:|
| Dense | 0.640 | 0.840 | 0.880 | 0.743 |
| Routed Hybrid | 0.800 | 0.960 | 1.000 | 0.883 |
| Metadata-Aware Qdrant | 0.760 | 0.960 | 1.000 | 0.848 |

Several conclusions follow.

First:

```text
Metadata Qdrant > plain dense
```

Second:

```text
Metadata Qdrant ≈ strong retrieval coverage
```

because Hit@5 reached 1.000.

Third:

```text
Routed hybrid still has better Hit@1 and MRR
```

because it includes lexical retrieval and identifier-aware ranking behavior that Qdrant dense retrieval does not yet include.

---

# 64. Important Interpretation of the Benchmark

The benchmark did **not** tell us:

> Qdrant should replace BM25.

Instead it told us:

> Qdrant substantially improves the dense infrastructure, especially when combined with metadata constraints.

The likely final retrieval architecture should combine both approaches.

---

# 65. Held-Out Evaluation

A separate 12-query held-out set was evaluated.

The Qdrant results were:

```text
Hit@1 = 0.750
Hit@3 = 0.750
Hit@5 = 0.750
MRR   = 0.750
```

Three cases failed.

Those failures became extremely informative.

---

# 66. Held-Out Failure: Spare Filter Procurement

Query:

```text
I need to order a replacement return-line filter for an MX-300.

Which item should purchasing request?
```

Expected:

```text
SOP-MNT-002

Related Spare Parts
```

Retrieved approximately:

```text
1. SOP-MNT-002 | Applicable Components
2. SOP-MNT-002 | Prerequisites
3. SOP-MNT-002 | Purpose and Scope
4. MAN-MX300 | Hydraulic Return-Line Filter
5. MAN-MX300 | Related Controlled Procedures
```

Notice something important:

The system found the correct SOP.

It did not find the correct **section**.

---

# 67. Held-Out Failure: Pressure Sensor Procedure

Query:

```text
I need the controlled steps for checking and calibrating the hydraulic pressure sensor.
```

Expected:

```text
SOP-MNT-003 | Procedure
```

Retrieved:

```text
SOP-MNT-003 | Purpose and Scope
```

at rank 1, while the desired Procedure section did not reach the required top position.

Again:

```text
correct document

wrong section
```

This suggested a section-selection problem rather than complete retrieval failure.

---

# 68. Held-Out Failure: Pressure Sensor Part

Query:

```text
Which pressure sensor part is suitable for the MX-220?
```

Expected:

```text
SOP-MNT-003 | Related Spare Parts
```

Retrieved:

```text
1. SOP-MNT-003 | Applicable Components
2. SOP-MNT-003 | Purpose and Scope
3. SOP-MNT-003 | Procedure
4. SOP-MNT-003 | Prerequisites
...
```

Again, the correct SOP was found.

But the correct spare-parts section was not selected.

---

# 69. Root-Cause Interpretation

Two of the three failures were spare-parts lookups.

The corpus already contained spare-parts information.

But the chunk metadata did not explicitly identify:

```text
which chunks contain actual spare-part numbers
```

This led to the next investigation.

---

# 70. Canonical Spare-Part Data

The canonical domain already had structured spare-part information.

Examples:

```text
HF-220-R10

10 Micron Hydraulic Return Filter Element

component: HYD_RETURN_FILTER

models: MX-200, MX-220
```

```text
HF-300-R10

Heavy-Duty 10 Micron Hydraulic Return Filter Element

component: HYD_RETURN_FILTER

model: MX-300
```

Pressure sensors included:

```text
PS-210-A

PS-225-B

PS-250-C
```

with model-specific compatibility.

Therefore the information existed in the source of truth.

The retrieval layer simply was not carrying it forward.

---

# 71. Spare-Part Domain Model

The canonical `SparePart` model includes fields such as:

```text
part_number

part_name

component_id

compatible_models

supplier

unit_cost_eur

stock_quantity

reorder_point

lead_time_days
```

This is much richer than ordinary unstructured text.

It provides future opportunities for:
- exact part retrieval,
- procurement tools,
- inventory reasoning,
- model compatibility checks,
- cost-aware agents.

For this milestone, we focused only on retrieval-relevant metadata.

---

# 72. SOP Generation Already Contained Spare Parts

The SOP generator already creates:

```text
## 8. Related Spare Parts
```

with a table containing part information.

Therefore this was not a document-generation failure.

The Markdown contained the information.

The missing link was:

```text
Markdown spare-parts content
        ↓
Chunk metadata
```

---

# 73. Extending the `Chunk` Model

Location:

```text
src/industrial_copilot/retrieval/models.py
```

The `Chunk` model was extended with:

```python
part_numbers: list[str] = Field(
    default_factory=list
)
```

This allows retrieval chunks to carry exact part identifiers.

---

# 74. Why `part_numbers` Belongs on `Chunk`

The chunk is the searchable unit.

If a retrieval result needs to be filtered or interpreted based on spare-part content, that information must be associated with the searchable unit.

Document-level knowledge alone is too coarse.

For example, an SOP may contain:

```text
Purpose

Prerequisites

Procedure

Related Spare Parts
```

Only one of those sections may actually contain the requested part numbers.

Therefore chunk-level metadata is necessary.

---

# 75. SOP Component Enrichment

The corpus builder constructs:

```python
procedures_by_id = {
    procedure.procedure_id: procedure
    for procedure
    in repository.procedures.procedures
}
```

If a chunk's `document_id` corresponds to a procedure, all chunks in that SOP inherit:

```python
procedure.applicable_components
```

For SOP-MNT-002:

```text
related_components:
['HYD_RETURN_FILTER']
```

For SOP-MNT-003:

```text
related_components:
['HYD_PRESSURE_SENSOR']
```

---

# 76. Why All SOP Chunks Get Component Metadata

A procedure as a whole is applicable to its components.

Therefore sections such as:

```text
Purpose

Prerequisites

Procedure

Related Spare Parts
```

can legitimately inherit the SOP's applicable component relationship.

This is document-level domain context that remains valid for each section.

---

# 77. Why Part Numbers Are Different

Part numbers are more specific.

Attaching every SOP part number to every SOP chunk would imply that sections such as:

```text
Purpose and Scope
```

or:

```text
Prerequisites
```

actually contain spare-part evidence.

That would make metadata filtering less precise.

Therefore part numbers are only attached when:

```python
"related spare parts"
in chunk.section_title.lower()
```

This is a deliberate precision decision.

---

# 78. Spare-Part Enrichment Logic

For the `Related Spare Parts` chunk, the corpus builder loops over canonical parts and checks:

```python
if (
    part.component_id
    in procedure.applicable_components
):
    part_numbers.add(
        part.part_number
    )
```

This creates the relationship:

```text
Procedure
   ↓
Applicable component
   ↓
Canonical spare parts for that component
   ↓
Related Spare Parts chunk
```

---

# 79. Enriched SOP Example

After enrichment:

```text
SOP-MNT-002::procedure::006

section: Procedure

components: ['HYD_RETURN_FILTER']

parts: []
```

while:

```text
SOP-MNT-002::related-spare-parts::007

section: Related Spare Parts

components: ['HYD_RETURN_FILTER']

parts:

['HF-220-R10', 'HF-300-R10']
```

This is exactly the intended distinction.

---

# 80. Pressure Sensor Example

For SOP-MNT-003:

```text
Procedure

components:
['HYD_PRESSURE_SENSOR']

parts:
[]
```

but:

```text
Related Spare Parts

components:
['HYD_PRESSURE_SENSOR']

parts:
['PS-210-A', 'PS-225-B', 'PS-250-C']
```

Again:

```text
broad component relationship + precise part-number relationship
```

are represented separately.

---

# 81. Corpus Enrichment Architecture

The complete enrichment process currently handles:

```text
alarm codes

related procedures

related components

part numbers
```

Conceptually:

```text
Generic Markdown chunk
        ↓
CanonicalRepository
        ↓
Domain relationship enrichment
        ↓
Enriched Chunk
        ↓
Embedding/indexing
```

This keeps the Markdown parser independent from domain-specific knowledge.

---

# 82. Qdrant Spare-Part Payload

The indexer now persists:

```python
"part_numbers": chunk.part_numbers,
"contains_spare_parts": bool(
    chunk.part_numbers
),
```

An actual stored point for:

```text
SOP-MNT-002 | Related Spare Parts
```

was inspected.

It contained:

```text
document_id:
SOP-MNT-002

section:
Related Spare Parts

models:
['MX-200', 'MX-220', 'MX-300']

components:
['HYD_RETURN_FILTER']

parts:
['HF-220-R10', 'HF-300-R10']

contains_spare_parts:
True
```

This verified persistence, not just in-memory enrichment.

---

# 83. Query Analyzer

Location:

```text
src/industrial_copilot/retrieval/query_analyzer.py
```

The analyzer extracts deterministic identifiers using regular expressions.

It currently recognizes:

```text
machine models

alarm codes

procedure IDs

part numbers
```

It also assigns a high-level query intent.

Current intents:

```text
GENERAL

PARTS_LOOKUP
```

---

# 84. Identifier Patterns

Machine models:

```text
MX-200

MX-220

MX-300
```

Alarm codes:

```text
HX-417

SF-101

CL-118

EX-312
```

Procedure IDs:

```text
SOP-MNT-002

SOP-OPS-001
```

Part numbers:

```text
HF-300-R10

PS-225-B
```

Matches are normalized to uppercase and duplicates are removed while preserving order.

---

# 85. Why Deterministic Query Analysis Comes Before an LLM

An LLM could theoretically classify these queries.

But many industrial identifiers follow deterministic formats.

For example:

```text
HX-417
```

does not require generative reasoning to detect.

Regex-based analysis is:
- fast,
- cheap,
- testable,
- deterministic,
- explainable.

Therefore exact structured signals are extracted before introducing any LLM-based query understanding.

---

# 86. Original Parts Intent Detector

The initial detector relied heavily on phrases such as:

```text
spare part

part number

replacement part

replacement filter

replacement sensor

which part

which filter is compatible

which sensor is compatible
```

This worked for obvious cases.

But it was brittle.

Natural users do not always phrase procurement questions using exactly those expressions.

---

# 87. Why Phrase Matching Was Too Brittle

Consider:

```text
replacement filter
```

versus:

```text
replacement return-line filter
```

A simple substring check for:

```text
replacement filter
```

does not necessarily match the second phrase because additional words appear between them.

Similarly:

```text
Which pressure sensor part is suitable for MX-220?
```

expresses parts intent without using one of the original exact phrases.

This motivated a more compositional detector.

---

# 88. Procurement Signals

The analyzer now recognizes procurement terms:

```text
buy

buying

order

ordering

purchase

purchasing

procure

procurement
```

These words alone do not automatically make a query a parts lookup.

They are combined with physical part/component terms.

---

# 89. Part Terms

Current part-related terms include:

```text
filter

filter element

sensor

part

component

service kit

seal
```

Again, these terms alone are insufficient.

A maintenance query can contain:

```text
filter
```

without asking for a spare part.

---

# 90. Compatibility Signals

Compatibility terms include:

```text
compatible

suitable

fits

fit
```

These help identify questions such as:

```text
Which hydraulic pressure sensor fits an MX-220?
```

---

# 91. Compositional Parts Intent

The general rule is conceptually:

```text
PART TERM
AND
(
    PROCUREMENT TERM
    OR
    COMPATIBILITY TERM
)
```

Then:

```text
PARTS_LOOKUP
```

Otherwise:

```text
GENERAL
```

This is more general than memorizing complete user sentences.

---

# 92. Protecting Maintenance Queries

An important negative test is:

```text
When should the MX-300 return filter be replaced?
```

The query contains:

```text
filter
```

but does not contain procurement or compatibility intent.

Therefore it remains:

```text
GENERAL
```

This matters because otherwise every maintenance question containing the word `filter` could be incorrectly forced into spare-parts retrieval.

---

# 93. Query-Service Parts Filtering

When:

```python
analysis.intent == QueryIntent.PARTS_LOOKUP
```

the query service sets:

```python
contains_spare_parts = True
```

and forwards it to Qdrant.

The query service therefore translates:

```text
semantic user intent
```

into:

```text
structured retrieval constraint
```

---

# 94. Fresh Smoke Test

After implementing parts filtering, fresh query phrasings were used for manual validation.

These were not intended as a formal benchmark.

They were used to test end-to-end behavior.

Queries included:

```text
What filter element should we buy for an MX-300?
```

```text
Which hydraulic pressure sensor fits an MX-220?
```

```text
When is the MX-300 return filter due for replacement?
```

```text
What does HX-417 mean on an MX-200?
```

---

# 95. Fresh Smoke-Test Failure: `buy`

The first query initially produced:

```text
1. SOP-MNT-002 | Prerequisites
2. SOP-MNT-002 | Applicable Components
3. SOP-MNT-002 | Related Spare Parts
...
```

This indicated that:

```text
contains_spare_parts=True
```

had not been activated.

The query clearly expressed procurement intent:

```text
should we buy
```

but the analyzer did not yet recognize:

```text
buy
```

as a procurement term.

---

# 96. Why Adding `buy` Was a Valid Improvement

We did not add a special case for the entire smoke-test sentence.

Instead, we generalized the procurement vocabulary with:

```text
buy

buying
```

This is a meaningful domain-independent procurement signal.

A regression test was added to protect the behavior.

This is preferable to repeatedly hard-coding benchmark sentences.

---

# 97. Result After `buy` Improvement

After the change:

```text
QUERY:
What filter element should we buy for an MX-300?
```

returned:

```text
1. 0.5740 | SOP-MNT-002 | Related Spare Parts
2. 0.4249 | SOP-MNT-003 | Related Spare Parts
3. 0.4155 | SOP-MNT-001 | Related Spare Parts
```

The desired evidence moved to rank 1.

More importantly, the candidate set now consisted only of spare-parts sections.

This confirmed that the metadata filter was active.

---

# 98. Pressure Sensor Smoke Test

Query:

```text
Which hydraulic pressure sensor fits an MX-220?
```

returned:

```text
1. SOP-MNT-003 | Related Spare Parts
2. SOP-MNT-002 | Related Spare Parts
3. SOP-MNT-001 | Related Spare Parts
```

The correct pressure-sensor spare-parts section ranked first.

This demonstrated compatibility-language handling.

---

# 99. Maintenance Smoke Test

Query:

```text
When is the MX-300 return filter due for replacement?
```

returned:

```text
1. MAN-MX300-001 | Hydraulic Return-Line Filter
2. MAN-MX300-001 | Preventive Maintenance Schedule — Hydraulic Return-Line Filter
...
```

This was especially important.

The query contains:

```text
filter

replacement
```

but is asking:

```text
when?
```

rather than:

```text
which part?
```

The system correctly avoided forcing the query into the spare-parts path.

---

# 100. Alarm Smoke Test

Query:

```text
What does HX-417 mean on an MX-200?
```

returned:

```text
TSG-MX200-001

HX-417 — Hydraulic Pressure Below Operating Threshold
```

This verified the combined:

```text
machine filter
+
alarm filter
```

behavior.

---

# 101. Automated Tests Added During This Milestone

Regression coverage was added for several important behaviors.

Corpus tests protect:
- alarm metadata enrichment,
- alarm related procedures,
- SOP component metadata,
- spare-part number metadata.

Domain validation protects:
- SOP document/procedure machine-scope consistency.

Query analyzer tests protect:
- alarm extraction,
- model extraction,
- procedure extraction,
- part-number extraction,
- normalization,
- deduplication,
- parts intent,
- procurement language,
- compatibility language,
- maintenance false-positive protection,
- `buy` procurement language.

Query-service tests protect forwarding of:
- machine model,
- alarm code,
- combined model + alarm,
- no unnecessary metadata filters,
- spare-parts filter.

---

# 102. Test-Suite Evolution

During this milestone the test suite grew incrementally.

At different points we observed:

```text
71 tests passing
```

then:

```text
74 tests passing
```

then:

```text
77 tests passing
```

and finally:

```text
78 tests passing
```

The final milestone state is:

```text
78 passed
```

This growth reflects regression tests added alongside newly discovered retrieval behavior.

---

# 103. Why Regression Tests Matter Here

Retrieval systems are easy to improve in one area while silently damaging another.

For example, aggressively detecting parts queries could improve procurement retrieval while breaking:

```text
When should the filter be replaced?
```

A regression test ensures that future changes preserve both:

```text
procurement → PARTS_LOOKUP
```

and:

```text
maintenance timing → GENERAL
```

This is much safer than relying on manual testing alone.

---

# 104. Benchmark Discipline

The original held-out benchmark was designed to measure generalization.

However, after inspecting its failures and making architectural decisions based on them, those queries influenced development.

Therefore they are no longer pristine held-out examples.

They can still be used as:

```text
diagnostic regression cases
```

but should not be presented as untouched final evaluation data.

---

# 105. Development vs Diagnostic vs Held-Out Data

A useful distinction is:

## Development set

Used repeatedly while building and tuning the system.

## Diagnostic cases

Used to investigate known failure modes.

## Held-out set

Kept unseen until the architecture is sufficiently stable.

Once a held-out failure directly influences implementation, that case becomes diagnostic rather than truly unseen.

---

# 106. Why We Need a Fresh Benchmark Later

After the hybrid-Qdrant architecture stabilizes, a new set of unseen questions should be created.

It should cover:
- semantic paraphrases,
- exact alarms,
- model-specific questions,
- spare-part procurement,
- part compatibility,
- maintenance intervals,
- procedures,
- safety,
- multi-constraint questions.

That fresh benchmark will provide a more honest estimate of retrieval generalization.

---

# 107. What Qdrant Solved

Qdrant gave the project several important capabilities.

## Persistent vector storage

Vectors no longer need to exist only in memory.

## Metadata payload storage

Chunks can carry structured industrial context.

## Metadata filtering

Queries can enforce exact constraints.

## Deterministic indexing

Stable UUIDs make repeated indexing safer.

## Separation of indexing and querying

Corpus preparation and runtime search become clearer architectural stages.

## Deployment foundation

The application now has a vector-store abstraction that can later move from local persistence to a deployed service.

---

# 108. What Qdrant Did Not Solve

Qdrant is not the complete retrieval system.

It did not automatically solve:
- BM25 lexical retrieval,
- exact-token ranking,
- reciprocal-rank fusion,
- query routing,
- reranking,
- procedure-section selection,
- answer generation,
- citation generation,
- hallucination prevention,
- agent/tool orchestration.

This distinction is essential.

A vector database is infrastructure.

It is not equivalent to a complete RAG system.

---

# 109. Current Limitation: Exact Part Number Filtering

The query analyzer already extracts explicit part numbers.

Example:

```text
HF-300-R10
```

However, `query_service.py` does not yet forward an exact part-number constraint to Qdrant.

The payload already stores:

```text
part_numbers
```

so this capability can be added later.

---

# 110. Current Limitation: Procedure-ID Filtering

The analyzer also extracts:

```text
SOP-MNT-002
```

but the Qdrant query service does not yet convert this into an exact document constraint.

This is another future metadata-filter opportunity.

---

# 111. Current Limitation: Procedure Section Selection

The held-out procedure query showed:

```text
correct SOP

wrong section
```

for controlled calibration steps.

This suggests future work around:
- procedure intent,
- section-type metadata,
- lexical signals,
- reranking,
- hybrid retrieval.

We should solve this architecturally rather than by adding a special phrase for one benchmark query.

---

# 112. Current Limitation: Qdrant Is Dense-Only

The current Qdrant search path performs:

```text
dense vector search + metadata constraints
```

The previous strongest retrieval architecture also used:

```text
BM25
+
routing
+
fusion
+
identifier boosting
```

Those capabilities have not yet been integrated into the Qdrant-backed path.

---

# 113. Why Qdrant Should Not Replace BM25

Consider:

```text
What does HX-417 mean?
```

Exact lexical signals are extremely valuable.

Consider:

```text
Why can hydraulic pressure become unstable during operation?
```

Semantic similarity is extremely valuable.

Industrial knowledge contains both kinds of questions.

Therefore the system should preserve both retrieval modes.

---

# 114. Recommended Next Retrieval Architecture

The likely next architecture is:

```text
                        User Query
                            │
                            ▼
                     Query Analyzer
                            │
                 ┌──────────┴──────────┐
                 │                     │
                 ▼                     ▼
         Metadata Constraints     Retrieval Router
                                       │
                            ┌──────────┴──────────┐
                            │                     │
                            ▼                     ▼
                   Qdrant Dense Search       BM25 Search
                            │                     │
                            └──────────┬──────────┘
                                       ▼
                                  Rank Fusion
                                       │
                                       ▼
                             Identifier Handling
                                       │
                                       ▼
                               Top Evidence
                                       │
                                       ▼
                         Future Answer Generation
```

This combines:
- semantic similarity,
- exact lexical matching,
- deterministic identifiers,
- structured metadata,
- ranking.

---

# 115. Why We Are Not Adding the LLM Yet

It would now be tempting to connect the top Qdrant chunks directly to an LLM.

However, the routed hybrid retriever still has slightly better rank-1 performance than the current Qdrant-only dense path.

Therefore the next engineering question is:

> How should the proven hybrid retrieval logic use Qdrant as its dense backend?

That should be answered before introducing answer generation.

Otherwise the LLM would be built on an avoidably incomplete retrieval architecture.

---

# 116. Current Retrieval Metrics to Remember

The key development results so far are:

| Retriever | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---:|---:|---:|
| Dense | 0.640 | 0.840 | 0.880 | 0.743 |
| Routed Hybrid | 0.800 | 0.960 | 1.000 | 0.883 |
| Metadata-Aware Qdrant | 0.760 | 0.960 | 1.000 | 0.848 |

These numbers should be treated as milestones rather than final project performance.

The final architecture still needs a fresh unseen evaluation.

---

# 117. Full Data Flow at the End of This Milestone

The system now behaves conceptually as follows:

```text
data/canonical/*.yaml
        │
        ▼
CanonicalRepository
        │
        ▼
Domain validation
        │
        ▼
Generated Markdown documents
        │
        ▼
markdown_chunker.py
        │
        ▼
Generic Chunk objects
        │
        ▼
corpus.py
        │
        ├── alarm enrichment
        ├── related procedures
        ├── SOP components
        └── spare-part numbers
        │
        ▼
Enriched Chunk objects
        │
        ▼
Embedder
        │
        ▼
384-dimensional vectors
        │
        ▼
indexer.py
        │
        ├── deterministic UUID
        ├── vector
        └── payload
        │
        ▼
Qdrant
        │
        ▼
User query
        │
        ▼
query_analyzer.py
        │
        ├── model IDs
        ├── alarm codes
        ├── procedure IDs
        ├── part numbers
        └── intent
        │
        ▼
query_service.py
        │
        ├── query embedding
        ├── machine constraint
        ├── alarm constraint
        └── spare-parts constraint
        │
        ▼
retriever.py
        │
        ▼
Qdrant Filter + vector search
        │
        ▼
Top evidence chunks
```

---

# 118. Reproducing the Milestone

From the repository root:

```bash
cd /Users/tusharrao/Documents/industrial-knowledge-copilot
```

Activate the environment:

```bash
source .venv/bin/activate
```

Validate the complete automated suite:

```bash
python -m pytest -v
```

Expected milestone result:

```text
78 passed
```

---

# 119. Rebuilding the Qdrant Index

Run:

```bash
python scripts/index_qdrant.py
```

Expected high-level output:

```text
Qdrant indexing complete

Chunks indexed: 154

Embedding dimension: 384

Stored points: 154
```

A Hugging Face warning about unauthenticated requests may appear.

That warning does not indicate a retrieval failure.

It means the embedding model is being downloaded/accessed without an authenticated Hugging Face token, which can result in lower rate limits.

---

# 120. Useful Qdrant Experiments

Collection exploration:

```bash
python experiments/qdrant_collection_lab.py
```

Point inspection:

```bash
python experiments/qdrant_point_lab.py
```

Dense Qdrant search:

```bash
python experiments/qdrant_search_lab.py
```

NumPy/Qdrant comparison:

```bash
python experiments/compare_numpy_qdrant.py
```

Metadata filtering:

```bash
python experiments/qdrant_filter_lab.py
```

Query-service behavior:

```bash
python experiments/qdrant_query_service_lab.py
```

Alarm payload inspection:

```bash
python experiments/qdrant_alarm_point_lab.py
```

Qdrant retrieval evaluation:

```bash
python experiments/evaluate_qdrant_retrieval.py
```

These experiment files are useful for understanding individual layers without running the complete future application.

---

# 121. File-by-File Reference

## `src/industrial_copilot/vector_store/config.py`

Owns:
- collection name,
- embedding dimension,
- local storage path.

Does not own:
- query behavior,
- indexing logic,
- domain metadata.

---

## `src/industrial_copilot/vector_store/client.py`

Owns:
- local Qdrant client creation,
- collection initialization.

Does not own:
- embedding generation,
- point construction,
- query intent.

---

## `src/industrial_copilot/vector_store/indexer.py`

Owns:
- deterministic point IDs,
- chunk-to-payload conversion,
- chunk/vector pairing,
- Qdrant upsert.

Does not own:
- domain enrichment,
- query analysis,
- retrieval routing.

---

## `src/industrial_copilot/vector_store/retriever.py`

Owns:
- Qdrant search,
- payload-filter construction,
- conversion of Qdrant points into application results.

Does not own:

- deciding what the user means,
- generating embeddings,
- canonical domain relationships.

---

## `src/industrial_copilot/vector_store/query_service.py`

Owns:
- coordinating query analysis,
- query embedding,
- safe metadata constraints,
- calling Qdrant retrieval.

Does not own:
- low-level Qdrant point construction,
- canonical metadata enrichment.

---

## `src/industrial_copilot/retrieval/models.py`

Owns:
- the retrieval `Chunk` contract.

Important fields include:

```text
text

document identity

machine scope

section information

related components

related procedures

part numbers

alarm codes

embedding text
```

---

## `src/industrial_copilot/retrieval/corpus.py`

Owns:
- corpus construction,
- canonical-domain enrichment.

This is where generic document chunks become domain-aware retrieval chunks.

---

## `src/industrial_copilot/retrieval/query_analyzer.py`

Owns:
- deterministic identifier extraction,
- simple deterministic intent detection.

It currently recognizes general vs parts lookup intent.

---

## `scripts/index_qdrant.py`

Owns:
- reproducible Qdrant indexing workflow.

This is the operational entry point for rebuilding the vector index.

---

## `tests/test_corpus.py`

Protects:
- corpus completeness,
- source metadata,
- alarm enrichment,
- procedure enrichment,
- component enrichment,
- spare-part enrichment.

---

## `tests/test_qdrant_query_service.py`

Protects:
- machine filter forwarding,
- alarm filter forwarding,
- combined filtering,
- semantic no-filter behavior,
- parts-filter forwarding.

---

## `tests/test_query_analyzer.py`

Protects:
- identifier extraction,
- normalization,
- parts-intent classification,
- maintenance false-positive behavior,
- procurement/compatibility vocabulary.

---

# 122. Key Engineering Decisions

The following decisions should be remembered.

### Decision 1

Use Qdrant as vector infrastructure, not as the entire retrieval strategy.

### Decision 2

Start with local persistent Qdrant before adding remote deployment complexity.

### Decision 3

Keep the Markdown chunker generic.

### Decision 4

Perform canonical domain enrichment in `corpus.py`.

### Decision 5

Use deterministic UUID5 point IDs.

### Decision 6

Store rich structured payload metadata alongside vectors.

### Decision 7

Use metadata for exact constraints and embeddings for semantic similarity.

### Decision 8

Automatically apply machine/alarm constraints only when unambiguous.

### Decision 9

Attach SOP component metadata broadly but part numbers only to actual spare-parts sections.

### Decision 10

Use a derived `contains_spare_parts` Boolean for generic parts discovery.

### Decision 11

Prefer deterministic query analysis for structured industrial identifiers.

### Decision 12

Protect maintenance queries from aggressive parts-intent classification.

### Decision 13

Do not repeatedly tune against a previously held-out benchmark and continue calling it unseen.

### Decision 14

Do not add the LLM until the Qdrant and hybrid retrieval architectures are reconciled.

---

# 123. Major Lessons Learned

## Lesson 1 — Better embeddings are not the answer to every retrieval problem

Exact machine IDs, alarm codes, part numbers, and document relationships often belong in metadata.

---

## Lesson 2 — Metadata quality can matter as much as vector quality

The SOP scope bug showed that perfect embeddings cannot compensate for incorrect structured metadata.

---

## Lesson 3 — Human-readable correctness does not guarantee machine-readable correctness

The generated SOP looked correct while its chunk metadata was wrong.

Both layers must be validated.

---

## Lesson 4 — Retrieval failures should be classified before being fixed

The spare-parts failures were not simply:

```text
bad retrieval
```

They were more specifically:

```text
correct document

wrong section

missing structured section metadata
```

That diagnosis led to a better solution.

---

## Lesson 5 — Preserve architectural boundaries

Domain enrichment in the Markdown parser would have made the parser increasingly coupled to industrial business logic.

Keeping enrichment in the corpus layer produces a cleaner system.

---

## Lesson 6 — Empty metadata can be safer than invented metadata

We intentionally did not fabricate alarm-component relationships.

---

## Lesson 7 — Query intent needs negative examples

Detecting parts lookups is only half the problem.

The system must also prove that ordinary maintenance questions are not incorrectly classified.

---

## Lesson 8 — Evaluation data changes status after it influences development

Once held-out failures guide implementation, they should become diagnostic cases and a new unseen set should be created later.

---

## Lesson 9 — A vector database is not a RAG system

Qdrant solves vector persistence and retrieval infrastructure.

RAG still requires:
- retrieval strategy,
- evidence selection,
- prompt construction,
- answer generation,
- grounding,
- citations,
- evaluation.

---

# 124. Glossary

## Embedding

A numerical vector representing semantic information about text.

---

## Embedding dimension

The number of numeric values in an embedding.

This project currently uses:

```text
384
```

dimensions.

---

## Vector database

A database designed to store vectors and efficiently retrieve similar vectors.

---

## Qdrant collection

A logical group of vector points with a defined vector configuration.

Current collection:

```text
industrial_knowledge
```

---

## Qdrant point

A stored unit consisting conceptually of:

```text
ID + vector + payload
```

In this project, one retrieval chunk corresponds to one Qdrant point.

---

## Payload

Structured metadata stored alongside a Qdrant vector.

Examples:

```text
document_id

machine_models

alarm_codes

part_numbers

section_title
```

---

## Metadata filtering

Restricting search candidates based on structured payload conditions.

Example:

```text
machine_models contains MX-300
```

---

## Cosine similarity

A measure of the angle between vectors.

It is used here to rank semantic similarity between the query embedding and chunk embeddings.

---

## Dense retrieval

Retrieval based on embedding-vector similarity.

---

## Lexical retrieval

Retrieval based primarily on words/tokens.

BM25 is the lexical retriever used in this project.

---

## Hybrid retrieval

Combining semantic and lexical retrieval.

---

## BM25

A lexical ranking algorithm that scores documents based on query-term occurrence and term importance.

---

## Reciprocal Rank Fusion

A method for combining rankings from multiple retrievers without requiring their raw scores to be directly comparable.

---

## UUID

Universally Unique Identifier.

Qdrant points in this project use UUID-form identifiers.

---

## UUID5

A deterministic UUID generated from a namespace and input string.

The same chunk ID produces the same point UUID.

---

## Idempotent indexing

Running the same indexing operation repeatedly produces the same logical database state instead of creating duplicates.

---

## Hit@1

Fraction of evaluation queries where an acceptable result appears at rank 1.

---

## Hit@3

Fraction where an acceptable result appears within the first three results.

---

## Hit@5

Fraction where an acceptable result appears within the first five results.

---

## MRR

Mean Reciprocal Rank.

A metric that rewards systems for ranking the first relevant result as highly as possible.

---

## Query intent

A high-level classification of what the user is trying to accomplish.

Current examples:

```text
GENERAL

PARTS_LOOKUP
```

---

## Canonical data

The authoritative structured domain representation used to generate and validate downstream artifacts.

In this project, canonical YAML is the source of truth.

---

## Metadata enrichment

Adding validated domain relationships to otherwise generic document chunks.

Examples:

```text
alarm codes

related procedures

components

part numbers
```

---

# 125. Next Milestone

The Qdrant V1 milestone is considered complete when:

```text
154 chunks are persistently indexed

384-dimensional embeddings are stored

machine filtering works

alarm filtering works

spare-parts filtering works

metadata enrichment is validated

query-service routing is tested

78 automated tests pass
```

Those conditions are now satisfied.

The next retrieval milestone should **not** immediately add an LLM.

The next goal is to integrate the strongest pieces developed so far:

```text
Qdrant dense retrieval
+
BM25 lexical retrieval
+
query routing
+
metadata constraints
+
identifier handling
+
rank fusion
```

After that architecture is evaluated on a fresh unseen benchmark, the project will be ready to introduce:

```text
retrieved evidence
        ↓
prompt construction
        ↓
LLM
        ↓
grounded answer
        ↓
source citations
```

That will mark the transition from a retrieval system toward a complete RAG system.

---

# 126. Milestone Summary

The Qdrant milestone began as a vector-database integration.

It ultimately improved much more than storage.

During the work, we discovered and corrected:
- machine-scope metadata inconsistencies,
- missing alarm metadata,
- missing alarm/procedure relationships,
- missing SOP component metadata,
- missing spare-part metadata,
- brittle procurement intent detection,
- inadequate section-level parts retrieval.

The most important architectural result is therefore not simply:

```text
"We added Qdrant."
```

It is:

```text
"We built a persistent, metadata-aware retrieval layer where structured industrial constraints and semantic vector search work together."
```
The system now has a much stronger foundation for the next stage of the Industrial Knowledge Copilot.
