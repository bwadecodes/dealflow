# Rubric Customization Guide

The rubric is the backbone of every Dealflow assessment. It determines what gets prioritized in data room reviews, what the model analysis focuses on, and which diligence questions get generated.

This guide walks through how to customize it to match your investment process.

---

## Where the config lives

Your config file is stored at:

```
~/.claude/dealflow/diligence-config.yaml
```

Run `/dd-setup` to create or update it interactively. Or edit the YAML file directly --- it's human-readable and well-commented.

You can also maintain multiple configs and pass a specific one to any skill:

```
/dd-dataroom ~/Deals/Acme --config ~/configs/my-pe-config.yaml
```

---

## Config structure

The config has three sections:

```yaml
version: 1

rubric:          # What to evaluate and how to weight it
  categories: [...]

buy_box:         # Your investment criteria
  revenue_range: "..."
  ...

preferences:     # Report settings
  output_dir: "dd-reports"
  ...
```

---

## Rubric categories

Each category has three fields:

```yaml
- name: "Revenue"
  weight: high
  questions:
    - "What is the business model?"
    - "What is driving the growth rate?"
```

### Name

The label for the category. Use whatever makes sense for your process --- there's no fixed list. Common categories:

- Product / Service
- Revenue
- Gross Margin
- Quality of Earnings
- Overhead / Investments
- Balance Sheet
- Market / Competitors
- Team / Management
- Legal / IP
- Unit Economics
- Burn / Runway
- Technology / Infrastructure

### Weight

`high`, `medium`, or `low`. This affects:

- **Data room assessment:** High-weight categories are analyzed first and in more detail. Documents relevant to high-weight categories are read before others.
- **Model review:** Key drivers are mapped to rubric categories. High-weight ones get deeper assumption analysis.
- **Question generation:** Questions from high-weight categories are more likely to be tagged Critical or Important.

### Questions

The specific things you want evaluated for each category. Write these as you would actually ask them --- the tools use these to guide their analysis.

**Good questions are specific and actionable:**
- "What is the customer concentration --- top 10 as % of revenue?"
- "How has gross margin trended over the last 3 years?"
- "What does the switching cost look like for customers?"

**Avoid generic questions that don't guide the analysis:**
- "Is the product good?"
- "How is the team?"

---

## Adding a category

Add a new block to the `categories` list:

```yaml
- name: "Technology / Infrastructure"
  weight: medium
  questions:
    - "What is the tech stack? How maintainable is it?"
    - "Is there technical debt that would require investment post-close?"
    - "How does the infrastructure scale with growth?"
```

The skills will automatically include this category in their assessment.

---

## Removing a category

Delete the block from `categories`. The skills only evaluate what's in your rubric --- removing a category means that area won't be covered in assessments or questions.

---

## Adjusting weights

Change the `weight` field to shift priority:

```yaml
# Before --- treating balance sheet as high priority
- name: "Balance Sheet"
  weight: high

# After --- de-prioritizing for an asset-light SaaS fund
- name: "Balance Sheet"
  weight: low
```

This doesn't remove the category --- it just changes how much emphasis it gets in reports and questions.

---

## Template differences

The three built-in templates aren't just cosmetically different. They reflect how different investor types actually think about diligence.

### PE Lower-Middle Market

Heavy on:
- Quality of earnings (its own category)
- Gross margin analysis
- Working capital and balance sheet
- Revenue sustainability and customer concentration

Lighter on:
- Product roadmap (assumes proven product)
- Burn/runway (assumes profitable or close)

### VC Seed / Pre-Seed

Heavy on:
- Team / founders (separate from management --- founder dynamics matter)
- Market / TAM
- Product / PMF evidence
- Traction / metrics
- Burn / runway

Lighter on:
- Quality of earnings (often not applicable)
- Balance sheet detail
- Overhead analysis

### Growth Equity

Blends both:
- Full financial categories (revenue, margins, operating leverage)
- Plus growth metrics (unit economics, CAC/LTV as its own category)
- Expects more data room completeness than VC but more growth tolerance than PE

---

## Tips for building your rubric

**Start with a template.** Even if your process is unique, one of the three templates will be close. Customize from there rather than building from scratch.

**Write questions you'd actually ask.** The rubric questions guide the analysis. If you'd ask a CFO "what are the key QoE adjustments?", put that in your rubric. If you wouldn't ask it, leave it out.

**Match weights to how you make decisions.** If gross margin is the first thing you look at in every deal, it should be `high`. If legal is something you defer to counsel, it can be `low` --- the tools will still cover it, just with less emphasis.

**Keep it under 12 categories.** More than that dilutes the focus. Combine related areas (e.g., "Legal / IP / Regulatory" instead of three separate categories).

**Iterate.** Run a few assessments, see what the reports emphasize, and adjust. The rubric isn't something you set once and forget --- it should evolve as your investment process does.

---

## Multiple configs

You can maintain different configs for different contexts:

```
~/.claude/dealflow/diligence-config.yaml          # default
~/.claude/dealflow/configs/pe-buyout.yaml          # PE buyout fund
~/.claude/dealflow/configs/personal-angel.yaml     # personal angel investing
```

Pass the one you want:

```
/dd-dataroom ~/Deals/Acme --config ~/.claude/dealflow/configs/pe-buyout.yaml
```

Or just switch your default by re-running `/dd-setup`.
