# Dealflow /Skills: Claude Code AI-Powered Diligence Tools for PE & VC Investors

Point it at a data room folder or a financial model, and it produces the kind of analysis you'd normally spend days on — organized against your own diligence rubric.

Dealflow is a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills package that gives PE and VC investors structured, AI-assisted workflows across the deal lifecycle — from prescreen, through diligence and review, to term sheet. Sourcing and post-deal modules are on the [roadmap](#roadmap).

Built by [Brian Wade](https://github.com/bwadecodes), an investor who has worked across [PE, growth equity, and VC](https://www.linkedin.com/in/brianmwade/).

---

## What It Does

Dealflow v2 covers the full deal lifecycle — prescreen through term sheet:

**Front door**
- **Prescreen** a deal from a pitch deck or CIM. Get a memo + simple model in minutes.
- **Desk research** on industry, competitors, news, and filings with full citations.

**Diligence**
- **Data room assessment** against your rubric, with findings, flags, and gap analysis.
- **Financial model review** — drivers, assumption reasonableness, hidden risks.
- **Diligence question list** — prioritized, deduped, with the "why" attached to every question.
- **Super analyst** — propose interesting analyses, execute as auditable Excel, or enhance/review existing analyses.
- **Cohort analysis** — specialized SaaS retention/NRR/GRR/concentration playbook.

**Review**
- **VP review** — line-by-line scrub for correctness and completeness. Catches math errors, broken citations, inconsistent claims, and unreasonable model assumptions.
- **Pre-IC review** — everything VP review does plus thoroughness, deeper model pressure-testing, devil's advocate, and pre-emptive IC question prep.

**Execution**
- **Deal process** — phases, third-party scope, workstream tracker. Stateful.
- **Checklist** — quick state-of-the-deal snapshot, cheap to run often.
- **Returns model** — standalone with full sensitivities, decoupled from operating model.
- **Term sheet** — cap table analysis + pro forma + draft TS aligned with firm preferences.

Outputs match **your firm's voice and templates** when you onboard sample materials via `/dealflow-firmstyle`. Each deal builds a persistent `.dealflow/` index so skills compose cleanly.

---

## Who This Is For

Investors who want to move faster through diligence without sacrificing depth. You don't need to be a developer. You do need to be comfortable pointing a tool at a folder and reading the output.

If you've never touched a command line, that's fine — the [CLI Quickstart](docs/cli-quickstart.md) covers everything you need in about 5 minutes.

If you need IT or compliance approval before installing, the [IT & Compliance Guide](docs/it-compliance-guide.md) has a one-page summary of how the tool works, where your data goes, and a template email you can forward to your IT team.

---

## Install

Inside a Claude Code session, run:

```
/plugin marketplace add bwadecodes/dealflow
/plugin install dealflow@dealflow
```

The first command adds the Dealflow marketplace. The second installs the plugin with all 15 `/dealflow-*` skills.

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Anthropic's CLI tool). If you don't have it yet, the [CLI Quickstart](docs/cli-quickstart.md) walks you through the full setup — Node.js, Python, Claude Code, and Dealflow — in one pass.

**Requirements:**
- [Node.js](https://nodejs.org/) (for Claude Code)
- [Python 3](https://www.python.org/downloads/) (for reading Excel, PDF, and Word files)
- An [Anthropic](https://www.anthropic.com/) account (Free, Pro, Team, or Enterprise)

---

## Quick Start

**1. One-time setup (~5 minutes):**
```
/dealflow-setup                              # rubric, buy box, preferences
/dealflow-firmstyle ~/firm-samples           # optional: capture firm voice & templates
```

**2. Prescreen a new deal:**
```
/dealflow-prescreen ~/Deals/Acme/deck.pdf
```

**3. If pursuing, set up the deal:**
```
/dealflow-process ~/Deals/Acme               # process plan + tracker
/dealflow-deskresearch "Acme Corp" --deal-folder ~/Deals/Acme
```

**4. Run diligence:**
```
/dealflow-dataroom ~/Deals/Acme/Data-Room "B2B SaaS, ~$8M ARR, Series A"
/dealflow-model ~/Deals/Acme/Model.xlsx
/dealflow-cohort ~/Deals/Acme/customers.csv --deal-folder ~/Deals/Acme
/dealflow-superanalyst ~/Deals/Acme/transactions.csv --create
/dealflow-questions ~/Deals/Acme
```

**5. Pressure test before IC:**
```
/dealflow-vp-review ~/Deals/Acme             # correctness + completeness
/dealflow-pre-ic ~/Deals/Acme                # plus thoroughness, stress test, devil's advocate
```

**6. Move to term sheet:**
```
/dealflow-returns ~/Deals/Acme
/dealflow-termsheet ~/Deals/Acme
```

**Anytime, check status:**
```
/dealflow-checklist ~/Deals/Acme
```

Reports save to `<deal-folder>/reports/`, dated so multiple runs don't overwrite each other. Deal state and the materials index live in `<deal-folder>/.dealflow/`.

---

## Skills

15 skills covering setup, sourcing-adjacent front door, diligence, review, and execution. Each is invoked as `/dealflow-<name>`. Run any one independently or chain them — every skill is self-contained but composes with the others through the shared deal state and index.

### Setup

| Skill | Purpose |
|---|---|
| `/dealflow-setup` | Build your diligence config: rubric, buy box, preferences. Run once. |
| `/dealflow-firmstyle` | Capture firm voice, templates, term preferences, visual identity from sample materials. Makes every output sound like *your* firm. |

### Front Door

| Skill | Purpose |
|---|---|
| `/dealflow-prescreen` | Prescreen memo + simple model from a pitch deck, CIM, or just a description. The natural front door to a new deal. |
| `/dealflow-deskresearch` | Pull industry reports, news, competitors, public filings. Configurable focus, source count (10/50/100), and stealth mode. MD + PDF output with full citations. |

### Diligence

| Skill | Purpose |
|---|---|
| `/dealflow-dataroom` | Structured assessment of a data room against your rubric. Builds the persistent deal index. |
| `/dealflow-model` | Drivers, assumption reasonableness, inflection points, hidden risks. |
| `/dealflow-questions` | Prioritized question list synthesizing dataroom + model + rubric. Deduped, categorized, every question with the "why" attached. |
| `/dealflow-superanalyst` | Create (raw data → analyses → auditable Excel), enhance (extend existing), or review (audit existing for correctness). |
| `/dealflow-cohort` | Specialized SaaS retention/NRR/GRR/concentration playbook. Templated, runs the standard set. |

### Review

| Skill | Purpose |
|---|---|
| `/dealflow-vp-review` | Line-by-line scrub for correctness and completeness. Math errors, broken citations, inconsistent claims, plus a reasonableness check on model assumptions and cases. Not a judgement call on the deal. |
| `/dealflow-pre-ic` | Everything VP review does plus thoroughness of analysis, deeper model pressure-testing (independent base case re-grade, true-downside construction), devil's advocate, and pre-emptive IC question prep. |

### Execution

| Skill | Purpose |
|---|---|
| `/dealflow-process` | Deal process plan + workstream tracker. Stateful — re-runs update status. |
| `/dealflow-checklist` | Quick state-of-the-deal snapshot. Cheap, runs in seconds, designed for daily use. |
| `/dealflow-returns` | Standalone returns model with full sensitivities. Decoupled from the operating model so you can iterate on structure. |
| `/dealflow-termsheet` | Cap table + charter analysis, pro forma cap table with waterfall, term sheet draft aligned with firm preferences. **Counsel must review before use.** |

Each skill has its own SKILL.md with full workflow detail. Type `/dealflow-` in Claude Code to see the list.

---

## Configuration & Rubric

The rubric is the backbone of every assessment. It determines what gets prioritized in data room reviews, what the model analysis focuses on, and which questions get generated.

### Five Built-In Templates

| Template | Revenue Range | Rubric Emphasis |
|----------|--------------|-----------------|
| **Venture Capital** | Pre-revenue – $5M ARR | Team, TAM, product-market fit, burn and runway |
| **Growth Equity** | $3M – $30M ARR | Unit economics, CAC/LTV, growth + path to profitability |
| **PE Lower-Middle Market** | $10M – $75M revenue | Financials, QoE, margins, working capital |
| **PE Middle Market** | $75M – $250M revenue | Operational complexity, platform strategy, leverage |
| **PE Large Buyout** | $250M+ revenue | Capital structure, integration, regulatory, institutional ops |

These templates are starting points, not limits. During `/dealflow-setup`, you can ask the AI to generate a custom rubric for any strategy — late-stage VC, investment banking, corporate development, credit, real estate, or anything else. Just describe your approach and it builds one from scratch.

The templates aren't cosmetically different — they reflect how different types of investors actually think about diligence. VC weights founder dynamics and market; Growth Equity blends financial rigor with growth metrics; PE templates scale from earnings quality at the lower end to capital structure and platform strategy at the upper end.

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
  revenue_range: "$10M - $75M"
  stage: "Series A, B, Growth"
  ownership_target: "20-40%"
  sector_focus: ["consumer", "technology", "healthcare"]

preferences:
  output_dir: "reports"
  detail_level: "deep"      # deep | executive
```

Weights affect everything — high-weight categories get analyzed first in data room reviews, get deeper assumption testing in model reviews, and generate higher-priority questions. See the [Rubric Customization Guide](docs/rubric-guide.md) for the full walkthrough.

### Multiple Configs

You can maintain different configs for different contexts and pass them per invocation:

```
/dealflow-dataroom ~/Deals/Acme --config ~/.claude/dealflow/configs/pe-buyout.yaml
```

---

## How It Works Under the Hood

**Data flow:** Local files on your machine → sent to [Anthropic's API](https://www.anthropic.com/api) over HTTPS for analysis → results returned → reports saved locally. No data is stored on third-party servers beyond the API interaction.

**File reading:** PDFs via [pymupdf](https://pymupdf.readthedocs.io/), Excel via [openpyxl](https://openpyxl.readthedocs.io/) (dual-open: formulas + cached values), Word via [python-docx](https://python-docx.readthedocs.io/). CSV and images read directly. Python dependencies install automatically on first run.

**Context management:** Large data rooms (hundreds of files) are triaged — Phase 1 reads filenames only, Phase 2 reads selectively based on rubric priority. The data room skill uses parallel subagents (3-4) to split the work across rubric categories, each with its own context window. If subagent dispatch fails, it falls back to sequential processing.

**Reports:** All output is markdown, saved to `{deal-folder}/reports/` with date stamps. Reports from different runs don't overwrite each other. Each report includes run metadata — model used, token counts, duration, and estimated cost — so you always know what an analysis cost. v1 is markdown-only; DOCX export is planned.

---

## Documentation

| Guide | Audience | What It Covers |
|-------|----------|----------------|
| [CLI Quickstart](docs/cli-quickstart.md) | Investors new to the command line | Opening a terminal, navigating folders, installing Claude Code, running your first command |
| [IT & Compliance Guide](docs/it-compliance-guide.md) | IT teams, compliance officers | Data flow, subscription tiers, security references, template approval email |
| [Rubric Customization Guide](docs/rubric-guide.md) | All users | Adding/removing categories, adjusting weights, writing effective questions, maintaining multiple configs |

---

## Roadmap

Dealflow v2 covers the full deal lifecycle from prescreen through term sheet. Two future modules:

**Sourcing**
| Skill | Purpose |
|-------|---------|
| `/dealflow-deepdive` | Thematic research on an industry or trend |
| `/dealflow-screen` | Screen companies against buy box criteria |
| `/dealflow-pipeline` | Pipeline tracker with conversion analytics |

**Post-Deal**
| Skill | Purpose |
|-------|---------|
| `/dealflow-180` | Build and track a 180-day post-close plan |
| `/dealflow-board` | Prepare board meeting materials |
| `/dealflow-monitor` | Monthly reporting and KPI tracking |
| `/dealflow-lp` | LP letters and quarterly updates in firm voice |

---

## About

Built by [Brian Wade](https://github.com/bwadecodes). Background across [PE, growth equity, and VC]((https://www.linkedin.com/in/brianmwade/)).

This started as a set of personal tools for running diligence faster without sacrificing depth. The goal is simple: spend less time on the mechanical parts of diligence so you can spend more time on the judgment calls that actually matter.

If you find a bug, have an idea, or just want to say "this didn't work on my deal" — [open an issue](https://github.com/bwadecodes/dealflow/issues). Your AI agent can do it too.

## License

[MIT](LICENSE)
