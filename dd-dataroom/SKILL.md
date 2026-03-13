---
name: dd-dataroom
description: Assess a deal data room against your diligence rubric. Point it at a folder of deal documents and get a structured assessment with findings, flags, gap analysis, and recommended next steps.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Data Room Assessment

Read a deal's data room and produce a structured diligence assessment against your rubric.

## Invocation

```
/dd-dataroom <path-to-data-room-folder>
/dd-dataroom <path-to-data-room-folder> "<deal context>"
```

The optional context string helps tailor the analysis — e.g., "B2B SaaS, ~$8M ARR, Series A, 200 enterprise customers."

## Prerequisites

### 1. Load the config

Look for the diligence config in this order:
1. If a `--config` path was passed in the invocation, use that file
2. `~/.claude/dealflow/diligence-config.yaml` (default location)
3. If neither exists, tell the user: *"No config found. Run /dd-setup first to set up your diligence preferences, or I can use the default PE Lower-Middle Market template."*
4. If they want to proceed without setup, load the PE default from the plugin directory:
   ```
   Glob **/dealflow/config/defaults/pe-lower-middle-market.yaml
   ```

Read the config with `Read` and parse the rubric categories, weights, and buy box.

### 2. Check Python dependencies

```bash
python3 -c "import pymupdf" 2>/dev/null || pip install pymupdf --quiet
python3 -c "import openpyxl" 2>/dev/null || pip install openpyxl --quiet
python3 -c "import docx" 2>/dev/null || pip install python-docx --quiet
```

If Python is not installed, stop and tell the user: *"Python is required for reading Excel, PDF, and Word files. Install it from python.org and try again."*

If pip install fails, tell the user: *"Couldn't install a required library. Try running: pip install pymupdf openpyxl python-docx"*

### 3. Validate the folder path

```
Glob <path>/**/*
```

If empty: *"This folder appears to be empty. Double-check the path and try again."*

## Phase 1: Inventory & Triage

Scan the folder tree. Read **filenames and folder structure only** — do not open files yet.

```
Glob <path>/**/*
```

Build a document manifest. Categorize each file by type based on filename and folder location:
- **Financials** — P&L, balance sheet, cash flow, QoE, tax returns, monthly/quarterly reports
- **Legal** — contracts, agreements, corporate docs, IP filings, litigation
- **Product / Operations** — product specs, technical docs, operational reports
- **Marketing / Sales** — pitch decks, marketing materials, sales reports, pipeline data
- **Team / HR** — org charts, bios, employment agreements, compensation
- **Customer** — customer lists, contracts, case studies, NPS/satisfaction data
- **Other** — anything that doesn't fit the above

Note file types:
- `.pdf` — will need Python extraction (pymupdf)
- `.xlsx` / `.xls` — will need openpyxl
- `.docx` — will need python-docx
- `.csv` / `.txt` / `.md` — direct Read
- `.png` / `.jpg` / `.jpeg` — direct Read (visual)
- Other — flag as unsupported, skip with note

**Gap analysis:** Compare what's in the room against what the rubric expects. For each rubric category, note:
- What documents are present
- What's missing or incomplete
- What the rubric expects that isn't covered

**Read order:** Prioritize by rubric weight. High-weight categories first.

### Output Phase 1 summary

Present to the user:

> **Data room inventory: [deal name / folder name]**
>
> **[X] documents found** across [Y] folders
>
> | Category | Files | Status |
> |----------|-------|--------|
> | Financials | 12 files | Good coverage |
> | Legal | 8 files | Missing: customer contracts |
> | ... | ... | ... |
>
> **Key gaps:**
> - [List missing items by rubric priority]
>
> **Ready to proceed with the full assessment, or want me to focus on specific areas?**

Use `AskUserQuestion` to checkpoint. If the user says proceed, move to Phase 2. If they specify areas, limit Phase 2 scope.

## Phase 2: Structured Assessment

Use subagents to parallelize the assessment across rubric categories. Spawn **3-4 agents max**:

**Agent 1 — Financials & Accounting:** Financial statements, QoE materials, tax returns, revenue data, margin analysis. Covers rubric categories related to revenue, gross margin, quality of earnings, balance sheet, overhead.

**Agent 2 — Legal & IP:** Contracts, corporate documents, IP filings, regulatory materials. Covers legal/IP rubric categories.

**Agent 3 — Product, Operations & Market:** Product documentation, operational reports, market research, competitive analysis, marketing materials. Covers product, market/competitors rubric categories.

**Agent 4 — Team, Customers & Sales:** Org charts, management bios, customer data, sales pipeline, HR documents. Covers team/management, customer-related rubric categories.

### Subagent instructions

Each subagent receives:
- The rubric categories it owns (with weights and questions)
- The file list for those categories (from Phase 1 manifest)
- The deal context string (if provided)
- The buy box criteria

Each subagent should:

1. **Read each assigned document** using appropriate method:
   - PDF: Use Bash to extract text with Python pymupdf:
     ```bash
     python3 -c "
     import pymupdf
     doc = pymupdf.open('<filepath>')
     for page in doc:
         print(page.get_text())
     "
     ```
     For PDFs with charts/images, also use `Read` on the PDF file directly (Claude's vision reads PDF pages visually).
   - Excel: Use Bash with Python openpyxl:
     ```bash
     python3 -c "
     import openpyxl
     wb = openpyxl.load_workbook('<filepath>', data_only=True)
     for sheet in wb.sheetnames:
         ws = wb[sheet]
         print(f'=== {sheet} ===')
         for row in ws.iter_rows(values_only=True):
             print('\t'.join(str(c) if c is not None else '' for c in row))
     "
     ```
   - Word: Use Bash with Python python-docx:
     ```bash
     python3 -c "
     import docx
     doc = docx.Document('<filepath>')
     for para in doc.paragraphs:
         print(para.text)
     "
     ```
   - CSV/TXT/MD: Use `Read` directly
   - Images: Use `Read` directly (visual)

2. **For each rubric category it owns, produce:**
   - **Findings** — what the documents say, with specific file references (filename + relevant detail)
   - **Strength / Concern flags:**
     - Green: strong evidence, no concerns
     - Yellow: partial evidence, needs more information
     - Red: concerning findings or significant gaps
   - **Information quality** — is the data detailed enough to form a view? What's missing?
   - **Cross-references** — where documents support or contradict each other

3. **Handle errors gracefully:**
   - Password-protected files: *"[filename] is password-protected — skipping. Remove the password and re-run to include it."*
   - Unsupported file types: *"Skipping [filename] — file type not supported."*
   - Corrupted files: *"Could not read [filename] — file may be corrupted."*

### Subagent fallback

If subagent dispatch fails (API rate limits, errors), fall back to sequential processing. Process categories one at a time in priority order (high-weight first). Slower but reliable.

### Synthesis

After all subagents return, the main agent synthesizes:
- Cross-category patterns (e.g., revenue growth story consistent with customer data?)
- Contradictions between documents in different categories
- Overall confidence assessment

## Phase 3: Report Output

Create the output directory:
```bash
mkdir -p "<deal-folder>/dd-reports"
```

Save the report using `Write` to:
```
<deal-folder>/dd-reports/dataroom-assessment-YYYY-MM-DD.md
```

Use today's date. If a report with the same date exists, append a sequence number: `dataroom-assessment-2026-03-13-2.md`.

### Report structure

```markdown
# Data Room Assessment: [Deal Name]

**Date:** YYYY-MM-DD
**Documents reviewed:** X of Y files in room
**Config template:** [PE / VC / Growth Equity / Custom]

---

## Executive Summary

[1-page overview in plain English. What does this deal look like at first glance?]

**Overall confidence:** [High / Medium / Low] — [one sentence explaining why]

**Top 3 strengths:**
1. [Strength with supporting evidence]
2. [Strength with supporting evidence]
3. [Strength with supporting evidence]

**Top 3 concerns:**
1. [Concern with supporting evidence]
2. [Concern with supporting evidence]
3. [Concern with supporting evidence]

---

## Buy Box Fit

| Criteria | Target | Actual | Fit |
|----------|--------|--------|-----|
| Revenue range | [from config] | [from documents] | ✓ / ✗ / ? |
| Stage | [from config] | [from documents] | ✓ / ✗ / ? |
| ... | ... | ... | ... |

[Commentary on fit and misfit — not just the table, but what it means]

---

## Category Assessments

### [Category Name] (Weight: [high/medium/low])

**Findings:**
- [Finding with document reference]
- [Finding with document reference]

**Flags:**
- 🟢 [Strength]
- 🟡 [Needs more info]
- 🔴 [Concern]

**Information quality:** [Assessment of data completeness]

[Repeat for each rubric category]

---

## Gap List

**High priority (needed for investment decision):**
- [ ] [Missing document or information]
- [ ] [Missing document or information]

**Medium priority (needed for IC memo):**
- [ ] [Missing document or information]

**Lower priority (would improve understanding):**
- [ ] [Missing document or information]

---

## Recommended Next Steps

1. [Specific action — what to request, who to ask, what to dig into]
2. [Specific action]
3. [Specific action]
```

## Phase 4: Interactive Mode

After saving, tell the user:

> **Report saved to `<path>/dd-reports/dataroom-assessment-YYYY-MM-DD.md`.**
>
> You can ask me follow-up questions about anything in the room — dig into specific documents, compare data across files, or explore areas the report flagged. Or move on to `/dd-model` for a financial model review or `/dd-questions` to generate your diligence question list.

Stay active for follow-ups. When the user asks a question:
- If the answer is in the report or in documents still in context, answer directly
- If it requires re-reading a specific document, read it and answer
- Reference specific files and data points — don't generalize

## Error Handling

| Scenario | Response |
|----------|----------|
| Empty folder | *"This folder appears to be empty. Double-check the path and try again."* |
| Password-protected file | *"[filename] is password-protected. Remove the password and re-run, or I'll skip it."* |
| Python not installed | *"Python is required for reading Excel and PDF files. Install it from python.org and try again."* |
| pip install fails | *"Couldn't install a required library. Try running: pip install pymupdf openpyxl python-docx"* |
| Config not found | *"No config found. Run /dd-setup first, or I can use the default PE template."* |
| Unsupported file type | *"Skipping [filename] — file type not supported. Supported: PDF, Excel, Word, CSV, images."* |
| Very large room (200+ files) | Warn the user that processing will take time. Triage aggressively — read high-priority documents first, summarize low-priority ones from filenames only. |