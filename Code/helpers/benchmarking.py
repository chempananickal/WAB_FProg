from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from helpers.case_generation import generate_cases, serialize_cases
from helpers.smithwaterman import EXECUTOR_ENV_VAR


def _format_seconds_as_timedelta(seconds: float) -> str:
    return str(timedelta(seconds=int(max(0, round(seconds)))))


def _estimate_case_work_units(sequence_a: str, sequence_b: str, repetitions: int) -> int:
    return max(1, len(sequence_a) + 1) * max(1, len(sequence_b) + 1) * max(1, repetitions)


def _render_progress(
    current_work: int,
    total_work: int,
    elapsed_seconds: float,
    eta_seconds: float,
    completed_cases: int,
    total_cases: int,
    *,
    runtime_name: str | None = None,
    case_name: str | None = None,
    case_length: int | None = None,
    width: int = 30,
) -> str:
    fraction = current_work / total_work if total_work else 1.0
    filled = int(width * fraction)
    bar = "=" * filled + "-" * (width - filled)
    percent = fraction * 100
    status = (
        f"[{bar}] {percent:6.2f}% "
        f"cases={completed_cases}/{total_cases} "
        f"elapsed={_format_seconds_as_timedelta(elapsed_seconds)} "
        f"eta={_format_seconds_as_timedelta(eta_seconds)}"
    )
    details: list[str] = []
    if runtime_name:
        details.append(runtime_name)
    if case_name:
        details.append(case_name)
    if case_length is not None:
        details.append(f"n={case_length}")
    if details:
        status += " | " + " ".join(details)
    return status


def _write_progress_line(message: str, previous_length: int) -> int:
    padded_message = message
    if previous_length > len(message):
        padded_message += " " * (previous_length - len(message))
    sys.stdout.write("\r" + padded_message)
    sys.stdout.flush()
    return len(message)


def _resolve_runtime_executable(executable: str) -> str:
    direct_match = shutil.which(executable)
    if direct_match:
        return direct_match

    candidate_paths: list[str] = []
    if executable.lower() in {"pypy", "pypy3", "pypy3.exe", "pypy.exe"}:
        candidate_paths.extend(
            [
                r"C:\PyPy\pypy3.exe",
                r"C:\PyPy\pypy.exe",
                r"C:\PyPy\python.exe",
            ]
        )

    for candidate in candidate_paths:
        if Path(candidate).exists():
            return candidate

    return executable


def run_benchmarks(
    problem_sizes: list[int],
    cases_per_length: int,
    runs: int,
    warmup: int,
    seed: int,
    pypy_executable: str,
    show_progress: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    cases = generate_cases(problem_sizes=tuple(problem_sizes), random_cases_per_length=cases_per_length, seed=seed)
    code_dir = Path(__file__).resolve().parents[1]
    runtime_specs = [
        {
            "algorithm": "CPython",
            "executable": sys.executable,
            "extra_env": {EXECUTOR_ENV_VAR: "default"},
        },
        {
            "algorithm": "CPython JIT",
            "executable": sys.executable,
            "extra_env": {EXECUTOR_ENV_VAR: "jit", "PYTHON_JIT": "1"},
        },
        {
            "algorithm": "PyPy",
            "executable": _resolve_runtime_executable(pypy_executable),
            "extra_env": {EXECUTOR_ENV_VAR: "pypy"},
        },
        {
            "algorithm": "Cython",
            "executable": sys.executable,
            "extra_env": {EXECUTOR_ENV_VAR: "cython"},
        },
    ]

    rows: list[dict[str, Any]] = []
    case_rows: list[dict[str, Any]] = []
    run_rows: list[dict[str, Any]] = []

    repetitions_per_case = warmup + runs
    work_units_per_runtime = sum(
        _estimate_case_work_units(case.sequence_a, case.sequence_b, repetitions_per_case) for case in cases
    )
    total_work_units = work_units_per_runtime * len(runtime_specs)
    total_cases = len(cases) * len(runtime_specs)
    completed_work_units = 0
    completed_cases = 0
    started_at = time.perf_counter()
    previous_progress_length = 0

    if show_progress:
        previous_progress_length = _write_progress_line(
            _render_progress(
                0,
                total_work_units,
                0.0,
                0.0,
                0,
                total_cases,
            ),
            previous_progress_length,
        )

    case_lookup = {(case.name, case.target_size): case for case in cases}
    baseline_scores: dict[tuple[str, int], int] = {}

    for runtime_spec in runtime_specs:
        runtime_name = str(runtime_spec["algorithm"])

        def on_progress(progress: dict[str, Any]) -> None:
            nonlocal previous_progress_length
            runtime_completed_work = int(progress["completed_work_units"])
            runtime_completed_cases = int(progress["completed_cases"])
            current_work_units = completed_work_units + runtime_completed_work
            current_completed_cases = completed_cases + runtime_completed_cases
            elapsed_wall = max(0.0, time.perf_counter() - started_at)
            eta_seconds = 0.0
            if current_work_units > 0:
                eta_seconds = elapsed_wall * max(0, total_work_units - current_work_units) / current_work_units
            previous_progress_length = _write_progress_line(
                _render_progress(
                    current_work_units,
                    total_work_units,
                    elapsed_wall,
                    eta_seconds,
                    current_completed_cases,
                    total_cases,
                    runtime_name=runtime_name,
                    case_name=str(progress["case_name"]),
                    case_length=int(progress["case_target_size"]),
                ),
                previous_progress_length,
            )

        payload = _run_runtime_payload(
            code_dir=code_dir,
            executable=runtime_spec["executable"],
            warmup=warmup,
            runs=runs,
            cases=cases,
            extra_env=runtime_spec["extra_env"],
            progress_callback=on_progress if show_progress else None,
        )

        for score_row in payload["scores"]:
            case_key = (str(score_row["name"]), int(score_row["target_size"]))
            case_definition = case_lookup[case_key]

            if runtime_name == "CPython":
                baseline_scores[case_key] = int(score_row["score"])
                case_rows.append(
                    {
                        "case_id": case_definition.case_id,
                        "scenario": case_definition.scenario,
                        "target_size": case_definition.target_size,
                        "sequence_a_length": case_definition.sequence_a_length,
                        "sequence_b_length": case_definition.sequence_b_length,
                        "sequence_a": case_definition.sequence_a,
                        "sequence_b": case_definition.sequence_b,
                        "score": score_row["score"],
                        "family": case_definition.family,
                        "name": case_definition.name,
                    }
                )
            elif int(score_row["score"]) != baseline_scores[case_key]:
                raise ValueError(f"Correctness mismatch detected for {runtime_name} on {case_definition.case_id}.")

            rows.append(
                {
                    "case_id": case_definition.case_id,
                    "scenario": case_definition.scenario,
                    "target_size": case_definition.target_size,
                    "sequence_a_length": case_definition.sequence_a_length,
                    "sequence_b_length": case_definition.sequence_b_length,
                    "algorithm": runtime_name,
                    "median_time_ms": score_row["median_ns"] / 1_000_000,
                    "score": score_row["score"],
                    "runs": runs,
                    "warmup": warmup,
                }
            )

            for i, t_ns in enumerate(score_row.get("warmup_times_ns", [])):
                run_rows.append(
                    {
                        "case_id": case_definition.case_id,
                        "scenario": case_definition.scenario,
                        "target_size": case_definition.target_size,
                        "algorithm": runtime_name,
                        "run_index": i,
                        "is_warmup": True,
                        "time_ms": t_ns / 1_000_000,
                    }
                )
            for i, t_ns in enumerate(score_row.get("run_times_ns", [])):
                run_rows.append(
                    {
                        "case_id": case_definition.case_id,
                        "scenario": case_definition.scenario,
                        "target_size": case_definition.target_size,
                        "algorithm": runtime_name,
                        "run_index": warmup + i,
                        "is_warmup": False,
                        "time_ms": t_ns / 1_000_000,
                    }
                )

        completed_work_units += work_units_per_runtime
        completed_cases += len(cases)

    if show_progress:
        if previous_progress_length:
            _write_progress_line("", previous_progress_length)
        sys.stdout.write("\n")
        sys.stdout.flush()

    return pd.DataFrame(rows), pd.DataFrame(case_rows), pd.DataFrame(run_rows)


def _run_runtime_payload(
    *,
    code_dir: Path,
    executable: str,
    warmup: int,
    runs: int,
    cases: list[dict[str, Any]] | list[Any],
    extra_env: dict[str, str],
    progress_callback: Any | None = None,
) -> dict[str, Any]:
    env = os.environ.copy()
    env.update(extra_env)
    env["PYTHONPATH"] = str(code_dir) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONUNBUFFERED"] = "1"

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as handle:
        json.dump(serialize_cases(cases), handle)
        cases_file = Path(handle.name)

    try:
        command = [
            executable,
            "-u",
            "-m",
            "helpers.smithwaterman.runtime_worker",
            "--cases-file",
            str(cases_file),
            "--warmup",
            str(warmup),
            "--runs",
            str(runs),
        ]
        if progress_callback is not None:
            command.append("--emit-progress")

        process = subprocess.Popen(
            command,
            cwd=code_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        result_payload: dict[str, Any] | None = None
        stdout_chunks: list[str] = []
        assert process.stdout is not None
        for raw_line in process.stdout:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("__PROGRESS__"):
                progress_callback(json.loads(line.removeprefix("__PROGRESS__")))
                continue
            if line.startswith("__RESULT__"):
                result_payload = json.loads(line.removeprefix("__RESULT__"))
                continue
            stdout_chunks.append(line)

        stderr_output = ""
        if process.stderr is not None:
            stderr_output = process.stderr.read().strip()
        return_code = process.wait()
        if return_code != 0:
            error_output = stderr_output or "\n".join(stdout_chunks).strip()
            raise RuntimeError(error_output)
        if result_payload is None:
            raw_output = "\n".join(stdout_chunks).strip()
            if not raw_output:
                raise RuntimeError("Benchmark worker produced no result payload.")
            result_payload = json.loads(raw_output)
        return result_payload
    finally:
        cases_file.unlink(missing_ok=True)


def print_console_summary(summary_df: pd.DataFrame) -> None:
    for scenario, scenario_df in summary_df.groupby("scenario"):
        print(f"\n=== Scenario: {scenario} ===")
        pivot = scenario_df.pivot_table(
            index="target_size",
            columns="algorithm",
            values="median_time_median_ms",
        ).sort_index()
        print("Median runtime [ms]:")
        print(pivot.round(3).to_string())