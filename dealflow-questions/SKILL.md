---
name: dealflow-questions
description: Generate a prioritized diligence question list from data room findings, model review, and your rubric. Works best after /dealflow-dataroom and /dealflow-model, but can run standalone.
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
/dealflow-questions <path-to-deal-folder>
```

The deal folder should contain a `reports/` subdirectory with prior assessment outputs. If no prior reports exist, the skill works directly from whatever documents are in the folder.

## Report Requirements (Non-Negotiable)

These rules apply to every report. Check each one before saving. A report missing any of these is non-compliant.

1. **Header:** `# [DEAL_NAME] — Diligence Questions — YYYY-MM-DD HH:MM`. Never use generic headers like "Diligence Questions: [Deal Name]".
2. **Run Metadata block:** Every report includes the `## Run Metadata` table immediately after the header — time initiated, duration, model, input tokens, output tokens, estimated cost. If token counts are unavailable (agent cannot introspect usage), write "See session stats" for those fields. Time, duration, and model name are always available — never skip them.
3. **HTML export:** Default to producing **both** `.md` and `.html` files. Only produce one format if the config explicitly sets `report_format` to `"markdown"` or `"html"`. If the config field is missing or empty, default to `"both"`.
4. **Shared template:** HTML reports use the template at `config/report-template.html` in the dealflow plugin directory. All `/dealflow-*` skills use the same template.
5. **Presentability:** These reports get shared with senior investment professionals. Professional formatting matters.

## Prerequisites

### 1. Load the config

Same resolution order as other `/dealflow-*` skills:
1. `~/.claude/dealflow/diligence-config.yaml`
2. If not found: prompt user to run `/dealflow-setup` or offer to use the default template

### 2. Check for prior reports

```
Glob <deal-folder>/reports/*.md
```

Look for:
- `dataroom-assessment-*.md` — from `/dealflow-dataroom`
- `model-review-*.md` — from `/dealflow-model`

If found, read them with `Read`. Use the most recent of each (sort by date in filename).

If no reports exist, note that the questions will be generated from the rubric and any documents in the folder directly. Tell the user: *"No prior reports found in reports/. I'll generate questions from your rubric and what's in the folder. For better results, run /dealflow-dataroom and /dealflow-model first."*

## Timing

Record the current timestamp as `START_TIME` when the skill begins execution. This will be used in the report metadata to calculate duration.

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

## Deal Identification

Before generating questions, determine the **deal/company name**:

1. If prior reports exist in `reports/`, extract DEAL_NAME from the report headers
2. Otherwise, use the deal folder name
3. If the folder name is generic, use `AskUserQuestion` to ask: *"What's the company/deal name?"*

## Report Output

### Determine output directory

Read the config's `preferences.output_dir` value. If set, use it (it can be a relative path from the deal folder, or an absolute path). If not set, default to `reports`.

```bash
mkdir -p "<output-dir>"
```

Save using `Write` to:
```
<output-dir>/diligence-questions-YYYY-MM-DD.md
```

### Report structure

```markdown
# [DEAL_NAME] — Diligence Questions — YYYY-MM-DD HH:MM

**Sources:** [list which reports were used, or "rubric + direct folder scan"]
**Config template:** [PE / VC / Growth Equity / Custom]
**Total questions:** [count] ([X] critical, [Y] important, [Z] nice to have)

---

## Run Metadata

| Field | Value |
|-------|-------|
| Time initiated | YYYY-MM-DD HH:MM:SS |
| Duration | Xm Ys |
| Model | [model name, e.g. Claude Sonnet 4] |
| Input tokens | [count] |
| Output tokens | [count] |
| Estimated cost | $X.XX |

Compute duration as `current_time - START_TIME`. For tokens and cost, use the cumulative totals from all API calls during this skill execution. Estimate cost using the rates in `docs/cfo-cost-guide.md`. **If you cannot access token counts, write "See session stats" for token and cost fields — but always fill in time initiated, duration, and model name.**

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

### HTML export

Check the config's `preferences.report_format` value:

- `"markdown"` — save only the `.md` file (above)
- `"html"` — save only an `.html` file
- `"both"` — save both `.md` and `.html`
- **If the field is missing, empty, or not set → default to `"both"`.**

Generate the styled HTML report:

1. Read the HTML template from the dealflow plugin directory:
   ```
   Glob **/dealflow/config/report-template.html
   ```
2. Convert the markdown report content to HTML elements:
   - `#` headings → `<h1>`, `<h2>`, `<h3>`
   - Numbered questions → `<ol>` with priority styling
   - Priority tags → bold colored spans: `[Critical]` → red, `[Important]` → amber, `[Nice to have]` → gray
   - Summary section → wrap in `<div class="exec-summary">`
3. Replace the template placeholders:
   - `{{COMPANY_NAME}}` → DEAL_NAME
   - `{{REPORT_TYPE}}` → "Diligence Questions"
   - `{{DATETIME}}` → YYYY-MM-DD HH:MM
   - `{{DOC_COUNT}}` → "[X] questions"
   - `{{CONFIG_TEMPLATE}}` → template name
   - `{{CONFIDENCE}}` → omit or leave blank
   - `{{REPORT_BODY}}` → converted HTML content
   - `{{REPORT_TITLE}}` → "DEAL_NAME — Diligence Questions"
   - `{{TIME_INITIATED}}` → YYYY-MM-DD HH:MM:SS (START_TIME)
   - `{{DURATION}}` → Xm Ys
   - `{{MODEL_USED}}` → model name
   - `{{INPUT_TOKENS}}` → token count
   - `{{OUTPUT_TOKENS}}` → token count
   - `{{ESTIMATED_COST}}` → $X.XX
4. Save to: `<output-dir>/diligence-questions-YYYY-MM-DD.html`

### Formatting rules

- Numbered sequentially across all categories (not restarting per category)
- Priority tag in bold brackets: **[Critical]**, **[Important]**, **[Nice to have]**
- Each question includes context — the finding or gap that prompted it
- Questions are written in plain language — as you would actually ask them to a CFO, CEO, or counsel
- No generic boilerplate. Every question should be specific to this deal.

## Interactive Mode

After saving:

> **Report saved to `<path>/reports/diligence-questions-YYYY-MM-DD.md`.**
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
| No reports and no documents | *"No reports or documents found. Run /dealflow-dataroom on your data room first, or point me at a folder with deal documents."* |
| Config not found | *"No config found. Run /dealflow-setup first, or I can use the default PE template."* |