# Dealflow v2 — Design Spec

**Status:** Draft for review. Captures the v2 architecture decided during the May 2026 ideation session. Supersedes `design-spec.md` once approved.

---

## What's New in v2

v1 shipped four diligence skills (`/dd-setup`, `/dd-dataroom`, `/dd-model`, `/dd-questions`) as standalone, stateless tools. v2 expands the package to cover the full deal lifecycle — prescreen through term sheet — and introduces shared infrastructure so skills compose cleanly instead of duplicating work.

**Three structural changes:**

1. **Naming convention**: all skills move from `/dd-*` to `/dealflow-*`. Breaking change at v2.0.0.
2. **Statefulness**: each deal folder gets a `.dealflow/` directory holding a persistent index of materials and deal state. Skills read on entry, write on exit.
3. **Shared utilities**: Excel author, PDF author, and the deal index become first-class infrastructure that every skill uses.

**Net additions:**

- 11 new skills across setup, sourcing-adjacent, diligence, and execution
- Firm-style profile that captures the firm's voice, templates, and term preferences (referenced by memo-producing skills)
- Deal index that cuts token cost on multi-skill workflows by avoiding re-reads

**Net removals:**

- `/dd-memo` (dropped — replaced by skills that produce their own narrative outputs)
- Sourcing module (`/src-*`) — out of scope for v2
- Post-deal module (`/pd-*`) — out of scope for v2

---

## Naming

| Stage | Prefix | Example |
|---|---|---|
| All Dealflow skills | `/dealflow-` | `/dealflow-dataroom`, `/dealflow-pre-ic` |

Single prefix across the entire package. No sub-prefixes for stage (no `dd-`, `de-`, `src-`, `pd-`). The skill name carries the meaning.

**Migration:** v1 names hard-renamed at v2.0.0:

| v1 | v2 |
|---|---|
| `/dd-setup` | `/dealflow-setup` |
| `/dd-dataroom` | `/dealflow-dataroom` |
| `/dd-model` | `/dealflow-model` |
| `/dd-questions` | `/dealflow-questions` |

No aliases. CHANGELOG calls out the breaking change. README updated. Plugin version bumps to 2.0.0.

---

## Full Skill List (v2)

### Setup
| Skill | Purpose |
|---|---|
| `/dealflow-setup` | Rubric + buy box (existing, renamed) |
| `/dealflow-firmstyle` | Firm voice/templates/preferences/term preferences/prescreen template |

### Front Door
| Skill | Purpose |
|---|---|
| `/dealflow-prescreen` | Prescreen memo + simple model |
| `/dealflow-deskresearch` | Industry/news/competitor research, MD + PDF output |

### Diligence
| Skill | Purpose |
|---|---|
| `/dealflow-dataroom` | Data room assessment (existing, renamed) |
| `/dealflow-model` | Financial model review (existing, renamed) |
| `/dealflow-questions` | Diligence question list (existing, renamed) |
| `/dealflow-superanalyst` | Propose + execute structured Excel analysis from source data; also enhances/iterates/reviews existing analyses |
| `/dealflow-cohort` | Specialized cohort/retention/NRR for recurring revenue |
| `/dealflow-vp-review` | Correctness + completeness review of memos/models/analysis |
| `/dealflow-pre-ic` | Correctness + completeness + thoroughness + pressure-test judgement |

### Execution
| Skill | Purpose |
|---|---|
| `/dealflow-process` | Deal process plan + workstream tracker |
| `/dealflow-checklist` | Granular state-of-deal, run often |
| `/dealflow-returns` | Standalone returns model (entry/debt/hold/exit/IRR/MOIC) |
| `/dealflow-termsheet` | Cap table + charter analysis + TS draft |

---

## State + Index Architecture

The most consequential addition in v2. Each deal folder gets a `.dealflow/` directory:

```
{deal-folder}/
├── .dealflow/
│   ├── index.jsonl         # Persistent index of all materials
│   ├── deal-state.yaml     # Deal stage, skills run, key decisions
│   └── notes/              # Intermediate skill outputs (not final reports)
└── reports/                # Finalized outputs (replaces dd-reports/)
```

**`.dealflow/` should be added to `.gitignore` recommendations** in the docs — it contains extracted facts that may be sensitive.

### `index.jsonl` — the deal index

One JSON record per file (or per logical section of a file). Schema:

```json
{
  "path": "financials/2024_Q3_P&L.xlsx",
  "hash": "sha256:abc123...",
  "category": "financials",
  "type": "xlsx",
  "size_bytes": 245760,
  "last_indexed": "2026-05-28T14:30:00Z",
  "indexed_by": "dealflow-dataroom",
  "summary": "Quarterly P&L through Q3 2024; consolidated entity",
  "key_facts": [
    {"fact": "Q3 2024 revenue: $2.1M", "source_ref": "P&L!B15", "added_by": "dealflow-dataroom"},
    {"fact": "YTD gross margin: 58%", "source_ref": "P&L!B25", "added_by": "dealflow-model"}
  ],
  "sections": [
    {"sheet": "P&L", "rows": "1-50", "topic": "monthly revenue"},
    {"sheet": "P&L", "rows": "60-120", "topic": "monthly OpEx"}
  ],
  "cross_refs": {
    "mentions": ["customers/master_customer_list.csv"],
    "referenced_by": ["board/board-deck-Q3-2024.pdf"]
  },
  "tags": ["gross_margin", "revenue", "Q3_2024"]
}
```

**Operating rules:**

- **Lazy initialization**: any skill creates `.dealflow/index.jsonl` if missing. Not just `/dealflow-dataroom`.
- **Read first**: every skill queries the index before opening source files. Returns file+section pointers; skill reads only the relevant slice.
- **Write additively**: skills append `key_facts` and `tags` as they discover new information. Never delete — facts accumulate.
- **Hash check**: on read, compare file hash to indexed hash. If different, mark stale; skill chooses to use-with-warning or re-read.
- **Owner of deepest pass**: `/dealflow-dataroom` produces the most thorough initial index (every file + summary + key facts + section pointers). Other skills enrich, not rebuild.
- **Reindex**: `/dealflow-dataroom --reindex` (or a standalone `/dealflow-index` skill, TBD) rebuilds from scratch.

**Why it matters:** `/dealflow-pre-ic` doesn't re-read the data room — it queries the index. `/dealflow-vp-review` checks claims-to-evidence by lookup, not by re-parsing PDFs. Token cost on multi-skill workflows drops materially.

**Open design questions:**

- Minimum schema each writer must produce — needs to be defined so index quality stays consistent.
- Index quality ceiling — only as good as the writing skill. May want a `--deep-index` mode for `/dealflow-dataroom` for high-stakes deals.
- Search interface — start simple (tag/category filter + substring on `summary`/`key_facts`). Embeddings later if it earns its keep.

### `deal-state.yaml` — deal state

```yaml
version: 1
deal_name: "Acme Corp"
stage: "diligence"           # prescreen | diligence | ic | termsheet | closed | dead
opened: 2026-05-15
last_updated: 2026-05-28
skills_run:
  - skill: dealflow-prescreen
    timestamp: 2026-05-15T10:00:00Z
    report: reports/prescreen-2026-05-15.md
  - skill: dealflow-dataroom
    timestamp: 2026-05-22T14:30:00Z
    report: reports/dataroom-assessment-2026-05-22.md
key_decisions:
  - date: 2026-05-15
    decision: "Pursue — passes buy box on revenue and sector"
  - date: 2026-05-20
    decision: "Issued LOI at $40M pre"
workstreams:
  # Updated by /dealflow-process and /dealflow-checklist
```

Skills read on entry, update on exit. `/dealflow-checklist` becomes a pure read of state.

---

## Shared Utilities

Not user-facing skills — internal helpers every skill can call. Built once, used across the package.

### Excel author

`openpyxl`-based helper for skills that produce structured Excel output (`/dealflow-superanalyst`, `/dealflow-cohort`, `/dealflow-returns`, `/dealflow-termsheet`, `/dealflow-process`, `/dealflow-prescreen`).

**Standards every output must follow:**
- Source data preserved on its own tab, unmodified
- Calculations reference source via formulas, not hardcoded values
- "Method" or "Notes" tab explains each calculation and any assumptions
- Clear column headers, frozen panes where useful
- Auditability over cleverness — a reader should be able to trace every number

### PDF author

Markdown → PDF rendering. Pandoc is the lightest dependency; weasyprint if CSS-controlled branded output becomes important. Used by `/dealflow-deskresearch`, `/dealflow-prescreen`, `/dealflow-pre-ic`, `/dealflow-vp-review`, and any skill the user requests PDF for.

**Behavior:**
- Reads firm-style profile for branding (logo, colors, font) if configured; falls back to clean default styling.
- Always outputs MD alongside PDF (both files saved, same base name).

### Firm-style profile

`~/.claude/dealflow/firm-style.yaml`. Built by `/dealflow-firmstyle`, read by every skill that produces narrative or branded output. This is the package's most influential config — it shapes voice, structure, visual identity, and term preferences across every output.

```yaml
version: 1
firm_name: "Primario Holdings"

# ---------------- VOICE ----------------
voice:
  tone: "professional, direct, no jargon"
  hedging: "moderate"                   # assertive | moderate | hedged
  length_preference: "concise"          # concise | balanced | thorough
  perspective: "first_person_plural"    # we, our team | third_person | mixed
  reading_level: "investor"             # investor | board | lp | mixed
  common_phrases:                       # extracted from sample memos
    - "We believe..."
    - "Our diligence confirmed..."
    - "The team is well-positioned to..."
  avoid_phrases:                        # things the firm doesn't say
    - "no-brainer"
    - "slam dunk"
  hedging_words:
    use: ["appears", "indicates", "suggests"]
    avoid: ["might", "could possibly"]

# ---------------- STRUCTURE ----------------
templates:
  ic_memo:
    path: ~/.claude/dealflow/templates/ic-memo.md
    sections:
      - {name: "Executive Summary", target_length: "1 page", required: true}
      - {name: "Investment Thesis", target_length: "1-2 pages", required: true}
      - {name: "Company Overview", target_length: "1 page", required: true}
      - {name: "Market", target_length: "1-2 pages", required: true}
      - {name: "Financials", target_length: "2-3 pages", required: true}
      - {name: "Risks & Mitigants", target_length: "1 page", required: true}
      - {name: "Returns Analysis", target_length: "1 page", required: true}
      - {name: "Recommendation", target_length: "0.5 page", required: true}
    standard_exhibits:                  # exhibits expected in every memo
      - "football field valuation"
      - "returns waterfall"
      - "sensitivity table"
      - "comparable transactions"
  prescreen:
    path: ~/.claude/dealflow/templates/prescreen.md
    sections: ["snapshot", "buy_box_fit", "thesis", "anti_thesis", "valuation", "recommendation", "open_questions"]
    length_target: "1-3 pages"
    model_complexity: "simple"          # simple | medium
  termsheet:
    path: ~/.claude/dealflow/templates/termsheet.md
    style: "NVCA-derived"
  model_layout:
    path: ~/.claude/dealflow/templates/model-layout.md
    tab_order: ["Cover", "Assumptions", "Revenue", "P&L", "BS", "CF", "Returns", "Sensitivities"]
    naming_convention: "PascalCase"     # PascalCase | snake_case | Title Case

# ---------------- VISUAL / FORMATTING ----------------
brand:
  logo: ~/.claude/dealflow/assets/logo.png
  logo_placement: "top-right"           # top-left | top-right | top-center | header-band
  primary_color: "#1a3a5c"              # navy
  secondary_color: "#c9a96e"            # gold accent
  accent_color: "#7a8a99"               # muted slate for callouts
  background_color: "#ffffff"
  text_color: "#1c1c1c"
  link_color: "#1a3a5c"
  font_family_headings: "Garamond"
  font_family_body: "Inter"
  font_family_monospace: "JetBrains Mono"
  heading_weight: "semibold"
  base_font_size_pt: 11
  line_height: 1.4

formatting:
  page_size: "Letter"                   # Letter | A4
  margins_in: {top: 1.0, bottom: 1.0, left: 1.0, right: 1.0}
  header:
    enabled: true
    content: "{firm_name} — Confidential"
    show_on_first_page: false
  footer:
    enabled: true
    content: "{deal_name}  |  Page {page} of {total}"
  cover_page:
    enabled: true
    elements: ["logo", "deal_name", "date", "author", "confidentiality_marking"]
  confidentiality_marking: "STRICTLY CONFIDENTIAL — DO NOT DISTRIBUTE"
  table_style: "minimal-grid"           # minimal-grid | banded | borderless
  callout_style: "left-bar"             # left-bar | shaded-box | icon
  pull_quote_style: "italic-indent"
  chart_style:
    palette: ["#1a3a5c", "#c9a96e", "#7a8a99", "#a0a0a0"]
    grid_lines: "horizontal-only"
    show_data_labels: true
  excel_formatting:
    header_fill: "#1a3a5c"
    header_font_color: "#ffffff"
    input_cell_color: "#fffacd"         # yellow for hardcoded inputs
    formula_cell_color: "#ffffff"
    output_cell_color: "#e6f0ff"        # light blue for key outputs
    border_style: "thin"
    number_format_currency: "$#,##0;($#,##0)"
    number_format_percent: "0.0%"
    decimal_places_default: 1

template_descriptions:                  # plain-English notes on how each template should feel
  ic_memo: |
    Cover page with deal name, logo, confidentiality marking. Executive
    summary on page 2, single-page. Body sections use serif headings on
    sans-serif body. Pull quotes from management calls set in italic with
    a left bar in navy. Every numerical claim references a model tab or
    data room file in a footnote. Sensitivity tables shaded with the
    accent palette.
  prescreen: |
    Tighter and more visual than the IC memo. Lead with a snapshot table,
    followed by buy-box fit as a one-page checklist with green/yellow/red
    flags. Thesis and anti-thesis in side-by-side columns. Recommendation
    boxed with the primary color.
  termsheet: |
    Conservative legal formatting. No logo on body pages, only cover.
    Standard NVCA-style headings. Each economic term in bold followed by
    a one-sentence plain-English summary, then the formal language.

# ---------------- TERM PREFERENCES ----------------
term_preferences:
  liquidation_preference: "1x non-participating"
  anti_dilution: "broad-based weighted average"
  board_composition: "5 seats: 2 investor, 2 founder, 1 independent"
  pro_rata_rights: true
  protective_provisions: "standard NVCA set"
  drag_along: "majority of preferred + majority of common"
  rofr: true
  vesting_default: "4 years, 1 year cliff"
  option_pool_target: "10-15% post-money"

# ---------------- PRESCREEN CONFIG ----------------
prescreen_config:
  sections: ["snapshot", "buy_box_fit", "thesis", "anti_thesis", "valuation", "recommendation", "open_questions"]
  length_target: "1-3 pages"
  model_complexity: "simple"            # simple | medium
  required_exhibits: ["snapshot_table", "buy_box_checklist"]

# ---------------- REFERENCE MATERIALS ----------------
reference_materials:                    # paths to source examples the profile was built from
  ic_memos: ["~/firm-samples/memo-acme.pdf", "~/firm-samples/memo-beta.pdf"]
  models: ["~/firm-samples/model-acme.xlsx"]
  termsheets: ["~/firm-samples/ts-acme.docx"]
  marketing: ["~/firm-samples/pitchbook.pdf"]
```

**Extraction rules during `/dealflow-firmstyle`:**

- **Voice**: analyze 2+ sample memos for tone, sentence length, hedging frequency, common opening phrases per section, words the firm uses and avoids.
- **Structure**: detect repeating section headings across memos, infer required vs. optional, infer length norms per section.
- **Visual**: extract colors from logo + sample PDFs (dominant palette), detect fonts via embedded font metadata where available, infer table/chart styling from sample exhibits.
- **Formatting**: infer page size, margins, header/footer conventions, cover page elements, callout styling.
- **Template descriptions**: generate plain-English "how it should feel" notes for each template — these guide skills when the exact template can't cover every case.
- **Excel conventions**: open sample models, detect tab order, naming, color conventions for inputs/outputs/formulas, number formats.

All extracted dimensions presented to the user for confirmation before saving — nothing is silently inferred.

---

## New Skill Designs

Tight specs — full SKILL.md drafted separately when we move to implementation.

### `/dealflow-firmstyle`

**Purpose:** Capture firm voice, templates, term preferences, and prescreen config from uploaded sample materials.

**Inputs:** Folder containing sample IC memos, prescreen memos, financial models, term sheets, marketing materials.

**Workflow:**
1. Scan folder, classify each file by type
2. Extract memo structure (sections, length, depth)
3. Extract voice/tone signals (hedging frequency, sentence length, common phrases)
4. Extract standard exhibits (football field, returns waterfall, sensitivity tables)
5. Extract term preferences from past term sheets
6. Prompt user to confirm/adjust each extracted dimension
7. Save firm-style profile

**Output:** `~/.claude/dealflow/firm-style.yaml` + template files in `~/.claude/dealflow/templates/`

**Privacy:** All processing local. Files never leave the user's machine except via the Anthropic API for analysis (same path as all other skills).

---

### `/dealflow-prescreen`

**Purpose:** Produce a prescreen memo + simple model in the first 48 hours of looking at a deal.

**Inputs:** Pitch deck, CIM, or even just a verbal description + URLs. Minimal input by design.

**Workflow:**
1. Read inputs, extract company snapshot
2. Run `/dealflow-deskresearch --quick` automatically (10 sources) for market context
3. Map to buy-box rubric from `/dealflow-setup`
4. Generate prescreen memo using firmstyle template
5. Build simple 3–5 year P&L + returns scenario in Excel
6. Recommendation: pass / pursue / pursue with conditions / need more info

**Outputs:**
- `reports/prescreen-YYYY-MM-DD.md` + `.pdf`
- `reports/prescreen-model-YYYY-MM-DD.xlsx`
- Initializes `.dealflow/deal-state.yaml` and `.dealflow/index.jsonl` if absent

**Dependencies:** `/dealflow-setup` (required), `/dealflow-firmstyle` (recommended), Excel author, PDF author.

---

### `/dealflow-deskresearch`

**Purpose:** Pull industry reports, news, competitor analysis, public filings for market context.

**Preamble dialog:**
1. "What's the focus? Market sizing / competitive landscape / customer signals / regulatory / hiring / everything?"
2. "How many sources? 10 (quick scan) / 100 (deep dive) / custom number"
3. "Any specific sources to prioritize or avoid?" (e.g., "include this industry report URL", "trust Crunchbase over PitchBook", "skip Reddit")
4. "Include target company by name in queries, or industry-only (stealth mode)?"
5. Confirm plan, then execute.

**Sources tapped:**
- Web search (WebSearch + WebFetch)
- SEC EDGAR for public filings
- USPTO for patent filings
- Customer review sites (G2, Capterra, Trustpilot)
- Any data MCPs the user has connected in their Claude Code environment (e.g., CRM, research databases, hiring data) — the skill detects available MCPs and offers to use them; the user adds their own.

**Output structure:**
- Market context (size, growth, trends, regulatory)
- Competitive landscape (direct + adjacent, recent funding/M&A)
- Customer signals (review themes, social signals)
- News and events (last 12 months default)
- Hiring signals (what/where/pace)
- Sources appendix (every claim cited, tiered by source quality)

**Outputs:** `reports/desk-research-YYYY-MM-DD.md` + `.pdf`

**Dependencies:** Web access, PDF author. Optional: any user-installed data MCPs.

---

### `/dealflow-superanalyst`

**Purpose:** Three modes:
1. **Create** — look at raw data, propose interesting analyses, execute as auditable Excel
2. **Enhance** — take an existing analysis (Excel or otherwise) and extend it with additional cuts, sensitivities, visualizations, or supporting data
3. **Review** — review an existing analysis for correctness, methodology, completeness, and surface what's missing or wrong

**Invocation:**
```
/dealflow-superanalyst <data-or-analysis-path>                   # auto-detect mode based on input
/dealflow-superanalyst --create <data-path>
/dealflow-superanalyst --enhance <existing-analysis-path>
/dealflow-superanalyst --review <existing-analysis-path>
```

**Create mode workflow:**
1. Profile source data (tables, variables, distributions, completeness)
2. Propose 5–10 analyses with rationale tailored to data shape (e.g., "this looks like customer-level transactions — I'd suggest cohort retention, basket analysis, customer concentration")
3. User selects which to run (or runs all)
4. Execute analyses
5. Write auditable Excel: source data tab unmodified, calculation tabs with formulas, method/notes tab, summary tab

**Enhance mode workflow:**
1. Read existing analysis (Excel file or referenced data)
2. Understand what's been done and what data sits behind it
3. Propose extensions: additional cuts, missing sensitivities, cross-tabs not yet run, visualizations to add, supporting data to pull in
4. User selects which extensions to apply
5. Output: new version of the analysis with extensions clearly marked (new tabs labeled "Enhanced: <topic>"; existing tabs preserved untouched)

**Review mode workflow:**
1. Read existing analysis
2. Check: math/formula correctness, methodology soundness (is this the right analytical approach?), data lineage (are source pulls correct?), completeness (what's a typical reader going to ask that this doesn't answer?), reasonableness of conclusions
3. Output: line-item review with severity flags + suggested fixes/extensions; optionally feeds into enhance mode

**Outputs:**
- `reports/analysis-YYYY-MM-DD.xlsx` (create/enhance)
- `reports/analysis-review-YYYY-MM-DD.md` + `.pdf` (review)
- `reports/analysis-summary-YYYY-MM-DD.md` (narrative findings, what to look at first)
- Updates index with key findings

**Dependencies:** Excel author, deal index (writes findings back).

---

### `/dealflow-cohort`

**Purpose:** Specialized cohort/retention/NRR/GRR analysis for recurring-revenue businesses.

**Inputs:** Customer-level data (CSV or Excel) with at minimum customer ID, signup date, MRR/ARR by period.

**Outputs:**
- Cohort retention curves
- NRR/GRR by cohort
- Expansion vs contraction breakdown
- Customer concentration analysis
- `reports/cohort-analysis-YYYY-MM-DD.xlsx` + summary MD

**Why separate from super-analyst:** SaaS diligence is high-frequency and the analyses are standard enough to template directly rather than propose every time.

---

### `/dealflow-vp-review`

**Purpose:** Super in-the-weeds review of materials before they go to a senior person. Focus on **correctness + completeness**.

**Inputs:** Auto-discovers memo, model, and analysis files in the deal folder. Or pass specific files.

**Checks:**
- Math errors and formula audit (model)
- Internal consistency between memo and model (claim X in memo matches assumption Y in model)
- Citations: every claim in the memo backed by something in the index
- Standard sections present (per firmstyle template)
- Formatting, typos, units, date consistency
- Missing exhibits or analysis that the firmstyle template expects
- **Reasonableness scrub on model assumptions and cases**:
  - Are individual assumption values reasonable vs. historicals, comps, industry norms, and what the data room supports?
  - **Is the "base case" actually a base case, or is it the management case in disguise?** (Flags when base assumptions track management forecast too closely without independent grounding.)
  - **Does the "downside case" properly reflect a real downside?** (Flags when downside is a mild haircut rather than a coherent stress — e.g., a downside that still shows growth, or where only revenue moves while everything else stays bull case.)
  - Bull case sanity — is it directionally plausible or fantasy?
  - Cross-case consistency — do the case mechanics tie out (e.g., if revenue is down 20%, does S&M efficiency or hiring pace adjust?)

**Output:** `reports/vp-review-YYYY-MM-DD.md` + `.pdf` — line-item review with file/section refs, severity flag, suggested fix.

**Not in scope:** judgement on whether the deal is good. That's `/dealflow-pre-ic` and the IC itself.

---

### `/dealflow-pre-ic`

**Purpose:** Final pressure test before IC submission. Focus on **correctness + completeness + thoroughness of analysis + verify/pressure-test judgement**.

**Inputs:** Auto-discovers all deal materials.

**Checks (everything VP review does, plus):**
- Thoroughness: is the analysis deep enough for IC? Missing standard analyses for the deal type?
- **Deeper reasonableness scrub on model cases** (extends VP-level checks):
  - Re-grades base vs. management case independently — does the base case have its own logic, or is it derivative?
  - Pressure-tests the downside case: what does a true downside actually look like for this business and is the model's downside that severe? (e.g., for a SaaS business, a real downside often involves logo churn acceleration + expansion compression + sales productivity drop, not just a revenue % haircut.)
  - Tests downside coherence: do all P&L lines move in plausible directions and magnitudes together?
  - Identifies missing scenarios the IC will want to see (e.g., "no scenario models a recession year — likely a question").
- Stress test: run additional downside scenarios on the model (revenue miss 10/20/30%, margin compression, multiple compression at exit, key customer loss). Surface what breaks.
- Thesis coherence: does the analysis actually support the conclusion?
- Devil's advocate: strongest counter-argument to the recommendation
- IC question prep: top 10 questions the IC will ask that the memo doesn't currently answer

**Output:** `reports/pre-ic-review-YYYY-MM-DD.md` + `.pdf` — structured by section, severity-flagged, with suggested fixes and pre-emptive IC question answers.

**Dependencies:** Reads heavily from deal index. Needs `/dealflow-model` outputs (or runs model checks itself if absent).

---

### `/dealflow-process`

**Purpose:** Lay out the deal process, scope third-party work, create a tracker.

**Workflow:**
1. Read `deal-state.yaml` to understand stage
2. Generate process plan tailored to deal type (PE vs VC, from firmstyle/setup) — phases from LOI through close
3. Scope third-party work: QoE, legal DD, IT/cyber, insurance, environmental, market study, customer refs, background checks, tax structuring (which apply depends on deal type)
4. Build workstream tracker: workstream, owner, dates, status, dependencies
5. Update `deal-state.yaml` with workstreams

**Outputs:**
- `reports/deal-process-plan-YYYY-MM-DD.md` + `.pdf`
- `reports/deal-tracker-YYYY-MM-DD.xlsx` (Gantt-ish, updateable)

**Stateful:** subsequent runs read prior tracker, update status, surface delays.

---

### `/dealflow-checklist`

**Purpose:** Granular state-of-the-deal snapshot. Run often during active diligence.

**Inputs:** `deal-state.yaml` + `index.jsonl`.

**Output:** `reports/checklist-YYYY-MM-DD.md` — what's done, what's open, who owns it, what's blocking.

**Lightweight:** runs in seconds, low token cost. Designed for daily-standup use.

---

### `/dealflow-returns`

**Purpose:** Standalone returns model — entry, debt, hold, exit, IRR/MOIC, sensitivities.

**Inputs:** Operating model (from `/dealflow-model` or user-provided) + deal structure assumptions.

**Output:** `reports/returns-model-YYYY-MM-DD.xlsx` — returns waterfall, sensitivity tables on entry multiple, exit multiple, leverage, growth.

**Why separate from operating model:** swap in different deal structures without touching the operating model.

---

### `/dealflow-termsheet`

**Purpose:** Analyze cap table + charter/LLC agreement, draft TS aligned with firm preferences.

**Workflow:**
1. Read cap table, identify existing preferences, build pro forma with new round
2. Read charter/LLC agreement, extract key terms (liquidation, anti-dilution, voting, board, protective provisions, ROFR, drag/tag)
3. Build waterfall at multiple exit values
4. Draft TS using firmstyle term preferences + NVCA-style starting template
5. Output: cap table analysis MD, pro forma cap table Excel, TS draft Word/MD

**Outputs:**
- `reports/cap-table-analysis-YYYY-MM-DD.md`
- `reports/pro-forma-cap-table-YYYY-MM-DD.xlsx`
- `reports/term-sheet-draft-YYYY-MM-DD.md` + `.docx`

**Strong disclaimers:** draft for counsel review, not legal advice. Disclaimer printed in every output file, not just chat.

**Dependencies:** `/dealflow-firmstyle` strongly recommended — without it, TS draft is generic.

---

## Build Order

1. **Deal-state + index infrastructure** — foundational; everything benefits
2. **`/dealflow-firmstyle`** — unlocks prescreen, vp-review, pre-ic, termsheet
3. **Excel author + PDF author utilities** — needed by 5+ skills
4. **`/dealflow-deskresearch`** — introduces web access cleanly, validates PDF output
5. **`/dealflow-prescreen`** — natural front door; depends on firmstyle + deskresearch
6. **`/dealflow-vp-review`** — high leverage on daily work
7. **`/dealflow-pre-ic`** — builds on vp-review patterns
8. **`/dealflow-superanalyst`** + **`/dealflow-cohort`**
9. **`/dealflow-process`** + **`/dealflow-checklist`** — stateful PM layer
10. **`/dealflow-returns`** + **`/dealflow-termsheet`** — execution stage

Each ships independently when ready. No big-bang release.

---

## Migration (v1 → v2)

**Breaking change at v2.0.0:**

- Rename all `/dd-*` skills to `/dealflow-*`
- Rename `dd-reports/` to `reports/` (new default; users with v1 layouts continue to work — skills check both)
- Bump plugin version to `2.0.0`
- CHANGELOG entry calling out the rename
- README updated with new commands
- Existing config at `~/.claude/dealflow/diligence-config.yaml` continues to work unchanged

**Justification:** very few users today, naming consistency matters long-term, cleaner break than carrying aliases.

---

## Out of Scope for v2

- Sourcing module (`/src-deepdive`, `/src-screen`, `/src-pipeline`) — separate future release
- Post-deal module (`/pd-180`, `/pd-board`, `/pd-monitor`, `/pd-lp`) — separate future release
- `/dd-memo` (dropped — replaced by memo-producing logic inside prescreen, pre-ic, etc.)
- Embeddings-based index search — start with tag/substring; revisit if it earns its keep
- DOCX output (TS draft is the exception — needs DOCX for counsel)

---

## Success Criteria

v2 is working when:

1. A new user can onboard via `/dealflow-setup` + `/dealflow-firmstyle` in under 15 minutes and have outputs that look and read like their firm's work.
2. Running `/dealflow-prescreen` produces a useful first-pass memo + model with minimal input.
3. Multi-skill workflows on the same deal show **measurably lower token cost** vs. v1, thanks to the deal index.
4. `/dealflow-pre-ic` catches errors and gaps that a human reviewer would catch, plus pressure-tests the thesis in ways that surface IC questions before the IC asks them.
5. The shared utilities (Excel author, PDF author, index) work consistently across every skill — outputs feel like they're from one package, not eleven separate tools.
