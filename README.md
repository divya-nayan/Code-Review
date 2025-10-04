# Simple Chatbot

A simple chatbot using Groq's LLaMA 3.2 API.

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

```bash
python chatbot.py
```

## Commands

- Type your message to chat
- Type `quit` to exit
- Type `reset` to clear conversation history
