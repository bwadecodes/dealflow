# Cost Guide for the CFO

This document breaks down what Dealflow costs to run, how pricing works, and what to expect on your monthly invoice. You can forward this page directly to finance.

---

## What You're Paying For (One-Page Summary)

Dealflow runs on [Anthropic's API](https://www.anthropic.com/api), which charges per token — the unit of text that goes into and comes out of the AI model. You pay for the document content sent in (input tokens) and the analysis produced (output tokens). There are no per-seat software licenses, no annual contracts for the tool itself, and no hidden platform fees. The tool is open-source and free. You pay Anthropic for the AI processing.

**What costs money:**
- Input tokens — document content sent to the API for analysis
- Output tokens — the reports, findings, and analysis the model produces

**What does NOT cost money:**
- Installing Dealflow (open-source, MIT license)
- Running the configuration wizard (`/dd-setup`)
- The reports themselves — they're saved as local files on your machine
- Re-reading reports or asking follow-up questions about content already in context

---

## API Pricing (Current as of March 2026)

Anthropic charges per million tokens. A token is roughly ¾ of a word — a typical 10-page PDF is about 5,000–6,000 tokens.

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Best For |
|-------|----------------------|------------------------|----------|
| **Claude Opus 4.6** | $5.00 | $25.00 | Deepest analysis, complex financial models |
| **Claude Sonnet 4.6** | $3.00 | $15.00 | Strong analysis at lower cost |
| **Claude Haiku 4.5** | $1.00 | $5.00 | Simple triage and categorization |

Most Dealflow users run on **Opus** (highest quality) or **Sonnet** (best value). The estimates below use Opus pricing as the ceiling.

Source: [Anthropic Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

---

## Cost Per Document Type

Not all documents cost the same. A 2-page certificate costs a fraction of a 50-page CIM. Here's what each type costs to process through a full data room assessment:

### PDFs

| Document Size | Example | Pages | Tokens | Cost per Doc |
|--------------|---------|-------|--------|-------------|
| Short | Certificates, cap table summaries, one-pagers | 1–5 | ~1,500 | **$0.01** |
| Medium | Quarterly financials, board decks, audit reports | 5–20 | ~6,000 | **$0.04** |
| Long | CIM, full legal agreements, QoE reports | 20–50+ | ~25,000 | **$0.13** |

PDFs are extracted as text via pymupdf. Scanned PDFs with charts or images are also read visually, which adds ~1,500 tokens per page of visual content.

### Excel Files

| Document Size | Example | Tabs | Tokens | Cost per Doc |
|--------------|---------|------|--------|-------------|
| Small | Simple reports, single-tab summaries | 1–3 | ~2,000 | **$0.02** |
| Medium | Budgets, revenue breakdowns, customer analyses | 5–10 | ~10,000 | **$0.06** |
| Large | Full financial models, detailed operating builds | 15+ | ~35,000 | **$0.18** |
| Model (via `/dd-model`) | The primary financial model — read twice (formulas + values) | 15+ | ~70,000 | **$0.37** |

The financial model review (`/dd-model`) reads the workbook twice — once for formulas to understand the model structure and once for computed values to see the actual numbers. This doubles the input tokens for that specific file.

### Word Documents

| Document Size | Example | Pages | Tokens | Cost per Doc |
|--------------|---------|-------|--------|-------------|
| Short | Memos, policies, employment agreements | 1–5 | ~2,000 | **$0.02** |
| Medium | Contracts, operating agreements, NDAs | 10–20 | ~8,000 | **$0.05** |

### CSV, TXT, and Images

| Type | Example | Tokens | Cost per Doc |
|------|---------|--------|-------------|
| CSV / TXT | Customer lists, data exports, cap tables | ~2,500 | **$0.02** |
| Images | Org charts, product screenshots, process diagrams | ~1,500 | **$0.01** |

---

## Full Data Room Analysis — 200 Documents

A moderate-sized data room with 200 documents across the three Dealflow skills:

### Document Mix Assumed

| Type | Count | Avg Tokens | Total Tokens |
|------|-------|------------|-------------|
| PDF — short | 40 | 1,500 | 60,000 |
| PDF — medium | 35 | 6,000 | 210,000 |
| PDF — long (CIM, QoE, etc.) | 15 | 25,000 | 375,000 |
| Excel — small | 20 | 2,000 | 40,000 |
| Excel — medium | 15 | 10,000 | 150,000 |
| Excel — large | 5 | 35,000 | 175,000 |
| Word — short | 20 | 2,000 | 40,000 |
| Word — medium | 15 | 8,000 | 120,000 |
| CSV / TXT | 20 | 2,500 | 50,000 |
| Images | 15 | 1,500 | 22,500 |
| **Total** | **200** | | **1,242,500** |

Not all 200 documents are read cover-to-cover. The data room skill triages by rubric priority — roughly 80% of documents get fully read, with the remainder assessed from filenames and folder structure only.

### Cost by Skill

| Skill | What It Does | Input Tokens | Output Tokens | Cost |
|-------|-------------|-------------|---------------|------|
| `/dd-dataroom` | Full data room assessment | ~940K | ~57K | **$6.14** |
| `/dd-model` | Financial model review | ~240K | ~35K | **$2.08** |
| `/dd-questions` | Prioritized question list | ~85K | ~10K | **$0.68** |
| **Full pipeline** | **All three skills** | **~1,265K** | **~102K** | **$8.90** |

Add 3–5 follow-up questions in interactive mode: +$0.50–$1.50.

### **Total cost for a complete deal analysis: ~$9–$11**

---

## What Drives the Cost

| Factor | % of Total | Notes |
|--------|-----------|-------|
| Long PDFs (CIM, QoE, legal) — 15 docs | ~28% | 8% of documents, 28% of cost |
| Excel files (all sizes) — 40 docs | ~25% | Models and financial builds are token-heavy |
| Medium PDFs — 35 docs | ~16% | Quarterly financials, board decks |
| System overhead | ~14% | Claude Code infrastructure per API call |
| Output (reports + analysis) | ~11% | Written findings, flags, recommendations |
| Everything else (Word, CSV, images) | ~6% | Lightweight to process |

**The 20 largest documents (10% of the room) drive ~40% of the cost.** If you need to reduce spend, focus on whether every long PDF and large Excel file needs a full read, or whether some can be deprioritized.

---

## Annual Budget Scenarios

| Scenario | Deals / Year | Cost per Deal | Annual API Cost |
|----------|-------------|---------------|-----------------|
| Active screener (VC/Growth) | 50 | ~$10 | **~$500** |
| Mid-market PE fund | 25 | ~$10 | **~$250** |
| Heavy diligence flow | 100 | ~$10 | **~$1,000** |
| Light usage (model reviews only) | 30 | ~$2 | **~$60** |

These are API-only costs. Add the Anthropic subscription (see below) for the complete picture.

---

## Subscription Costs (Separate from API Usage)

Dealflow requires an Anthropic account. API token costs are the same across all tiers — the subscription fee covers access, governance, and data handling:

| Plan | Monthly Cost | Data Policy | Best For |
|------|-------------|-------------|----------|
| **Free** | $0 | Data may be used for training | Personal experimentation only |
| **Pro** | $20/user | Data may be used for training | Individual investors (non-confidential) |
| **Team — Standard** | $25/user (annual) | **Not used for training** | Investment teams without Claude Code |
| **Team — Premium** | $150/user (annual) | **Not used for training** | Investment teams using Claude Code |
| **Enterprise** | Custom | **Not used for training** + audit logs, SCIM, custom retention | Firms with compliance requirements |

**For confidential deal materials, use Team or Enterprise.** On these plans, Anthropic does not use your data for model training and provides the governance controls your compliance team expects.

See the [IT & Compliance Guide](it-compliance-guide.md) for data flow details and a template email for IT approval.

---

## Cost Optimization Options

If you need to reduce per-deal costs, Anthropic offers several levers:

| Technique | Savings | How It Works |
|-----------|---------|-------------|
| **Prompt caching** | ~10% | Repeated instructions are cached across API calls at 90% discount on input tokens |
| **Sonnet instead of Opus** | ~40% | $3/$15 vs $5/$25 per MTok — strong analysis with minor quality tradeoff |
| **Batch API** | 50% | Process deals asynchronously (not real-time) at half price |
| **Haiku for triage** | ~80% on Phase 1 | Use the cheapest model for document categorization, Opus for deep analysis |

With Sonnet + prompt caching, a full deal drops to **~$5–$6**. With Batch API, **~$4–$5**.

---

## Comparison: Dealflow vs. Traditional Diligence Costs

| | Dealflow | Junior Analyst | Third-Party Provider |
|--|---------|---------------|---------------------|
| **Cost per deal** | ~$10 | $2,000–$5,000 (40–100 hrs × $50–$75) | $15,000–$50,000+ |
| **Turnaround** | Minutes to hours | 1–3 weeks | 2–6 weeks |
| **Consistency** | Same rubric every time | Varies by analyst | Varies by provider |
| **Customization** | Your rubric, your buy box | Training required | Scope negotiation |

Dealflow does not replace deep expert diligence — it accelerates the initial assessment so your team spends time on judgment, not document processing. The cost per deal is roughly equivalent to a large coffee.

---

## Frequently Asked Questions

**How do I track what we're spending?**
Anthropic provides usage dashboards in the [API console](https://console.anthropic.com/). You can view token consumption by day, week, or month. Enterprise plans include additional usage reporting and the ability to set spending limits.

**Is there a way to set a spending cap?**
Yes. The Anthropic API console allows you to set monthly spending limits. If the limit is reached, API calls will stop until the next billing cycle or until the limit is raised.

**Do follow-up questions cost extra?**
Yes, but minimally. Each follow-up question in interactive mode costs roughly $0.10–$0.30 depending on how much document context is still loaded. The first few follow-ups are cheap because the documents are already in context.

**What if we only need the model review, not the full data room?**
Skills are independent. Running `/dd-model` alone costs ~$2 per model. You don't pay for skills you don't run.

**Does the cost scale linearly with document count?**
Roughly, yes. A 100-document room costs about half of a 200-document room. However, the system overhead (instructions, report generation) is fixed, so very small rooms have a slightly higher per-document cost.

**What happens if a run fails partway through?**
You pay for tokens already processed. If a subagent fails, the system falls back to sequential processing and continues. Partial results are not lost — they're incorporated into the final report.

**Are there volume discounts?**
Anthropic offers custom pricing on Enterprise plans for high-volume usage. Contact [Anthropic sales](https://www.anthropic.com/contact-sales) for details.

---

## Template Email for CFO / Finance Approval

---

> **Subject: Budget approval — AI diligence tool (Dealflow + Anthropic API)**
>
> Hi [Finance team],
>
> I'd like to add an AI-powered diligence tool to our workflow. Here's the cost breakdown:
>
> **What it is:** Dealflow is a free, open-source tool that reads deal data rooms and financial models, then produces structured diligence reports. It runs on Anthropic's Claude API.
>
> **Cost structure:**
> - **Anthropic subscription:** [Team at $25–$150/user/month or Enterprise — custom pricing]. This is the access fee and ensures our data is not used for AI training.
> - **API usage:** ~$9–$11 per deal for a full data room analysis (200 documents). Model-only reviews are ~$2/deal.
> - **Dealflow software:** Free (open-source, MIT license)
>
> **Projected annual spend:**
> - [X] deals/year × ~$10/deal = ~$[X] in API costs
> - [Y] users × $[Z]/month = ~$[X] in subscription costs
> - **Total: ~$[X]/year**
>
> **For context:** A junior analyst typically spends 40–100 hours on initial data room review ($2K–$5K in loaded cost). This tool produces a comparable first-pass assessment in under an hour for ~$10.
>
> **Billing:** Anthropic bills monthly via credit card or invoicing (Enterprise). Usage is tracked in their API console with configurable spending caps.
>
> **Data handling:** On Team/Enterprise plans, our deal documents are not used for model training. See the attached [IT & Compliance Guide](it-compliance-guide.md) for data flow details.
>
> Let me know if you need additional information or would like to set up a call with Anthropic's sales team.
>
> [Your name]

---

## Additional Resources

- [Anthropic API Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Anthropic API Console](https://console.anthropic.com/) (usage tracking and spending caps)
- [Anthropic Enterprise Plans](https://www.anthropic.com/enterprise)
- [IT & Compliance Guide](it-compliance-guide.md) (data flow, security, template IT approval email)
- [Rubric Customization Guide](rubric-guide.md) (adjusting what gets analyzed affects cost)
