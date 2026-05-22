"""
CLI entry point for chord recognition evaluation.

Usage:
    python -m tests.evaluation.run_eval                    # default: 1D grid search
    python -m tests.evaluation.run_eval --mode 2d          # 2D grid search
    python -m tests.evaluation.run_eval --mode per-prog    # per-progression breakdown
    python -m tests.evaluation.run_eval --mode wrong       # error analysis
    python -m tests.evaluation.run_eval --boost 1.5        # single point evaluation
"""

import argparse

from .evaluation import (
    evaluate,
    grid_search_1d,
    grid_search_2d,
    per_progression_breakdown,
    show_wrong_cases,
)
from .progressions import ALL_TEST_CASES


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate chord recognition on labeled progressions.",
    )
    parser.add_argument(
        "--mode",
        choices=["single", "1d", "2d", "per-prog", "wrong"],
        default="1d",
        help="Evaluation mode (default: 1d).",
    )
    parser.add_argument(
        "--boost",
        type=float,
        default=1.75,
        help="3rd/7th position weight (used in 'single', 'per-prog', 'wrong' modes).",
    )
    parser.add_argument(
        "--key-prior",
        type=float,
        default=None,
        help="Override KEY_PRIOR_BOOST (default: use module constant).",
    )
    args = parser.parse_args()

    weights = (1.0, args.boost, 1.0, args.boost)

    if args.mode == "single":
        acc, wrong = evaluate(ALL_TEST_CASES, weights, args.key_prior)
        print(f"boost={args.boost}, key_prior={args.key_prior}: "
              f"top-1 = {acc:.2%} ({len(wrong)} wrong of {len(ALL_TEST_CASES)})")

    elif args.mode == "1d":
        grid_search_1d()

    elif args.mode == "2d":
        grid_search_2d()

    elif args.mode == "per-prog":
        per_progression_breakdown(weights, args.key_prior)

    elif args.mode == "wrong":
        show_wrong_cases(weights, args.key_prior)


if __name__ == "__main__":
    main()