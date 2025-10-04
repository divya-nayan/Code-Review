"""
Format code review results in different output formats
"""
import json
from llm_reviewer import ReviewResult, ReviewIssue
from typing import Dict


class OutputFormatter:
    """Format review results for different output types"""

    def format(self, result: ReviewResult, format_type: str) -> str:
        """Format review result"""
        if format_type == 'terminal':
            return self._format_terminal(result)
        elif format_type == 'markdown':
            return self._format_markdown(result)
        elif format_type == 'json':
            return self._format_json(result)
        else:
            raise ValueError(f"Unknown format type: {format_type}")

    def _format_terminal(self, result: ReviewResult) -> str:
        """Format for terminal output with colors"""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("CODE REVIEW RESULTS")
        lines.append("=" * 80)
        lines.append("")

        # Summary
        lines.append(result.summary)
        lines.append("")

        if result.issues:
            lines.append("-" * 80)
            lines.append("")

            # Group by file
            issues_by_file: Dict[str, list] = {}
            for issue in result.issues:
                if issue.file not in issues_by_file:
                    issues_by_file[issue.file] = []
                issues_by_file[issue.file].append(issue)

            # Output issues by file
            for file_path, issues in issues_by_file.items():
                lines.append(f"📁 {file_path}")
                lines.append("")

                for issue in issues:
                    # Severity icon
                    if issue.severity == 'critical':
                        icon = '🔴'
                    elif issue.severity == 'warning':
                        icon = '🟡'
                    else:
                        icon = '🔵'

                    lines.append(f"{icon} {issue.severity.upper()} [{issue.category}] Line {issue.line}")
                    lines.append(f"   {issue.message}")
                    lines.append(f"   💡 {issue.suggestion}")
                    lines.append("")

                lines.append("-" * 80)
                lines.append("")

        return "\n".join(lines)

    def _format_markdown(self, result: ReviewResult) -> str:
        """Format as markdown"""
        lines = []

        # Header
        lines.append("# Code Review Results")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append("")
        lines.append(result.summary)
        lines.append("")

        if result.issues:
            lines.append("## Issues Found")
            lines.append("")

            # Group by file
            issues_by_file: Dict[str, list] = {}
            for issue in result.issues:
                if issue.file not in issues_by_file:
                    issues_by_file[issue.file] = []
                issues_by_file[issue.file].append(issue)

            # Output issues by file
            for file_path, issues in issues_by_file.items():
                lines.append(f"### {file_path}")
                lines.append("")

                for issue in issues:
                    severity_badge = {
                        'critical': '🔴 **CRITICAL**',
                        'warning': '🟡 **WARNING**',
                        'info': '🔵 **INFO**'
                    }.get(issue.severity, issue.severity)

                    lines.append(f"#### {severity_badge} [{issue.category}] Line {issue.line}")
                    lines.append("")
                    lines.append(f"**Issue:** {issue.message}")
                    lines.append("")
                    lines.append(f"**Suggestion:** {issue.suggestion}")
                    lines.append("")

        return "\n".join(lines)

    def _format_json(self, result: ReviewResult) -> str:
        """Format as JSON"""
        output = {
            "summary": result.summary,
            "files_reviewed": result.files_reviewed,
            "total_issues": result.total_issues,
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "file": issue.file,
                    "line": issue.line,
                    "message": issue.message,
                    "suggestion": issue.suggestion
                }
                for issue in result.issues
            ]
        }
        return json.dumps(output, indent=2)
