#let introduction_content = [
  = Introduction

  == Background

  Python @python has emerged to be the most widely used programming language among many fields, including bioinformatics@pythonbioinf. It has many strengths, such as a very beginner friedly syntax, an exceptionally large ecosystem of packages, dynamic typing, and a feature rich standard library. One area where it is clearly lacking, however, is performance. This is due to the fact that the default implementation of Python, CPython, is interpreted and dynamically typed, which leads to significant overhead at runtime.

  #quote(
    "The Python interpreter does a lot of work to try to abstract away the underlying computing elements that are being used. At no point does a programmer need to worry about allocating memory for arrays, how to arrange that memory, or in what sequence it is being sent to the CPU. This is a benefit of Python, since it lets you focus on the algorithms that are being implemented. However, it comes at a huge performance cost.",
    attribution: [#cite(<pythonperf>, form: "prose")],
    block: true,
  )

  Many solutions have been proposed to address this issue while still remaining within the Python ecosystem. Chief among them are:
  - Transpilation into C using Cython @cython
  - Tracing @jit compilation, as implemented in an alternative Python interpreter to CPython, called PyPy @pypy
  - Copy-and-patch @jit compilation, as proposed in @pep:short 744 @pythonjit, and with the latest stable implementation as of writing in Python 3.14 @python314.

    This is far from an exhaustive list. Many other approaches exist, such as the .NET-based IronPython @ironpython, the Python superset Mojo @mojo, etc., but due to the limited scope of this paper and the fact that these are either not as mature or as frequently maintained as the ones mentioned above, they will not be included in this comparison.

  === Cython

  Cython is a python module that allows users to write Python code interspersed with optional type annotations (in the form of `#cdef <variable>: <type>`). The file is then saved as a `.pyx` file and transpiled into C code using its _cythonize_ toolchain. In the end, it creates a compiled module (a `.pyd` file on Windows, `.so` on Linux) using `setuptools` that can be imported and used from Python just like any regular module (see @cythonfigure). This naturally requires a compiler such as the @gcc or @msvc to be installed on the system @cython.

  // Cython build pipeline as a figure:
  #figure(
    image("../Code/Graphics/cython_transpilation_workflow.pdf", width: 75%),
    caption: "The Cython build pipeline, from a .pyx file to a compiled extension module.",
  ) <cythonfigure>

  === PyPy

  PyPy is an alternative implementation of the Python language, which features a tracing @jit compiler. It is a drop-in replacement for CPython, meaning that most Python code can be run on PyPy without modification.

  PyPy runs on RPython @rpython, a subset of Python that is used to implement the PyPy interpreter itself. When a Python program is run on PyPy, the interpreter starts executing the code using an interpreter loop, similar to CPython. However, as it runs, it collects profiling information about which parts of the code are executed frequently (called "hot loops"). When it identifies such hot loops, it compiles them into native machine code using a tracing @jit compiler, which can lead to significant performance improvements for long-running programs after a @warm_up_phase @pypy_interpreter.

  The latest stable version of PyPy as of writing supports upto Python 3.11 @pypy, and according to the PyPy team, it is on average 3 times faster than CPython 3.11 @pypy_performance.

  === CPython @jit

  The CPython @jit is a new experimental addition to the CPython codebase, which was added in Python 3.14 @python314. It is a copy-and-patch @jit compiler, which means that instead of tracing hot loops and compiling them, it allows developers to write optimized versions of certain "hot" functions in C, and then at runtime, it patches the CPython bytecode to call these optimized versions instead of the original Python implementations @pythonjit.

  === The Benchmarking Algorithm

  The @sw algorithm @smith_waterman is a very common algorithm in bioinformatics. It is a @local_alignment algorithm that computes the highest-scoring matching subsequence(s) between two DNA/RNA/protein sequences (see @swfigure). It is a very computationally intensive algorithm, with a time complexity of O(m*n) for two sequences of length m and n, so a naive implementation in Python is expected to perform very poorly. The algorithm nevertheless has two nested "hot loops", which the performance-minded runtimes could potentially optimize. That, and the fact that it is still the best non-heuristic local alignment algorithm, and that it is relatively simple to implement (fewer than 100 lines of code), were the reasons why it was chosen as the algorithm for this performance comparison.

  // Example of a smith-waterman alignment:
  #figure(
    image("../Code/Graphics/smith_waterman_alignment_example.pdf", width: 75%),
    caption: "Example of a local alignment between two DNA sequences, as produced by the Smith-Waterman algorithm.",
  ) <swfigure>

  == Research Question

  How does the @sw algorithm perform across the different Python runtimes, namely the default CPython interpreter, the newer CPython @jit, PyPy, and Cython?

  == Hypotheses

  - H0: There is no significant difference in the execution time of the Smith-Waterman algorithm across CPython, CPython JIT, PyPy, and Cython.

  - H1: There is a significant difference in the execution time of the Smith-Waterman algorithm across CPython, CPython JIT, PyPy, and Cython.




]
