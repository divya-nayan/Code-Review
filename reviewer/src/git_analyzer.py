"""
Git diff extraction and analysis
"""
import subprocess
import re
import logging
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path

from .constants import ChangeType, DEFAULT_REPO_PATH, DEFAULT_TARGET
from .exceptions import GitAnalysisError

logger = logging.getLogger(__name__)


@dataclass
class FileChange:
    """Represents a change to a file"""
    path: str
    change_type: str
    additions: List[str]
    deletions: List[str]
    line_numbers: List[int]
    diff: str

    def __post_init__(self):
        """Validate change type"""
        valid_types = {ct.value for ct in ChangeType}
        if self.change_type not in valid_types:
            raise ValueError(f"Invalid change type: {self.change_type}")


class GitAnalyzer:
    """Extracts and analyzes git changes"""

    def __init__(self, repo_path: str = DEFAULT_REPO_PATH):
        """
        Initialize GitAnalyzer

        Args:
            repo_path: Path to git repository

        Raises:
            GitAnalysisError: If repository path is invalid
        """
        self.repo_path = Path(repo_path)
        self._validate_repo()

    def _validate_repo(self) -> None:
        """
        Validate that the path is a git repository

        Raises:
            GitAnalysisError: If not a valid git repository
        """
        if not self.repo_path.exists():
            raise GitAnalysisError(f"Repository path does not exist: {self.repo_path}")

        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise GitAnalysisError(
                f"Not a git repository: {self.repo_path}. "
                "Please run this tool from within a git repository."
            )

    def get_changes(self, target: str = DEFAULT_TARGET, base: Optional[str] = None) -> List[FileChange]:
        """
        Extract changes from git

        Args:
            target: Commit, branch, or 'HEAD' to analyze
            base: Base commit/branch to compare against

        Returns:
            List of FileChange objects

        Raises:
            GitAnalysisError: If git operation fails
        """
        logger.info(f"Analyzing git changes: target={target}, base={base}")

        if base:
            diff_command = ['git', 'diff', base, target]
        else:
            # Compare with previous commit
            diff_command = ['git', 'diff', f'{target}~1', target]

        try:
            result = subprocess.run(
                diff_command,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            changes = self._parse_diff(result.stdout)
            logger.info(f"Found {len(changes)} file change(s)")
            return changes

        except subprocess.TimeoutExpired:
            raise GitAnalysisError("Git command timed out after 30 seconds")

        except subprocess.CalledProcessError as e:
            # If diff fails, try showing the commit itself
            try:
                logger.debug("Trying git show command as fallback")
                result = subprocess.run(
                    ['git', 'show', target, '--format=', '--patch'],
                    cwd=str(self.repo_path),
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=30
                )
                changes = self._parse_diff(result.stdout)
                logger.info(f"Found {len(changes)} file change(s) using git show")
                return changes

            except subprocess.CalledProcessError as show_error:
                raise GitAnalysisError(
                    f"Failed to get git diff: {e.stderr}\n"
                    f"Also failed with git show: {show_error.stderr}"
                )

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
        """
        Detect if file was added, modified, or deleted

        Args:
            diff_lines: Lines from the diff

        Returns:
            Change type string
        """
        diff_text = '\n'.join(diff_lines)
        if 'new file mode' in diff_text:
            return ChangeType.ADDED.value
        elif 'deleted file mode' in diff_text:
            return ChangeType.DELETED.value
        else:
            return ChangeType.MODIFIED.value
