# Dealflow — AI-Powered Due Diligence Tools for PE & VC Investors

**Design Spec — March 12, 2026**

## Overview

Dealflow is a Claude Code skills package that gives PE and VC investors structured, AI-assisted due diligence workflows. Point it at a data room folder or a financial model, and it produces the kind of analysis you'd normally spend days on — organized against your own diligence rubric.

The first release focuses on **diligence** — the highest-value, most-frequent workflow. Sourcing (thematic deep dives, company screening) and post-deal (180-day plans, board prep, portfolio monitoring) are on the roadmap.

Built by [Brian Wade](https://github.com/bwadecodes), an investor who has worked across PE, growth equity, and VC — now investing independently out of Primario Holdings.

---

## Who This Is For

Investors who want to move faster through diligence without sacrificing depth. You don't need to be a developer. You do need to be comfortable pointing a tool at a folder and reading the output.

If you've never touched a command line, that's fine — the repo includes a quick onramp.

---

## Package Architecture

### Approach: Modular Skills

Each skill does one job well. They can be used independently or sequenced together. This keeps context windows manageable (a 600-file data room will eat context fast) and lets you re-run individual pieces as new information comes in during diligence.

### Repository Structure

```
dealflow/
├── SKILL.md                          # Package overview
├── package.json                      # Plugin metadata
├── LICENSE                           # MIT
├── CHANGELOG.md
├── .claude-plugin/
│   └── plugin.json                   # Claude Code plugin config
├── config/
│   ├── defaults/
│   │   ├── pe-lower-middle-market.yaml   # PE LMM default rubric
│   │   ├── pe-middle-market.yaml         # PE MM default rubric
│   │   ├── pe-large-buyout.yaml          # PE large buyout rubric
│   │   ├── venture-capital.yaml          # VC default rubric
│   │   └── growth-equity.yaml            # Growth equity rubric
│   └── example-config.yaml               # Annotated template
├── dd-setup/
│   └── SKILL.md                      # /dd-setup
├── dd-dataroom/
│   └── SKILL.md                      # /dd-dataroom
├── dd-model/
│   └── SKILL.md                      # /dd-model
├── dd-questions/
│   └── SKILL.md                      # /dd-questions
└── docs/
    ├── cli-quickstart.md             # CLI basics for finance people
    ├── it-compliance-guide.md        # What to send IT/compliance
    └── rubric-guide.md               # How to customize your rubric
```

### Naming Convention

`dd-` prefix for diligence skills. Future modules use `src-` (sourcing) and `pd-` (post-deal). Short to type, self-documenting, and grouped logically.

---

## Skill Designs

### 1. `/dd-setup` — Configuration Wizard

**Purpose:** Build or update the user's diligence config file.

**Flow:**

1. Present five starting templates:
   - **Venture Capital** — team/market/product focused, lighter data room expectations, burn/runway emphasis (pre-revenue to $5M ARR)
   - **Growth Equity** — blends PE-style diligence rigor with growth-stage metrics (unit economics, CAC/LTV, channel attribution) ($3M-$30M ARR)
   - **PE Lower-Middle Market** — financials-heavy, QoE emphasis ($10M-$75M revenue)
   - **PE Middle Market** — operational complexity, platform strategy, leverage ($75M-$250M revenue)
   - **PE Large Buyout** — institutional-grade operations, capital structure, regulatory, integration ($250M+ revenue)
2. Walk through each section, letting the user adjust or accept defaults
3. Save to `~/.claude/dealflow/diligence-config.yaml`

**Config file structure:**

```yaml
# Diligence Configuration
version: 1

rubric:
  categories:
    - name: "Product / Service"
      weight: high
      questions:
        - "What job is it doing for the customer?"
        - "Is it easily replicable or replaceable?"
        - "How is the product evolving?"
      # ... more questions per category

    - name: "Revenue"
      weight: high
      questions:
        - "What is the business model?"
        - "What is driving the growth rate?"
        - "Are growth trends sustainable?"

    - name: "Gross Margin"
      weight: high
      questions:
        - "What does GM say about where the product fits in the value chain?"
        - "What are the risks in the supply chain?"

    - name: "Overhead / Investments"
      weight: medium
      questions:
        - "Is the team properly resourced to deliver on growth?"
        - "What investments does the company need to make?"

    - name: "Balance Sheet"
      weight: medium
      questions:
        - "How much working capital does the business need?"
        - "Debt and other liabilities?"

    - name: "Market / Competitors"
      weight: high
      questions:
        - "Total and addressable market sizing?"
        - "Key competitors — product, revenue, profitability?"
        - "M&A in the sector — who are the buyers?"

    - name: "Team / Management"
      weight: high
      questions:
        - "Background and track record?"
        - "Ability to accept and incorporate feedback?"

    - name: "Legal / IP"
      weight: medium
      questions:
        - "Corporate formation and cap table clean?"
        - "IP ownership and defensibility?"

buy_box:
  revenue_range: "$5M - $50M"
  stage: "Series A, B, Growth"
  ownership_target: "20-40%"
  sector_focus: ["consumer", "technology", "healthcare"]
  profitability: "profitable or clear path"
  hold_period: "3-7 years"
  # Users customize these to their fund

preferences:
  output_dir: "dd-reports"          # relative to deal folder
  report_format: "markdown"         # markdown | docx | both
  detail_level: "deep"             # executive | deep
  auto_save: true
```

**Key design decisions:**

- Config differences between templates are meaningful, not cosmetic. PE weights financials/QoE heavily. VC weights team/market/product. Growth equity blends both.
- The rubric is the backbone — every other skill reads it.
- Users who skip `/dd-setup` get prompted to run it the first time they invoke any `/dd-*` skill.

**Allowed tools:** `Read`, `Write`, `Bash`, `Glob`, `AskUserQuestion`

---

### 2. `/dd-dataroom` — Data Room Assessment

**Purpose:** Read a deal's data room folder and produce a structured diligence assessment against the user's rubric.

**Invocation:**
```
/dd-dataroom ~/Dropbox/Deals/Acme-Corp/Data-Room
/dd-dataroom ~/Dropbox/Deals/Acme-Corp/Data-Room "B2B SaaS, ~$8M ARR, Series A, 200 enterprise customers"
```

**Phase 1 — Inventory & Triage**

Scans the folder tree. Produces:
- **Document manifest** — every file, categorized by type (financials, legal, product, marketing, team, etc.)
- **Gap analysis** — what's present vs. what the rubric expects. Flags missing items clearly (e.g., "No tax returns found," "No customer contracts in the room")
- **Read order** — prioritizes documents based on rubric weights

Outputs a summary and checkpoint: *"Here's what I found in the room. Want me to proceed with the full assessment, or focus on specific areas?"*

**Phase 2 — Structured Assessment**

Reads documents in priority order. For each rubric category:
- **Findings** — what the documents say, with specific references
- **Strength / Concern flags** — green (strong), yellow (needs more info), red (concerning)
- **Information quality** — is the data detailed enough or are there holes?
- **Cross-references** — where documents corroborate or contradict each other

Uses subagents to parallelize across categories (financials agent, legal agent, product agent, etc.) to manage context windows on large rooms.

**Phase 3 — Report Output**

Saves to:
```
{deal-folder}/dd-reports/dataroom-assessment-YYYY-MM-DD.md
```

Report structure:
1. **Executive Summary** — 1-page overview. Overall confidence level. Top 3 strengths, top 3 concerns.
2. **Buy Box Fit** — how the deal maps to the user's criteria, with specific callouts on fit and misfit.
3. **Category Assessments** — one section per rubric category. Findings, flags, and evidence with document references.
4. **Gap List** — missing documents and information, prioritized.
5. **Recommended Next Steps** — what to dig into further.

**Phase 4 — Interactive Mode**

Report is delivered, then the skill stays active. The user can:
- "Dig deeper into the financials"
- "Compare the P&L across 2023 and 2024"
- "What does the customer data tell us about retention?"
- "Cross-reference the marketing spend with the revenue growth"

**Technical considerations:**

- Large data rooms (hundreds of files) require smart triaging. Phase 1 reads filenames and folder structure first, not file contents. Phase 2 reads selectively based on priority.
- PDFs are read via Python extraction (pymupdf). Excel files via openpyxl. Word docs via python-docx.
- The skill should handle messy folder structures gracefully — not everything will be perfectly organized.

**Allowed tools:** `Read`, `Write`, `Bash`, `Glob`, `Grep`, `Agent`, `AskUserQuestion`

---

### 3. `/dd-model` — Financial Model Review

**Purpose:** Read a financial model (.xlsx) and produce a business-intelligence-focused review — understanding the business model, testing assumptions, and surfacing the most interesting data points.

**Invocation:**
```
/dd-model ~/Dropbox/Deals/Acme-Corp/Model/Acme-Model-v3.xlsx
/dd-model ~/Dropbox/Deals/Acme-Corp/Model/Acme-Model-v3.xlsx "B2B SaaS, Series A at $40M pre, net revenue retention 120%"
```

**Phase 1 — Model Comprehension**

Reads the workbook and maps out:
- **Tab inventory** — what each sheet does (assumptions, revenue build, P&L, balance sheet, cash flow, scenarios, etc.)
- **Business model identification** — DTC? Marketplace? SaaS? Subscription? What are the revenue lines?
- **Driver map** — the key inputs that drive the outputs. How deep are the assumptions? (e.g., "Revenue is built bottom-up from SKU-level units x price" vs. "Revenue is a top-line growth % applied to last year")

Outputs a plain-English summary: *"This is a 5-year SaaS model built on a bottoms-up seat-based pricing structure with three customer tiers. Revenue is driven by..."*

**Phase 2 — Assumption Analysis**

For each key driver:
- **What's assumed** — the actual numbers and rates
- **Depth assessment** — is it a single growth % or built from unit economics, conversion funnels, cohort data?
- **Reasonableness flags** — aggressive, conservative, or in-line? Compared to historicals if available in the model.
- **Sensitivity** — which assumptions move the needle most? Where does a small input change create a big output swing?

**Phase 3 — Key Data Points & Insights**

The business intelligence layer:
- **Inflection points** — step-changes in the model (e.g., "Gross margin jumps from 62% to 78% in Year 3 as the company shifts from professional services revenue to pure software")
- **Operating leverage** — where margins expand as revenue scales
- **Key assumptions to test in diligence** — the 5-10 assumptions that matter most and need validation
- **Cash dynamics** — burn rate, runway, when does the business turn cash-flow positive?
- **Hidden risks** — assumptions that are unusually optimistic or internally inconsistent

**Phase 4 — Report Output**

Saves to:
```
{deal-folder}/dd-reports/model-review-YYYY-MM-DD.md
```

Report structure:
1. **Business Model Summary** — plain-English description of what the model says the business is and how it makes money
2. **Driver Map** — the key inputs and their depth
3. **Assumption Analysis** — by driver, with reasonableness flags
4. **Key Findings** — inflection points, operating leverage, cash dynamics, risks
5. **Assumptions to Test** — prioritized list of what to validate in diligence

Then drops into interactive mode.

**Technical considerations:**

- Excel reading via Python (openpyxl). The skill must open each workbook **twice**: once with `data_only=False` to read formula strings (understanding model structure and relationships), and once with `data_only=True` to read cached computed values. Note: `data_only=True` returns values from the last time the file was saved in Excel — if a file was never opened in Excel (e.g., exported from Google Sheets), cached values may be `None`. The skill should detect this and warn the user.
- Models vary wildly in quality and organization. The skill needs to handle everything from a clean 3-statement model to a messy single-tab spreadsheet.
- Named ranges, linked workbooks, and macros are common in financial models. The skill should note when it encounters these and flag any it can't fully parse.

**Allowed tools:** `Read`, `Write`, `Bash`, `Glob`, `Agent`, `AskUserQuestion`

---

### 4. `/dd-questions` — Diligence Question Generation

**Purpose:** Synthesize findings from the data room and model reviews into a single, prioritized list of diligence questions.

**Invocation:**
```
/dd-questions ~/Dropbox/Deals/Acme-Corp
```

Works best after `/dd-dataroom` and `/dd-model` have run (reads their reports from `dd-reports/`). Can also run standalone — it'll work from whatever's in the folder directly.

**How it builds the list:**

1. **Three sources:**
   - Data room gaps and concerns (from `dataroom-assessment-*.md`)
   - Model assumptions to test (from `model-review-*.md`)
   - Rubric-driven standard questions (from the config — baseline questions that apply regardless of deal-specific findings)

2. **Deduplication and prioritization:**
   - Merges overlapping items (e.g., model flags a margin assumption AND data room is missing COGS detail → one question, not two)
   - Priority levels: **Critical** (deal-breaker if unanswered), **Important** (needed for IC memo), **Nice to have** (would improve understanding)

3. **Categorization by domain:**
   - Financial / Accounting
   - Product / Operations
   - Market / Competitive
   - Team / Management
   - Legal / IP / Regulatory
   - Customer / Sales / Marketing
   - Technology / Infrastructure

**Output:**

Saves to:
```
{deal-folder}/dd-reports/diligence-questions-YYYY-MM-DD.md
```

Format — clean numbered list, grouped by category, with priority tags and context:

```markdown
## Financial / Accounting

1. **[Critical]** The model shows gross margin improving from 52% to 68%
   between Y1 and Y2 — what specifically drives this? Is there a signed
   manufacturing agreement that supports the new COGS assumptions?

2. **[Important]** Monthly P&L shows a $45K marketing spike in March 2024
   with no corresponding revenue lift. What was this spend and what was learned?

3. **[Important]** No tax returns prior to 2022 in the data room. Can these
   be provided, or is there a reason they're excluded?
```

Every question includes the **"why"** — what finding or gap triggered it — so anyone reading the list understands the reasoning, not just the ask.

After output, interactive mode for refinement: "add questions about supply chain risk," "rewrite these for sending to the CFO," etc.

**Allowed tools:** `Read`, `Write`, `Bash`, `Glob`, `Grep`, `AskUserQuestion`

---

## Documentation

### Root SKILL.md (Package Overview)

Tone: Professional, direct, human. Written for investors, not developers. No jargon where plain language works. Hyperlinks to real sources.

Structure:
1. **One-liner** — "AI-powered due diligence tools for PE and VC investors."
2. **What it does** — 3 bullets, plain English
3. **New to the command line?** — pointer to `docs/cli-quickstart.md`
4. **IT & compliance** — pointer to `docs/it-compliance-guide.md`
5. **Install** — `claude install github:bwadecodes/dealflow`
6. **Quick start** — three commands with examples
7. **First-time setup** — `/dd-setup`
8. **Skills reference** — one paragraph per skill
9. **Customizing your rubric** — pointer to `docs/rubric-guide.md`
10. **Default configs** — explains the five templates
11. **Roadmap** — sourcing, post-deal, memo generation
12. **About** — Brian Wade, Primario Holdings, background across PE/growth/VC

### docs/cli-quickstart.md

For investors who have never opened a terminal. Covers:
- What is a terminal and how to open it (Mac + Windows)
- Navigating to a folder
- What [Claude Code](https://docs.anthropic.com/en/docs/claude-code) is
- How to install it
- Running your first command

Tone: Respectful, zero condescension. "You spend your days in Excel and data rooms, not terminals. Here's the 5 minutes you need."

### docs/it-compliance-guide.md

For when the user needs approval from IT or compliance before installing. Includes:
- **One-page summary** of what the tool does — suitable for forwarding
- **Data flow explanation** — local files are read by Claude Code on your machine, sent to [Anthropic's API](https://www.anthropic.com/api) for processing, responses come back. No data is stored on third-party servers beyond the API interaction.
- **Subscription tier data handling:**
  - [Free/Pro plans](https://www.anthropic.com/pricing) — conversations may be used to improve models (check [Anthropic's privacy policy](https://www.anthropic.com/policies/privacy))
  - [Team/Enterprise plans](https://www.anthropic.com/enterprise) — data is not used for training, additional security and compliance controls
  - Recommendation: firms reviewing confidential deal materials should use Team or Enterprise
- **FAQs:** "Does this store my documents?" "Can Anthropic see my data room?" "Is this SOC 2 compliant?" — with links to [Anthropic's security page](https://www.anthropic.com/security) and [trust center](https://trust.anthropic.com/)
- **Template email** the user can send to their IT team

### docs/rubric-guide.md

How to customize the diligence rubric. Walks through:
- What each field in the config does
- How weights affect prioritization
- Adding/removing rubric categories
- Examples from each default config showing the differences
- Tips for building a rubric that matches your fund's process

---

## Default Config Differences

| | Venture Capital | Growth Equity | PE Lower-Middle Market | PE Middle Market | PE Large Buyout |
|---|---|---|---|---|---|
| **Rubric emphasis** | Team, TAM, PMF, burn/runway | Financials + growth metrics, unit economics | Financials, QoE, margins, working capital | Operational complexity, platform, leverage | Capital structure, integration, regulatory, ESG |
| **Buy box** | Pre-rev to $5M ARR, minority | $3M-$30M ARR, growth inflection | $10M-$75M rev, EBITDA positive, control | $75M-$250M rev, scaled, control | $250M+ rev, institutional-grade, control |
| **Model review focus** | Burn rate, runway, CAC/LTV | Unit economics, channel attribution, margin expansion | Assumption depth, operating leverage, cash conversion | Leverage scenarios, platform synergies, segment P&Ls | Capital structure stress testing, integration economics |
| **Data room expectations** | Lighter — pitch deck, cap table, basic financials | Full room expected, tolerance for early-stage gaps | Full financials, tax returns, legal, customer contracts | Institutional-quality room, segment reporting, integration plans | Complete institutional room, regulatory filings, ESG materials |
| **Question style** | Market validation, team capability, product roadmap | Financial rigor + growth thesis validation | QoE-oriented, accounting detail, contract review | Platform thesis, operational scale, leverage terms | Governance, integration risk, regulatory, exit planning |

---

## Technical Notes

### SKILL.md Structure

Each skill's `SKILL.md` follows the standard Claude Code skill format:

```yaml
---
name: dd-dataroom
description: Assess a deal data room against your diligence rubric
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---
```

The markdown body contains the full prompt instructions: workflow steps, output format, error handling, and tool-calling sequences. `AskUserQuestion` is a built-in Claude Code tool that prompts the user for input during skill execution.

Each SKILL.md should be structured as:
1. **Purpose** — one sentence
2. **Prerequisites** — config file check, Python dependency check
3. **Input parsing** — how to extract the folder/file path and optional context from the invocation
4. **Workflow steps** — numbered, with tool calls specified
5. **Output format** — exact report structure with markdown template
6. **Interactive mode transition** — how to hand off to conversation
7. **Error handling** — what to do when things go wrong (see below)

### Plugin Metadata

`.claude-plugin/plugin.json` follows the [Claude Code plugin specification](https://docs.anthropic.com/en/docs/claude-code/skills):

```json
{
  "name": "dealflow",
  "description": "AI-powered due diligence tools for PE and VC investors",
  "version": "1.0.0",
  "author": {
    "name": "Brian Wade",
    "url": "https://github.com/bwadecodes"
  },
  "repository": "https://github.com/bwadecodes/dealflow",
  "license": "MIT",
  "keywords": ["private-equity", "venture-capital", "due-diligence", "finance", "investing"]
}
```

The root `SKILL.md` serves as both the plugin entry point and the package-level README displayed on GitHub. A separate `README.md` is not needed — `SKILL.md` at root is the convention for Claude Code plugins and GitHub renders it.

### File Reading

- **PDF** — Python pymupdf for text extraction. Note: embedded images/charts in PDFs require screenshot-based reading (Claude's `Read` tool on the PDF renders pages visually). Text extraction alone will miss charts and diagrams.
- **Excel (.xlsx)** — Python openpyxl, dual-open strategy (see `/dd-model` technical notes)
- **Word (.docx)** — Python python-docx for text extraction
- **CSV** — Direct read via Claude's `Read` tool
- **Images** — Claude's `Read` tool handles standalone image files (PNG, JPG) natively via vision. For images embedded within PDFs or DOCX, extract them first or use page-level PDF rendering.

### Python Dependencies

Skills that need Python libraries (pymupdf, openpyxl, python-docx) handle installation inline via `pip install --quiet` in a Bash call at the start of execution. No `requirements.txt` or separate setup step.

Each SKILL.md should check for the library first and install only if missing:
```bash
python3 -c "import openpyxl" 2>/dev/null || pip install openpyxl --quiet
```

The CLI quickstart guide (`docs/cli-quickstart.md`) should note that Python is required and link to [python.org](https://www.python.org/downloads/) for installation if not already present.

### Config Resolution

All `/dd-*` skills look for the config in this order:
1. Path passed via invocation argument (e.g., `/dd-dataroom path --config my-config.yaml`)
2. `~/.claude/dealflow/diligence-config.yaml` (default location)
3. If neither exists, prompt the user to run `/dd-setup`

Users can maintain multiple configs (e.g., one for their PE fund, one for personal angel investing) and pass the relevant one per invocation. The default config is the one set up by `/dd-setup`.

### Interactive Mode

After a skill delivers its report, "interactive mode" means the skill's conversation context remains active in the Claude Code session. The user can type follow-up questions in the same session and Claude retains context from the documents it read and the report it generated.

- The skill works from **both** the generated report and any documents still in context
- For large data rooms, the skill may need to re-read specific documents on follow-up (the report serves as an index back to source files)
- The user exits interactive mode naturally by starting a new command or closing the session
- The skill should explicitly tell the user: *"Report saved. You can ask me follow-up questions about anything in the room, or move on to another command."*

### Subagent Strategy for `/dd-dataroom`

- Spawn **3-4 subagents max** to stay within API rate limits: one for financials + accounting, one for legal + IP, one for product + operations + market, one for team + customers + marketing
- Documents that span categories go to the most relevant agent; cross-references are handled in the synthesis step (main agent)
- If subagent dispatch fails, fall back to sequential processing (slower but reliable)
- Each subagent receives: the rubric categories it owns, the file list for those categories, and the deal context string

### Error Handling

Skills should handle these common failures gracefully:

| Scenario | Response |
|----------|----------|
| Empty folder / no files found | "This folder appears to be empty. Double-check the path and try again." |
| Password-protected Excel/PDF | "This file is password-protected. Remove the password and re-run, or skip it." |
| Python not installed | "Python is required for reading Excel and PDF files. Install it from python.org and try again." |
| pip install fails (permissions) | "Couldn't install a required library. Try running: pip install openpyxl pymupdf python-docx" |
| Config file not found | "No config found. Run /dd-setup first to set up your diligence preferences." |
| File type not supported | "Skipping [filename] — file type not supported. Supported: PDF, Excel, Word, CSV, images." |

Tone: direct, no jargon, actionable. Tell the user what happened and exactly what to do about it.

### Context Window Management

Large data rooms are the main challenge. Strategy:
- Phase 1 (inventory) reads filenames and folder structure only — minimal context usage
- Phase 2 (assessment) uses subagents per rubric category, each with their own context window
- Documents are read selectively based on rubric priority, not exhaustively
- The skill handles messy folders gracefully — mixed naming conventions, nested structures, duplicate files

### Output Location

All reports save to `{deal-folder}/dd-reports/`. This keeps everything with the deal, not in a separate location. Reports are dated so multiple runs don't overwrite each other.

### v1 Scope: Report Format

v1 outputs markdown only. The config option `report_format: "docx | both"` is reserved for a future release. The config file includes the field so the schema doesn't need to change later, but the skills will only produce `.md` files in v1.

---

## Future Skills (Not In Scope, Reserving Architecture)

These skills are planned but **not included in the v1 repo**. No empty directories or placeholder files ship for future modules.

| Skill | Module | Purpose |
|-------|--------|---------|
| `/dd-memo` | Diligence | Draft IC pre-screen or diligence memo from findings |
| `/src-deepdive` | Sourcing | Thematic research on an industry/trend |
| `/src-screen` | Sourcing | Screen companies against buy box criteria |
| `/pd-180` | Post-Deal | Build and track a 180-day plan |
| `/pd-board` | Post-Deal | Prepare board meeting materials |
| `/pd-monitor` | Post-Deal | Monthly reporting and KPI tracking |

---

## Success Criteria

The diligence module is working when:
1. A user can install with one command and configure in under 5 minutes
2. `/dd-dataroom` produces an assessment that a senior investor would find useful — not perfect, but a strong first pass that saves hours
3. `/dd-model` correctly identifies the business model, key drivers, and flags the assumptions worth testing
4. `/dd-questions` produces questions that an investor would actually want to ask, not generic boilerplate
5. Someone who has never used a CLI can get from zero to running their first data room scan using only the repo's documentation
6. The rubric system is flexible enough that a buyout fund and a seed fund can both use this with meaningfully different configurations
