---
name: dd-setup
description: Set up your diligence configuration — choose a starting template and customize your rubric, buy box, and preferences. Run this before your first data room review.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - AskUserQuestion
---

# Diligence Setup

Configure your diligence preferences. This builds a config file that all other `/dd-*` skills use to tailor their analysis to your investment approach.

## Prerequisites

Check if a config already exists:

```
Glob ~/.claude/dealflow/diligence-config.yaml
```

If it exists, read it and ask: *"You already have a config file. Want to update it or start fresh?"*

## Workflow

### Step 1: Choose a starting template

Present the five options:

> **Which template fits your investment approach?**
>
> 1. **Venture Capital** — team and market focused, lighter data room expectations, burn and runway emphasis (pre-revenue to $5M ARR)
> 2. **Growth Equity** — blends PE-style financial rigor with growth-stage metrics (unit economics, CAC/LTV, channel attribution) ($3M-$30M ARR)
> 3. **PE Lower-Middle Market** — financials-heavy, quality of earnings emphasis ($10M-$75M revenue)
> 4. **PE Middle Market** — operational complexity, platform strategy, leverage ($75M-$250M revenue)
> 5. **PE Large Buyout** — institutional-grade operations, capital structure, regulatory, integration ($250M+ revenue)
>
> Pick one as a starting point — you can customize everything in the next steps.

Use `AskUserQuestion` to get the selection.

### Step 2: Load the template

Based on the selection, read the corresponding default config using `Read`:

- Venture Capital: `config/defaults/venture-capital.yaml` (relative to the dealflow plugin directory)
- Growth Equity: `config/defaults/growth-equity.yaml`
- PE Lower-Middle Market: `config/defaults/pe-lower-middle-market.yaml`
- PE Middle Market: `config/defaults/pe-middle-market.yaml`
- PE Large Buyout: `config/defaults/pe-large-buyout.yaml`

Locate the plugin directory by searching for the config files:
```
Glob **/dealflow/config/defaults/pe-lower-middle-market.yaml
```

### Step 3: Walk through each section

For each rubric category in the loaded template:

1. Show the category name, weight, and questions
2. Ask: *"Keep as-is, adjust, or skip this category?"*
3. If they want to adjust — let them change the weight, add/remove questions, or rename the category
4. If they want to add a new category not in the template, add it

Use `AskUserQuestion` for each decision point. Keep the conversation moving — don't over-explain. Most users will accept defaults with minor tweaks.

### Step 4: Buy box configuration

Show the buy box section and ask the user to confirm or customize:

> **Your buy box criteria:**
>
> (show each field with its default value)
>
> *Update any of these, or hit enter to keep the defaults.*

### Step 5: Preferences

Show preferences and confirm:

> **Report preferences:**
> - Output directory: `dd-reports` (relative to deal folder, or an absolute path like `~/Dropbox/Reports`)
> - Report format: `both` (saves markdown + styled HTML for sharing), `markdown`, or `html`
> - Detail level: `deep` (full analysis) or `executive` (shorter)
> - Auto-save reports: yes
>
> *Any changes?*

### Step 6: Save the config

Save to `~/.claude/dealflow/diligence-config.yaml`:

```bash
mkdir -p ~/.claude/dealflow
```

Then use `Write` to save the final YAML config.

Confirm: *"Config saved to ~/.claude/dealflow/diligence-config.yaml. You're ready to run /dd-dataroom or /dd-model on your next deal."*

## Error Handling

| Scenario | Response |
|----------|----------|
| Config directory doesn't exist | Create it silently with `mkdir -p` |
| User gives ambiguous input | Ask a clarifying follow-up — don't guess |
| User wants to see an example | Show the relevant section from the template they chose |