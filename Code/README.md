# Smith-Waterman Benchmark Suite

This directory contains the code used to benchmark a Smith-Waterman local sequence alignment implementation across four Python execution modes:

- CPython 3.14
- CPython 3.14 with JIT enabled
- PyPy
- Cython on CPython 3.14

The `helpers.smithwaterman` package exposes a single scoring function. Runtime selection is driven by the `EXECUTOR` environment variable with the values `DEFAULT`, `JIT`, `PYPY`, or `CYTHON`.

## Windows Prerequisites

Before running the benchmark suite on Windows, install the Visual Studio C++ build tools so Cython extensions can compile.

1. Download and install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
2. In the installer, select the `Desktop development with C++` workload.
3. Install PyPy from [pypy.org](https://www.pypy.org/download.html).
4. Ensure `pypy` or `pypy3` resolves in a terminal, or plan to pass the full executable path via `--pypy`.
5. Bootstrap `pip` inside PyPy if needed.

```powershell
pypy -m ensurepip
```

## Quick Start

From the workspace root:

```powershell
python -m pip install -r Code/requirements.txt
python Code/benchmark_sw.py --mode both
```

If PyPy is not on `PATH`, pass it explicitly:

```powershell
python Code/benchmark_sw.py --mode both --pypy C:\Path\To\pypy3.exe
```

## Command-Line Options

`benchmark_sw.py` supports these main options:

- `--mode {run,plot,both}`: run benchmarks, regenerate plots from existing CSV data, or do both
- `--problem-sizes`: comma-separated target sizes
- `--cases-per-length`: number of generated sequence pairs per scenario and problem size
- `--runs`: number of timed repetitions per case
- `--warmup`: number of warmup repetitions before timed runs
- `--seed`: random seed for reproducible case generation
- `--pypy`: PyPy executable name or full path
- `--output-dir`: output directory, default `Code/Results`
- `--progress` / `--no-progress`: enable or disable single-line progress reporting

Current defaults are:

- problem sizes: `100,200,500,800,1000,2000,5000,8000,10000`
- cases per scenario per problem size: `10`
- warmup repetitions: `2`
- timed repetitions: `10`
- seed: `42`

Examples:

```powershell
python Code/benchmark_sw.py --mode run
python Code/benchmark_sw.py --mode plot
python Code/benchmark_sw.py --problem-sizes 100,1000,10000 --cases-per-length 2 --runs 5 --warmup 1
```

## Outputs

By default, all benchmark outputs are written to `Code/Results/`:

- `per_case_results.csv`: one row per case and runtime, containing median timed runtime, score, target size, and both sequence lengths
- `case_scores.csv`: generated input pairs and their validated Smith-Waterman scores from the CPython baseline
- `per_run_times.csv`: one row per individual run, including warmup runs, for convergence analysis
- `summary_stats.csv`: aggregated runtime summary statistics by scenario, size, and algorithm
- `benchmark_config.txt`: the exact benchmark configuration used for the run

`helpers/plotting.py` generates these plot files:

- `plots/runtime_by_scenario.pdf`
- `plots/speedup_vs_cpython.pdf`
- `plots/runtime_boxplot.pdf`
- `plots/throughput_by_size.pdf`
- `plots/run_convergence.pdf`

The empirical scaling figure, `plots/scaling_exponent.pdf`, is produced separately from `plotting.ipynb`, not by the batch CLI plot generator.

## Notebook Workflow

`plotting.ipynb` is used for interactive analysis that is easier to inspect manually than in the batch plot pipeline. It currently contains:

- run-convergence analysis based on `per_run_times.csv`
- empirical scaling exponent analysis and export of `scaling_exponent.pdf`

Use the notebook when you want to filter by scenario, problem size, or algorithm and inspect the behavior interactively.

## Tests

From the `Code/` directory, run:

```powershell
pytest
```

The tests cover both Smith-Waterman scoring behavior and synthetic scenario generation.

## Notes

- Runtime is measured with `time.perf_counter_ns()`.
- Correctness is enforced by comparing every non-CPython runtime result against the CPython baseline score for the same generated case.
- The benchmark records both `sequence_a_length` and `sequence_b_length`, so asymmetric cases remain explicit in the raw data.
- If the compiled Cython module is missing, `helpers.smithwaterman` automatically runs `python setup.py build_ext --inplace` from `helpers/smithwaterman/`.
- The local Cython `setup.py` uses static-runtime flags where the platform toolchain supports them.
