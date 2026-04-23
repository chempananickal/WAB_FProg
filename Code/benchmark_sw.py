from __future__ import annotations

import argparse
from pathlib import Path

from helpers.benchmarking import print_console_summary, run_benchmarks
from helpers.plotting import generate_plots
from helpers.statistics_io import generate_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark Smith-Waterman across CPython, JIT, PyPy, and Cython."
    )
    parser.add_argument(
        "--mode",
        choices=["run", "plot", "both"],
        default="both",
        help="Run benchmarks, generate plots from existing results, or both.",
    )
    parser.add_argument(
        "--problem-sizes",
        type=str,
        default="100,500,1000,5000,10000",
        help="Comma-separated benchmark size targets, e.g. 100,1000,10000",
    )
    parser.add_argument(
        "--cases-per-length",
        type=int,
        default=10,
        help="How many sequence pairs to generate per scenario and problem size.",
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=10,
        help="Benchmark repetitions per case and runtime.",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=2,
        help="Warmup repetitions before timed runs. This helps stabilize JIT and PyPy performance.",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument("--pypy", type=str, default="pypy3", help="PyPy executable or path.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="Code/Results",
        help="Directory for raw runs, summaries, and config files.",
    )
    parser.add_argument(
        "--progress",
        dest="show_progress",
        action="store_true",
        default=True,
        help="Show single-line progress output.",
    )
    parser.add_argument(
        "--no-progress",
        dest="show_progress",
        action="store_false",
        help="Disable progress output.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    problem_sizes = [int(item.strip()) for item in args.problem_sizes.split(",") if item.strip()]
    if any(problem_size <= 0 for problem_size in problem_sizes):
        raise ValueError("All problem sizes must be positive integers.")
    if args.cases_per_length <= 0:
        raise ValueError("--cases-per-length must be > 0")
    if args.runs <= 0:
        raise ValueError("--runs must be > 0")
    if args.warmup < 0:
        raise ValueError("--warmup must be >= 0")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.mode in {"run", "both"}:
        raw_df, cases_df = run_benchmarks(
            problem_sizes=problem_sizes,
            cases_per_length=args.cases_per_length,
            runs=args.runs,
            warmup=args.warmup,
            seed=args.seed,
            pypy_executable=args.pypy,
            show_progress=args.show_progress,
        )
        raw_df.to_csv(output_dir / "raw_runs.csv", index=False)
        cases_df.to_csv(output_dir / "case_scores.csv", index=False)

        config = {
            "problem_sizes": problem_sizes,
            "cases_per_length": args.cases_per_length,
            "runs": args.runs,
            "warmup": args.warmup,
            "seed": args.seed,
            "pypy": args.pypy,
            "output_dir": str(output_dir),
        }
        (output_dir / "benchmark_config.txt").write_text(
            "\n".join(f"{key}: {value}" for key, value in config.items()),
            encoding="utf-8",
        )

    if args.mode in {"plot", "both"}:
        summary_df = generate_summary(output_dir)
        print_console_summary(summary_df)
        print(f"\nSaved summary to: {output_dir / 'summary_stats.csv'}")

        plot_paths = generate_plots(output_dir)
        for plot_path in plot_paths:
            print(f"Saved plot to: {plot_path}")

    if args.mode in {"run", "both"}:
        print(f"Saved raw data to: {output_dir / 'raw_runs.csv'}")
        print(f"Saved case scores to: {output_dir / 'case_scores.csv'}")


if __name__ == "__main__":
    main()