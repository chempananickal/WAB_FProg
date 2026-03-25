#let exposee_content = [
  = Introduction
  Python @python has emerged to be the most widely used programming language among many fields, including bioinformatics@pythonbioinf. It has many strengths, such as a very beginner friedly syntax, an exceptionally large ecosystem of packages, dynamic typing, and a feature rich standard library. One area where it is clearly lacking, however, is performance. This is due to the fact that the default implementation of Python, CPython, is interpreted and dynamically typed, which leads to significant overhead at runtime.

  #quote(
    "The Python interpreter does a lot of work to try to abstract away the underlying computing elements that are being used. At no point does a programmer need to worry about allocating memory for arrays, how to arrange that memory, or in what sequence it is being sent to the CPU. This is a benefit of Python, since it lets you focus on the algorithms that are being implemented. However, it comes at a huge performance cost.",
    attribution: [#cite(<pythonperf>, supplement: [p. 11])],
    block: true,
  )

  Many solutions have been proposed to address this issue while still remaining within the Python ecosystem. Chief among them are:
  - Transpilation into C using Cython @cython
  - Tracing @jit compilation, as implemented in an alternative Python interpreter to CPython, called PyPy @pypy_performance
  - Copy-and-patch @jit compilation, as proposed in @pythonjit, and with the latest stable implementation in Python 3.14 @python314.

  The native @jit approach is by far the newest, and it's still under active development and marked as experimental.

  The @sw algorithm @smith_waterman is a very common algorithm in bioinformatics. It is a @local_alignment algorithm that computes the highest-scoring matching subsequence(s) between two DNA/RNA/protein sequences. It is a very computationally intensive algorithm, with a time complexity of O(m*n) for two sequences of length m and n, so a naive implementation in Python is expected to perform very poorly. The algorithm nevertheless has two nested "hot loops", which the performance-minded runtimes could potentially optimize. That, and the fact that it is still the best non-heuristic local alignment algorithm, and that it is relatively simple to implement (fewer than 100 lines of code), were the reasons why it was chosen as the algorithm for this performance comparison.

  = Research Question

  How does the @sw algorithm perform across the different Python runtimes, namely the default CPython interpreter, the newer CPython @jit, PyPy, and Cython?

  = Hypothesis
  The hypothesis is that either Cython or PyPy will outperform the rest by a wide margin in terms of execution time. PyPy is expected to show a warm-up effect: early runs should be slower, while later runs should become faster once the tracing @jit compiler has optimized frequently executed code paths. Afterward, performance is expected to stabilize. Cython's execution time should be very fast from the first run, since it is transpiled into C and compiled ahead of time.

  The native @jit implementation is still in its infancy, therefore it may not perform better than PyPy and Cython, but it is still expected to outperform the default CPython interpreter.

  = Objectives

  The main objectives of this paper are as follows:
  - To compare the performance of the @sw algorithm across CPython, CPython with native @jit, PyPy, and Cython.
  - To evaluate how different runtime and compilation strategies affect execution time for this computationally intensive bioinformatics algorithm.
  - To identify the strengths and limitations of each runtime for this specific use case.

  = Methodology

  The benchmarking methodology is designed to make the comparison between runtimes as fair and reproducible as possible. The same @sw implementation will be used across the default CPython interpreter, CPython with native @jit enabled, and PyPy.

  For Cython, the same algorithm will be transferred into a corresponding `.pyx` implementation with type annotations where necessary, and compiled as a native extension module with Cython and `setuptools`. Since this test will be run on Windows 11, this build step relies on the Microsoft C++ build tools. The compiled module is then loaded from CPython and executed through the same benchmark interface as the pure Python implementations, so that the main difference under comparison is the compilation strategy rather than a completely different program structure.

  A list of DNA sequence pairs benchmark cases will be generated synthetically, and will include a few specific scenarios likely to be encountered in real-world bioinformatics applications, in addition to random string pairs. The benchmark is likely to target sequences of lengths from 100 to 1000 in increments of 200, since much larger sequences would lead to prohibitively long execution times as the time complexity is quadratic. To ensure a fair comparison, the exact same generated cases will be reused across all runtimes.

  Each case will then be executed on four runtimes sequentially: CPython, CPython with native @jit, PyPy, and Cython. For every case-runtime combination, two warm-up runs will be executed first and then ten timed runs per sequence pair will be measured. The median of these timed runs will be used as the representative execution time for that case in order to reduce the influence of outliers. In addition, the alignment scores produced by each runtime will be checked against the CPython baseline to ensure that incorrectness is not mistaken for performance differences.

  The collected raw runtime measurements will then be aggregated by scenario and problem size, and analyzed with statistical methods and visualizations.

  = Planned Structure

  The paper will likely be structured as follows:

  - Introduction
  - Background and Related Work
  - Methodology
  - Results
  - Discussion
  - Conclusion and Future Work
  - References
  - AI Declaration
  - Declaration of Authorship
]
