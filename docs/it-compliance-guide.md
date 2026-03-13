# IT & Compliance Guide

This document explains what Dealflow is, how it handles data, and what your IT or compliance team needs to know before approving installation. You can forward this page directly.

---

## What It Does (One-Page Summary)

Dealflow is a set of analysis tools that run inside [Claude Code](https://docs.anthropic.com/en/docs/claude-code), Anthropic's command-line interface. It helps investors assess deal data rooms and financial models by reading documents on your machine and producing structured reports.

**What it does:**
- Reads documents from a local folder (PDFs, Excel files, Word docs)
- Sends document content to Anthropic's API for analysis
- Receives analysis results and writes reports to a local folder
- All input and output stays on the user's machine --- no third-party storage

**What it does NOT do:**
- Does not upload files to any server or cloud storage
- Does not store data beyond the API interaction
- Does not require database access or network permissions beyond HTTPS to Anthropic's API
- Does not modify source documents --- it only reads them

---

## How Data Flows

```
Your Machine                         Anthropic API
+-------------------+                 +-------------------+
|                   |   HTTPS (TLS)   |                   |
|  Local files      | --------------->|  Claude model     |
|  (data room,      |                 |  processes text   |
|   Excel models)   | <---------------|  and returns      |
|                   |   HTTPS (TLS)   |  analysis         |
|  Reports saved    |                 |                   |
|  locally          |                 |  No persistent    |
|                   |                 |  storage*         |
+-------------------+                 +-------------------+
```

1. The user runs a command pointing at a local folder or file
2. Claude Code reads the files on the user's machine
3. File contents are sent to [Anthropic's API](https://www.anthropic.com/api) over HTTPS (TLS encrypted)
4. The API processes the content and returns analysis
5. Results are written as markdown files to a local `dd-reports/` folder

**No data is stored on third-party servers beyond the API interaction itself.*

---

## Data Handling by Subscription Tier

How Anthropic handles your data depends on your subscription:

### Free and Pro Plans

- Conversations **may be used** to improve Anthropic's models
- Review [Anthropic's Privacy Policy](https://www.anthropic.com/policies/privacy) for details
- **Not recommended** for confidential deal materials

### Team and Enterprise Plans

- Data is **not used** for model training
- Additional security controls, audit logging, and admin management
- SSO integration available on Enterprise
- See [Anthropic Enterprise](https://www.anthropic.com/enterprise) for details
- **Recommended** for firms reviewing confidential deal materials

### Recommendation

Firms working with confidential deal documents, financial models, and legal agreements should use a **Team or Enterprise** plan. This ensures your data is not used for training and provides the security controls your compliance team expects.

---

## Frequently Asked Questions

**Does this tool store my documents anywhere?**
No. Documents are read from your local machine, sent to Anthropic's API for processing, and results are saved back to your machine. No copies are stored on external servers beyond the API interaction.

**Can Anthropic see my data room?**
During processing, document content is sent to Anthropic's API. On Team and Enterprise plans, this data is not used for training and is subject to Anthropic's [enterprise data handling policies](https://www.anthropic.com/enterprise). On Free/Pro plans, data may be used to improve models per the [privacy policy](https://www.anthropic.com/policies/privacy).

**Is Anthropic SOC 2 compliant?**
Visit [Anthropic's Trust Center](https://trust.anthropic.com/) for current certifications and compliance documentation.

**What network access does it need?**
HTTPS access to `api.anthropic.com`. No other network access is required. The tool does not open inbound ports or run a local server.

**What software is installed?**
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (npm package from Anthropic)
- Dealflow (Claude Code plugin --- markdown files, no executables)
- Python libraries: openpyxl (Excel), pymupdf (PDF), python-docx (Word) --- installed on first use

**Can I run this in an air-gapped environment?**
No. The tool requires internet access to communicate with Anthropic's API. All analysis is performed by Claude on Anthropic's servers --- the local machine provides the documents and saves the results.

**Can I audit what data is sent?**
Claude Code provides conversation logs. Users can review what was sent and received in each session.

---

## Template Email for IT Approval

Feel free to customize and send this to your IT team:

---

> **Subject: Approval request --- Claude Code + Dealflow plugin**
>
> Hi [IT team],
>
> I'd like to install a tool called Dealflow that helps with investment due diligence analysis. Here are the details:
>
> **What it is:** A set of analysis skills that run inside Claude Code, Anthropic's command-line tool. It reads deal documents (PDFs, Excel, Word) from my machine and produces structured assessment reports.
>
> **Data flow:** Local files -> Anthropic API (HTTPS/TLS) -> analysis returned -> reports saved locally. No data stored on third-party servers beyond the API call.
>
> **What gets installed:**
> - Claude Code: `npm install -g @anthropic-ai/claude-code` (Node.js package)
> - Dealflow plugin: `claude install github:bwadecodes/dealflow` (markdown files, no executables)
> - Python libraries: openpyxl, pymupdf, python-docx (for reading Excel/PDF/Word files)
>
> **Network access:** HTTPS to `api.anthropic.com` only.
>
> **Our Anthropic plan:** [Free / Pro / Team / Enterprise] --- [on Team/Enterprise plans, data is not used for model training].
>
> **Security references:**
> - Anthropic security: https://www.anthropic.com/security
> - Trust center: https://trust.anthropic.com/
> - Privacy policy: https://www.anthropic.com/policies/privacy
>
> Let me know if you need any additional information.
>
> [Your name]

---

## Additional Resources

- [Anthropic Security](https://www.anthropic.com/security)
- [Anthropic Trust Center](https://trust.anthropic.com/)
- [Anthropic Privacy Policy](https://www.anthropic.com/policies/privacy)
- [Anthropic Enterprise Plans](https://www.anthropic.com/enterprise)
- [Claude Code Documentation](https://docs.anthropic.com/en/docs/claude-code)
