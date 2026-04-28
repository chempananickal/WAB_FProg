#let conclusion_content = [
  = Conclusion

  This thesis investigated how different Python execution environments affect the performance of the @sw:long local sequence alignment algorithm. To answer this question, a benchmark suite was developed and used to compare the standard CPython interpreter, the experimental CPython 3.14 @jit compiler, PyPy, and Cython across multiple synthetic sequence scenarios and problem sizes.

  The results show that the choice of runtime has a substantial impact on execution speed. PyPy consistently achieved the strongest performance and highest throughput across the tested workloads. The Cython implementation also improved performance over the CPython baseline, although to a smaller extent, while offering the practical advantage of being easier to integrate into an otherwise standard Python workflow. The CPython 3.14 @jit showed promising but limited gains.

  Overall, the findings indicate that significant performance improvements for dynamic-programming workloads can be achieved without abandoning Python as a language. For @sw:long in particular, PyPy appears to be the strongest choice when changing the full runtime is acceptable, whereas Cython is a practical compromise when targeted optimization of individual modules is preferred.

  == Future Work

  Future research could explore the performance of additional runtimes. Of particular interest are Numba @numba, a @jit compiler that specializes in numerical code and has strong numpy support, and Mojo @mojo, a new language that is designed for python compatibility while offering performance comparable to system programming languages. Future versions of the CPython @jit compiler could also be analyzed if the project reaches a more mature state.

  Additionally, the runtimes could be tested on a wider range of bioinformatics algorithms and workloads, including those that involve more complex data structures (like suffix automata @sam). Finally, future benchmarks could also measure additional performance metrics such as memory usage.
]
