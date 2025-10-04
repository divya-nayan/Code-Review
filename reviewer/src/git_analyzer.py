"""
Git diff extraction and analysis
"""
import subprocess
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FileChange:
    """Represents a change to a file"""
    path: str
    change_type: str  # added, modified, deleted
    additions: List[str]
    deletions: List[str]
    line_numbers: List[int]
    diff: str


class GitAnalyzer:
    """Extracts and analyzes git changes"""

    def __init__(self, repo_path='.'):
        self.repo_path = repo_path

    def get_changes(self, target='HEAD', base=None) -> List[FileChange]:
        """
        Extract changes from git

        Args:
            target: Commit, branch, or 'HEAD' to analyze
            base: Base commit/branch to compare against

        Returns:
            List of FileChange objects
        """
        if base:
            diff_command = ['git', 'diff', base, target]
        else:
            # Compare with previous commit
            diff_command = ['git', 'diff', f'{target}~1', target]

        try:
            result = subprocess.run(
                diff_command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return self._parse_diff(result.stdout)
        except subprocess.CalledProcessError as e:
            # If diff fails, try showing the commit itself
            try:
                result = subprocess.run(
                    ['git', 'show', target, '--format=', '--patch'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return self._parse_diff(result.stdout)
            except subprocess.CalledProcessError:
                raise RuntimeError(f"Failed to get git diff: {e.stderr}")

    def _parse_diff(self, diff_text: str) -> List[FileChange]:
        """Parse git diff output into FileChange objects"""
        changes = []
        current_file = None
        current_additions = []
        current_deletions = []
        current_line_numbers = []
        current_diff = []

        for line in diff_text.split('\n'):
            # New file header
            if line.startswith('diff --git'):
                if current_file:
                    changes.append(FileChange(
                        path=current_file,
                        change_type=self._detect_change_type(current_diff),
                        additions=current_additions,
                        deletions=current_deletions,
                        line_numbers=current_line_numbers,
                        diff='\n'.join(current_diff)
                    ))
                current_additions = []
                current_deletions = []
                current_line_numbers = []
                current_diff = []

            if line.startswith('+++'):
                # Extract filename
                match = re.search(r'\+\+\+ b/(.*)', line)
                if match:
                    current_file = match.group(1)
                current_diff.append(line)

            elif line.startswith('@@'):
                # Extract line numbers
                match = re.search(r'@@ -\d+,?\d* \+(\d+),?\d* @@', line)
                if match:
                    current_line_numbers.append(int(match.group(1)))
                current_diff.append(line)

            elif line.startswith('+') and not line.startswith('+++'):
                current_additions.append(line[1:])
                current_diff.append(line)

            elif line.startswith('-') and not line.startswith('---'):
                current_deletions.append(line[1:])
                current_diff.append(line)

            else:
                current_diff.append(line)

        # Add the last file
        if current_file:
            changes.append(FileChange(
                path=current_file,
                change_type=self._detect_change_type(current_diff),
                additions=current_additions,
                deletions=current_deletions,
                line_numbers=current_line_numbers,
                diff='\n'.join(current_diff)
            ))

        return changes

    def _detect_change_type(self, diff_lines: List[str]) -> str:
        """Detect if file was added, modified, or deleted"""
        diff_text = '\n'.join(diff_lines)
        if 'new file mode' in diff_text:
            return 'added'
        elif 'deleted file mode' in diff_text:
            return 'deleted'
        else:
            return 'modified'
