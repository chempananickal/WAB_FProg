from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

ALGORITHM_ORDER = ["CPython", "CPython JIT", "PyPy", "Cython"]
ALGORITHM_COLORS = {
    "CPython": "#1f3a5f",
    "CPython JIT": "#2a7f62",
    "PyPy": "#c26d1f",
    "Cython": "#7d2e68",
}
SCENARIO_LABELS = {
    "homologous_region": "Homologous region",
    "indel_disruption": "Indel disruption",
    "conserved_motif": "Conserved motif",
    "contained_fragment": "Contained fragment",
    "random_uniform": "Random uniform",
}


def generate_plots(output_dir: Path) -> list[Path]:
    raw_path = output_dir / "raw_runs.csv"
    if not raw_path.exists():
        raise FileNotFoundError(f"Missing raw results at {raw_path}. Run benchmark_sw.py first.")
    raw_df = pd.read_csv(raw_path)
    summary_df = _aggregate(raw_df)

    plots_dir = output_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    plot_paths = [
        _plot_metric_by_scenario(
            summary_df,
            value_column="median_time_median_ms",
            ylabel="Median runtime [ms]",
            title="Smith-Waterman Runtime by Scenario and Problem Size",
            output_path=plots_dir / "runtime_by_scenario.pdf",
            log_scale=True,
        ),
        _plot_speedup_vs_baseline(
            summary_df,
            output_path=plots_dir / "speedup_vs_cpython.pdf",
        ),
    ]

    return plot_paths


def _plot_metric_by_scenario(
    summary_df: pd.DataFrame,
    *,
    value_column: str,
    ylabel: str,
    title: str,
    output_path: Path,
    log_scale: bool,
) -> Path:
    scenarios = list(summary_df["scenario"].drop_duplicates())
    fig, axes = _make_axes(len(scenarios))

    for axis, scenario in zip(axes, scenarios):
        scenario_df = summary_df[summary_df["scenario"] == scenario].sort_values("target_size")
        for algorithm in ALGORITHM_ORDER:
            algorithm_df = scenario_df[scenario_df["algorithm"] == algorithm]
            if algorithm_df.empty:
                continue
            axis.plot(
                algorithm_df["target_size"],
                algorithm_df[value_column],
                marker="o",
                linewidth=2,
                markersize=5,
                color=ALGORITHM_COLORS[algorithm],
                label=algorithm,
            )

        axis.set_title(SCENARIO_LABELS.get(scenario, scenario.replace("_", " ").title()))
        axis.set_xlabel("Problem size")
        axis.set_ylabel(ylabel)
        axis.grid(True, alpha=0.3)
        if log_scale:
            axis.set_yscale("log")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.suptitle(title)
    _place_legend(axes, len(scenarios), handles, labels)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(output_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_speedup_vs_baseline(summary_df: pd.DataFrame, *, output_path: Path) -> Path:
    speedup_df = _build_speedup_frame(summary_df)
    scenarios = list(speedup_df["scenario"].drop_duplicates())
    fig, axes = _make_axes(len(scenarios))

    for axis, scenario in zip(axes, scenarios):
        scenario_df = speedup_df[speedup_df["scenario"] == scenario].sort_values("target_size")
        for algorithm in ALGORITHM_ORDER:
            algorithm_df = scenario_df[scenario_df["algorithm"] == algorithm]
            if algorithm_df.empty:
                continue
            axis.plot(
                algorithm_df["target_size"],
                algorithm_df["speedup_vs_cpython"],
                marker="o",
                linewidth=2,
                markersize=5,
                color=ALGORITHM_COLORS[algorithm],
                label=algorithm,
            )

        axis.axhline(1.0, color="#555555", linestyle="--", linewidth=1)
        axis.set_title(SCENARIO_LABELS.get(scenario, scenario.replace("_", " ").title()))
        axis.set_xlabel("Problem size")
        axis.set_ylabel("Speedup vs CPython [x]")
        axis.grid(True, alpha=0.3)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.suptitle("Runtime Speedup Relative to CPython")
    _place_legend(axes, len(scenarios), handles, labels)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(output_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _aggregate(raw_df: pd.DataFrame) -> pd.DataFrame:
    return (
        raw_df.groupby(["scenario", "target_size", "algorithm"], as_index=False)
        .agg(
            median_time_median_ms=("median_time_ms", "median"),
            median_time_q1_ms=("median_time_ms", lambda s: s.quantile(0.25)),
            median_time_q3_ms=("median_time_ms", lambda s: s.quantile(0.75)),
            observations=("case_id", "count"),
        )
        .sort_values(["scenario", "target_size", "algorithm"])
        .reset_index(drop=True)
    )


def _build_speedup_frame(summary_df: pd.DataFrame) -> pd.DataFrame:
    baseline_df = summary_df[summary_df["algorithm"] == "CPython"][
        ["scenario", "target_size", "median_time_median_ms"]
    ].rename(columns={"median_time_median_ms": "baseline_time_ms"})
    merged = summary_df.merge(baseline_df, on=["scenario", "target_size"], how="inner")
    merged["speedup_vs_cpython"] = merged["baseline_time_ms"] / merged["median_time_median_ms"]
    return merged


def _make_axes(plot_count: int) -> tuple[plt.Figure, list[plt.Axes]]:
    columns = min(2, max(1, plot_count))
    rows = math.ceil(plot_count / columns)
    fig, axes = plt.subplots(rows, columns, figsize=(7 * columns, 4.5 * rows), squeeze=False)
    return fig, list(axes.ravel())


def _place_legend(axes: list[plt.Axes], used_count: int, handles: list[object], labels: list[str]) -> None:
    unused_axes = axes[used_count:]
    if unused_axes:
        legend_axis = unused_axes[0]
        legend_axis.set_axis_off()
        legend_axis.legend(
            handles,
            labels,
            loc="lower right",
            frameon=False,
            fontsize=14,
            handlelength=2.8,
            handletextpad=0.8,
            labelspacing=1.0,
            borderaxespad=0.8,
            markerscale=1.4,
        )
        for axis in unused_axes[1:]:
            axis.set_visible(False)
        return

    axes[0].figure.legend(
        handles,
        labels,
        loc="upper center",
        ncol=min(len(labels), 4),
        frameon=False,
        fontsize=12,
        handlelength=2.8,
        handletextpad=0.8,
        labelspacing=0.8,
        markerscale=1.3,
    )