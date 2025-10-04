"""
LLM-powered code review using Groq API
"""
import logging
from groq import Groq
from typing import List, Optional

from ..config.settings import GROQ_API_KEY, MODEL_NAME
from .context_builder import CodeContext
from .constants import (
    Severity, Category, ChangeType,
    DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS
)
from .exceptions import LLMReviewError, InvalidAPIKeyError
from ..utils.validators import validate_api_key
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ReviewIssue:
    """Represents a code review issue"""
    severity: str
    category: str
    file: str
    line: int
    message: str
    suggestion: str

    def __post_init__(self):
        """Validate issue fields"""
        valid_severities = {s.value for s in Severity}
        if self.severity not in valid_severities:
            logger.warning(f"Invalid severity: {self.severity}, defaulting to 'info'")
            self.severity = Severity.INFO.value

        valid_categories = {c.value for c in Category}
        if self.category not in valid_categories:
            logger.warning(f"Invalid category: {self.category}, defaulting to 'general'")
            self.category = Category.GENERAL.value


@dataclass
class ReviewResult:
    """Complete review result for all changes"""
    issues: List[ReviewIssue]
    summary: str
    files_reviewed: int
    total_issues: int


class LLMReviewer:
    """Performs AI-powered code review"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = MODEL_NAME,
        temperature: float = DEFAULT_TEMPERATURE,
        max_tokens: int = DEFAULT_MAX_TOKENS
    ):
        """
        Initialize LLM reviewer

        Args:
            api_key: Groq API key
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens per response

        Raises:
            InvalidAPIKeyError: If API key is invalid
        """
        self.api_key = validate_api_key(api_key or GROQ_API_KEY)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        try:
            self.client = Groq(api_key=self.api_key)
        except Exception as e:
            raise LLMReviewError(f"Failed to initialize Groq client: {e}")

    def review(self, contexts: List[CodeContext]) -> ReviewResult:
        """
        Review code changes using LLM

        Args:
            contexts: List of code contexts to review

        Returns:
            ReviewResult containing all issues found

        Raises:
            LLMReviewError: If review process fails
        """
        if not contexts:
            logger.warning("No contexts to review")
            return ReviewResult(
                issues=[],
                summary="No files to review",
                files_reviewed=0,
                total_issues=0
            )

        logger.info(f"Starting review of {len(contexts)} file(s)")
        all_issues = []

        for i, context in enumerate(contexts, 1):
            if context.file_change.change_type == ChangeType.DELETED.value:
                logger.debug(f"Skipping deleted file: {context.file_change.path}")
                continue

            logger.info(f"Reviewing file {i}/{len(contexts)}: {context.file_change.path}")
            try:
                issues = self._review_file_change(context)
                all_issues.extend(issues)
                logger.debug(f"Found {len(issues)} issue(s) in {context.file_change.path}")
            except Exception as e:
                logger.error(f"Failed to review {context.file_change.path}: {e}")
                # Continue with other files instead of failing entirely

        summary = self._generate_summary(all_issues, len(contexts))
        logger.info(f"Review complete: {len(all_issues)} total issue(s) found")

        return ReviewResult(
            issues=all_issues,
            summary=summary,
            files_reviewed=len(contexts),
            total_issues=len(all_issues)
        )

    def _review_file_change(self, context: CodeContext) -> List[ReviewIssue]:
        """
        Review a single file change

        Args:
            context: Code context to review

        Returns:
            List of review issues

        Raises:
            LLMReviewError: If review fails
        """
        # Build prompt
        prompt = self._build_review_prompt(context)

        # Call LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert code reviewer. Analyze the code changes and identify:
1. Bugs and logic errors
2. Security vulnerabilities (SQL injection, XSS, hardcoded secrets, etc.)
3. Performance issues
4. Code smells and anti-patterns
5. Best practice violations

For each issue found, respond in this exact format:
SEVERITY: [critical/warning/info]
CATEGORY: [bug/security/style/performance]
LINE: [line number or 0 if general]
MESSAGE: [brief description]
SUGGESTION: [how to fix it]
---

Be concise and focus on real issues. Don't nitpick formatting unless it affects readability."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Parse response
            return self._parse_review_response(
                response.choices[0].message.content,
                context.file_change.path
            )

        except Exception as e:
            raise LLMReviewError(f"Failed to review {context.file_change.path}: {e}")

    def _build_review_prompt(self, context: CodeContext) -> str:
        """Build prompt for LLM review"""
        prompt_parts = [
            f"File: {context.file_change.path}",
            f"Change Type: {context.file_change.change_type}",
            "",
            "Git Diff:",
            "```",
            context.file_change.diff,
            "```",
            ""
        ]

        if context.imports:
            prompt_parts.append(f"Imports: {', '.join(context.imports[:10])}")

        if context.modified_functions:
            prompt_parts.append(f"Modified Functions: {', '.join(context.modified_functions)}")

        if context.modified_classes:
            prompt_parts.append(f"Modified Classes: {', '.join(context.modified_classes)}")

        if context.related_code:
            prompt_parts.append("\nRelated Code Context:")
            for file, code in list(context.related_code.items())[:2]:
                prompt_parts.append(f"\n--- {file} ---")
                prompt_parts.append(code[:500])  # Limit context size

        return "\n".join(prompt_parts)

    def _parse_review_response(self, response: str, file_path: str) -> List[ReviewIssue]:
        """Parse LLM response into ReviewIssue objects"""
        issues = []
        current_issue = {}

        for line in response.split('\n'):
            line = line.strip()

            if line.startswith('SEVERITY:'):
                current_issue['severity'] = line.split(':', 1)[1].strip()
            elif line.startswith('CATEGORY:'):
                current_issue['category'] = line.split(':', 1)[1].strip()
            elif line.startswith('LINE:'):
                try:
                    current_issue['line'] = int(line.split(':', 1)[1].strip())
                except ValueError:
                    current_issue['line'] = 0
            elif line.startswith('MESSAGE:'):
                current_issue['message'] = line.split(':', 1)[1].strip()
            elif line.startswith('SUGGESTION:'):
                current_issue['suggestion'] = line.split(':', 1)[1].strip()
            elif line == '---' and current_issue:
                # Complete issue
                issues.append(ReviewIssue(
                    severity=current_issue.get('severity', 'info'),
                    category=current_issue.get('category', 'general'),
                    file=file_path,
                    line=current_issue.get('line', 0),
                    message=current_issue.get('message', 'No message'),
                    suggestion=current_issue.get('suggestion', 'No suggestion')
                ))
                current_issue = {}

        return issues

    def _generate_summary(self, issues: List[ReviewIssue], files_count: int) -> str:
        """Generate summary of review results"""
        if not issues:
            return f"✅ No issues found in {files_count} file(s). Great work!"

        critical = len([i for i in issues if i.severity == 'critical'])
        warnings = len([i for i in issues if i.severity == 'warning'])
        info = len([i for i in issues if i.severity == 'info'])

        summary_parts = [
            f"Found {len(issues)} issue(s) in {files_count} file(s):",
            f"  • {critical} critical",
            f"  • {warnings} warnings",
            f"  • {info} info"
        ]

        # Category breakdown
        categories = {}
        for issue in issues:
            categories[issue.category] = categories.get(issue.category, 0) + 1

        if categories:
            summary_parts.append("\nBy category:")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                summary_parts.append(f"  • {cat}: {count}")

        return "\n".join(summary_parts)
