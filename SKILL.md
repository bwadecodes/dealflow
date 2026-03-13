---
name: dealflow
description: AI-powered due diligence tools for PE and VC investors. Install with claude install github:bwadecodes/dealflow.
---

# Dealflow

AI-powered due diligence tools for PE and VC investors.

- **Point it at a data room** and get a structured assessment --- findings, flags, gaps, and next steps --- organized against your own diligence rubric.
- **Point it at a financial model** and get a plain-English review of the business model, key drivers, assumptions worth testing, and hidden risks.
- **Generate a prioritized question list** that synthesizes everything into the actual questions you'd want to ask management, not generic boilerplate.

Built by [Brian Wade](https://github.com/bwadecodes), an investor who has worked across PE, growth equity, and VC --- now investing independently out of [Primario Holdings](https://github.com/bwadecodes).

---

## New to the command line?

No problem. Most investors haven't spent time in a terminal. The [CLI Quickstart](docs/cli-quickstart.md) covers everything you need in about 5 minutes --- from opening a terminal to running your first data room scan.

## Need IT or compliance approval?

The [IT & Compliance Guide](docs/it-compliance-guide.md) has a one-page summary of how the tool works, where your data goes, and a template email you can forward to your IT team.

---

## Install

```bash
claude install github:bwadecodes/dealflow
```

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Anthropic's CLI tool). If you don't have it yet, the [CLI Quickstart](docs/cli-quickstart.md) walks you through setup.

## Quick Start

**Set up your diligence config** (one-time, ~3 minutes):
```
/dd-setup
```

**Assess a data room:**
```
/dd-dataroom ~/Deals/Acme-Corp/Data-Room "B2B SaaS, ~$8M ARR, Series A"
```

**Review a financial model:**
```
/dd-model ~/Deals/Acme-Corp/Model/Acme-Model-v3.xlsx
```

**Generate diligence questions:**
```
/dd-questions ~/Deals/Acme-Corp
```

---

## First-Time Setup

Run `/dd-setup` to configure your diligence preferences. It walks you through choosing a starting template and customizing your rubric, buy box, and report preferences.

Three built-in templates:

| Template | Focus | Typical Deals |
|----------|-------|---------------|
| **PE Lower-Middle Market** | Financials, quality of earnings, margins, working capital | $5-50M revenue, control deals, established businesses |
| **VC Seed / Pre-Seed** | Team, TAM, product-market fit, burn and runway | Pre-revenue to $5M, minority stakes, early-stage |
| **Growth Equity** | Blends both --- financials + growth metrics, unit economics | $5-25M revenue, growth inflection, path to profitability |

Pick the closest fit. You can customize every question, weight, and buy box criterion.

---

## Skills Reference

### `/dd-setup` --- Configuration Wizard

Builds your diligence config file --- your rubric, buy box criteria, and report preferences. Run this once. Update it when your investment criteria change.

### `/dd-dataroom` --- Data Room Assessment

Reads a folder of deal documents and produces a structured assessment against your rubric. Inventories the room, flags gaps, reads documents by priority, and delivers findings organized by rubric category with strength/concern flags. Handles PDFs, Excel, Word, CSV, and images. Works on messy folder structures.

### `/dd-model` --- Financial Model Review

Reads an Excel model (.xlsx) and produces a business-intelligence review. Maps the business model, traces key drivers, tests assumptions against historicals, and surfaces inflection points, operating leverage, and hidden risks. Opens the workbook twice --- once for formulas (model structure), once for values (actual numbers).

### `/dd-questions` --- Diligence Question List

Synthesizes findings from the data room and model reviews into a prioritized question list. Questions include the "why" --- what triggered each one --- so the reasoning is clear to anyone reading the list. Deduplicates overlapping items and categorizes by domain (financial, product, market, team, legal, customer, technology).

---

## Customizing Your Rubric

The rubric is the backbone of every assessment. It determines what gets prioritized, what gets flagged, and what questions get generated. See the [Rubric Customization Guide](docs/rubric-guide.md) for details on:

- Adding and removing categories
- Adjusting weights (high / medium / low)
- Writing effective rubric questions
- Maintaining multiple configs for different investment approaches

---

## Default Configs

The three built-in templates are designed to reflect how different types of investors actually think about diligence:

- **PE Lower-Middle Market** weights financials and quality of earnings heavily. Expects a full data room with tax returns, customer contracts, and QoE-ready materials. Questions are oriented toward accounting detail and contract review.

- **VC Seed / Pre-Seed** weights team, market, and product-market fit. Expects a lighter data room --- pitch deck, cap table, basic financials. Questions focus on market validation, team capability, and product roadmap.

- **Growth Equity** blends both. Expects financial rigor but adds growth-stage metrics --- unit economics depth, channel attribution, margin expansion trajectory. Questions validate both the financial story and the growth thesis.

The templates are starting points. Every investor's process is different --- customize them to match yours.

---

## Roadmap

Dealflow currently focuses on diligence --- the highest-value, most-frequent workflow. Planned additions:

- **`/dd-memo`** --- Draft an IC pre-screen or diligence memo from findings
- **`/src-deepdive`** --- Thematic research on an industry or trend
- **`/src-screen`** --- Screen companies against buy box criteria
- **`/pd-180`** --- Build and track a 180-day post-close plan
- **`/pd-board`** --- Prepare board meeting materials
- **`/pd-monitor`** --- Monthly reporting and KPI tracking

---

## About

Built by [Brian Wade](https://github.com/bwadecodes). Background across PE, growth equity, and VC --- now investing independently out of Primario Holdings.

This started as a set of personal tools for running diligence faster without sacrificing depth. If you find it useful or have ideas for what would make it better, [open an issue](https://github.com/bwadecodes/dealflow/issues).

## License

[MIT](LICENSE)
