"""
Custom exceptions for chatbot
"""


class ChatBotError(Exception):
    """Base exception for chatbot errors"""
    pass


class APIError(ChatBotError):
    """Raised when API call fails"""
    pass


class ConfigurationError(ChatBotError):
    """Raised when configuration is invalid"""
    pass


class InvalidAPIKeyError(ConfigurationError):
    """Raised when API key is missing or invalid"""
    pass
