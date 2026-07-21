---
name: dealflow
description: AI-powered due diligence tools for PE and VC investors. Install with /plugin marketplace add bwadecodes/dealflow then /plugin install dealflow@dealflow.
---

# Dealflow

AI-powered tools for the full deal lifecycle — prescreen through term sheet — for PE and VC investors.

- **Prescreen a new deal** from a pitch deck or CIM and get a memo plus a simple model in minutes
- **Assess a data room** against your rubric, with findings, flags, gaps, and next steps
- **Review a financial model** for business model, key drivers, assumption reasonableness, and hidden risks
- **Run cohort, retention, and custom analyses** as auditable Excel workbooks
- **Pressure-test your work** before IC with VP-level scrub and pre-IC review
- **Lay out the deal process** with workstreams, third-party scope, and a tracker
- **Analyze cap table and draft term sheet** aligned with your firm's standard preferences

Outputs match **your firm's voice** when you onboard sample materials via `/dealflow-firmstyle`. Every deal builds a persistent index so skills compose cleanly and don't waste tokens re-reading files.

Built by [Brian Wade](https://github.com/bwadecodes), an investor who has worked across PE, growth equity, and VC --- now investing independently out of [Primario Holdings](https://github.com/bwadecodes).

---

## New to the command line?

No problem. Most investors haven't spent time in a terminal. The [CLI Quickstart](docs/cli-quickstart.md) covers everything you need in about 5 minutes --- from opening a terminal to running your first data room scan.

## Need IT or compliance approval?

The [IT & Compliance Guide](docs/it-compliance-guide.md) has a one-page summary of how the tool works, where your data goes, and a template email you can forward to your IT team.

---

## Install

Inside a Claude Code session, run:

```
/plugin marketplace add bwadecodes/dealflow
/plugin install dealflow@dealflow
```

Requires [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (Anthropic's CLI tool). If you don't have it yet, the [CLI Quickstart](docs/cli-quickstart.md) walks you through setup.

## Quick Start

**One-time setup (~5 minutes):**
```
/dealflow-setup                           # rubric, buy box, preferences
/dealflow-firmstyle ~/firm-samples        # optional: capture firm voice & templates
```

**Prescreen a new deal:**
```
/dealflow-prescreen ~/Deals/Acme/deck.pdf
```

**Once you decide to pursue:**
```
/dealflow-process ~/Deals/Acme            # build process plan + tracker
/dealflow-dataroom ~/Deals/Acme/Data-Room # full data room assessment
/dealflow-model ~/Deals/Acme/Model.xlsx   # model review
/dealflow-cohort ~/Deals/Acme/customers.csv  # cohort analysis if recurring revenue
```

**Pressure test before IC:**
```
/dealflow-vp-review ~/Deals/Acme
/dealflow-pre-ic ~/Deals/Acme
```

**Term sheet:**
```
/dealflow-termsheet ~/Deals/Acme
```

**Quick status anytime:**
```
/dealflow-checklist ~/Deals/Acme
```

---

## First-Time Setup

Run `/dealflow-setup` to configure your diligence preferences. It walks you through choosing a starting template and customizing your rubric, buy box, and report preferences.

Five built-in templates:

| Template | Focus | Typical Deals |
|----------|-------|---------------|
| **Venture Capital** | Team, TAM, product-market fit, burn and runway | Pre-revenue to $5M ARR, minority stakes, early-stage |
| **Growth Equity** | Blends financial rigor with growth metrics, unit economics | $3M-$30M ARR, growth inflection, path to profitability |
| **PE Lower-Middle Market** | Financials, quality of earnings, margins, working capital | $10M-$75M revenue, control deals, established businesses |
| **PE Middle Market** | Operational complexity, platform strategy, leverage | $75M-$250M revenue, scaled businesses, buy-and-build |
| **PE Large Buyout** | Capital structure, integration, regulatory, institutional ops | $250M+ revenue, institutional-grade, platform investments |

Pick the closest fit. You can customize every question, weight, and buy box criterion.

---

## Skills Reference

### Setup

**`/dealflow-setup`** --- Build your diligence config: rubric, buy box, preferences. Run once.

**`/dealflow-firmstyle`** --- Capture your firm's voice, templates, term preferences, and visual identity from sample IC memos, models, term sheets, and marketing materials. Every memo- and document-producing skill reads this profile, so outputs feel like your firm's work.

### Front Door

**`/dealflow-prescreen`** --- Prescreen memo + simple model from minimal inputs (deck, CIM, or just a description). The natural front door to a new deal. Outputs Markdown + PDF memo and Excel model.

**`/dealflow-deskresearch`** --- Pull industry reports, news, competitor analysis, public filings. Configurable focus, source budget (10/50/100), and stealth mode. Outputs structured Markdown + PDF report with full citations.

### Diligence

**`/dealflow-dataroom`** --- Reads a folder of deal documents and produces a structured assessment against your rubric. Inventories the room, flags gaps, reads by priority, delivers findings with strength/concern flags. Now builds the persistent deal index used by other skills.

**`/dealflow-model`** --- Reads an Excel model (.xlsx) and produces a business-intelligence review. Maps the business, traces key drivers, tests assumptions, surfaces inflection points and hidden risks.

**`/dealflow-questions`** --- Prioritized diligence question list from data room findings, model assumptions, and rubric. Categorized, deduped, with the "why" attached to every question.

**`/dealflow-superanalyst`** --- Three modes: **create** (raw data → proposed analyses → auditable Excel), **enhance** (extend existing analysis), **review** (audit existing analysis for correctness and completeness).

**`/dealflow-cohort`** --- Specialized SaaS/recurring-revenue cohort analysis: cohort retention curves, NRR/GRR, expansion vs. contraction, customer concentration. Templated, runs the playbook.

**`/dealflow-vp-review`** --- Detailed scrub of memos, models, and analyses for correctness and completeness. Math errors, broken citations, inconsistent claims, missing sections, plus reasonableness check on model assumptions and cases. Not a judgement call on the deal.

**`/dealflow-pre-ic`** --- Everything VP review does plus thoroughness of analysis, deeper model pressure-testing (independent base case re-grade, real-downside construction), devil's advocate, and top-10 IC question prep.

### Execution

**`/dealflow-process`** --- Lay out the full deal process: phases from LOI through close, scope third-party work (QoE, legal, IT/cyber, etc.), build a workstream tracker. Stateful — re-runs update status.

**`/dealflow-checklist`** --- Lightweight state-of-the-deal snapshot. What's done, open, blocked. Reads state and index. Cheap, runs in seconds, designed for daily use.

**`/dealflow-returns`** --- Standalone returns model with full sensitivities (entry, exit, growth, leverage, hold). Decoupled from the operating model so you can iterate on deal structure without touching the ops build.

**`/dealflow-termsheet`** --- Analyze cap table + charter/LLC agreement, build pro forma cap table with waterfall, draft term sheet aligned with firm preferences. **Counsel must review before use.**

---

## Customizing Your Rubric

The rubric is the backbone of every assessment. It determines what gets prioritized, what gets flagged, and what questions get generated. See the [Rubric Customization Guide](docs/rubric-guide.md) for details on:

- Adding and removing categories
- Adjusting weights (high / medium / low)
- Writing effective rubric questions
- Maintaining multiple configs for different investment approaches

---

## Default Configs

The five built-in templates are designed to reflect how different types of investors actually think about diligence:

- **Venture Capital** weights team, market, and product-market fit. Expects a lighter data room --- pitch deck, cap table, basic financials. Questions focus on market validation, team capability, and product roadmap.

- **Growth Equity** blends financial rigor with growth-stage metrics --- unit economics depth, channel attribution, margin expansion trajectory. Questions validate both the financial story and the growth thesis.

- **PE Lower-Middle Market** weights financials and quality of earnings heavily. Expects a full data room with tax returns, customer contracts, and QoE-ready materials. Questions are oriented toward accounting detail and contract review.

- **PE Middle Market** adds operational complexity, platform strategy, and leverage. Expects institutional-quality data rooms with management presentations, integration plans, and detailed segment reporting. Questions cover M&A track record, systems infrastructure, and capital structure.

- **PE Large Buyout** is built for institutional-scale deals. Full regulatory, ESG, and compliance categories alongside capital structure and integration planning. Questions address leverage scenarios, platform synergies, and governance at scale.

The templates are starting points. Every investor's process is different --- customize them to match yours.

---

## Roadmap

Dealflow v2 covers the full deal lifecycle from prescreen through term sheet. The next layer of work focuses on **sourcing** (industry deep dives, company screening, pipeline tracking) and **post-deal** (180-day plans, board prep, portfolio monitoring) — each as its own future release.

For internals: every deal builds a persistent index in `<deal-folder>/.dealflow/` so skills compose cleanly and don't re-read files unnecessarily. The firm-style profile in `~/.claude/dealflow/firm-style.yaml` shapes voice and visual identity across every output, layered on top of the baseline writing rules in `docs/report-style-guide.md` (IC-ready: plain language, defined abbreviations, bullets over dense paragraphs, no AI-artifact phrasing).

---

## About

Built by [Brian Wade](https://github.com/bwadecodes). Background across PE, growth equity, and VC --- now investing independently out of Primario Holdings.

This started as a set of personal tools for running diligence faster without sacrificing depth. If you find a bug, have an idea, or just want to say "this didn't work on my deal" --- [open an issue](https://github.com/bwadecodes/dealflow/issues). Your AI agent can do it too.

## License

[MIT](LICENSE)
