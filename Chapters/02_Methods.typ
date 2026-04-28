#let methods_content = [
  = Methods

  == Design

  The following strategies were used to ensure the benchmark was as fair as possible to each runtime, while playing to their individual strengths:

  - Each runtime is given the same generated sequence pairs as input
  - Each runtime is given the same number of warm-up iterations whether or not they'd theoretically benefit from them
  - Each runtime was tested with problem sizes ranging from very short (\~100 characters) to very long (\~10,000 characters)
  - The Cython version of the algorithm uses type annotations (`#cdef`) and was statically compiled (/MT flag) with default optimizations
  - Each run is executed in a separate subprocess, but nevertheless run sequentially (no parallelism)
  - The timing for each run was measured using the same method (`time.perf_counter_ns()`)
  - Memory usage was not measured, as a method to do so that would be completely fair to all runtimes could not be found
  - Every run was executed on the exact same hardware, on the same operating system (Windows 11 x64 version 25H2)

  The benchmark code is available in the supplementary materials, with the entrypoint being `benchmark_sw.py`.

  == Hardware Specifications

  The tests were run on a laptop with the following specifications:

  - CPU model: Intel Core i5-10210U
  - CPU cores: 4 @intel
  - CPU threads: 8 @intel
  - CPU base frequency: 1.60 GHz @intel
  - CPU max turbo frequency: 4.20 GHz @intel
  - RAM: 16 GB DDR4 2933 MT/s
  - Storage: 512 GB NVMe SSD

  To reduce interference, the tests were run with no other applications active apart from the @ide:short (VS Code), with the laptop connected to power, and with heavy background processes such as Windows Update disabled.

  == Python Runtimes and Tools

  The test were performed on the following runtimes (@runtime_table):

  #figure(
    {
      show table.cell: set block(breakable: true)
      table(
        columns: (auto, auto, auto),
        inset: 6pt,
        align: left,
        stroke: (x: 0.8pt, y: 0.8pt),
        table.header([*Runtime*], [*Version*], [*Implementation Type*]),
        [CPython], [3.14.3], [Interpreter (default Python runtime)],
        [CPython JIT], [3.14.3], [Copy-and-patch JIT compiler],
        [PyPy], [7.3.20 with @msvc v.1941 (Python 3.11.13)], [Tracing JIT compiler],
        [Cython], [3.2.4 with @msvc v.1944 (Python 3.14.3)], [Transpiler to C],
      )
    },
    caption: "The runtimes included in the benchmark and their specifications.",
  ) <runtime_table>

  Additionally, the following Python packages were indispensible in the analysis and plotting of the results (@packages_table):

  #figure(
    {
      show table.cell: set block(breakable: true)
      table(
        columns: (auto, auto, auto),
        inset: 6pt,
        align: left,
        stroke: (x: 0.8pt, y: 0.8pt),
        table.header([*Package*], [*Version*], [*Purpose*]),
        [Pandas], [3.0.1], [Data manipulation and analysis],
        [NumPy], [2.4.2], [Numerical computing],
        [Matplotlib], [3.10.8], [Plotting and visualization],
        [JupyterLab], [4.5.5], [Notebook environment for interactive analysis],
      )
    },
    caption: "The additional (non-stdlib) Python packages used in the project. Only the primary packages are listed, not their dependencies.",
  ) <packages_table>

  == Dataset

  The dataset was generated synthetically using the DNA alphabet (A, C, G, T) to cover a few common scenarios encountered in bioinformatics. The specific tested scenarios, and the rationale behind their choice, are described in @scenario_table.


  #figure(
    {
      show table.cell: set block(breakable: true)
      table(
        columns: (1.3fr, 1fr, 1.1fr, 3fr),
        inset: 6pt,
        align: left,
        stroke: (x: 0.8pt, y: 0.8pt),
        table.header([*Scenario Name*], [*Length of A*], [*Length of B*], [*Description*]),
        [Homologous region],
        [$p$],
        [$p$],
        [Two mostly identical sequences that differ by a limited number of substitutions, as expected for homologous regions that diverged through mutation @homologous.],

        [Indel disruption],
        [$p$],
        [$p +/- p / 8$],
        [Homologous sequences that additionally contain a significant insertion or deletion event @homologous.],

        [Conserved motif],
        [$p$],
        [$p$],
        [A short conserved element embedded in otherwise unrelated sequence context, as observed in interspersed repeats @interspersedrepeats and transposons @transposons.],

        [Contained fragment],
        [$p / 2$],
        [$p / 3 + p / 2 + p / 4$],
        [A shorter sequence contained within a longer one. The "needle in a haystack" scenario.],

        [Random uniform], [$p$], [$p$], [Unrelated sequences of the same length. Serves as a baseline.],
      )
    },
    caption: [Description of the synthetic scenario families used in the @sw:long benchmark. $p$ denotes the problem size.],
  ) <scenario_table>

  The sequences were generated using a custom script (available in the supplementary materials under `Code/helpers/case_generation.py`). To ensure reproducibility, the random seed was set to 42. The problem size $p$ was tested at 100, 200, 500, 800, 1000, 2000, 5000, 8000, and 10,000 characters. For each problem size and scenario, 10 sequence pairs were generated, and each sequence pair was tested on each runtime 12 times (2 warmup runs and 10 timed runs) to account for variablity at the system-level. The median was chosen as the summary statistic for the timed runs to account for outliers, and the correctness of the scores were validated by checking them against the CPython interpreter implementation.

]
