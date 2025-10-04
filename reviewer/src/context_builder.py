"""
Build context for code review by analyzing related files and imports
"""
import os
import re
from dataclasses import dataclass
from typing import List, Dict, Set
from .git_analyzer import FileChange


@dataclass
class CodeContext:
    """Context for a code change"""
    file_change: FileChange
    related_code: Dict[str, str]  # filename -> code snippet
    imports: List[str]
    modified_functions: List[str]
    modified_classes: List[str]


class ContextBuilder:
    """Builds context for code changes"""

    def __init__(self, repo_path='.'):
        self.repo_path = repo_path

    def build_contexts(self, changes: List[FileChange], full_context=False) -> List[CodeContext]:
        """Build context for each file change"""
        contexts = []

        for change in changes:
            context = CodeContext(
                file_change=change,
                related_code={},
                imports=[],
                modified_functions=[],
                modified_classes=[]
            )

            # Skip deleted files
            if change.change_type == 'deleted':
                contexts.append(context)
                continue

            file_path = os.path.join(self.repo_path, change.path)

            # Read the current file
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Extract imports
                context.imports = self._extract_imports(content, change.path)

                # Extract modified functions/classes
                context.modified_functions = self._extract_modified_functions(change.diff)
                context.modified_classes = self._extract_modified_classes(change.diff)

                # Add related code if full context requested
                if full_context:
                    context.related_code = self._get_related_code(
                        content,
                        context.imports,
                        change.path
                    )

            contexts.append(context)

        return contexts

    def _extract_imports(self, content: str, file_path: str) -> List[str]:
        """Extract import statements from code"""
        imports = []

        # Python imports
        if file_path.endswith('.py'):
            imports.extend(re.findall(r'^import\s+(.+)$', content, re.MULTILINE))
            imports.extend(re.findall(r'^from\s+(.+?)\s+import', content, re.MULTILINE))

        # JavaScript/TypeScript imports
        elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
            imports.extend(re.findall(r'import\s+.*?from\s+[\'"](.+?)[\'"]', content))
            imports.extend(re.findall(r'require\([\'"](.+?)[\'"]\)', content))

        # Java imports
        elif file_path.endswith('.java'):
            imports.extend(re.findall(r'^import\s+(.+?);', content, re.MULTILINE))

        # Go imports
        elif file_path.endswith('.go'):
            imports.extend(re.findall(r'import\s+"(.+?)"', content))

        return imports

    def _extract_modified_functions(self, diff: str) -> List[str]:
        """Extract names of functions that were modified"""
        functions = []

        # Python functions
        functions.extend(re.findall(r'^\+\s*def\s+(\w+)', diff, re.MULTILINE))

        # JavaScript/TypeScript functions
        functions.extend(re.findall(r'^\+\s*function\s+(\w+)', diff, re.MULTILINE))
        functions.extend(re.findall(r'^\+\s*const\s+(\w+)\s*=\s*(?:async\s*)?\(', diff, re.MULTILINE))

        # Java methods
        functions.extend(re.findall(r'^\+\s*(?:public|private|protected).*?(\w+)\s*\(', diff, re.MULTILINE))

        return list(set(functions))

    def _extract_modified_classes(self, diff: str) -> List[str]:
        """Extract names of classes that were modified"""
        classes = []

        # Python classes
        classes.extend(re.findall(r'^\+\s*class\s+(\w+)', diff, re.MULTILINE))

        # JavaScript/TypeScript classes
        classes.extend(re.findall(r'^\+\s*class\s+(\w+)', diff, re.MULTILINE))

        # Java classes
        classes.extend(re.findall(r'^\+\s*(?:public|private)?\s*class\s+(\w+)', diff, re.MULTILINE))

        return list(set(classes))

    def _get_related_code(self, content: str, imports: List[str], file_path: str) -> Dict[str, str]:
        """Get code from related/imported files"""
        related = {}

        for imp in imports[:5]:  # Limit to avoid too much context
            # Try to find the imported file
            related_path = self._resolve_import_path(imp, file_path)
            if related_path and os.path.exists(related_path):
                try:
                    with open(related_path, 'r', encoding='utf-8', errors='ignore') as f:
                        # Read first 100 lines to avoid huge context
                        lines = [f.readline() for _ in range(100)]
                        related[imp] = ''.join(lines)
                except Exception:
                    pass

        return related

    def _resolve_import_path(self, import_name: str, current_file: str) -> str:
        """Resolve import to actual file path"""
        # This is simplified - a real implementation would handle:
        # - Package managers (pip, npm, etc.)
        # - Relative imports
        # - Module resolution rules per language

        current_dir = os.path.dirname(os.path.join(self.repo_path, current_file))

        # Try common patterns
        candidates = [
            os.path.join(current_dir, f"{import_name}.py"),
            os.path.join(current_dir, import_name, "__init__.py"),
            os.path.join(self.repo_path, f"{import_name}.py"),
            os.path.join(current_dir, f"{import_name}.js"),
            os.path.join(current_dir, f"{import_name}.ts"),
        ]

        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate

        return None
