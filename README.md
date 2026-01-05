# 🤖 Wordle Bot
Python project to play Wordle for me because I'm lazy

### Table of Contents
- [Quickstart](#quickstart)
- [Progress Overview](#progress-overview)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)

## Quickstart

Already have Python and `uv` installed? Run via:

```bash
git clone https://github.com/davidsrrose/wordle-bot.git
cd wordle-bot
uv sync
uv run playwright install
uv run src/main.py
```
## Progress Overview

- [x] Play Wordle with Playwright
- [ ] Send results to a phone number (via provider email-to-SMS gateway)?
- [ ] Add tailored message/taunting to the daily Wordle message (ChatGPT prompt/API)?
- [ ] Improve Wordle algorithm/logic
  - If corresponding with someone over SMS, always retry until you beat them?

## Prerequisites

You will need the following (install if you do not have them):

| Tool | Purpose | Install |
| --- | --- | --- |
| 🛠️ Git | Clone the repository | https://git-scm.com/downloads or `brew install git` (macOS) |
| 🐍 Python (>=3.13, see `uv.lock`) | Runtime for the bot | https://www.python.org/downloads/ or use `pyenv` |
| 🪄 uv | Manage virtual env and dependencies | `curl -Ls https://astral.sh/uv/install.sh | sh` (see https://docs.astral.sh/uv/) |

## Setup

Follow these steps to set up the environment using `uv`.

### 1. Clone the repository

```bash
git clone https://github.com/davidsrrose/wordle-bot.git
cd wordle-bot
```

### 2. Install dependencies

```bash
uv sync
uv run playwright install
```

If you're developing, install git hooks so lint/format run before commits:

```bash
uv run pre-commit install
```

## Usage

### 3. Run the program and watch it play Wordle 🎮

```bash
uv run src/main.py
```
