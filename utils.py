"""
Utility functions for chatbot
"""

def clean_text(text):
    """Remove extra whitespace from text"""
    return " ".join(text.split())


def truncate_message(message, max_length=100):
    """Truncate message to max length"""
    if len(message) <= max_length:
        return message
    return message[:max_length] + "..."


def validate_api_key(api_key):
    """Basic API key validation"""
    if not api_key:
        return False
    if len(api_key) < 20:
        return False
    return True


def format_conversation(history):
    """Format conversation history for display"""
    formatted = []
    for msg in history:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        formatted.append(f"{role.upper()}: {content}")
    return "\n".join(formatted)
