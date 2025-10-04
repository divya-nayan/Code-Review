"""
Validation utilities
"""
import os
from typing import Optional
from ..src.exceptions import InvalidAPIKeyError


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
            "GROQ_API_KEY not found. Please set it in your .env file or environment."
        )

    if len(api_key) < 20:
        raise InvalidAPIKeyError(
            "API key appears to be invalid (too short). Please check your configuration."
        )

    if not api_key.startswith("gsk_"):
        raise InvalidAPIKeyError(
            "API key format appears incorrect. Groq API keys should start with 'gsk_'."
        )

    return api_key


def validate_file_path(file_path: str, must_exist: bool = True) -> str:
    """
    Validate file path

    Args:
        file_path: Path to validate
        must_exist: Whether file must exist

    Returns:
        Validated file path

    Raises:
        ValueError: If path is invalid
    """
    if not file_path:
        raise ValueError("File path cannot be empty")

    if must_exist and not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")

    return file_path


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
    if not 0.0 <= temperature <= 2.0:
        raise ValueError("Temperature must be between 0.0 and 2.0")
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
    if max_tokens < 1 or max_tokens > 32000:
        raise ValueError("max_tokens must be between 1 and 32000")
    return max_tokens
