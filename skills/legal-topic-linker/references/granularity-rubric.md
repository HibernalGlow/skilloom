# Atomic legal-topic granularity rubric

## Purpose

A topic ID is a reusable relationship key for one legal proposition. It is not a table-of-contents label, subject taxonomy node, or summary of the entire question.

## Acceptance test

A topic is atomic enough only when all answers below are yes:

1. Can a reviewer state one operative legal proposition from the ID and display name?
2. Does it identify the condition, exception, procedure, or consequence that changes the answer?
3. Would two questions sharing this ID be answerable from substantially the same rule paragraph?
4. Could one compact note block explain the topic without becoming a chapter summary?
5. Does the ID remain valid if the source, year, question number, and document path change?

If a question tests two independently reviewable propositions, assign two topic IDs instead of joining them into one vague label.

## Naming pattern

Use lowercase ASCII kebab-case:

```text
{domain}-{doctrine-or-procedure}-{operative-condition-or-consequence}
```

Add further qualifiers only when they distinguish a legally different proposition.

Good components include:

- subject or procedure: `civil-procedure`, `criminal-evidence`, `administrative-litigation`;
- doctrine or stage: `summary-service`, `retrial-application`, `contract-rescission`;
- decisive qualifier: `confirmed-receipt`, `citizen-parties-original-court`, `third-party-fraud-exception`;
- consequence: `default-judgment-allowed`, `execution-stay-exception`, `burden-shifts`.

Do not encode:

- source collection, lecture, or recitation volume;
- year, paper, question number, or display order;
- a temporary SiYuan block ID;
- answer option letters;
- generic words such as `overview`, `basics`, `system`, or `chapter` as the decisive suffix.

## Examples

Too broad:

```text
civil-procedure-summary-procedure
civil-procedure-retrial-supervision
civil-procedure-execution
```

Atomic candidates:

```text
civil-procedure-summary-service-default-judgment-confirmed-receipt
civil-procedure-retrial-application-citizen-parties-original-court
civil-procedure-retrial-medical-expense-execution-stay-exception
```

These examples show granularity and naming shape only. Verify the controlling rule against the actual question; never copy an example merely because its wording looks similar.

## Existing IDs

Presence is not proof of quality. Review every current ID against the question's decisive reasoning.

Use these dispositions:

| Disposition | Meaning | Action |
| --- | --- | --- |
| `exact` | Same atomic proposition | Keep and reuse |
| `incomplete` | Related but omits a tested qualifier | Replace or add a second atomic ID |
| `broad` | Chapter, system, or专题 label | Migrate to atomic IDs |
| `wrong` | Different controlling proposition | Replace after legal review |

Before replacing a shared ID, inventory all questions and providers that use it. Never silently split or rename a relationship key.

## Provider fit

An exact provider contains enough law and explanation to answer the proposition represented by the ID. The provider boundary should be the smallest stable block that remains understandable on its own.

Reject these false matches:

- the nearest ancestor heading when only one distant descendant is relevant;
- a heading with the same broad name but no decisive condition or consequence;
- the question itself serving as its own reusable note;
- a fuzzy keyword match that discusses a neighboring rule;
- an exact rule embedded in a huge chapter when a narrower stable paragraph or heading exists.

If 精讲卷 and 背诵卷 both contain exact standalone explanations, both may declare the same topic ID. Source preference affects ranking and display, not semantic identity.
