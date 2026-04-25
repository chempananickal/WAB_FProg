from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
import time
from pathlib import Path

from helpers.case_generation import (
    DEFAULT_PROBLEM_SIZES,
    DEFAULT_RANDOM_CASES_PER_LENGTH,
    deserialize_cases,
    generate_cases,
    serialize_cases,
)
from helpers.smithwaterman import (
    EXECUTOR_ENV_VAR,
    smith_waterman_score,
)


MATCH_SCORE = 2
MISMATCH_SCORE = -1
GAP_SCORE = -2


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute Smith-Waterman cases in a single runtime.")
    parser.add_argument("--problem-sizes", default=",".join(str(size) for size in DEFAULT_PROBLEM_SIZES))
    parser.add_argument("--cases-per-length", type=int, default=DEFAULT_RANDOM_CASES_PER_LENGTH)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--cases-file")
    parser.add_argument("--emit-progress", action="store_true")
    args = parser.parse_args()

    problem_sizes = tuple(int(item) for item in args.problem_sizes.split(",") if item)
    if args.cases_file:
        raw_cases = json.loads(Path(args.cases_file).read_text(encoding="utf-8"))
        cases = deserialize_cases(raw_cases)
    else:
        cases = generate_cases(problem_sizes=problem_sizes, random_cases_per_length=args.cases_per_length, seed=args.seed)

    executor_name = os.environ.get(EXECUTOR_ENV_VAR, "default").lower().strip()
    benchmark_samples: list[int] = []
    score_records: list[dict[str, object]] = []
    total_work_units = sum(
        _estimate_case_work_units(case.sequence_a, case.sequence_b, args.warmup + args.runs)
        for case in cases
    )
    completed_work_units = 0

    for case_index, case in enumerate(cases, start=1):
        score, warmup_times, run_times = _measure_case(case.sequence_a, case.sequence_b, args.warmup, args.runs)
        median_ns = int(statistics.median(run_times))
        benchmark_samples.append(median_ns)
        score_records.append(
            {
                "name": case.name,
                "family": case.family,
                "target_size": case.target_size,
                "sequence_a_length": case.sequence_a_length,
                "sequence_b_length": case.sequence_b_length,
                "score": score,
                "median_ns": median_ns,
                "warmup_times_ns": warmup_times,
                "run_times_ns": run_times,
            }
        )
        completed_work_units += _estimate_case_work_units(
            case.sequence_a,
            case.sequence_b,
            args.warmup + args.runs,
        )
        if args.emit_progress:
            print(
                "__PROGRESS__"
                + json.dumps(
                    {
                        "case_name": case.name,
                        "case_target_size": case.target_size,
                        "completed_cases": case_index,
                        "total_cases": len(cases),
                        "completed_work_units": completed_work_units,
                        "total_work_units": total_work_units,
                    }
                ),
                flush=True,
            )

    digest_source = "|".join(
        f"{record['name']}:{record['family']}:{record['target_size']}:{record['score']}"
        for record in score_records
    )
    digest = hashlib.sha256(digest_source.encode("utf-8")).hexdigest()

    payload = {
        "executor": executor_name,
        "implementation": executor_name,
        "case_count": len(score_records),
        "digest": digest,
        "median_case_ns": int(statistics.median(benchmark_samples)) if benchmark_samples else 0,
        "summary": _summarize_records(score_records),
        "scores": score_records,
        "scoring": {
            "match": MATCH_SCORE,
            "mismatch": MISMATCH_SCORE,
            "gap": GAP_SCORE,
        },
        "serialized_cases": serialize_cases(cases),
    }
    print("__RESULT__" + json.dumps(payload), flush=True)
    return 0


def _measure_case(
    sequence_a: str, sequence_b: str, warmup: int, runs: int
) -> tuple[int, list[int], list[int]]:
    warmup_times: list[int] = []
    for _ in range(warmup):
        t0 = time.perf_counter_ns()
        smith_waterman_score(sequence_a, sequence_b)
        warmup_times.append(time.perf_counter_ns() - t0)

    run_times: list[int] = []
    score = 0
    for _ in range(max(1, runs)):
        t0 = time.perf_counter_ns()
        score = smith_waterman_score(sequence_a, sequence_b)
        run_times.append(time.perf_counter_ns() - t0)

    return score, warmup_times, run_times


def _estimate_case_work_units(sequence_a: str, sequence_b: str, repetitions: int) -> int:
    return max(1, len(sequence_a) + 1) * max(1, len(sequence_b) + 1) * max(1, repetitions)


def _summarize_records(score_records: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[str, int], list[int]] = {}
    for record in score_records:
        key = (str(record["family"]), int(record["target_size"]))
        grouped.setdefault(key, []).append(int(record["median_ns"]))

    summary = []
    for (family, target_size), timings in sorted(grouped.items(), key=lambda item: (item[0][1], item[0][0])):
        summary.append(
            {
                "family": family,
                "target_size": target_size,
                "median_ns": int(statistics.median(timings)),
                "cases": len(timings),
            }
        )
    return summary


if __name__ == "__main__":
    raise SystemExit(main())