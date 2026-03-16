#let exposee_content = [
  = Introduction
  Python@python has emerged to be the most widely used programming language among many fields, including bioinformatics@pythonbioinf. It has many strengths, such as a very beginner friedly syntax, an exceptionally large ecosystem of packages, dynamic typing, and a feature rich standard library. One area where it is clearly lacking, however, is performance. This is due to the fact that the default implementation of Python, CPython, is interpreted and dynamically typed, which leads to significant overhead at runtime.

  Many solutions have been proposed to address this issue while still remaining within the Python ecosystem. These are:
  - Transpilation into C using Cython@cython
  - Tracing @jit compilation, as implemented in an alternative Python interpreter to CPython, called PyPy@pypy_performance
  - Copy-and-patch @jit compilation, as proposed in @pythonjit, and with the latest stable implementation in python 3.14@python314.

  The native @jit approach is by far the newest, and it's still under active development and marked as experimental.

  The @sw@smith_waterman algorithm is a very common algorithm in bioinformatics. It is a @local_alignment algorithm that computes the highest-scoring matching subsequence(s) between two DNA/RNA/protein sequences. It is a very computationally intensive algorithm, with a time complexity of O(m*n) for two sequences of length m and n, so a naive implementation in Python is expected to perform very poorly. The algorithm nevertheless has two nested "hot loops", which the performance-minded runtimes could potentially optimize. That, and the fact that it is still the best non-heuristic local alignment algorithm, and that it is relatively simple to implement (fewer than 100 lines of code), were the reasons why it was chosen as the algorithm for this performance comparison.

  = Research Question

  How does the @sw algorithm perform across the different Python runtimes, namely the default CPython interpreter, the newer Cpython @jit, PyPy, and Cython?

  = Objectives

  The main objectives of this paper are as follows:
  - To write the same implementation of the @sw algorithm in a way that can be executed across all three runtimes with minimal changes.
  - To write a benchmark suite that can be used to execute reproducible performance measurements across all three runtimes.
  - To analyze the results and identify the strengths and weaknesses of each runtime for this specific use case.

  = Planned Structure

  The paper will likely be structured as follows:

  - Introduction
  - Research Question and Motivation
  - Methodology
  - Results
  - Discussion
  - Conclusion and Future Work
  - References
  - AI Declaration
  - Declaration of Authorship
]
