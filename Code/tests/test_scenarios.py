from __future__ import annotations

import helpers.benchmarking as benchmarking_module
from helpers.case_generation import BenchmarkCase
from helpers.case_generation import DEFAULT_PROBLEM_SIZES, generate_cases


def test_homologous_cases_match_declared_length() -> None:
    cases = generate_cases(problem_sizes=(100, 1000), random_cases_per_length=1)
    homologous_cases = [case for case in cases if case.family == "homologous"]
    assert homologous_cases
    for case in homologous_cases:
        assert len(case.sequence_a) == case.target_size
        assert len(case.sequence_b) == case.target_size


def test_all_problem_sizes_have_balanced_case_families() -> None:
    problem_sizes = (100, 1000)
    cases = generate_cases(problem_sizes=problem_sizes, random_cases_per_length=2)
    for problem_size in problem_sizes:
        family_counts = {
            family: sum(1 for case in cases if case.target_size == problem_size and case.family == family)
            for family in {"homologous", "indel", "motif", "contained", "random"}
        }
        assert family_counts == {
            "homologous": 2,
            "indel": 2,
            "motif": 2,
            "contained": 2,
            "random": 2,
        }


def test_motif_cases_are_not_identical_when_length_is_large_enough() -> None:
    cases = generate_cases(problem_sizes=(100,), random_cases_per_length=0)
    motif_cases = [case for case in cases if case.family == "motif"]
    if not motif_cases:
        cases = generate_cases(problem_sizes=(100,), random_cases_per_length=1)
        motif_cases = [case for case in cases if case.family == "motif"]
    assert motif_cases
    case = motif_cases[0]
    assert case.sequence_a != case.sequence_b


def test_case_names_are_unique_within_each_problem_size() -> None:
    cases = generate_cases(problem_sizes=(100, 1000), random_cases_per_length=2)
    for problem_size in (100, 1000):
        case_names = [case.name for case in cases if case.target_size == problem_size]
        assert len(case_names) == len(set(case_names))


def test_run_benchmarks_preserves_cases_with_same_name_across_lengths(monkeypatch) -> None:
    cases = [
        BenchmarkCase("homologous_0", "homologous", 100, "A" * 100, "A" * 100),
        BenchmarkCase("homologous_0", "homologous", 1000, "A" * 1000, "A" * 1000),
    ]

    def fake_run_runtime_payload(**kwargs):
        case = kwargs["cases"][0]
        return {
            "scores": [
                {
                    "name": benchmark_case.name,
                    "family": benchmark_case.family,
                    "target_size": benchmark_case.target_size,
                    "sequence_a_length": len(benchmark_case.sequence_a),
                    "sequence_b_length": len(benchmark_case.sequence_b),
                    "rss_delta": 0,
                    "score": 200 if benchmark_case.target_size == 100 else 2000,
                    "median_ns": 1000 if benchmark_case.target_size == 100 else 2000,
                }
                for benchmark_case in kwargs["cases"]
            ],
        }

    monkeypatch.setattr(benchmarking_module, "generate_cases", lambda **kwargs: cases)
    monkeypatch.setattr(benchmarking_module, "_run_runtime_payload", fake_run_runtime_payload)

    raw_df, case_df, _per_run_df = benchmarking_module.run_benchmarks(
        problem_sizes=[100, 1000],
        cases_per_length=1,
        runs=1,
        warmup=0,
        seed=314159,
        pypy_executable="pypy3",
        show_progress=False,
    )

    assert set(raw_df["target_size"]) == {100, 1000}
    assert set(case_df["target_size"]) == {100, 1000}
    assert set(case_df["sequence_a_length"]) == {100, 1000}
    assert set(case_df["sequence_b_length"]) == {100, 1000}
    assert sorted(case_df["score"].tolist()) == [200, 2000]


def test_default_problem_sizes_match_bio_scale_targets() -> None:
    assert DEFAULT_PROBLEM_SIZES == (100, 1000)
