
# ADR-001: Use a Synthetic Industrial Domain

## Status

Accepted

## Context

The project needs realistic technical documents and structured operational data for RAG development, evaluation, and public demonstration. Employer documents, source code, internal workflows, and confidential data cannot be used.

## Decision

Build an independently designed fictional manufacturing environment called NovaTech Manufacturing. The environment will include synthetic machine models, manuals, SOPs, troubleshooting guides, maintenance rules, alarm codes, parts inventory, machines, and work orders.

## Reasons

- Avoids exposing proprietary or confidential information.

- Provides complete control over ground truth.

- Enables repeatable retrieval evaluation.

- Allows deliberate creation of hard-negative and unanswerable examples.

- Produces a coherent industrial product demonstration.

## Consequences

The project must clearly label all operational values and procedures as synthetic and unsuitable for use as real machine or safety instructions without expert validation.

