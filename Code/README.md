# Smith-Waterman Benchmark Suite

This benchmark suite evaluates the performance of a Smith-Waterman local sequence alignment implementation across multiple Python runtimes and execution modes. It is designed to provide insights into the trade-offs between pure Python, JIT compilation, PyPy's optimizations, and Cython's native extensions for a computationally intensive algorithm.

## Structure

- `benchmark_sw.py`: main benchmark entrypoint
- `helpers/`: benchmarking, case generation, statistics, and a nested `smithwaterman/` package for the algorithm/runtime code
- `Results/`: generated raw runs, case scores, and summary statistics
- `Results/plots/`: generated PDF figures for paper inclusion
- `tests/`: correctness and generator tests

The suite compares Smith-Waterman local alignment scores across four execution modes:

- CPython 3.14
- CPython 3.14 with JIT
- PyPy
- Cython on CPython 3.14

The `helpers.smithwaterman` package exposes a single scoring function. Runtime selection is driven by the `EXECUTOR` environment variable with the values `DEFAULT`, `JIT`, `PYPY`, or `CYTHON`.

## Windows Prerequisites

Before running the benchmark suite on Windows, install the Visual Studio C++ build tools so Cython extensions can compile.

1. Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
2. In the installer, select the `Desktop development with C++` workload.
3. Download and install [PyPy](https://www.pypy.org/download.html).
4. Make sure the PyPy executable is on `PATH` so `pypy` or `pypy3` resolves in a terminal.
5. Bootstrap `pip` inside PyPy.

   ```powershell
   pypy -m ensurepip
   ```

6. Install `psutil` into the PyPy environment so memory measurements are comparable across runtimes.

   ```powershell
   pypy -m pip install psutil
   ```

## Quick Start

From the workspace root:

```powershell
python -m pip install -r Code/requirements.txt
python Code/benchmark_sw.py
```

If `pypy3` is not on your `PATH`, pass the full executable path with `--pypy`.

## Default Benchmark Shape

The default benchmark profile is intentionally biased toward fewer but larger bioinformatics-style cases rather than many tiny strings.

- default problem sizes: `100,1000`
- sequence pairs per scenario and problem size: `2`
- timed repetitions per case and runtime: `10`
- warmup repetitions: `2`

The benchmark scenarios are intentionally compact and biologically motivated:

- homologous regions with a small number of substitutions
- indel-heavy pairs with insertion or deletion events
- conserved motifs embedded in unrelated flanking sequence
- short fragments embedded in a longer sequence context
- random pairs as a baseline control

Case generation now lives entirely in `helpers/case_generation.py`. For each problem size, every scenario produces the same number of sequence pairs, controlled by `--cases-per-length`. Those exact pairs are then reused across CPython, CPython JIT, PyPy, and Cython for a fair comparison.

The result files also record `target_size`, `sequence_a_length`, and `sequence_b_length` so asymmetric local-alignment cases remain explicit in the data.

Within `helpers/smithwaterman/`, the pure-Python baseline lives in `smith_waterman_python.py` and the matching Cython port lives in `smith_waterman_cython.pyx`.

## Executor Selection

External tools should call `helpers.smithwaterman.smith_waterman_score` only.

- `EXECUTOR=DEFAULT` uses the pure Python implementation on the active interpreter.
- `EXECUTOR=JIT` uses the same Python implementation with CPython JIT enabled via `PYTHON_JIT=1`.
- `EXECUTOR=PYPY` uses the same Python implementation when the worker is launched with a PyPy executable.
- `EXECUTOR=CYTHON` loads or builds the Cython extension automatically and routes calls through it.

The benchmark runner sets `EXECUTOR` automatically for each subprocess it launches.

## Commands

Run benchmarks and generate plots:

```powershell
python Code/benchmark_sw.py --mode both
```

Run the same methodology on larger problem sizes:

```powershell
python Code/benchmark_sw.py --problem-sizes 100,1000,10000 --cases-per-length 1 --runs 1 --warmup 0
```

Generate plots from existing raw data without rerunning benchmarks:

```powershell
python Code/benchmark_sw.py --mode plot
```

## Output

By default, outputs are written to `Code/Results/`:

- `raw_runs.csv`: one row per case and runtime measurement, including target and per-sequence lengths
- `case_scores.csv`: generated sequence pairs and validated scores, including target and per-sequence lengths
- `summary_stats.csv`: aggregated timing and memory statistics
- `plots/runtime_by_scenario.pdf`: runtime curves by scenario and problem size
- `plots/memory_by_scenario.pdf`: memory curves by scenario and problem size
- `plots/speedup_vs_cpython.pdf`: runtime speedup relative to CPython
- `benchmark_config.txt`: benchmark settings used for the run

## Notes

- Runtime is measured with `time.perf_counter_ns`.
- Memory is approximated with simple per-case resident-set-size deltas via `psutil`.
- Each runtime runs in its own worker subprocess for the full benchmark workload, so PyPy and CPython JIT can warm up normally.
- Within that worker, each case records RSS before and after execution, while timing only measures the timed run loop.
- The benchmark enforces correctness by comparing every runtime against the CPython baseline score for the same generated case.
- The Cython extension is built automatically when needed. If the compiled module is missing, `helpers.smithwaterman` runs `python setup.py build_ext --inplace` from `helpers/smithwaterman/`.
- The local `setup.py` uses static-runtime flags where the platform toolchain supports them.
