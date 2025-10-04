"""
Validation utilities for chatbot
"""
from typing import Optional
from .exceptions import InvalidAPIKeyError
from .constants import MIN_TEMPERATURE, MAX_TEMPERATURE, MIN_TOKENS, MAX_TOKENS


def validate_api_key(api_key: Optional[str]) -> str:
    """
    Validate Groq API key

    Args:
        api_key: API key to validate

    Returns:
        Validated API key

    Raises:
        InvalidAPIKeyError: If API key is invalid
    """
    if not api_key:
        raise InvalidAPIKeyError(
            "GROQ_API_KEY not found. Please set it in your .env file."
        )

    if len(api_key) < 20:
        raise InvalidAPIKeyError(
            "API key appears to be invalid (too short)."
        )

    if not api_key.startswith("gsk_"):
        raise InvalidAPIKeyError(
            "API key format appears incorrect. Groq API keys should start with 'gsk_'."
        )

    return api_key


def validate_temperature(temperature: float) -> float:
    """
    Validate temperature parameter

    Args:
        temperature: Temperature value

    Returns:
        Validated temperature

    Raises:
        ValueError: If temperature is invalid
    """
    if not MIN_TEMPERATURE <= temperature <= MAX_TEMPERATURE:
        raise ValueError(
            f"Temperature must be between {MIN_TEMPERATURE} and {MAX_TEMPERATURE}"
        )
    return temperature


def validate_max_tokens(max_tokens: int) -> int:
    """
    Validate max_tokens parameter

    Args:
        max_tokens: Maximum tokens value

    Returns:
        Validated max_tokens

    Raises:
        ValueError: If max_tokens is invalid
    """
    if not MIN_TOKENS <= max_tokens <= MAX_TOKENS:
        raise ValueError(
            f"max_tokens must be between {MIN_TOKENS} and {MAX_TOKENS}"
        )
    return max_tokens


def validate_message(message: str) -> str:
    """
    Validate user message

    Args:
        message: User message

    Returns:
        Validated message

    Raises:
        ValueError: If message is invalid
    """
    if not message or not message.strip():
        raise ValueError("Message cannot be empty")

    if len(message) > 10000:
        raise ValueError("Message is too long (max 10000 characters)")

    return message.strip()
