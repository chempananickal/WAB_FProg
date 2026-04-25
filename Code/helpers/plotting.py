from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
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
    raw_path = output_dir / "per_case_results.csv"
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
        _plot_runtime_boxplot(raw_df, output_path=plots_dir / "runtime_boxplot.pdf"),
        _plot_throughput(raw_df, output_path=plots_dir / "throughput_by_size.pdf"),
        _plot_scaling_exponent(raw_df, output_path=plots_dir / "scaling_exponent.pdf"),
    ]

    per_run_path = output_dir / "per_run_times.csv"
    if per_run_path.exists():
        per_run_df = pd.read_csv(per_run_path)
        plot_paths.append(
            _plot_run_convergence(per_run_df, output_path=plots_dir / "run_convergence.pdf")
        )

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


def _plot_run_convergence(per_run_df: pd.DataFrame, *, output_path: Path) -> Path:
    """Runtime per run relative to stable median, revealing JIT/PyPy warmup effects."""
    sizes = sorted(per_run_df["target_size"].unique())
    fig, axes = _make_axes(len(sizes))

    # Reference: median of real (non-warmup) runs per (case, algorithm)
    real_df = per_run_df[~per_run_df["is_warmup"]]
    ref_times = (
        real_df.groupby(["case_id", "algorithm"])["time_ms"]
        .median()
        .rename("ref_time_ms")
        .reset_index()
    )
    merged = per_run_df.merge(ref_times, on=["case_id", "algorithm"], how="inner")
    merged = merged[merged["ref_time_ms"] > 0].copy()
    merged["relative_time"] = merged["time_ms"] / merged["ref_time_ms"]

    warmup_count = 0
    warmup_rows = per_run_df[per_run_df["is_warmup"]]
    if not warmup_rows.empty:
        warmup_count = int(warmup_rows["run_index"].max()) + 1

    total_runs = int(per_run_df["run_index"].max()) + 1

    for axis, size in zip(axes, sizes):
        size_df = merged[merged["target_size"] == size]
        agg = (
            size_df.groupby(["algorithm", "run_index"])["relative_time"]
            .median()
            .reset_index()
        )
        for algorithm in ALGORITHM_ORDER:
            alg_df = agg[agg["algorithm"] == algorithm].sort_values("run_index")
            if alg_df.empty:
                continue
            axis.plot(
                alg_df["run_index"],
                alg_df["relative_time"],
                marker="o",
                linewidth=2,
                markersize=4,
                color=ALGORITHM_COLORS[algorithm],
                label=algorithm,
            )

        if warmup_count > 0:
            axis.axvspan(-0.5, warmup_count - 0.5, alpha=0.10, color="#888888")
            axis.axvline(warmup_count - 0.5, color="#888888", linestyle=":", linewidth=1)

        axis.axhline(1.0, color="#555555", linestyle="--", linewidth=1)
        axis.set_title(f"n = {size:,}")
        axis.set_xlabel("Run index")
        axis.set_ylabel("Relative runtime [×]")
        axis.set_xticks(range(total_runs))
        axis.grid(True, alpha=0.3)

    handles, labels = axes[0].get_legend_handles_labels()
    title = "Runtime Convergence Across Runs (relative to stable median)"
    if warmup_count > 0:
        title += f"\nShaded region = warmup ({warmup_count} run{'s' if warmup_count != 1 else ''})"
    fig.suptitle(title)
    _place_legend(axes, len(sizes), handles, labels)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(output_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_runtime_boxplot(raw_df: pd.DataFrame, *, output_path: Path) -> Path:
    """Box plots of per-case median runtime distributions per algorithm, faceted by problem size."""
    sizes = sorted(raw_df["target_size"].unique())
    fig, axes = _make_axes(len(sizes))

    for axis, size in zip(axes, sizes):
        size_df = raw_df[raw_df["target_size"] == size]
        present_algs = [alg for alg in ALGORITHM_ORDER if alg in size_df["algorithm"].values]
        data_by_alg = [size_df[size_df["algorithm"] == alg]["median_time_ms"].dropna().values for alg in present_algs]

        bps = axis.boxplot(
            data_by_alg,
            labels=present_algs,
            patch_artist=True,
            medianprops={"color": "white", "linewidth": 2},
            flierprops={"marker": ".", "markersize": 4, "alpha": 0.5},
        )
        for patch, alg in zip(bps["boxes"], present_algs):
            patch.set_facecolor(ALGORITHM_COLORS[alg])
            patch.set_alpha(0.85)

        axis.set_title(f"n = {size:,}")
        axis.set_ylabel("Median runtime [ms]")
        axis.set_yscale("log")
        axis.yaxis.set_major_locator(ticker.LogLocator(base=10, subs=[1, 2, 5], numticks=10))
        axis.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{x:g}"))
        axis.grid(True, alpha=0.3, axis="y")

    for axis in axes[len(sizes):]:
        axis.set_visible(False)

    fig.suptitle("Runtime Distribution Across Cases\n(each box = spread over all scenario cases)")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(output_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_throughput(raw_df: pd.DataFrame, *, output_path: Path) -> Path:
    """Computational throughput (Mcells/s) by problem size, normalizing out sequence length differences."""
    df = raw_df.copy()
    df["cells"] = df["sequence_a_length"] * df["sequence_b_length"]
    df["throughput_mcells_per_s"] = df["cells"] / (df["median_time_ms"] / 1000.0) / 1e6

    agg = (
        df.groupby(["scenario", "target_size", "algorithm"])["throughput_mcells_per_s"]
        .median()
        .reset_index()
    )

    scenarios = list(agg["scenario"].drop_duplicates())
    fig, axes = _make_axes(len(scenarios))

    for axis, scenario in zip(axes, scenarios):
        scenario_df = agg[agg["scenario"] == scenario].sort_values("target_size")
        for algorithm in ALGORITHM_ORDER:
            alg_df = scenario_df[scenario_df["algorithm"] == algorithm]
            if alg_df.empty:
                continue
            axis.plot(
                alg_df["target_size"],
                alg_df["throughput_mcells_per_s"],
                marker="o",
                linewidth=2,
                markersize=5,
                color=ALGORITHM_COLORS[algorithm],
                label=algorithm,
            )

        axis.set_title(SCENARIO_LABELS.get(scenario, scenario.replace("_", " ").title()))
        axis.set_xlabel("Problem size")
        axis.set_ylabel("Throughput [Mcells/s]")
        axis.grid(True, alpha=0.3)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.suptitle("Computational Throughput by Scenario and Problem Size\n(cells = len_a × len_b; higher is faster)")
    _place_legend(axes, len(scenarios), handles, labels)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(output_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return output_path


def _plot_scaling_exponent(raw_df: pd.DataFrame, *, output_path: Path) -> Path:
    """Fit t ~ n^alpha per algorithm via OLS in log-log space; plot alpha with 95% CI."""
    # Use the product of sequence lengths as the cell count (actual work ~ len_a * len_b)
    df = raw_df.copy()
    df["log_n"] = np.log10(np.sqrt(df["sequence_a_length"] * df["sequence_b_length"]))
    df["log_t"] = np.log10(df["median_time_ms"].clip(lower=1e-9))

    fig, axis = plt.subplots(figsize=(8, 5))

    bar_width = 0.18
    x_positions = np.arange(len(ALGORITHM_ORDER))

    for bar_x, algorithm in zip(x_positions, ALGORITHM_ORDER):
        alg_df = df[df["algorithm"] == algorithm].dropna(subset=["log_n", "log_t"])
        if len(alg_df) < 3:
            continue
        log_n = alg_df["log_n"].values
        log_t = alg_df["log_t"].values

        # OLS: log_t = alpha * log_n + const
        A = np.column_stack([log_n, np.ones(len(log_n))])
        result = np.linalg.lstsq(A, log_t, rcond=None)
        coeffs = result[0]
        alpha = coeffs[0]

        # 95% confidence interval via residual variance
        residuals = log_t - A @ coeffs
        n_obs = len(log_n)
        if n_obs > 2:
            s2 = np.sum(residuals**2) / (n_obs - 2)
            ATA_inv = np.linalg.inv(A.T @ A)
            se_alpha = np.sqrt(s2 * ATA_inv[0, 0])
            ci = 1.96 * se_alpha
        else:
            ci = 0.0

        axis.bar(bar_x, alpha, width=bar_width, color=ALGORITHM_COLORS[algorithm],
                 label=algorithm, alpha=0.85)
        axis.errorbar(bar_x, alpha, yerr=ci, fmt="none", color="black", capsize=5, linewidth=1.5)

    # Reference line at alpha=2 (theoretical O(n^2))
    axis.axhline(2.0, color="#555555", linestyle="--", linewidth=1.2, label="Theoretical $O(n^2)$")

    axis.set_xticks(x_positions)
    axis.set_xticklabels(ALGORITHM_ORDER)
    axis.set_ylabel("Scaling exponent $\\alpha$  ($t \\propto n^\\alpha$)")
    axis.set_title("Empirical Scaling Exponent per Algorithm\n(OLS fit in log–log space, 95% CI error bars)")
    axis.legend(frameon=False)
    axis.grid(True, alpha=0.3, axis="y")

    fig.tight_layout()
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