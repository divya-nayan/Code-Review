# AI-Powered Code Reviewer

An intelligent code review tool that analyzes git diffs using LLM to detect bugs, security issues, and suggest improvements.

## Features

- 📊 **Git Diff Analysis** - Extracts and analyzes code changes from commits/branches
- 🤖 **Smart Code Review** - Detects bugs, security vulnerabilities, and code smells
- 🔍 **Context-Aware** - Reads related files, imports, and dependencies
- 📝 **Multiple Output Formats** - Terminal, Markdown, and JSON

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file from the example:
```bash
cp .env.example .env
```

3. Add your Groq API key to `.env`:
```
GROQ_API_KEY=your_actual_api_key
```

## Usage

Review the latest commit:
```bash
python code_reviewer.py
```

Review a specific commit:
```bash
python code_reviewer.py abc123
```

Compare two branches:
```bash
python code_reviewer.py feature-branch --base main
```

Save review to markdown:
```bash
python code_reviewer.py --format markdown --output review.md
```

Get JSON output:
```bash
python code_reviewer.py --format json --output review.json
```

Include full file context (slower but more accurate):
```bash
python code_reviewer.py --context
```

## What It Reviews

- **Bugs** - Logic errors, null pointer issues, type mismatches
- **Security** - SQL injection, XSS, hardcoded secrets
- **Performance** - Inefficient algorithms, memory leaks
- **Code Smells** - Anti-patterns, complexity issues
- **Best Practices** - Language-specific conventions
