"""
Constants for chatbot
"""

# Model configuration
DEFAULT_MODEL = "llama-3.2-90b-text-preview"
AVAILABLE_MODELS = [
    "llama-3.2-90b-text-preview",
    "llama-3.2-11b-text-preview",
    "llama-3.1-8b-instant",
]

# Temperature limits
MIN_TEMPERATURE = 0.0
MAX_TEMPERATURE = 2.0
DEFAULT_TEMPERATURE = 0.7

# Token limits
MIN_TOKENS = 256
MAX_TOKENS = 2048
DEFAULT_MAX_TOKENS = 1024

# UI Configuration
APP_TITLE = "AI Chatbot"
APP_ICON = "🤖"
DEFAULT_PLACEHOLDER = "Type your message here..."
