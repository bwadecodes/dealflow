# CLI Quickstart for Investors

You spend your days in spreadsheets and data rooms, not terminals. Here's the 5 minutes you need to get set up.

---

## What is a terminal?

A terminal (also called command line or shell) is a text-based way to talk to your computer. Instead of clicking through menus, you type commands. It looks like a black screen with a blinking cursor --- less intimidating than it sounds.

### How to open it

**Mac:**
1. Press `Cmd + Space` to open Spotlight
2. Type "Terminal" and press Enter
3. A window opens with a prompt like `yourname@computer ~ %`

**Windows:**
1. Press `Win + R`, type `cmd`, and press Enter
2. Or search "Command Prompt" in the Start menu
3. A window opens with a prompt like `C:\Users\YourName>`

For a better Windows experience, install [Windows Terminal](https://aka.ms/terminal) from the Microsoft Store --- it's free and more pleasant to use.

---

## Navigating to a folder

The terminal starts in your home directory. To work with a deal's data room, you need to navigate to that folder.

**Mac / Linux:**
```bash
cd ~/Dropbox/Deals/Acme-Corp
```

**Windows:**
```bash
cd C:\Users\YourName\Dropbox\Deals\Acme-Corp
```

`cd` stands for "change directory" --- it's how you move between folders.

**Tip:** You can drag a folder from Finder (Mac) or File Explorer (Windows) into the terminal to paste its path.

---

## What is Claude Code?

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) is a command-line tool from Anthropic that lets you work with Claude directly on your files. You type a command, Claude reads your files, does the analysis, and writes the output. Everything runs on your machine --- files are sent to Anthropic's API for processing and responses come back.

Dealflow is a set of skills (think: specialized commands) that run inside Claude Code to handle due diligence workflows.

---

## Installing Claude Code

### Step 1: Install Node.js

Claude Code requires Node.js. Check if you have it:

```bash
node --version
```

If you see a version number (like `v20.11.0`), you're set. If not, download it from [nodejs.org](https://nodejs.org/) --- use the LTS (Long Term Support) version.

### Step 2: Install Python

Dealflow uses Python to read Excel, PDF, and Word files. Check if you have it:

```bash
python3 --version
```

If you see a version number, you're set. If not, download it from [python.org](https://www.python.org/downloads/). During installation on Windows, check the box that says "Add Python to PATH."

### Step 3: Install Claude Code

```bash
npm install -g @anthropic-ai/claude-code
```

Then authenticate with your Anthropic account:

```bash
claude auth
```

This opens a browser window. Sign in, and you're connected.

### Step 4: Install Dealflow

```bash
claude install github:bwadecodes/dealflow
```

That's it. The diligence skills are now available.

---

## Running your first command

### 1. Set up your config

```
claude
```

This starts Claude Code. Then type:

```
/dd-setup
```

It will ask you a few questions about your investment approach and save your preferences. Takes about 3 minutes.

### 2. Assess a data room

Point it at a folder of deal documents:

```
/dd-dataroom ~/Dropbox/Deals/Acme-Corp/Data-Room "B2B SaaS, ~$8M ARR"
```

Replace the path with wherever your deal files are. The context string in quotes is optional but helps the analysis.

### 3. Review a financial model

```
/dd-model ~/Dropbox/Deals/Acme-Corp/Model/Acme-Model-v3.xlsx
```

### 4. Generate diligence questions

```
/dd-questions ~/Dropbox/Deals/Acme-Corp
```

Reports are saved in a `dd-reports` folder inside your deal directory.

---

## Tips

- **You don't need to memorize commands.** Type `/dd-` and Claude Code will show you the available skills.
- **You can ask follow-up questions.** After any report is generated, just type your question in the same session --- "dig deeper into the financials," "compare the P&L across years," etc.
- **Reports don't overwrite each other.** Each run is dated, so you can re-run as new documents come in.
- **If something goes wrong,** the error messages tell you what to do. Most issues are a missing Python library (the tool will tell you the install command) or a wrong file path.

---

## Need help?

- [Open an issue](https://github.com/bwadecodes/dealflow/issues) on GitHub
- Check the [IT & Compliance Guide](it-compliance-guide.md) if you need approval before installing
