from __future__ import annotations

from types import SimpleNamespace

import pytest
from hypothesis import given
from hypothesis import settings
from hypothesis import strategies as st

from helpers.case_generation import DEFAULT_PROBLEM_SIZES, generate_cases
import helpers.smithwaterman as smithwaterman_module
from helpers.smithwaterman import EXECUTOR_ENV_VAR, smith_waterman_score
from helpers.smithwaterman.scoring import (
    DEFAULT_GAP_SCORE,
    DEFAULT_MATCH_SCORE,
    DEFAULT_MISMATCH_SCORE,
)
from helpers.smithwaterman.smith_waterman_python import (
    smith_waterman_score as python_smith_waterman_score,
)


def test_known_edge_scores() -> None:
    assert smith_waterman_score("", "") == 0
    assert smith_waterman_score("A", "") == 0
    assert smith_waterman_score("", "A") == 0
    assert smith_waterman_score("A", "A") == 2
    assert smith_waterman_score("A", "T") == 0
    assert smith_waterman_score("ACGT", "ACGT") == 8
    assert smith_waterman_score("AAAA", "TTTT") == 0


def test_generated_cases_cover_all_default_lengths() -> None:
    problem_sizes = {case.target_size for case in generate_cases()}
    assert problem_sizes == set(DEFAULT_PROBLEM_SIZES)


def test_generated_cases_include_structured_and_random_families() -> None:
    families = {case.family for case in generate_cases(problem_sizes=(8,), random_cases_per_length=2)}
    assert families == {"homologous", "indel", "motif", "contained", "random"}


def test_case_count_per_family_and_length_is_respected() -> None:
    cases = generate_cases(problem_sizes=(4, 8), random_cases_per_length=3)
    for family in {"homologous", "indel", "motif", "contained", "random"}:
        family_cases = [case for case in cases if case.family == family]
        assert len(family_cases) == 6


@given(
    st.text(alphabet="ACGT", min_size=0, max_size=24),
    st.text(alphabet="ACGT", min_size=0, max_size=24),
)
@settings(max_examples=250)
def test_score_is_non_negative(sequence_a: str, sequence_b: str) -> None:
    assert python_smith_waterman_score(sequence_a, sequence_b) >= 0


@given(
    st.text(alphabet="ACGT", min_size=0, max_size=24),
    st.text(alphabet="ACGT", min_size=0, max_size=24),
)
@settings(max_examples=250)
def test_score_is_symmetric_for_symmetric_scoring(sequence_a: str, sequence_b: str) -> None:
    left = python_smith_waterman_score(sequence_a, sequence_b)
    right = python_smith_waterman_score(sequence_b, sequence_a)
    assert left == right


def test_cython_matches_python_on_generated_cases() -> None:
    try:
        smith_waterman_cython = smithwaterman_module._load_cython_module()
    except ImportError:
        pytest.skip("Cython extension not built")
    cases = generate_cases(problem_sizes=(0, 1, 2, 4, 8, 16, 32, 64, 128), random_cases_per_length=3)
    for case in cases:
        python_score = python_smith_waterman_score(case.sequence_a, case.sequence_b)
        cython_score = smith_waterman_cython.smith_waterman_score_cython(
            case.sequence_a,
            case.sequence_b,
            DEFAULT_MATCH_SCORE,
            DEFAULT_MISMATCH_SCORE,
            DEFAULT_GAP_SCORE,
        )
        assert python_score == cython_score, case.name


def test_executor_env_var_is_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    for value in ("Default", "DEFAULT", "default"):
        monkeypatch.setenv(EXECUTOR_ENV_VAR, value)
        assert smith_waterman_score("ACGT", "ACGT") == 8


@pytest.mark.parametrize(
    ("executor", "expected_impl", "expected_score"),
    [
        ("default", "python", 101),
        ("jit", "python", 101),
        ("pypy", "python", 101),
        ("cython", "cython", 202),
    ],
)
def test_executor_env_var_dispatches_to_expected_implementation(
    monkeypatch: pytest.MonkeyPatch,
    executor: str,
    expected_impl: str,
    expected_score: int,
) -> None:
    calls: list[str] = []

    def fake_python_impl(
        sequence_a: str,
        sequence_b: str,
        match: int = DEFAULT_MATCH_SCORE,
        mismatch: int = DEFAULT_MISMATCH_SCORE,
        gap: int = DEFAULT_GAP_SCORE,
    ) -> int:
        assert sequence_a == "ACGT"
        assert sequence_b == "ACGT"
        assert (match, mismatch, gap) == (
            DEFAULT_MATCH_SCORE,
            DEFAULT_MISMATCH_SCORE,
            DEFAULT_GAP_SCORE,
        )
        calls.append("python")
        return 101

    def fake_cython_score(sequence_a: str, sequence_b: str, match: int, mismatch: int, gap: int) -> int:
        assert sequence_a == "ACGT"
        assert sequence_b == "ACGT"
        assert (match, mismatch, gap) == (
            DEFAULT_MATCH_SCORE,
            DEFAULT_MISMATCH_SCORE,
            DEFAULT_GAP_SCORE,
        )
        calls.append("cython")
        return 202

    monkeypatch.setattr(smithwaterman_module, "_python_impl", fake_python_impl)
    monkeypatch.setattr(
        smithwaterman_module,
        "_load_cython_module",
        lambda: SimpleNamespace(smith_waterman_score_cython=fake_cython_score),
    )
    monkeypatch.setenv(EXECUTOR_ENV_VAR, executor)

    assert smith_waterman_score("ACGT", "ACGT") == expected_score
    assert calls == [expected_impl]


def test_package_entrypoint_uses_default_executor_when_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(EXECUTOR_ENV_VAR, raising=False)
    assert smith_waterman_score("ACGT", "ACGT") == python_smith_waterman_score("ACGT", "ACGT")


def test_package_entrypoint_uses_cython_when_selected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(EXECUTOR_ENV_VAR, "cython")
    assert smith_waterman_score("ACGT", "ACGT") == python_smith_waterman_score("ACGT", "ACGT")


def test_package_entrypoint_uses_cython_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(EXECUTOR_ENV_VAR, "cython")

    def fake_cython_score(sequence_a: str, sequence_b: str, match: int, mismatch: int, gap: int) -> int:
        assert (match, mismatch, gap) == (
            DEFAULT_MATCH_SCORE,
            DEFAULT_MISMATCH_SCORE,
            DEFAULT_GAP_SCORE,
        )
        return python_smith_waterman_score(sequence_a, sequence_b)

    monkeypatch.setattr(
        "helpers.smithwaterman._load_cython_module",
        lambda: SimpleNamespace(smith_waterman_score_cython=fake_cython_score),
    )

    assert smith_waterman_score("ACGT", "ACGT") == 8


def test_massive_default_case_count() -> None:
    cases = generate_cases()
    assert len(cases) == 20


def test_default_problem_sizes_are_bio_scale() -> None:
    assert DEFAULT_PROBLEM_SIZES == (100, 1000)
