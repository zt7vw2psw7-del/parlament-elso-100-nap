---
name: workplace-setup
description: Checks and sets up a coding agent workspace on macOS, Linux or Windows. Runs a read-only scan first, fixes gaps in dependency order, and establishes reporting and git workflows.
---

# workplace-setup

A starting point that works for most people on most setups. It holds no personal accounts, hosts or keys. Everything specific to you lives in one file you fill in: `config.md` (copy it from `config.example.md`). Read that file first on every run; where it is empty, use the defaults below.

## Wizard — scan first, then fix only the gaps (START HERE)

1. **Scan (read-only, always first).**
   ```bash
   # run from this skill's own folder (default: ~/.agents/skills/workplace-setup)
   # macOS / Linux / WSL / Git Bash
   bash scripts/scan.sh
   # Windows PowerShell
   powershell -ExecutionPolicy Bypass -File scripts\scan.ps1
   ```
   Each row is `✓` present · `!` present but needs attention · `✗` missing, with the fix next to it.

2. **Fix each ✗ / ! in dependency order:** package manager → git → Node → the agent CLI → Python → the optional tools. Propose the command, run it if the user agrees, move on. Don't install optional tools the user has no use for.

3. **Things only the user can do (logins, passwords, 2FA):** print the exact command and wait. Never type a password, token or key for them.

4. **Re-scan and report the result in one short table.**

---

## 1. Toolchain — three tiers

| Tier | Tool | Why |
|---|---|---|
| Required | git | Version control: every change is saved and reversible |
| Required | A coding agent CLI (default: Codex, codex) | The agent itself; run codex once and choose "Sign in with ChatGPT" |
| Recommended | GitHub account + gh | Private repo for your skills; gh auth login |
| Recommended | Python 3.11+ in a virtual environment | Data work without breaking the system Python |
| Recommended | Node.js LTS | Needed to install the agent CLI via npm |
| Optional | pandoc | Convert Markdown ↔ Word ↔ HTML ↔ LaTeX |
| Optional | poppler (pdftoppm, pdfinfo) | Turn PDF pages into images so the agent can look at them |
| Optional | ImageMagick (magick) | Resize and convert images |
| Optional | LibreOffice (soffice) | Word/Excel → PDF without Office |
| Optional | Ollama | Run open-weight models locally; text never leaves the machine |

### Install commands by platform (use the package manager that is already there)

| Tool | macOS (Homebrew) | Linux (Debian/Ubuntu) | Windows (winget) |
|---|---|---|---|
| package manager | brew.sh | built in (apt) | built in (winget) |
| git | `brew install git` | `sudo apt install git` | `winget install Git.Git` |
| Node | `brew install node` | `sudo apt install nodejs npm` | `winget install OpenJS.NodeJS.LTS` |
| Codex CLI | `brew install --cask codex`<br>or `npm install -g @openai/codex` | `npm install -g @openai/codex` | same |
| gh | `brew install gh` | `sudo apt install gh` | `winget install GitHub.cli` |
| Python | `brew install python` | `sudo apt install python3 python3-venv` | `winget install Python.Python.3.12` |
| pandoc | `brew install pandoc` | `sudo apt install pandoc` | `winget install JohnMacFarlane.Pandoc` |
| poppler | `brew install poppler` | `sudo apt install poppler-utils` | `winget install oschwartz10612.Poppler` |
| ImageMagick | `brew install imagemagick` | `sudo apt install imagemagick` | `winget install ImageMagick.ImageMagick` |
| LibreOffice | `brew install --cask libreoffice` | `sudo apt install libreoffice` | `winget install TheDocumentFoundation.LibreOffice` |
| Ollama | `brew install ollama` | see ollama.com/download | `winget install Ollama.Ollama` |

Package names change; if one fails, search the package manager (`brew search`, `apt search`, `winget search`) rather than guessing. Check the agent's own docs for the currently recommended installer.

### Python — one virtual environment per project, never pip install into the system Python

```bash
python3 -m venv .venv && source .venv/bin/activate # macOS / Linux
py -m venv .venv; .venv\Scripts\Activate.ps1       # Windows
pip install pandas matplotlib openpyxl             # what the project needs
```

Several Pythons on one machine is normal. Check which one runs: `python3 --version` and `which python3` (`where python` on Windows).

---

## 2. How the agent reports back (house rules)

These apply in every session once this skill is loaded. Adjust them in `config.md`.

1. **Outcome first.** Open with one or two sentences: what happened and what it means.
2. **Number every choice (1. 2. 3.)** so the user can reply with a digit. Use letters (A, B, C) for section labels, never digits, so a reply of "2" is never ambiguous.
3. **One question at a time.** Never a list of ten questions.
4. **Explain the jargon once, inline:** git push (= upload your saved changes to GitHub). Keep the term; add the gloss.
5. **No needless pauses.** In a multi-step setup, propose the sensible default and proceed; stop only for things that are destructive, cost money, or need the user's credentials.
6. **Short and scannable.** Tables small enough to fit a terminal (about 4 columns); no walls of text.
7. **Link what changed.** If the result is visible somewhere (a page, a file, a document), give the link or path.
8. **Say what's verified and what isn't.** "Done and checked" vs "done, not tested", never a hedge that hides which.
9. **End with what's next:** either "working, ETA …", "done here", or numbered decisions for the user.

---

## 3. Your skills live in git (so they follow you)

Skills are folders under `~/.agents/skills/<name>/SKILL.md` (set another folder in `config.md` if your agent reads skills elsewhere). Put that folder under version control and push it to a private GitHub repo, so a second machine, a reinstall, or a colleague gets the same setup with one clone.

```bash
cd ~/.agents/skills
git init && git add -A && git commit -m "My skills"
gh repo create my-agent-skills --private --source . --push

# on another machine:
git clone https://github.com/<you>/my-agent-skills ~/.agents/skills
```

- Commit after each skill edit, with a message saying what changed and why. Push the same day.
- `git pull` when you start work on a machine; `git push` when you stop.
- Never put secrets in this repo (see §6). Add a `.gitignore` with `.env*`, `*.pem`, `*.key`, `*credentials*.json`.
- Do not sync the skills folder (or a git repo) with Dropbox/OneDrive/iCloud: sync clients and git fight over the same files. Git is the sync.

---

## 4. Moving work to another machine

Conversations are stored per machine and do not travel. What travels is the work:

1. **On machine A:** commit and push the project, and write a two-line note of where things stand and the next step (in the project's README or its skill).
2. **On machine B:** `git pull`, open the agent in the project, point it at the note.

---

## 5. Where output goes, and how it is named

- Deliverables (PDF, Word, figures, exports) go to the output folder in `config.md` (default: `~/Documents/agent-output/`). Tell the user the full path.
- Version the filename, version last: `<name>_<YYYYMMDD>_v<N>.<ext>` → `report_20261005_v2.pdf`. Never overwrite v1 with v2.
- Scratch files go in a temporary folder, not the output folder.
- Code lives in a git repo in a normal folder (e.g. `~/code/<project>`), not in a cloud-sync folder.

---

## 6. Secrets

- API keys, passwords and tokens never go into chat, skills, commits or filenames.
- Keep them in a password manager, and hand them to programs through environment variables (`export MY_API_KEY=…` in your shell profile, or a `.env` file that git ignores).
- If a key was ever pasted into a chat or committed, treat it as leaked: revoke it and make a new one.
- The agent should refer to a key by its variable name (`$MY_API_KEY`), never print its value.

---

## 7. Look at the output (render toolkit)

The agent cannot judge a PDF or a chart it has not seen. After producing one, render it and look:

```bash
pdftoppm -png -r 100 out.pdf page              # PDF → page-1.png, page-2.png …
pandoc in.md -o out.docx                       # Markdown → Word
soffice --headless --convert-to pdf in.docx    # Word → PDF
magick in.png -resize 1200x out.jpg            # resize an image
```

HTML → PDF/PNG: any Chromium browser in headless mode, e.g.:
`chrome --headless=new --print-to-pdf=out.pdf file:///full/path/in.html`
(the binary is `google-chrome` on Linux, `"C:\Program Files\Google\Chrome\Application\chrome.exe"` on Windows, `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` on macOS; Edge works the same).

A build that exits without error can still be visually wrong. Check page count, then look at the pages.

---

## 8. Long runs (hours, overnight)

1. Put the script and its log in a normal project folder, not in `/tmp` (temporary folders can be cleaned while the job runs).
2. Make it resumable: write results as you go and skip what is already done on restart.
3. Retry network calls a few times with a pause; one failed request should not kill the run.
4. Keep the machine awake:
   - macOS: `caffeinate -ims <command>` (a closed laptop lid still sleeps)
   - Linux: `systemd-inhibit <command>`
   - Windows: Settings → Power → Sleep = Never while it runs (or `powercfg /change standby-timeout-ac 0`)
5. Jobs that must survive a closed laptop belong on a server or a cloud machine, not on the laptop.

---

## 9. Local models (optional)

For text that must not leave the machine, run an open-weight model with Ollama: `ollama pull <model>` then `ollama run <model>`. Rule of thumb: the model file must fit in RAM with room to spare (8 GB → small models of a few billion parameters; 16 GB → up to roughly 8–14B, quantised). Ollama serves an OpenAI-style API on `http://localhost:11434`, so scripts can switch between a hosted and a local model by changing one address.

Example: Qwen3.5. Tags on Ollama: `qwen3.5:4b` (3.4 GB file, fine on 8 GB RAM) · `qwen3.5:9b` (6.6 GB, 16 GB RAM) · larger ones need 32 GB and up. `ollama pull qwen3.5:4b`, then `ollama run qwen3.5:4b "…"`.

**The agent on a local model.** Ollama's default context is 4,096 tokens; an agent needs far more, so start the server with `OLLAMA_CONTEXT_LENGTH=65536 ollama serve`, then run `codex --oss --local-provider ollama -m <model>`. Tested September 28, 2026: `qwen3.5:4b` could not drive the agent's tools reliably, and a 20B model did not fit a 16 GB laptop with a 64k context. On such a machine, use the local model for text tasks (`ollama run`) and the hosted agent for setup work. Record the exact tag and the date you pulled it in `config.md`: a named, pinned model is part of the method.

---

## 10. Connectors (MCP)

Connectors let the agent use other apps (Google Drive, Slack, a browser, GitHub). To check: ask the agent which tools it has in this session, or run `codex mcp list` in the terminal. Add only the ones you need; each one is another place your data goes.

### Output format of a scan report

```
WORKSPACE — <machine> · <OS>
| Tier | ✓ | ! | ✗ |
|---|---|---|---|
| Required | 2 | 0 | 0 |
| Recommended | 2 | 1 | 1 |
| Optional | 3 | 0 | 2 |
Needs you: gh auth login
```

---

## What NOT to do

- Don't install everything "just in case": ask what the user works on first.
- Don't use `sudo pip install` or change the system Python.
- Don't enter passwords, tokens or payment details for the user.
- Don't store anything personal in this skill file; it goes in `config.md`.
