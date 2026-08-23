# Security And Answerability

## Purpose

This document defines how future investigation workflows should decide what a question means, whether the platform can answer it, whether the user is authorized, and how the response should be constrained by evidence.

This is a reference specification. It does not implement security, agents, RLS, tools, SQL, or runtime behavior.

## Investigation Control Flow

```text
Management Question
    -> Intent / Metric / Entity Resolution
    -> Ambiguity Classification
    -> Capability Mapping
    -> Authorization / RLS Check
    -> Data Sufficiency Check
    -> Evidence Boundary
    -> Investigation
    -> Response Policy
    -> Audit / Evaluation / Feedback
```

## Ambiguity

Ambiguous questions must not automatically be classified as unsupported.

Supported ambiguity behaviours:

- `AUTO_RESOLVE`
- `ASK_CLARIFICATION`
- `MULTI_METRIC_SUMMARY`

Examples:

```text
"How are we doing?"
-> may use MULTI_METRIC_SUMMARY.
```

```text
"Why are we doing badly in APAC?"
-> clarify or explicitly state the KPI interpretation.
```

Principle:

```text
AMBIGUOUS != UNSUPPORTED
```

## Answerability

Use exactly:

- `SUPPORTED`
- `PARTIALLY_SUPPORTED`
- `UNSUPPORTED`

`SUPPORTED`:

- Required evidence exists.

`PARTIALLY_SUPPORTED`:

- Some requested analysis is supported but some evidence is missing.

`UNSUPPORTED`:

- Required evidence does not exist.

## Authorization

Authorization is separate from answerability.

Authorization outcomes:

- `ALLOW`
- `DENY`

Principles:

- Authorization should occur before protected data is exposed.
- RLS/security must ultimately be enforced in the data/tool/query layer, not only through prompts.
- Unauthorized users should not receive protected information merely as part of an explanation of the denial.

Examples:

```text
APAC Finance Manager -> APAC margin
-> potentially ALLOW
```

```text
APAC Finance Manager -> EMEA payroll
-> DENY
```

## Evidence Boundary

The investigation agent must not make causal or diagnostic claims beyond the available evidence.

Allowed:

- Calculate supported metrics.
- Trace supported operational drivers.
- Inspect agent-visible business events.
- Report supported correlations.

Not allowed:

- Invent missing business causes.
- Substitute adjacent metrics for unavailable evidence.
- Claim causality purely from correlation.
- Access evaluator-only scenario ground truth.

Example:

```text
Revenue + Orders + Churn exist.
Customer Satisfaction / NPS does not exist.

Question:
"Did customer satisfaction cause revenue decline?"

Correct behaviour:
- investigate supported revenue evidence
- state that customer satisfaction causality cannot be determined
- do not use churn as proof of satisfaction
```

## Response Policy

`SUPPORTED`:

- Investigate and answer with evidence.

`AMBIGUOUS`:

- Clarify, explicitly state interpretation, or provide multi-metric summary.

`PARTIALLY_SUPPORTED`:

- Answer supported portion and clearly state limitations.

`UNSUPPORTED`:

- Abstain from unsupported analysis.

`UNAUTHORIZED`:

- Deny access without exposing protected data.

## Milestone Ownership

M1:

- Define metadata and architectural requirements.

M2:

- Implement ambiguity handling.
- Implement capability mapping.
- Implement answerability checks.
- Implement evidence-grounded investigation.

M6:

- Implement authentication.
- Implement authorization.
- Implement RLS.
- Implement secure tool/query access.

M7:

- Evaluate answerability accuracy.
- Evaluate abstention accuracy.
- Evaluate hallucination rate.
- Evaluate ambiguity handling.
- Evaluate authorization compliance.
- Evaluate RLS compliance.
- Evaluate evidence grounding.
