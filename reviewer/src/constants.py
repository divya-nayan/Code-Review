"""
Constants for code reviewer
"""
from enum import Enum


class ChangeType(Enum):
    """File change types"""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"


class Severity(Enum):
    """Issue severity levels"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Category(Enum):
    """Issue categories"""
    BUG = "bug"
    SECURITY = "security"
    STYLE = "style"
    PERFORMANCE = "performance"
    GENERAL = "general"


# Model configuration
DEFAULT_MODEL = "llama-3.2-90b-text-preview"
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 2000

# Context limits
MAX_IMPORTS_TO_ANALYZE = 10
MAX_RELATED_FILES = 5
MAX_RELATED_CODE_LINES = 100
MAX_CONTEXT_CHARS = 500

# Git configuration
DEFAULT_REPO_PATH = "."
DEFAULT_TARGET = "HEAD"

# Output configuration
OUTPUT_FORMATS = ["terminal", "markdown", "json"]
DEFAULT_OUTPUT_FORMAT = "terminal"
