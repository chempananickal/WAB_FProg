from __future__ import annotations

from pathlib import Path

import pandas as pd


def iqr(series: pd.Series) -> float:
    return float(series.quantile(0.75) - series.quantile(0.25))


def q1(series: pd.Series) -> float:
    return float(series.quantile(0.25))


def q3(series: pd.Series) -> float:
    return float(series.quantile(0.75))


def aggregate_results(raw_df: pd.DataFrame) -> pd.DataFrame:
    grouped = raw_df.groupby(["scenario", "target_size", "algorithm"], as_index=False).agg(
        median_time_mean_ms=("median_time_ms", "mean"),
        median_time_median_ms=("median_time_ms", "median"),
        median_time_std_ms=("median_time_ms", "std"),
        median_time_iqr_ms=("median_time_ms", iqr),
        median_time_q1_ms=("median_time_ms", q1),
        median_time_q3_ms=("median_time_ms", q3),
        score_mean=("score", "mean"),
        score_median=("score", "median"),
        sequence_a_length_mean=("sequence_a_length", "mean"),
        sequence_a_length_median=("sequence_a_length", "median"),
        sequence_b_length_mean=("sequence_b_length", "mean"),
        sequence_b_length_median=("sequence_b_length", "median"),
        observations=("case_id", "count"),
    )
    return grouped.sort_values(by=["scenario", "target_size", "algorithm"]).reset_index(drop=True)


def load_raw_results(output_dir: Path) -> pd.DataFrame:
    raw_path = output_dir / "raw_runs.csv"
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Missing raw results at {raw_path}. Run benchmark_sw.py with --mode run or --mode both first."
        )
    return pd.read_csv(raw_path)


def generate_summary(output_dir: Path) -> pd.DataFrame:
    raw_df = load_raw_results(output_dir)
    summary_df = aggregate_results(raw_df)
    summary_df.to_csv(output_dir / "summary_stats.csv", index=False)
    return summary_df