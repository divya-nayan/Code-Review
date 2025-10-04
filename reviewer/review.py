"""
Main CLI for AI-powered code review
"""
import argparse
import sys
from src.git_analyzer import GitAnalyzer
from src.context_builder import ContextBuilder
from src.llm_reviewer import LLMReviewer
from src.output_formatter import OutputFormatter


def main():
    parser = argparse.ArgumentParser(description="AI-powered code review tool")
    parser.add_argument(
        "target",
        nargs="?",
        default="HEAD",
        help="Git commit, branch, or diff target (default: HEAD)"
    )
    parser.add_argument(
        "--base",
        default=None,
        help="Base commit or branch to compare against"
    )
    parser.add_argument(
        "--format",
        choices=["terminal", "markdown", "json"],
        default="terminal",
        help="Output format (default: terminal)"
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--context",
        action="store_true",
        help="Include full file context (slower but more accurate)"
    )

    args = parser.parse_args()

    try:
        # Extract git changes
        print("📊 Analyzing git changes...")
        git_analyzer = GitAnalyzer()
        changes = git_analyzer.get_changes(args.target, args.base)

        if not changes:
            print("No changes found to review.")
            return 0

        # Build context
        print(f"🔍 Building context for {len(changes)} changed file(s)...")
        context_builder = ContextBuilder()
        contexts = context_builder.build_contexts(changes, full_context=args.context)

        # Perform review
        print("🤖 Running AI code review...")
        reviewer = LLMReviewer()
        review_results = reviewer.review(contexts)

        # Format and output
        formatter = OutputFormatter()
        output = formatter.format(review_results, args.format)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"✅ Review saved to {args.output}")
        else:
            print("\n" + output)

        return 0

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
