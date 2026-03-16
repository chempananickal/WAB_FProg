#let exposee_content = [
  = Introduction
  Python@python has emerged to be the most widely used programming language among many fields, including bioinformatics@pythonbioinf. It has many strengths, such as a very beginner friedly syntax, an exceptionally large ecosystem of packages, dynamic typing, and a feature rich standard library. One area where it is clearly lacking, however, is performance. This is due to the fact that the default implementation of Python, CPython, is interpreted and dynamically typed, which leads to significant overhead at runtime.

  Many solutions have been proposed to address this issue while still remaining within the Python ecosystem. Thse are:
  - Transpilation into C using Cython@cython
  - Tracing @jit compilation, as implemented in an alternative Python interpreter to CPython, called PyPy@pypy_performance
  - Copy-and-patch @jit compilation, as proposed in @pythonjit, and with the latest stable implementation in python 3.14@python314.

  The native @jit approach is by far the newest, and it's still under active development and marked as experimental. So

  = Problem Statement

  = Objectives

  = Methodology

  == Test Suite Design

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
