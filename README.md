# Wordle Friend Bot
A bot to play wordle daily, then text it's results to you

### Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Usage](#usage)
- [Docs](#docs)
 
## Overview (currently a work in progress)

[x] play wordle with playwright 
[] text reults to given phone number (via provider's email to SMS gateway)
[] add tailored message/taunting to wordle message daily via chatgpt prompt/api
[] improve wordle algorithm/logic

## Prerequisites

You will need to following:
- **Git**: To clone the repository.
- **Python**: Ensure you have python installed, and your version is >= the version specified in the uv.lock file.
- **uv**: A package manager for virtual environments.

## Setup

Follow the steps below to set up a Python environment using `uv` and play wordle

### 1. Clone the Repository & check out dev branch

Clone the repository to your local machine using Git:

```bash
git clone https://github.com/davidsrrose/wordle-bot.git
```
```bash
git fetch
```
```bash
git checkout dev
```
### 2. Set up environment

Set up virtual env with uv
```bash
uv sync
```

## Usage
### Run program and watch it play wordle
```bash
uv run src/main.py
```