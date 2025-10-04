"""
Main CLI for AI-powered code review
"""
import argparse
import sys
import logging
from pathlib import Path

from src.git_analyzer import GitAnalyzer
from src.context_builder import ContextBuilder
from src.llm_reviewer import LLMReviewer
from src.output_formatter import OutputFormatter
from src.exceptions import CodeReviewError
from src.constants import OUTPUT_FORMATS, DEFAULT_OUTPUT_FORMAT, DEFAULT_TARGET
from utils.logger import setup_logger


def main() -> int:
    """
    Main entry point for code reviewer

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="AI-powered code review tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Review latest commit
  %(prog)s abc123                   # Review specific commit
  %(prog)s feature --base main      # Review branch vs main
  %(prog)s --format markdown -o review.md  # Save as markdown
        """
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=DEFAULT_TARGET,
        help=f"Git commit, branch, or diff target (default: {DEFAULT_TARGET})"
    )
    parser.add_argument(
        "--base",
        default=None,
        help="Base commit or branch to compare against"
    )
    parser.add_argument(
        "--format",
        choices=OUTPUT_FORMATS,
        default=DEFAULT_OUTPUT_FORMAT,
        help=f"Output format (default: {DEFAULT_OUTPUT_FORMAT})"
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
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger("code_reviewer", level=log_level)

    try:
        # Extract git changes
        logger.info("📊 Analyzing git changes...")
        git_analyzer = GitAnalyzer()
        changes = git_analyzer.get_changes(args.target, args.base)

        if not changes:
            logger.info("No changes found to review.")
            return 0

        logger.info(f"Found {len(changes)} file(s) with changes")

        # Build context
        logger.info(f"🔍 Building context for {len(changes)} changed file(s)...")
        context_builder = ContextBuilder()
        contexts = context_builder.build_contexts(changes, full_context=args.context)

        # Perform review
        logger.info("🤖 Running AI code review...")
        reviewer = LLMReviewer()
        review_results = reviewer.review(contexts)

        # Format and output
        formatter = OutputFormatter()
        output = formatter.format(review_results, args.format)

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output)
            logger.info(f"✅ Review saved to {args.output}")
        else:
            print("\n" + output)

        return 0

    except CodeReviewError as e:
        logger.error(f"❌ Review failed: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1

    except KeyboardInterrupt:
        logger.warning("\n⚠️  Review interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


if __name__ == "__main__":
    sys.exit(main())
