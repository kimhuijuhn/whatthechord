# tests/evaluation/run_eval.py
"""
CLI entry point for evaluation.

Usage:
    python -m tests.evaluation.run_eval
    python -m tests.evaluation.run_eval --boost 1.75
"""
import argparse
from .evaluation import evaluate, grid_search
from .progressions import ALL_TEST_CASES, PROGRESSIONS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["single", "grid", "per-progression"],
        default="grid",
        help="Evaluation mode.",
    )
    parser.add_argument(
        "--boost",
        type=float,
        default=1.75,
        help="3rd/7th position weight (single mode only).",
    )
    args = parser.parse_args()

    if args.mode == "single":
        weights = (1.0, args.boost, 1.0, args.boost)
        acc = evaluate(ALL_TEST_CASES, weights)
        print(f"Boost = {args.boost}: top-1 accuracy = {acc:.2%}")
    
    elif args.mode == "grid":
        grid_search()
    
    elif args.mode == "per-progression":
        # 각 progression set별 accuracy
        print(f"{'Progression':<30} | {'Accuracy':>10}")
        print("-" * 45)
        weights = (1.0, args.boost, 1.0, args.boost)
        for name, cases in PROGRESSIONS.items():
            acc = evaluate(cases, weights)
            print(f"{name:<30} | {acc:>9.2%}")


if __name__ == "__main__":
    main()