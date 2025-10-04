# AI Chatbot (Streamlit)

A simple, elegant chatbot web application built with Streamlit and Groq's LLaMA 3.2.

## Features

- 💬 Interactive chat interface
- 🎨 Clean, modern UI
- ⚙️ Adjustable temperature and token settings
- 📝 Conversation history
- 🔄 Reset chat functionality

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file in the project root with your API key:
```
GROQ_API_KEY=your_api_key_here
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Project Structure

```
test_chatbot/
├── app.py                 # Main Streamlit application
├── src/
│   ├── __init__.py
│   └── chatbot.py        # Chatbot logic
├── config/
│   ├── __init__.py
│   └── settings.py       # Configuration settings
├── requirements.txt
└── README.md
```

## Controls

- **Temperature**: Controls randomness (0.0 = focused, 2.0 = creative)
- **Max Tokens**: Maximum length of response
- **Clear Chat**: Reset conversation history
