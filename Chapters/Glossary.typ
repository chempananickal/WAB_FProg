#let glossary_group = "Glossary"
#let abbreviation_group = "Abbreviations"

#let all_glossary_entries = (
  smith_waterman: (
    short: "Smith-Waterman alignment",
    description: "A dynamic-programming algorithm for local sequence alignment that computes the highest-scoring matching subsequences between two input sequences.",
    group: glossary_group,
  ),
  local_alignment: (
    short: "local alignment",
    description: "An alignment strategy that searches for the best matching subsections of two sequences instead of forcing an end-to-end alignment.",
    group: glossary_group,
  ),
  warm_up_phase: (
    short: "warm-up phase",
    description: "The initial execution period in which a JIT-enabled runtime collects profiling information and may compile hot paths before reaching steady-state performance.",
    group: glossary_group,
  ),
  benchmark_harness: (
    short: "benchmark harness",
    description: "The controlled code and tooling used to execute reproducible performance measurements across implementations and runtimes.",
    group: glossary_group,
  ),
  differential_testing: (
    short: "differential testing",
    description: "A testing strategy that compares the outputs of multiple implementations against the same inputs to detect behavioral deviations.",
    group: glossary_group,
  ),
  jit: (
    short: "JIT",
    long: "Just-in-Time",
    group: abbreviation_group,
  ),
  dp: (
    short: "DP",
    long: "Dynamic Programming",
    group: abbreviation_group,
  ),
  sw: (
    short: "SW",
    long: "Smith-Waterman",
    group: abbreviation_group,
  ),
  ci: (
    short: "CI",
    long: "Continuous Integration",
    group: abbreviation_group,
  ),
)
