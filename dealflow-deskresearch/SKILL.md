---
name: dealflow-deskresearch
description: Pull industry reports, news, competitor analysis, public filings, and other market context on a target company or industry. Outputs a structured research report in Markdown and PDF.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - WebSearch
  - WebFetch
  - Agent
  - AskUserQuestion
---

# Desk Research

Pull industry and company context from the web. Configurable by focus area, source depth, and stealth mode. Outputs Markdown + PDF with full source citations.

## Invocation

```
/dealflow-deskresearch "<company or industry>"
/dealflow-deskresearch "<company>" --deal-folder <path>
```

If a deal folder is given, write outputs to `<deal-folder>/reports/` and update the deal index. If not, write to the current directory.

## Prerequisites

### 1. Confirm Python deps

```bash
python3 -c "import yaml" 2>/dev/null || pip install pyyaml --quiet
```

### 2. Resolve deal folder (optional)

If `--deal-folder` is provided, init state and index lazily:

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" init "<deal-folder>"
python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" init "<deal-folder>"
```

Where `$DEALFLOW_ROOT` is the dealflow plugin directory.

## Phase 1 — Preamble dialog

Use `AskUserQuestion` to ask, in this order:

### Question 1: Focus

"What's the focus of this research?" Options:
- Market sizing
- Competitive landscape
- Customer signals (reviews, social, sentiment)
- Regulatory backdrop
- Hiring and team signals
- Recent news and events
- Everything (broad scan)
- Other (let me describe)

Allow multi-select.

### Question 2: Depth

"How many sources should I pull?" Options:
- 10 sources (quick scan, ~15 min)
- 50 sources (standard, ~45 min)
- 100 sources (deep dive, ~90 min)
- Custom number

### Question 3: Specific sources

"Are there specific sources I should prioritize, avoid, or include?" Free-text. Examples to give the user:
- "Include this industry report: <URL>"
- "Prioritize Crunchbase over PitchBook"
- "Skip Reddit and Twitter"
- "Include these competitor URLs: ..."

### Question 4: Stealth mode

"Should I include the target company by name in web queries, or stay industry-only?" Options:
- Include company name (normal mode)
- Industry-only (stealth mode — won't query the target's own brand)

### Confirm plan

Summarize:
- Focus areas chosen
- Source budget
- Specific sources to include / avoid
- Stealth mode setting

Ask: "Look right? Proceed?"

## Phase 2 — Research execution

Spawn 3 parallel subagents to cover the focus areas. Each subagent gets:
- The focus area(s) assigned to it
- Its share of the source budget
- The specific sources to include/avoid
- Stealth mode setting
- Tool access: WebSearch, WebFetch, Read

### Subagent task templates

**Market context subagent:**
- Industry size, growth rate, structure
- Trends shaping the next 3–5 years
- Regulatory environment
- Sources to pull: industry trade press, analyst summaries, public filings (SEC EDGAR for public comparables), trade associations, USPTO for patent activity

**Competitive landscape subagent:**
- Direct competitors and adjacent players
- Recent funding rounds and M&A in the space
- Positioning differences
- Product comparison where public info allows
- Sources: Crunchbase summaries, press releases, company websites, product pages

**Customer / hiring / news subagent:**
- Customer review themes (G2, Capterra, Trustpilot, app stores)
- Recent material news (last 12 months default — funding, leadership changes, lawsuits, regulatory actions)
- Hiring signals (job postings count, what they're hiring, where, tech stack hints)
- Sources: review sites, news search, LinkedIn-adjacent public data

Each subagent returns: structured findings + every claim with a source URL.

### MCP detection

Before launching subagents, check what MCP servers are available in the user's Claude Code environment (e.g., CRM tools, research databases, hiring data MCPs). If relevant MCPs are connected, ask the user: "I see you have [MCP name] connected. Want me to use it for [relevant focus area]?"

Do not assume any specific MCPs are available — the user adds their own.

## Phase 3 — Synthesis

Main agent synthesizes the subagent outputs into a single report. Structure:

1. **Executive snapshot** — 5 bullets on the most important findings
2. **Market context** — size, growth, structure, key trends, regulatory backdrop
3. **Competitive landscape** — direct + adjacent, recent funding/M&A, positioning
4. **Customer signals** — review themes, sentiment, social signals
5. **News and events** — chronological, last 12 months
6. **Hiring signals** — what/where/pace
7. **What this means for the deal** — 3–5 bullets connecting findings back to the investment thesis (only if a deal folder was provided)
8. **Sources appendix** — every URL cited, tiered:
   - **Tier 1**: filings, primary documents, company sources
   - **Tier 2**: industry reports, reputable trade press
   - **Tier 3**: blogs, Reddit, social

Every factual claim in the body must have a numbered citation `[12]` pointing to the appendix. No uncited claims.

## Phase 4 — Output

Determine output location:

- If `--deal-folder` was provided: `<deal-folder>/reports/desk-research-<topic>-YYYY-MM-DD.md`
- Otherwise: `./desk-research-<topic>-YYYY-MM-DD.md`

Save the Markdown. Render to PDF:

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-pdf.py" \
  "<output>.md" "<output>.pdf" --title "Desk Research — <topic>"
```

If the PDF step reports `ERROR — no renderer found`, tell the user: *"Markdown saved. To enable PDF output, install pandoc (https://pandoc.org/installing.html) or run: pip install weasyprint markdown"*

If a deal folder was provided, update state and index:

```bash
python3 "$DEALFLOW_ROOT/scripts/dealflow-state.py" add-skill-run "<deal-folder>" \
  --skill dealflow-deskresearch --report "reports/desk-research-<topic>-YYYY-MM-DD.md"

python3 "$DEALFLOW_ROOT/scripts/dealflow-index.py" add "<deal-folder>" \
  --path "reports/desk-research-<topic>-YYYY-MM-DD.md" \
  --category research --type md --indexed-by dealflow-deskresearch \
  --summary "Desk research on <topic>: <one-line takeaway>" \
  --tags "market,competition,desk-research"
```

## Phase 5 — Interactive

Tell the user: *"Research saved to [path]. Ask follow-up questions or refine — 'pull more on competitor X', 'dig into regulatory risk in <state>', 'find me 5 more customer reviews', etc."*

## Error handling

| Scenario | Response |
|---|---|
| No internet access | "I can't reach the web in this environment. WebSearch and WebFetch aren't responding. Check your Claude Code network settings." |
| Source quota exhausted | "Hit the source budget. Want me to keep going or wrap up with what I have?" |
| Specific URL fails to fetch | Note in the report and continue. Don't abort the whole run. |
| Stealth mode requested but user later names the company in follow-up | Re-confirm: "You're in stealth mode — should I use the company name now, or stay industry-only?" |
