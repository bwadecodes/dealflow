---
name: dd-questions
description: Generate a prioritized diligence question list from data room findings, model review, and your rubric. Works best after /dd-dataroom and /dd-model, but can run standalone.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# Diligence Question Generation

Synthesize findings from the data room assessment and model review into a single, prioritized list of diligence questions.

## Invocation

```
/dd-questions <path-to-deal-folder>
```

The deal folder should contain a `dd-reports/` subdirectory with prior assessment outputs. If no prior reports exist, the skill works directly from whatever documents are in the folder.

## Prerequisites

### 1. Load the config

Same resolution order as other `/dd-*` skills:
1. `~/.claude/dealflow/diligence-config.yaml`
2. If not found: prompt user to run `/dd-setup` or offer to use the default template

### 2. Check for prior reports

```
Glob <deal-folder>/dd-reports/*.md
```

Look for:
- `dataroom-assessment-*.md` — from `/dd-dataroom`
- `model-review-*.md` — from `/dd-model`

If found, read them with `Read`. Use the most recent of each (sort by date in filename).

If no reports exist, note that the questions will be generated from the rubric and any documents in the folder directly. Tell the user: *"No prior reports found in dd-reports/. I'll generate questions from your rubric and what's in the folder. For better results, run /dd-dataroom and /dd-model first."*

## Workflow

### Step 1: Gather question sources

Build the question list from three sources:

**Source 1 — Data room gaps and concerns:**
If `dataroom-assessment-*.md` exists, extract:
- Items from the Gap List section
- Red and yellow flags from Category Assessments
- Items from Recommended Next Steps

**Source 2 — Model assumptions to test:**
If `model-review-*.md` exists, extract:
- Items from Assumptions to Test
- Red flags from Assumption Analysis
- Items from Hidden Risks

**Source 3 — Rubric baseline questions:**
From the config's rubric categories, include standard questions that haven't been answered by the data room or model review. These are the baseline — questions that apply regardless of deal-specific findings.

If no prior reports exist, expand this source — use the rubric questions as the primary framework and supplement with observations from any documents found in the deal folder.

### Step 2: Deduplicate and merge

Overlapping items become one question. Examples:
- Model flags a margin assumption AND data room is missing COGS detail → one question about margin assumptions and supporting documentation
- Both sources raise customer concentration → one question, combining the data points from each

Preserve the most specific version. If the model review flags "gross margin jumps from 52% to 68% between Y1 and Y2" and the rubric has a generic "what drives gross margin?", keep the specific version.

### Step 3: Prioritize

Assign priority levels:
- **Critical** — deal-breaker if unanswered. These are questions where the answer could fundamentally change the investment thesis. Red flags from assessments, key missing documents, internally inconsistent data.
- **Important** — needed for the IC memo. Yellow flags, assumptions that need validation, standard diligence items for the deal type.
- **Nice to have** — would improve understanding but won't change the decision. Lower-weight rubric items, nice-to-know context.

### Step 4: Categorize by domain

Group questions into these categories:
- Financial / Accounting
- Product / Operations
- Market / Competitive
- Team / Management
- Legal / IP / Regulatory
- Customer / Sales / Marketing
- Technology / Infrastructure

A question goes in the category that best fits the person who would answer it — e.g., a question about revenue recognition goes in Financial, even if it was triggered by a product finding.

### Step 5: Write the context

Every question includes the **"why"** — what finding or gap triggered it. This is critical. Anyone reading the list should understand the reasoning behind each question, not just the ask.

## Report Output

Create the output directory if needed:
```bash
mkdir -p "<deal-folder>/dd-reports"
```

Save using `Write` to:
```
<deal-folder>/dd-reports/diligence-questions-YYYY-MM-DD.md
```

### Report structure

```markdown
# Diligence Questions: [Deal Name]

**Date:** YYYY-MM-DD
**Sources:** [list which reports were used, or "rubric + direct folder scan"]
**Config template:** [PE / VC / Growth Equity / Custom]
**Total questions:** [count] ([X] critical, [Y] important, [Z] nice to have)

---

## Financial / Accounting

1. **[Critical]** The model shows gross margin improving from 52% to 68%
   between Y1 and Y2 — what specifically drives this? Is there a signed
   manufacturing agreement that supports the new COGS assumptions?

2. **[Important]** Monthly P&L shows a $45K marketing spike in March 2024
   with no corresponding revenue lift. What was this spend and what was learned?

3. **[Important]** No tax returns prior to 2022 in the data room. Can these
   be provided, or is there a reason they're excluded?

---

## Product / Operations

4. **[Critical]** ...

[Continue for each category with questions present]

---

## Summary

**Critical items ([count]):** [one-line summary of the themes]
**Key areas to focus management conversations on:** [2-3 bullets]
```

### Formatting rules

- Numbered sequentially across all categories (not restarting per category)
- Priority tag in bold brackets: **[Critical]**, **[Important]**, **[Nice to have]**
- Each question includes context — the finding or gap that prompted it
- Questions are written in plain language — as you would actually ask them to a CFO, CEO, or counsel
- No generic boilerplate. Every question should be specific to this deal.

## Interactive Mode

After saving:

> **Report saved to `<path>/dd-reports/diligence-questions-YYYY-MM-DD.md`.**
>
> [count] questions generated — [X] critical, [Y] important, [Z] nice to have.
>
> You can ask me to refine the list — add questions about specific topics, rewrite questions for a particular audience (e.g., "rewrite these for sending to the CFO"), or reprioritize based on what you've learned.

Handle follow-ups like:
- "Add questions about supply chain risk" — generate and append
- "Rewrite the critical questions for an email to management" — adjust tone
- "Which of these should I ask in the first management meeting?" — filter and recommend
- "Remove the legal questions — our counsel handles those separately" — filter out

## Error Handling

| Scenario | Response |
|----------|----------|
| No deal folder found | *"Can't find that folder. Check the path and try again."* |
| No reports and no documents | *"No reports or documents found. Run /dd-dataroom on your data room first, or point me at a folder with deal documents."* |
| Config not found | *"No config found. Run /dd-setup first, or I can use the default PE template."* |