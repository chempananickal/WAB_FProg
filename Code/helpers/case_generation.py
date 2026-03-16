from __future__ import annotations

from dataclasses import asdict, dataclass
from random import Random


DNA_ALPHABET = "ACGT"
DEFAULT_PROBLEM_SIZES = (100, 1000)
DEFAULT_RANDOM_CASES_PER_LENGTH = 2
DEFAULT_SEED = 42

SCENARIO_NAME_MAP = {
    "homologous": "homologous_region",
    "indel": "indel_disruption",
    "motif": "conserved_motif",
    "contained": "contained_fragment",
    "random": "random_uniform",
}


@dataclass(frozen=True, slots=True)
class BenchmarkCase:
    name: str
    family: str
    target_size: int
    sequence_a: str
    sequence_b: str

    @property
    def case_id(self) -> str:
        return f"{self.name}_n{self.target_size}"

    @property
    def sequence_a_length(self) -> int:
        return len(self.sequence_a)

    @property
    def sequence_b_length(self) -> int:
        return len(self.sequence_b)

    @property
    def scenario(self) -> str:
        return SCENARIO_NAME_MAP.get(self.family, self.family)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def generate_cases(
    problem_sizes: tuple[int, ...] = DEFAULT_PROBLEM_SIZES,
    random_cases_per_length: int = DEFAULT_RANDOM_CASES_PER_LENGTH,
    seed: int = DEFAULT_SEED,
) -> list[BenchmarkCase]:
    cases: list[BenchmarkCase] = []
    scenario_builders = [
        ("homologous", _make_homologous_case),
        ("indel", _make_indel_case),
        ("motif", _make_motif_case),
        ("contained", _make_contained_case),
        ("random", _make_random_case),
    ]

    for problem_size in problem_sizes:
        for family_index, (family, builder) in enumerate(scenario_builders):
            for case_index in range(random_cases_per_length):
                case_generator = Random(seed + problem_size * 1009 + family_index * 97 + case_index)
                cases.append(builder(problem_size, case_index, case_generator))

    return cases


def serialize_cases(cases: list[BenchmarkCase]) -> list[dict[str, object]]:
    return [case.to_dict() for case in cases]


def deserialize_cases(raw_cases: list[dict[str, object]]) -> list[BenchmarkCase]:
    return [BenchmarkCase(**raw_case) for raw_case in raw_cases]


def _make_homologous_case(problem_size: int, case_index: int, generator: Random) -> BenchmarkCase:
    sequence_a = _random_sequence(problem_size, generator)
    mutation_count = _bounded_count(problem_size, minimum=1, divisor=20)
    sequence_b = _mutate_positions(
        sequence_a,
        [_safe_index(problem_size, generator.randrange(max(1, problem_size))) for _ in range(mutation_count)],
    )
    return BenchmarkCase(
        name=f"homologous_{case_index}",
        family="homologous",
        target_size=problem_size,
        sequence_a=sequence_a,
        sequence_b=sequence_b,
    )


def _make_indel_case(problem_size: int, case_index: int, generator: Random) -> BenchmarkCase:
    sequence_a = _random_sequence(problem_size, generator)
    gap_length = _bounded_count(problem_size, minimum=1, divisor=8)
    insertion = _random_sequence(gap_length, generator)
    if case_index % 2 == 0:
        sequence_b = _insert_middle(sequence_a, insertion)
    else:
        sequence_b = _delete_middle_run(sequence_a, gap_length)
        sequence_b = _mutate_positions(
            sequence_b,
            [_safe_index(len(sequence_b), generator.randrange(max(1, len(sequence_b))))],
        )
    return BenchmarkCase(
        name=f"indel_{case_index}",
        family="indel",
        target_size=problem_size,
        sequence_a=sequence_a,
        sequence_b=sequence_b,
    )


def _make_motif_case(problem_size: int, case_index: int, generator: Random) -> BenchmarkCase:
    motif = _motif(_bounded_count(problem_size, minimum=4, divisor=6))
    sequence_a = _embed_motif(problem_size, motif, generator)
    sequence_b = _embed_motif(problem_size, motif, generator)
    return BenchmarkCase(
        name=f"motif_{case_index}",
        family="motif",
        target_size=problem_size,
        sequence_a=sequence_a,
        sequence_b=sequence_b,
    )


def _make_contained_case(problem_size: int, case_index: int, generator: Random) -> BenchmarkCase:
    fragment_length = _bounded_count(problem_size, minimum=1, divisor=2)
    fragment = _random_sequence(fragment_length, generator)
    left_flank = _random_sequence(_bounded_count(problem_size, minimum=0, divisor=3), generator)
    right_flank = _random_sequence(_bounded_count(problem_size, minimum=0, divisor=4), generator)
    sequence_b = left_flank + fragment + right_flank
    return BenchmarkCase(
        name=f"contained_{case_index}",
        family="contained",
        target_size=problem_size,
        sequence_a=fragment,
        sequence_b=sequence_b,
    )


def _make_random_case(problem_size: int, case_index: int, generator: Random) -> BenchmarkCase:
    return BenchmarkCase(
        name=f"random_{case_index}",
        family="random",
        target_size=problem_size,
        sequence_a=_random_sequence(problem_size, generator),
        sequence_b=_random_sequence(problem_size, generator),
    )


def _random_sequence(length: int, generator: Random) -> str:
    return "".join(generator.choice(DNA_ALPHABET) for _ in range(length))


def _mutate_positions(sequence: str, positions: list[int]) -> str:
    if not sequence:
        return sequence
    sequence_chars = list(sequence)
    for position in positions:
        index = max(0, min(len(sequence_chars) - 1, position))
        current = sequence_chars[index]
        sequence_chars[index] = "A" if current != "A" else "C"
    return "".join(sequence_chars)


def _insert_middle(sequence: str, insertion: str) -> str:
    middle_index = len(sequence) // 2
    return sequence[:middle_index] + insertion + sequence[middle_index:]


def _delete_middle_run(sequence: str, run_length: int) -> str:
    if not sequence or run_length <= 0:
        return sequence
    run_length = min(run_length, len(sequence))
    middle_index = len(sequence) // 2
    start_index = max(0, middle_index - (run_length // 2))
    end_index = min(len(sequence), start_index + run_length)
    return sequence[:start_index] + sequence[end_index:]


def _motif(size: int) -> str:
    if size <= 0:
        return ""
    return ("GATTACA" * ((size // 7) + 1))[:size]


def _embed_motif(length: int, motif: str, generator: Random) -> str:
    if length == 0:
        return ""
    if len(motif) >= length:
        return motif[:length]
    flank_length = length - len(motif)
    left_flank_length = generator.randrange(flank_length + 1)
    right_flank_length = flank_length - left_flank_length
    left_flank = _random_sequence(left_flank_length, generator)
    right_flank = _random_sequence(right_flank_length, generator)
    return left_flank + motif + right_flank


def _bounded_count(length: int, *, minimum: int, divisor: int) -> int:
    if length <= 0:
        return 0
    return max(minimum, length // divisor)


def _safe_index(length: int, candidate: int) -> int:
    if length <= 0:
        return 0
    return max(0, min(length - 1, candidate))