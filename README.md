# Dealflow: AI-Powered Diligence Tools for PE & VC Investors

Point it at a data room folder or a financial model, and it produces the kind of analysis you'd normally spend days on — organized against your own diligence rubric.

Dealflow is a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills package that gives PE and VC investors structured, AI-assisted due diligence workflows. The first release focuses on **diligence** — the highest-value, most-frequent workflow. Sourcing and post-deal modules are on the [roadmap](#roadmap).

Built by [Brian Wade](https://github.com/bwadecodes), an investor who has worked across [PE, growth equity, and VC](https://www.linkedin.com/in/brianmwade/).

---

## What It Does

- **Point it at a data room** and get a structured assessment — findings, strength/concern flags, gap analysis, and recommended next steps — organized against your own diligence rubric.
- **Point it at a financial model** and get a plain-English review of the business model, key drivers, assumption reasonableness, sensitivity analysis, and hidden risks.
- **Generate a prioritized diligence question list** that synthesizes findings from both the data room and model review into the actual questions you'd want to ask management — not generic boilerplate.

Each skill can be used independently or sequenced together. Run the data room assessment first, then the model review, then generate questions that synthesize everything. Or just point the model reviewer at an Excel file and get a standalone analysis. Your call.

---

## Who This Is For

Investors who want to move faster through diligence without sacrificing depth. You don't need to be a developer. You do need to be comfortable pointing a tool at a folder and reading the output.

If you've never touched a command line, that's fine — the [CLI Quickstart](docs/cli-quickstart.md) covers everything you need in about 5 minutes.

If you need IT or compliance approval before installing, the [IT & Compliance Guide](docs/it-compliance-guide.md) has a one-page summary of how the tool works, where your data goes, and a template email you can forward to your IT team.

---

## Install

```bash
claude install github:bwadecodes/dealflow
```

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Anthropic's CLI tool). If you don't have it yet, the [CLI Quickstart](docs/cli-quickstart.md) walks you through the full setup — Node.js, Python, Claude Code, and Dealflow — in one pass.

**Requirements:**
- [Node.js](https://nodejs.org/) (for Claude Code)
- [Python 3](https://www.python.org/downloads/) (for reading Excel, PDF, and Word files)
- An [Anthropic](https://www.anthropic.com/) account (Free, Pro, Team, or Enterprise)

---

## Quick Start

**1. Set up your diligence config** (one-time, ~3 minutes):
```
/dd-setup
```
Choose from three starting templates (PE, VC, or Growth Equity), customize your rubric and buy box, and save your preferences. Every other skill reads this config.

**2. Assess a data room:**
```
/dd-dataroom ~/Deals/Acme-Corp/Data-Room "B2B SaaS, ~$8M ARR, Series A, 200 enterprise customers"
```

**3. Review a financial model:**
```
/dd-model ~/Deals/Acme-Corp/Model/Acme-Model-v3.xlsx "B2B SaaS, Series A at $40M pre"
```

**4. Generate diligence questions:**
```
/dd-questions ~/Deals/Acme-Corp
```

Reports are saved to a `dd-reports/` folder inside your deal directory, dated so multiple runs don't overwrite each other.

---

## Skills

### `/dd-setup` — Configuration Wizard

Builds your diligence config file — your rubric, buy box criteria, and report preferences. Run this once before your first data room review. Update it when your investment criteria change or when you want a different config for a different fund.

**What it does:**
1. Presents three starting templates (PE, VC, or Growth Equity)
2. Walks through each rubric category — keep as-is, adjust weights, add/remove questions
3. Configures your buy box criteria (revenue range, stage, ownership target, sector focus)
4. Sets report preferences (output directory, detail level)
5. Saves to `~/.claude/dealflow/diligence-config.yaml`

You can maintain multiple configs (e.g., one for your PE fund, one for personal angel investing) and pass the relevant one per invocation with `--config`.

---

### `/dd-dataroom` — Data Room Assessment

Reads a deal's data room folder and produces a structured diligence assessment against your rubric. This is the workhorse skill — it handles everything from a clean 20-file room to a messy 600-file dump.

**Invocation:**
```
/dd-dataroom <path-to-data-room-folder>
/dd-dataroom <path-to-data-room-folder> "<optional deal context>"
```

**How it works:**

**Phase 1 — Inventory & Triage.** Scans the folder tree (filenames and structure only — doesn't open files yet). Produces a document manifest, categorizes files by type (financials, legal, product, marketing, team, customer), runs a gap analysis against your rubric, and builds a prioritized read order. Presents a summary and asks: *"Here's what I found in the room. Want me to proceed with the full assessment, or focus on specific areas?"*

**Phase 2 — Structured Assessment.** Reads documents in priority order using parallel subagents (3-4 max) to manage context windows on large rooms — one agent handles financials and accounting, another legal and IP, another product and market, another team and customers. For each rubric category, produces findings with specific document references, strength/concern flags (green, yellow, red), information quality notes, and cross-references where documents corroborate or contradict each other.

**Phase 3 — Report Output.** Saves a structured report to `dd-reports/dataroom-assessment-YYYY-MM-DD.md` with:
- **Executive summary** — 1-page overview, overall confidence level, top 3 strengths, top 3 concerns
- **Buy box fit** — how the deal maps to your criteria, with specific callouts on fit and misfit
- **Category assessments** — one section per rubric category with findings, flags, and evidence
- **Gap list** — missing documents and information, prioritized
- **Recommended next steps** — what to dig into further

**Phase 4 — Interactive Mode.** After the report is delivered, you can ask follow-up questions in the same session: *"Dig deeper into the financials," "Compare the P&L across 2023 and 2024," "What does the customer data tell us about retention?"*

**Supported file types:** PDF, Excel (.xlsx), Word (.docx), CSV, TXT, images (PNG, JPG). Password-protected and unsupported files are flagged and skipped with a clear message.

---

### `/dd-model` — Financial Model Review

Reads a financial model (.xlsx) and produces a business-intelligence-focused review — understanding the business model, mapping key drivers, testing assumptions, and surfacing the data points that matter most for your investment decision.

**Invocation:**
```
/dd-model <path-to-excel-file>
/dd-model <path-to-excel-file> "<optional deal context>"
```

**How it works:**

**Phase 1 — Model Comprehension.** Opens the workbook twice — once with formulas visible (to understand model structure and relationships) and once with computed values (to see the actual numbers). Maps out the tab inventory, identifies the business model (SaaS? Marketplace? DTC?), and traces the key drivers: what feeds into revenue, what drives costs, and how deep the assumptions go.

Outputs a plain-English summary: *"This is a 5-year SaaS model built on a bottoms-up seat-based pricing structure with three customer tiers. Revenue is driven by..."*

**Phase 2 — Assumption Analysis.** For each key driver: what's assumed (actual numbers and rates), how deep the build is (single growth % vs. built from unit economics and cohort data), reasonableness flags (conservative, in-line, or aggressive compared to historicals), and sensitivity — which assumptions move the needle most.

**Phase 3 — Key Data Points & Insights.** The business intelligence layer:
- **Inflection points** — step-changes in the model (e.g., "Gross margin jumps from 62% to 78% in Year 3 as the company shifts from professional services to software")
- **Operating leverage** — where margins expand as revenue scales
- **Cash dynamics** — burn rate, runway, when does the business turn cash-flow positive
- **Hidden risks** — assumptions that are internally inconsistent or unusually optimistic
- **Assumptions to test** — the 5-10 assumptions that matter most and need validation

**Phase 4 — Report Output.** Saves to `dd-reports/model-review-YYYY-MM-DD.md`, then drops into interactive mode for follow-up questions.

---

### `/dd-questions` — Diligence Question List

Synthesizes findings from the data room assessment and model review into a single, prioritized list of diligence questions. Works best after `/dd-dataroom` and `/dd-model` have run (reads their reports from `dd-reports/`). Can also run standalone.

**Invocation:**
```
/dd-questions <path-to-deal-folder>
```

**How it builds the list:**

1. **Three sources:** Data room gaps and concerns, model assumptions that need testing, and rubric-driven baseline questions that apply regardless of deal-specific findings.

2. **Deduplication and merging:** Overlapping items become one question. If the model flags a margin assumption AND the data room is missing COGS detail, that becomes one question — not two.

3. **Prioritization:** Critical (deal-breaker if unanswered), Important (needed for IC memo), Nice to have (would improve understanding).

4. **Categorization by domain:** Financial / Accounting, Product / Operations, Market / Competitive, Team / Management, Legal / IP / Regulatory, Customer / Sales / Marketing, Technology / Infrastructure.

**Every question includes the "why"** — what finding or gap triggered it — so anyone reading the list understands the reasoning, not just the ask. Questions are written as you'd actually ask them to a CFO, CEO, or counsel.

**Example output:**

```markdown
## Financial / Accounting

1. [Critical] The model shows gross margin improving from 52% to 58%
   between Y1 and Y2 — what specifically drives this? Is there a signed
   manufacturing agreement that supports the new COGS assumptions?

2. [Important] Monthly P&L shows a $2mm marketing spike in March 2024
   with no corresponding revenue lift. What was this spend and what was learned?
```

After output, interactive mode for refinement: *"Add questions about supply chain risk," "Rewrite these for sending to the CFO," "Which ones should I ask in the first management meeting?"*

---

## Configuration & Rubric

The rubric is the backbone of every assessment. It determines what gets prioritized in data room reviews, what the model analysis focuses on, and which questions get generated.

### Three Built-In Templates

| | Private Equity | VC Seed / Pre-Seed | Growth Equity |
|---|---|---|---|
| **Rubric emphasis** | Financials, QoE, margins, working capital, overhead | Team, TAM, product-market fit, unit economics | Blends both — financials + growth metrics |
| **Buy box** | Revenue $25-100M, EBITDA positive | Pre-revenue to $5M, high growth, large market | $5-25M revenue, growth inflection, path to profitability |
| **Model review focus** | Assumption depth, operating leverage, cash conversion | Burn rate, runway, path to next round, CAC/LTV | Unit economics depth, channel attribution, margin expansion |
| **Data room expectations** | Full financials, tax returns, legal, customer contracts | Lighter — pitch deck, cap table, basic financials, IP | Full room expected but tolerance for gaps in early-stage areas |
| **Question style** | QoE-oriented, accounting detail, contract review | Market validation, team capability, product roadmap | Financial rigor + growth thesis validation |

The templates aren't cosmetically different — they reflect how different types of investors actually think about diligence. PE weights quality of earnings; VC weights founder dynamics; Growth Equity blends both with a unit economics lens.

### Config Structure

```yaml
version: 1

rubric:
  categories:
    - name: "Revenue"
      weight: high          # high | medium | low — drives prioritization
      questions:
        - "What is the business model?"
        - "What is driving the growth rate?"
        - "Are growth trends sustainable?"

buy_box:
  revenue_range: "$5M - $50M"
  stage: "Series A, B, Growth"
  ownership_target: "20-40%"
  sector_focus: ["consumer", "technology", "healthcare"]

preferences:
  output_dir: "dd-reports"
  detail_level: "deep"      # deep | executive
```

Weights affect everything — high-weight categories get analyzed first in data room reviews, get deeper assumption testing in model reviews, and generate higher-priority questions. See the [Rubric Customization Guide](docs/rubric-guide.md) for the full walkthrough.

### Multiple Configs

You can maintain different configs for different contexts and pass them per invocation:

```
/dd-dataroom ~/Deals/Acme --config ~/.claude/dealflow/configs/pe-buyout.yaml
```

---

## How It Works Under the Hood

**Data flow:** Local files on your machine → sent to [Anthropic's API](https://www.anthropic.com/api) over HTTPS for analysis → results returned → reports saved locally. No data is stored on third-party servers beyond the API interaction.

**File reading:** PDFs via [pymupdf](https://pymupdf.readthedocs.io/), Excel via [openpyxl](https://openpyxl.readthedocs.io/) (dual-open: formulas + cached values), Word via [python-docx](https://python-docx.readthedocs.io/). CSV and images read directly. Python dependencies install automatically on first run.

**Context management:** Large data rooms (hundreds of files) are triaged — Phase 1 reads filenames only, Phase 2 reads selectively based on rubric priority. The data room skill uses parallel subagents (3-4) to split the work across rubric categories, each with its own context window. If subagent dispatch fails, it falls back to sequential processing.

**Reports:** All output is markdown, saved to `{deal-folder}/dd-reports/` with date stamps. Reports from different runs don't overwrite each other. v1 is markdown-only; DOCX export is planned.

---

## Documentation

| Guide | Audience | What It Covers |
|-------|----------|----------------|
| [CLI Quickstart](docs/cli-quickstart.md) | Investors new to the command line | Opening a terminal, navigating folders, installing Claude Code, running your first command |
| [IT & Compliance Guide](docs/it-compliance-guide.md) | IT teams, compliance officers | Data flow, subscription tiers, security references, template approval email |
| [Rubric Customization Guide](docs/rubric-guide.md) | All users | Adding/removing categories, adjusting weights, writing effective questions, maintaining multiple configs |

---

## Roadmap

Dealflow currently covers **diligence** — the highest-value, most-frequent investor workflow. Planned modules:

**Diligence (expanding)**
| Skill | Purpose |
|-------|---------|
| `/dd-memo` | Draft an IC pre-screen or full diligence memo from findings |

**Sourcing**
| Skill | Purpose |
|-------|---------|
| `/src-deepdive` | Thematic research on an industry or trend |
| `/src-screen` | Screen companies against buy box criteria |

**Post-Deal**
| Skill | Purpose |
|-------|---------|
| `/pd-180` | Build and track a 180-day post-close plan |
| `/pd-board` | Prepare board meeting materials |
| `/pd-monitor` | Monthly reporting and KPI tracking |

---

## About

Built by [Brian Wade](https://github.com/bwadecodes). Background across [PE, growth equity, and VC]((https://www.linkedin.com/in/brianmwade/)).

This started as a set of personal tools for running diligence faster without sacrificing depth. The goal is simple: spend less time on the mechanical parts of diligence so you can spend more time on the judgment calls that actually matter.

If you find it useful or have ideas for what would make it better, [open an issue](https://github.com/bwadecodes/dealflow/issues).

## License

[MIT](LICENSE)
