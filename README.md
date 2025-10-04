# Code Review Projects

A collection of intelligent development tools for code analysis and interaction.

## Projects

### 🤖 [test_chatbot](./test_chatbot)
A simple, elegant chatbot web application built with Streamlit.

**Features:**
- Interactive web-based chat interface
- Adjustable temperature and token settings
- Conversation history
- Clean, modern UI

**Quick Start:**
```bash
cd test_chatbot
pip install -r requirements.txt
streamlit run app.py
```

### 🔍 [reviewer](./reviewer)
An intelligent code review tool that analyzes git diffs to detect bugs, security issues, and suggest improvements.

**Features:**
- Git diff analysis from commits/branches
- Smart code review (bugs, security, performance)
- Context-aware analysis
- Multiple output formats (Terminal, Markdown, JSON)

**Quick Start:**
```bash
cd reviewer
pip install -r requirements.txt
python review.py
```

## Setup

1. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

2. Add your API key to `.env`:
```
GROQ_API_KEY=your_api_key_here
```

## Project Structure

```
.
├── test_chatbot/          # Streamlit chatbot web app
│   ├── app.py            # Main Streamlit app
│   ├── src/              # Source code
│   ├── config/           # Configuration
│   └── README.md
│
├── reviewer/             # Code reviewer
│   ├── review.py         # Main CLI
│   ├── src/              # Source code
│   ├── config/           # Configuration
│   └── README.md
│
├── .env.example          # Environment template
└── README.md
```
