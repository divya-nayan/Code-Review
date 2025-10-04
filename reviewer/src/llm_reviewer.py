"""
LLM-powered code review using Groq API
"""
from groq import Groq
from ..config.settings import GROQ_API_KEY
from .context_builder import CodeContext
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ReviewIssue:
    """Represents a code review issue"""
    severity: str  # critical, warning, info
    category: str  # bug, security, style, performance
    file: str
    line: int
    message: str
    suggestion: str


@dataclass
class ReviewResult:
    """Complete review result for all changes"""
    issues: List[ReviewIssue]
    summary: str
    files_reviewed: int
    total_issues: int


class LLMReviewer:
    """Performs AI-powered code review"""

    def __init__(self, api_key=None):
        self.api_key = api_key or GROQ_API_KEY
        self.client = Groq(api_key=self.api_key)

    def review(self, contexts: List[CodeContext]) -> ReviewResult:
        """Review code changes using LLM"""
        all_issues = []

        for context in contexts:
            if context.file_change.change_type == 'deleted':
                continue

            issues = self._review_file_change(context)
            all_issues.extend(issues)

        summary = self._generate_summary(all_issues, len(contexts))

        return ReviewResult(
            issues=all_issues,
            summary=summary,
            files_reviewed=len(contexts),
            total_issues=len(all_issues)
        )

    def _review_file_change(self, context: CodeContext) -> List[ReviewIssue]:
        """Review a single file change"""
        # Build prompt
        prompt = self._build_review_prompt(context)

        # Call LLM
        try:
            response = self.client.chat.completions.create(
                model="llama-3.2-90b-text-preview",
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
                temperature=0.3,
                max_tokens=2000
            )

            # Parse response
            return self._parse_review_response(
                response.choices[0].message.content,
                context.file_change.path
            )

        except Exception as e:
            print(f"Warning: Failed to review {context.file_change.path}: {e}")
            return []

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
