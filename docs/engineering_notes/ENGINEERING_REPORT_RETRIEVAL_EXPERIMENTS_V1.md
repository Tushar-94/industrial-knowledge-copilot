# Engineering Report: Retrieval Experiments V1

**Project**: Industrial Knowledge Copilot

**Scope**: Dense Retrieval → Lexical Retrieval → Hybrid Retrieval → Query-Aware Routing

**Status**: Retrieval V1 experiment complete

**Embedding Model**: sentence-transformers/all-MiniLM-L6-v2

**Corpus Size**: 154 chunks

**Embedding Dimension**: 384

**Embedding Model Maximum Sequence Length**: 256 tokens

---

# 1. Purpose of This Report

This report documents the evolution of the Industrial Knowledge Copilot retrieval system from a simple dense semantic retriever into a query-aware retrieval architecture.

The objective is to capture not only the final implementation, but also the engineering reasoning that led to it.

The retrieval system was developed experimentally.

Each architectural change followed the same process:

1. Build the simplest reasonable retrieval approach.
2. Evaluate it using a reproducible benchmark.
3. Inspect concrete failures.
4. Form a hypothesis explaining those failures.
5. Introduce one retrieval improvement.
6. Measure the system again.
7. Keep or reject the change based on evidence.

The final architecture was therefore not selected because hybrid search, BM25, routing, or score boosting are commonly used in RAG systems.

Each component was introduced because a measurable failure demonstrated that it was needed.

---

# 2. Starting Point

Before these experiments began, the project already had a retrieval-ready corpus.

The generated industrial documents had been converted into semantic chunks.

The complete corpus contained:
```txt
154 chunks
```
The chunks originated from:

* operation and maintenance manuals,
* troubleshooting guides,
* standard operating procedures.

Each chunk contained retrieval text together with source metadata such as:

* document ID,
* document type,
* machine model,
* section title,
* revision,
* language,
* heading path.

All chunks had also been checked against the embedding model’s token limit.

The embedding model used throughout the experiments was:
```txt
sentence-transformers/all-MiniLM-L6-v2
```

Its relevant properties were:
```txt
Embedding dimension: 384

Maximum sequence length: 256 tokens
```

All 154 corpus chunks were below the 256-token limit.

Therefore the retrieval experiments could proceed without embedding-time truncation.

---

# 3. Retrieval Architecture at the Beginning

The initial search pipeline was intentionally simple:
```txt
User Query
    |
    v
Embedding Model
    |
    v
384-dimensional query vector
    |
    v
Compare against all chunk vectors
    |
    v
Cosine similarity
    |
    v
Rank chunks
    |
    v
Top-K results
```

Because embeddings were normalized, similarity could be calculated efficiently with vector dot products.

At this stage there was:

* no BM25,
* no hybrid search,
* no query router,
* no identifier boosting,
* no intent detection,
* no vector database.

The purpose was to establish a simple dense-search baseline before adding complexity.

---

# 4. Relevant Dense Retrieval Files

The main files involved in dense retrieval are:
```txt
src/industrial_copilot/retrieval/embedder.py
```

Responsibilities:

* loading the SentenceTransformer model,
* embedding chunks,
* embedding user queries,
* normalizing embeddings,
* exposing embedding dimension and maximum sequence length.

```txt
src/industrial_copilot/retrieval/in_memory.py
```
Responsibilities:

* calculating similarity between the query embedding and chunk embeddings,
* ranking chunks,
* returning the top-K semantic results.

The central dense-search operation is conceptually:
```python
scores = chunk_embeddings @ query_embedding
```

With:
```txt
chunk_embeddings shape = (154, 384)

query_embedding shape = (384,)
```

the result is:
```txt
154 similarity scores
```

one score for every corpus chunk.
```txt
src/industrial_copilot/retrieval/corpus.py
```

Responsibilities:

* loading every generated document,
* chunking each document,
* combining all chunks into one searchable corpus.
Important exploratory scripts include:
```txt
experiments/retrieval_lab.py

experiments/corpus_retrieval_lab.py
```

The first was used to understand retrieval over one manual.

The second expanded retrieval to all 154 chunks.

---

# 5. First Full-Corpus Retrieval Experiment

The complete corpus experiment used representative queries such as:
```txt
How often should the hydraulic pump on the MX-200 be inspected?

When should the MX-300 return filter be replaced?

What does alarm HX-417 mean?

What can cause HX-417?

Which procedure explains hydraulic return filter replacement?

Which replacement filter is compatible with the MX-300?
```

This experiment immediately demonstrated an important pattern.

Dense retrieval was excellent for semantic questions.

For example:

QUERY:
```txt
How often should the hydraulic pump on the MX-200 be inspected?
```
Results:
```txt
1. 0.7756 | MAN-MX200-001 | Preventive Maintenance Schedule — Hydraulic Pump
2. 0.7737 | MAN-MX200-001 | Hydraulic Pump
3. 0.7721 | MAN-MX220-001 | Preventive Maintenance Schedule — Hydraulic Pump
4. 0.7683 | MAN-MX300-001 | Preventive Maintenance Schedule — Hydraulic Pump
5. 0.7651 | MAN-MX300-001 | Hydraulic Pump
```

The two best results both came from the correct MX-200 manual.

Dense retrieval also performed strongly on:
```txt
When should the MX-300 return filter be replaced?
```
with:
```txt
Rank 1:
MAN-MX300-001 | Hydraulic Return-Line Filter
```

This established that dense embeddings could successfully capture semantic relationships such as:
```txt
inspection

servicing

maintenance

replacement

hydraulic pump

return filter
```

even when the exact wording differed.

---

# 6. First Major Dense Retrieval Failure: Industrial Identifiers

The same experiment exposed a completely different behavior for industrial identifiers.

Consider:
```txt
What does alarm HX-417 mean?
```

Dense retrieval returned:
```txt
1. 0.5127 | TSG-MX220-001 | Alarm Response Principles
2. 0.5023 | TSG-MX200-001 | Alarm Response Principles
3. 0.4897 | TSG-MX300-001 | Alarm Response Principles
4. 0.4633 | SOP-OPS-002 | Prerequisites
5. 0.4552 | SOP-OPS-001 | Safety Warnings
```

The actual:
```txt
HX-417 — Hydraulic Pressure Below Operating Threshold
```

chunk did not appear in the top five.

This suggested that the embedding model understood the general meaning of:
```txt
alarm
```
but did not treat:
```txt
HX-417
```
as a sufficiently strong exact identifier.

Another example made this weakness even clearer.

Query:
```txt
What does HX-421 indicate?
```

Dense results:
```txt
1. TSG-MX220-001 | HX-430 — Hydraulic Reservoir Fluid Level Low
2. TSG-MX220-001 | HX-418 — Hydraulic Pressure Sensor Signal Implausible
3. TSG-MX220-001 | HX-417 — Hydraulic Pressure Below Operating Threshold
4. TSG-MX300-001 | HX-430 — Hydraulic Reservoir Fluid Level Low
5. TSG-MX200-001 | HX-430 — Hydraulic Reservoir Fluid Level Low
```
The query explicitly contained:
```txt
HX-421
```

but dense retrieval returned neighboring hydraulic alarm codes instead.

This produced the first important retrieval lesson:

> Dense embeddings are good at semantic similarity, but exact industrial identifiers require stronger lexical signals.

---

# 7. Second Dense Failure: Structured Parts Lookup

Dense retrieval also failed on:
```txt
Which replacement filter is compatible with the MX-300?
```

Results:
```txt
1. SOP-OPS-001 | Applicable Machine Models
2. SOP-MNT-003 | Applicable Machine Models
3. SOP-OPS-002 | Applicable Machine Models
4. SOP-HSE-001 | Applicable Machine Models
5. SOP-MNT-001 | Applicable Machine Models
```
All five results strongly matched:
```txt
MX-300
compatible
applicable models
```
but failed to understand that the query was asking for a physical replacement part.

The correct evidence was:
```txt
SOP-MNT-002 | Related Spare Parts
```
containing the relevant MX-300 filter information.

This exposed another limitation:

> Semantic similarity alone does not necessarily understand structured lookup intent.

---

# 8. Building a Retrieval Benchmark

Manual inspection was useful, but it was not sufficient.

A reproducible benchmark was created so changes could be measured consistently.

Relevant benchmark file:
```txt
src/industrial_copilot/evaluation/benchmark.py
```

Relevant evaluation logic:
```txt
src/industrial_copilot/evaluation/retrieval.py
```

Dense evaluation script:
```txt
experiments/evaluate_dense_retrieval.py
```
The development benchmark contained:
```txt
25 retrieval cases
```
covering:

* specifications,
* maintenance,
* condition-based maintenance,
* alarms,
* safety,
* procedures,
* spare parts,
* components,
* paraphrases.

Metrics included:

* Hit@1,
* Hit@3,
* Hit@5,
* Mean Reciprocal Rank (MRR).

---

# 9. Understanding the Metrics

## Hit@1

Measures whether acceptable evidence appears as the first result.

For example:

```txt
Expected evidence rank = 1
```
counts as a Hit@1 success.

---

## Hit@3

Measures whether acceptable evidence appears anywhere in the first three results.

---

## Hit@5

Measures whether acceptable evidence appears anywhere in the first five results.

This is particularly important for RAG because multiple retrieved chunks may later be passed into an LLM.

---

## Mean Reciprocal Rank

MRR rewards systems that rank relevant evidence higher.

Examples:
```txt
Relevant rank = 1 -> reciprocal rank = 1.00

Relevant rank = 2 -> reciprocal rank = 0.50

Relevant rank = 3 -> reciprocal rank = 0.33

Miss -> reciprocal rank = 0
```
The mean is calculated across all benchmark cases.

---

# 10. Correcting the Benchmark Before Optimizing Retrieval

The first version of the benchmark assumed that every question had one exact correct document and section.

This proved too strict.

For example:
```txt
What does HX-417 mean?
```
did not specify a machine model.

Valid evidence could exist in:
```txt
TSG-MX200-001 | HX-417
TSG-MX220-001 | HX-417
TSG-MX300-001 | HX-417
```
Similarly, a safety question could legitimately be answered by:

* the manual safety section,
* the light curtain section,
* or the relevant troubleshooting alarm section.

The benchmark was therefore redesigned to support:

multiple acceptable evidence sources
using:
```txt
ExpectedEvidence
```
objects.

This was an important methodological decision.

Instead of modifying retrieval to satisfy incorrect labels, the benchmark itself was corrected first.

This prevented evaluation errors from being mistaken for model errors.

---

# 11. Dense Retrieval Baseline

After correcting the benchmark, dense-only retrieval produced:
```txt
Cases: 25

Hit@1: 0.640
Hit@3: 0.840
Hit@5: 0.880
MRR:   0.743
```
Category-level Hit@5:
```txt
alarm                0.500
component            1.000
condition            1.000
maintenance          1.000
paraphrase           1.000
parts                0.500
procedure            1.000
safety               1.000
specification        1.000
```
This result established the official dense baseline.

The remaining failures were:
```txt
alarm-001
What does alarm HX-417 mean?

alarm-003
What does HX-421 indicate?

parts-001
Which replacement filter is compatible with the MX-300?
```
This failure pattern strongly supported the hypothesis that dense retrieval struggled mainly with exact identifiers and structured parts lookup.

---

# 12. Dense Baseline Summary

Dense Retrieval Baseline
```txt
Hit@1 = 64%
Hit@3 = 84%
Hit@5 = 88%
MRR   = 0.743
```
Strengths:

* maintenance questions,
* specifications,
* semantic paraphrases,
* component descriptions,
* safety questions,
* procedure questions.

Weaknesses:

* exact alarm codes,
* exact industrial identifiers,
* structured spare-part lookup.

---

# 13. Introducing BM25 Lexical Retrieval

Based on the identifier failures, lexical retrieval was introduced.

The implementation uses BM25.

Relevant implementation file:
```txt
src/industrial_copilot/retrieval/lexical.py
```
Library:
```txt
rank-bm25
```
The tokenizer was intentionally designed to preserve identifiers such as:
```txt
HX-417
HX-421
MX-300
SOP-MNT-002
HF-300-R10
```
instead of incorrectly splitting them into smaller pieces.

Relevant lexical test file:
```txt
tests/test_lexical_retrieval.py
```
Exploratory script:
```txt
experiments/lexical_retrieval_lab.py
```

Full lexical benchmark:
```txt
experiments/evaluate_lexical_retrieval.py
```

---

# 14. Why BM25 Was Introduced

Dense retrieval understands meaning.

BM25 is better suited for exact lexical matching.

The working hypothesis was:
```txt
Dense search
-> strong semantic matching

BM25
-> strong exact-code and keyword matching
```
The three known dense failures were tested first.

---

# 15. BM25 Experiment Results on Known Failures

Query:
```txt
What does alarm HX-417 mean?
```
BM25 results:
```txt
1. 3.4058 | TSG-MX200-001 | HX-417 — Hydraulic Pressure Below Operating Threshold
2. 3.4058 | TSG-MX300-001 | HX-417 — Hydraulic Pressure Below Operating Threshold
3. 3.4058 | TSG-MX220-001 | HX-417 — Hydraulic Pressure Below Operating Threshold
4. 1.7367 | TSG-MX220-001 | Alarm Response Principles
5. 1.7367 | TSG-MX200-001 | Alarm Response Principles
```
BM25 immediately solved the exact identifier problem.

---

Query:
```txt
What does HX-421 indicate?
```

Results:
```txt
1. 2.4581 | TSG-MX200-001 | HX-421 — Return Filter Differential Pressure High
2. 2.4581 | TSG-MX220-001 | HX-421 — Return Filter Differential Pressure High
3. 2.4581 | TSG-MX300-001 | HX-421 — Return Filter Differential Pressure High
```

Again, exact identifier matching worked perfectly.

---

Query:
```txt
Which replacement filter is compatible with the MX-300?
```
Results:
```txt
1. 8.8234 | SOP-MNT-002 | Related Spare Parts
2. 8.4953 | TSG-MX300-001 | HX-421 — Return Filter Differential Pressure High
3. 7.7953 | TSG-MX220-001 | HX-421 — Return Filter Differential Pressure High
4. 7.7953 | TSG-MX200-001 | HX-421 — Return Filter Differential Pressure High
5. 7.4462 | MAN-MX300-001 | Related Controlled Procedures
```
The correct parts evidence moved to rank 1.

This confirmed that lexical retrieval addressed exactly the failures observed in dense retrieval.

---

# 16. BM25 Full Benchmark

The next question was whether BM25 should replace dense retrieval entirely.

The answer was no.

Full BM25 results:
```txt
Cases: 25

Hit@1: 0.520
Hit@3: 0.560
Hit@5: 0.640
MRR:   0.558
```

Category-level Hit@5:
```txt
alarm                1.000
component            0.500
condition            1.000
maintenance          0.250
paraphrase           0.667
parts                1.000
procedure            0.500
safety               0.500
specification        0.500
```

BM25 was excellent for:
```txt
alarms
parts
```

but dramatically worse for semantic maintenance and procedure questions.

This produced a second major lesson:

> Lexical retrieval fixed exact identifiers, but could not replace semantic retrieval.

---

# 17. Dense vs BM25

|Retriever|Hit@1|Hit@3|Hit@5|MRR|
|---------|-----|-----|-----|---|
|Dense|0.640|0.840|0.880|0.743|
|BM25|0.520|0.560|0.640|0.558|

Dense retrieval was clearly stronger overall.

BM25 had specialized strengths.

This suggested combining them rather than selecting only one.

---

# 18. First Hybrid Retrieval Attempt

Dense and BM25 results were combined using Reciprocal Rank Fusion.

Relevant files:
```txt
src/industrial_copilot/retrieval/hybrid.py
src/industrial_copilot/retrieval/hybrid_retriever.py
```

Evaluation script:
```txt
experiments/evaluate_hybrid_retrieval.py
```
---

# 19. Reciprocal Rank Fusion

Dense similarity scores and BM25 scores use different numerical scales.

For example:
```txt
Dense:
0.72
0.68
0.61

BM25:
8.4
5.2
2.1
```

Therefore raw scores were not simply added.

Instead, rankings were combined using Reciprocal Rank Fusion.

Conceptually:
```txt
RRF score += 1 / (k + rank)
```
Chunks appearing highly in both rankings receive greater combined weight.

---

# 20. Naive Hybrid Results

The first hybrid implementation applied dense + BM25 to every query.

Results:
```txt
Hit@1: 0.640
Hit@3: 0.760
Hit@5: 0.840
MRR:   0.705
```

Compared with dense:
```txt
Dense:
Hit@5 = 0.880
MRR   = 0.743

Naive hybrid:
Hit@5 = 0.840
MRR   = 0.705
```

Overall retrieval became worse.

This was an important negative result.

Hybrid search did not automatically improve the system.

---

# 21. Why Naive Hybrid Search Failed

BM25 improved identifier-heavy queries but introduced noise into semantic ones.

For example, dense retrieval successfully understood:
```txt
What are the steps for replacing the hydraulic return filter?
```
because:
```txt
"steps for replacing"
```

is semantically related to:
```txt
Procedure
```

BM25 focused on literal words such as:
```txt
hydraulic
filter
replacement
```

which occur in many different chunks.

When both systems received equal influence, lexical noise could push good dense results downward.

This produced a third major lesson:

> Retrieval techniques should not necessarily be applied uniformly to every query.

---

# 22. Query Analysis

Instead of forcing every query through the same retrieval pipeline, a deterministic query analyzer was introduced.

Relevant file:
```txt
src/industrial_copilot/retrieval/query_analyzer.py
```

Tests:
```txt
tests/test_query_analyzer.py
```

Exploration script:
```txt
experiments/query_analysis_lab.py
```

The analyzer extracts structured identifiers such as:
```txt
Machine models:
MX-200
MX-220
MX-300

Alarm codes:
HX-417
HX-421
SF-108

Procedure IDs:
SOP-MNT-002

Part numbers:
HF-300-R10
PS-225-B
```

Regular expressions are used instead of an LLM because these identifiers have deterministic formats.

This makes query analysis:

* faster,
* cheaper,
* reproducible,
* easier to test.

---

# 23. Query Routing

The analyzer enabled query-aware retrieval routing.

Relevant file:
```txt
src/industrial_copilot/retrieval/router.py
```

Tests:
```txt
tests/test_retrieval_router.py
```

Evaluation script:
```txt
experiments/evaluate_routed_retrieval.py
```

Initial routing logic:
```txt
Alarm code detected?
Procedure ID detected?
Part number detected?

YES
-> Hybrid Retrieval

NO
-> Dense Retrieval
```

A machine model such as:
```txt
MX-300
```
was intentionally not enough to force hybrid retrieval.

This was because many successful semantic maintenance questions contain machine IDs, and BM25 had performed poorly on maintenance questions.

---

# 24. First Query-Routed Results

Query-aware routing produced:
```txt
Hit@1: 0.680
Hit@3: 0.880
Hit@5: 0.920
MRR:   0.783
```

Compared with dense:
```txt
Dense:
Hit@5 = 0.880
MRR   = 0.743

Routed:
Hit@5 = 0.920
MRR   = 0.783
```

This validated the routing hypothesis.

Semantic questions retained dense retrieval.

Identifier-heavy queries gained access to BM25.

---

# 25. Remaining Routed Failure: HX-417

One important failure still remained.

Query:
```txt
What does alarm HX-417 mean?
```

the router correctly selected hybrid retrieval.

BM25 alone ranked HX-417 correctly.

Yet hybrid retrieval still missed it.

The problem was therefore no longer:

* query analysis,
* dense embeddings,
* or BM25.

The problem was fusion.

Generic:
```txt
Alarm Response Principles
```

chunks appeared reasonably high in both dense and lexical rankings.

The exact HX-417 chunk was extremely strong lexically but weaker semantically.

RRF therefore still allowed generic alarm chunks to outrank the exact code.

This motivated exact identifier boosting.

---

# 26. Exact Identifier Boosting

Relevant file:
```txt
src/industrial_copilot/retrieval/identifier_boost.py
```

Tests:
```txt
tests/test_identifier_boost.py
```

The system already knew that the query explicitly contained:
```txt
HX-417
```

Therefore retrieved candidates containing exactly:
```txt
HX-417
```


received a deterministic post-retrieval score boost.

Identifiers considered for boosting included:

* alarm codes,
* procedure IDs,
* explicit part numbers.

Machine models alone were deliberately excluded because they occur in too many generic chunks.

---

# 27. Candidate Generation and Boosting

Instead of retrieving only five hybrid results, the system retrieves a larger candidate pool:
```txt
top 20 candidates
```

Then:
```txt
Exact identifier boosting
```
is applied.

Finally:
```txt
top 5
```

are returned.

Conceptually:
```txt
Query
   |
   v
Dense + BM25
   |
   v
20 candidates
   |
   v
Exact identifier boost
   |
   v
Re-rank
   |
   v
Final top 5
```

This is an early form of:
```txt
candidate generation
+
reranking
```
---

# 28. Results After Exact Identifier Boosting

After adding exact identifier boosting:
```txt
Hit@1: 0.720
Hit@3: 0.920
Hit@5: 0.960
MRR:   0.823
```

The previously failing:
```txt
What does alarm HX-417 mean?
```

moved to:
```txt
Rank 1
```

Alarm category Hit@5 became:
```txt
1.000
```

This confirmed that deterministic exact-match signals were valuable for industrial search.

---

# 29. Final Remaining Development Failure: Parts Intent

Only one development benchmark failure remained:
```txt
Which replacement filter is compatible with the MX-300?
```

The router selected:
```txt
Dense
```

because the query contained:
```txt
MX-300
```

but no explicit part number.

Humans immediately understand that this is a:
```txt
parts lookup
```

but identifier extraction alone could not infer that.

This introduced the distinction between:
```txt
entity extraction
```

and:
```txt
query intent
```
---

# 30. Parts Intent Detection

The query analyzer was extended with simple deterministic intent detection.

Supported initial intents:
```txt
PARTS_LOOKUP

GENERAL
```

Examples of phrases that indicate parts lookup include concepts such as:
```txt
spare part
part number
replacement part
replacement filter
replacement sensor
which part
```

The design intentionally avoided simply using:
```txt
filter
```

as a trigger.

Otherwise:
```txt
When should the MX-300 filter be replaced?
```

could incorrectly become a parts query even though it is asking about a maintenance interval.

---

# 31. Routing After Parts Intent Detection

Routing logic evolved to:
```txt
Explicit alarm code?
Explicit SOP ID?
Explicit part number?
Parts lookup intent?

YES
-> Hybrid

NO
-> Dense
```

The previously failing:
```txt
Which replacement filter is compatible with the MX-300?
```

was now routed to hybrid search.

---

# 32. Final Development Benchmark Result

The final Retrieval V1 architecture produced:
```txt
Cases: 25

Hit@1: 0.800
Hit@3: 0.960
Hit@5: 1.000
MRR:   0.883
```

Category-level Hit@5:
```txt
alarm                1.000
component            1.000
condition            1.000
maintenance          1.000
paraphrase           1.000
parts                1.000
procedure            1.000
safety               1.000
specification        1.000
```

This does NOT mean the system has 100% real-world retrieval accuracy.

The 25 questions had been repeatedly inspected during development.

They therefore represent a:
```txt
development benchmark
```
rather than an unbiased final test set.

---

# 33. Experimental Performance Timeline

|Retrieval Version|Hit@1|Hit@3|Hit@5|MRR|
|-----------------|-----|-----|-----|---|
|Dense only|0.640|0.840|0.880|0.743|
|BM25 only|0.520|0.560|0.640|0.558|
|Naive Hybrid RRF|0.640|0.760|0.840|0.705|
|Query-Routed V1|0.680|0.880|0.920|0.783|
|Routed + Identifier Boost|0.720|0.920|0.960|0.823|
|Routed + Identifier Boost + Parts Intent|0.800|0.960|1.000|0.883

This table represents the main engineering story of Retrieval V1.

The final result was not achieved by continuously adding more retrieval techniques.

One experiment actually made performance worse.

The improvements came from learning when each retrieval technique should be used.

---

# 34. Held-Out Evaluation

Because the development benchmark had influenced system design, a second benchmark was created.

Relevant file:
```txt
src/industrial_copilot/evaluation/heldout_benchmark.py
```

Evaluation script:
```txt
experiments/evaluate_routed_retrieval_heldout.py
```

The held-out set contained:
```txt
12 previously unseen queries
```

These queries intentionally used different formulations from the development benchmark.

Examples included:
```txt
The MX-300 return-line filter has reached 760 operating hours.
Is it already due for replacement?
```

and:
```txt
Our MX-220 panel is showing HX-421.
What condition does that alarm represent?
```

and:
```txt
I need to order a replacement return-line filter for an MX-300.
Which item should purchasing request?
```

---

# 35. Held-Out Results

The current routed retriever achieved:
```txt
Cases: 12

Hit@1: 0.750
Hit@3: 0.750
Hit@5: 0.833
MRR:   0.771
```
Category Hit@5:
```txt
alarm                1.000
component            1.000
maintenance          1.000
parts                0.000
procedure            1.000
safety               1.000
specification        1.000
```

Two failures remained.

---

## 35.1. Held-Out Failure 1

Query:
```txt
I need to order a replacement return-line filter for an MX-300.
Which item should purchasing request?
```

Result:
```txt
MISS
```

The query was routed to:
```txt
Dense
```

because the current rule-based parts-intent detector did not recognize this unseen phrasing.

---

## 35.2. Held-Out Failure 2

Query:
```txt
Which pressure sensor part is suitable for the MX-220?
```

Result:
```txt
MISS
```

Again the query was routed to:
```txt
Dense
```

because the phrase did not match the narrow parts-intent rules learned during development.

---

# 36. Why the Held-Out Failures Matter

The held-out results exposed an important limitation:

> Rule-based intent detection is precise but brittle to unseen natural-language formulations.

The system generalized extremely well across:

* alarms,
* maintenance,
* procedures,
* safety,
* specifications,
* component queries.

But parts-intent classification failed to generalize.

The correct engineering response is not to immediately add the two held-out phrases to the rule list.

Doing that would turn the held-out set into another development set.

Instead, the held-out metrics were frozen as Retrieval V1 generalization results.

---

# 37. Development vs Held-Out Results

|valuation Set|Hit@1|Hit@3|Hit@5|MRR|
|-------------|-----|-----|-----|---|
|Development, 25 cases|0.800|0.960|1.000|0.883|
|Held-out, 12 cases|0.750|0.750|0.833|0.771|


This difference is expected.

The development benchmark influenced system decisions.

The held-out benchmark measures how well those decisions generalize to unseen wording.

---

# 38. Final Retrieval V1 Architecture

The final in-memory retrieval architecture is:
```txt

                         USER QUERY
                              |
                              v
                       QUERY ANALYZER
                    /         |          \
                   /          |           \
          Machine IDs     Exact IDs       Intent
             MX-300        HX-417       PARTS_LOOKUP
                              |
                              v
                       RETRIEVAL ROUTER
                          /        \
                         /          \
                      DENSE        HYBRID
                       |           /    \
                       |       Dense    BM25
                       |          \      /
                       |           \    /
                       |             RRF
                       |              |
                       |       Candidate Pool
                       |              |
                       |      Exact ID Boosting
                       |              |
                         \            /
                          \          /
                           FINAL TOP-K

```
---

# 39. File Map

Corpus and chunk loading
```txt
src/industrial_copilot/retrieval/corpus.py
```

Dense embeddings
```txt
src/industrial_copilot/retrieval/embedder.py
```

Dense in-memory search
```txt
src/industrial_copilot/retrieval/in_memory.py
```

BM25 lexical retrieval
```txt
src/industrial_copilot/retrieval/lexical.py
```

Hybrid fusion
```txt
src/industrial_copilot/retrieval/hybrid.py
```

Hybrid retrieval orchestration
```txt
src/industrial_copilot/retrieval/hybrid_retriever.py
```

Query identifier and intent analysis
```txt
src/industrial_copilot/retrieval/query_analyzer.py
```

Query-aware retrieval routing
```txt
src/industrial_copilot/retrieval/router.py
```

Exact identifier boosting
```txt
src/industrial_copilot/retrieval/identifier_boost.py
```

Development benchmark
```txt
src/industrial_copilot/evaluation/benchmark.py
```

Held-out benchmark
```txt
src/industrial_copilot/evaluation/heldout_benchmark.py
```

Evaluation metrics
```txt
src/industrial_copilot/evaluation/retrieval.py
```

---

# 40. Experiment Map

Initial semantic retrieval
```txt
experiments/retrieval_lab.py
```

Complete-corpus retrieval
```txt
experiments/corpus_retrieval_lab.py
```

BM25 investigation
```txt
experiments/lexical_retrieval_lab.py
```

Dense baseline
```txt
experiments/evaluate_dense_retrieval.py
```

Result:
```txt
Hit@1 = 0.640
Hit@3 = 0.840
Hit@5 = 0.880
MRR   = 0.743
```

Full BM25 benchmark
```txt
experiments/evaluate_lexical_retrieval.py
```

Result:
```txt
Hit@1 = 0.520
Hit@3 = 0.560
Hit@5 = 0.640
MRR   = 0.558
```

Naive hybrid benchmark
```txt
experiments/evaluate_hybrid_retrieval.py
```

Result:
```txt
Hit@1 = 0.640
Hit@3 = 0.760
Hit@5 = 0.840
MRR   = 0.705
```

Query-routed benchmark
```txt
experiments/evaluate_routed_retrieval.py
```

Final development result:
```txt
Hit@1 = 0.800
Hit@3 = 0.960
Hit@5 = 1.000
MRR   = 0.883
```
Held-out routed evaluation
```txt
experiments/evaluate_routed_retrieval_heldout.py
```

Result:
```txt
Hit@1 = 0.750
Hit@3 = 0.750
Hit@5 = 0.833
MRR   = 0.771
```

---

# 41. Important Test Files

Relevant automated tests include:
```txt
tests/test_similarity.py
tests/test_lexical_retrieval.py
tests/test_query_analyzer.py
tests/test_retrieval_router.py
tests/test_identifier_boost.py
tests/test_retrieval_evaluation.py
tests/test_corpus.py
```

These tests protect:

* vector similarity behavior,
* BM25 exact matching,
* identifier tokenization,
* query entity extraction,
* intent detection,
* routing decisions,
* identifier boosting,
* benchmark metric calculations,
* corpus integrity.

---

# 42. Key Engineering Decisions

## Decision 1 — Start with dense retrieval

**Reason**:

Dense retrieval provides a clean semantic baseline and exposes retrieval weaknesses without unnecessary complexity.

---

## Decision 2 — Measure before adding BM25

BM25 was not introduced because hybrid retrieval is fashionable.

It was introduced because dense retrieval specifically failed on industrial identifiers.

---

## Decision 3 — Reject BM25 as the universal retriever

BM25 solved identifier queries but performed substantially worse on semantic maintenance and procedure queries.

---

## Decision 4 — Reject naive always-on hybrid retrieval

Equal RRF degraded overall benchmark performance.

Therefore combining two retrieval algorithms does not automatically produce a better system.

---

## Decision 5 — Introduce query-aware routing

Different queries require different retrieval behavior.

Semantic questions remained dense-first.

Identifier-heavy questions used hybrid retrieval.

---

## Decision 6 — Use deterministic identifier extraction

Alarm codes, SOP IDs, part numbers, and machine IDs follow structured patterns.

Regex-based extraction is cheaper, faster, and more reproducible than invoking an LLM.

---

## Decision 7 — Add exact identifier boosting

When the user explicitly asks for HX-417, a candidate containing exactly HX-417 should receive stronger ranking evidence than a generic alarm section.

---

## Decision 8 — Introduce intent only when required

The project did not begin with a large intent taxonomy.

Parts-intent detection was introduced only after the benchmark demonstrated that identifier extraction alone could not understand parts lookup questions.

---

## Decision 9 — Maintain a separate held-out benchmark

Development metrics were not treated as unbiased final accuracy because those questions had influenced architecture decisions.

---

## Decision 10 — Do not tune directly against held-out failures

The two held-out parts failures were recorded as limitations rather than immediately patched.

This preserves the meaning of the held-out evaluation.

---

# 43. Major Lessons Learned

## 43.1 Dense retrieval is not enough for industrial search

Semantic embeddings work extremely well for natural-language meaning but can struggle with identifiers such as:
```txt
HX-417
HX-421
HF-300-R10
SOP-MNT-002
```
---

## 43.2 BM25 and embeddings solve different problems

Dense retrieval answers:
```txt
What text means something similar to this question?
```

BM25 answers:
```txt
What text contains these important words or identifiers?
```
Neither is universally superior.

---

## 43.3 Hybrid search is not automatically better

The first hybrid implementation performed worse than dense retrieval.

This was one of the most important experimental findings.

Hybrid architectures still require careful candidate selection, fusion, routing, and reranking.

---

## 43.4 Query understanding improves retrieval

Even a small deterministic query analyzer significantly improved retrieval architecture.

The system began distinguishing between:
```txt
semantic meaning
exact identifiers
query intent
```
before searching.

---

## 43.5 Exact matches are important in technical domains

Industrial documentation frequently contains:

* alarm codes,
* equipment models,
* part numbers,
* procedure IDs.

Exact lexical signals should not be discarded just because semantic embeddings are available.

---

## 43.6 Evaluation must drive architecture

The architecture evolved through:
```txt
Measure
   |
   v
Find failure
   |
   v
Form hypothesis
   |
   v
Implement one change
   |
   v
Measure again
```

This was more reliable than selecting retrieval technologies based on tutorials or popularity.

---

## 43.7 Benchmarks can also be wrong

Some early “retrieval failures” were actually benchmark-label problems.

Multiple documents sometimes contained equally valid evidence.

The benchmark therefore had to support multi-relevance labels.

---

## 43.8 Development results and test results are different

A development Hit@5 of:
```txt
1.000
```
does not imply 100% production retrieval accuracy.

The unseen benchmark produced:
```txt
Hit@5 = 0.833
```

which is a more realistic estimate of generalization.

---

# 44. Current Limitations

Retrieval V1 still has several known limitations.

## Rule-based intent classification

The current parts-intent classifier uses deterministic phrases.

Held-out evaluation showed that it does not generalize perfectly to unseen wording.

---

## Small evaluation sets

The development benchmark contains 25 questions.

The held-out benchmark contains 12 questions.

These are sufficient for engineering iteration but not sufficient for statistically strong production claims.

---

## In-memory vector search

Chunk vectors currently live in NumPy memory.

This is suitable for:
```txt
154 chunks
```

but not intended for large-scale production retrieval.

---

## No persistent vector index

Embeddings must currently be regenerated when experiment scripts start.

The next architecture milestone will move vectors to Qdrant.

---

## No metadata filtering during retrieval

Metadata exists on chunks, but machine-model and document-type filters are not yet fully incorporated into vector retrieval.

---

## No cross-encoder reranker

The system currently relies on:

* dense ranking,
* BM25,
* RRF,
* exact identifier boosting.

A learned reranker has not yet been introduced.

---

## No LLM

Retrieval V1 only answers:
```txt
Which evidence should be retrieved?
```
It does not yet generate a final natural-language answer.

---

# 45. Next Engineering Milestone

The next major stage is Qdrant integration.

Current architecture:
```txt
154 chunks
    |
    v
Embedding model
    |
    v
NumPy matrix in application memory
    |
    v
Search
```

Target architecture:
```txt
Documents
    |
    v
Chunks
    |
    v
Embeddings
    |
    v
Qdrant Collection
    |
    +-- vector
    +-- chunk text
    +-- metadata
    |
    v
Persistent Vector Search
```

The primary objective of the Qdrant phase is not to artificially improve retrieval metrics.

It is to separate:
```txt
INDEXING TIME
```

from:
```txt
QUERY TIME
```
and provide:

* persistent storage,
* scalable vector search,
* metadata-aware search,
* infrastructure closer to a production RAG system.

The Retrieval V1 benchmark will remain available to verify that moving from NumPy to Qdrant does not unexpectedly degrade retrieval quality.

---

# 46. Final Retrieval V1 Conclusion

Retrieval V1 began as a simple dense semantic search system.

The dense baseline already performed well:
```txt
Hit@5 = 0.880
```

but concrete failures exposed weaknesses around industrial identifiers and structured parts lookup.

BM25 successfully addressed those weaknesses but performed poorly as a universal retriever.

A naive hybrid architecture also reduced overall performance.

The system improved only after retrieval became query-aware.

The final development architecture combines:

* dense semantic retrieval,
* BM25 lexical retrieval,
* Reciprocal Rank Fusion,
* deterministic query analysis,
* retrieval routing,
* exact identifier boosting,
* parts-intent detection.

Development performance reached:
```txt
Hit@1 = 0.800
Hit@3 = 0.960
Hit@5 = 1.000
MRR   = 0.883
```

A separate held-out benchmark produced:
```txt
Hit@1 = 0.750
Hit@3 = 0.750
Hit@5 = 0.833
MRR   = 0.771
```

The difference between those numbers is an important result rather than a problem.

It demonstrates why retrieval systems must be evaluated on unseen queries and why development benchmarks should not be presented as unbiased production accuracy.

The most important outcome of Retrieval V1 is therefore not one metric.

It is the engineering process that produced the final architecture:
```txt
Start simple
    |
    v
Measure
    |
    v
Understand failures
    |
    v
Introduce targeted improvements
    |
    v
Reject changes that do not help
    |
    v
Measure generalization
```

This retrieval layer now provides the foundation for the next phases of the Industrial Knowledge Copilot: persistent vector storage with Qdrant, metadata filtering, retrieval services, and eventually grounded LLM answer generation.