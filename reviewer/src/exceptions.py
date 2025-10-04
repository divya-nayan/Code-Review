"""
Custom exceptions for code reviewer
"""


class CodeReviewError(Exception):
    """Base exception for code review errors"""
    pass


class GitAnalysisError(CodeReviewError):
    """Raised when git analysis fails"""
    pass


class LLMReviewError(CodeReviewError):
    """Raised when review process fails"""
    pass


class ConfigurationError(CodeReviewError):
    """Raised when configuration is invalid"""
    pass


class InvalidAPIKeyError(ConfigurationError):
    """Raised when API key is missing or invalid"""
    pass
