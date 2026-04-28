#let discussion_content = [
  = Discussion
  As is clear from the findings, the choice of Python runtime has a significant impact on the performance of the @sw:long algorithm. The results from @speedup_plot clearly show that PyPy offers, at minimum, a 6x speedup over CPython, even at the smallest problem size of 100 characters. This performance gap widens even further as the problem size increases, with PyPy achieving up to a 12-14x speedup at the largest tested size of 10,000 characters. Its throughput (@throughput_plot) is also substantially higher than every other runtime, and it demonstrates the only scaling exponent (@scaling_plot) that is clearly below the theoretical $O(n^2)$ baseline. These results suggest that PyPy's tracing @jit approach is particularly effective at optimizing this specific class of problem (dynamic programming involving nested loops).

  The statically compiled Cython implementation also demonstrates a speedup (2-4x the CPython interpreter baseline, see @speedup_plot and @runtime_boxplot). This still lags behind PyPy by a large margin, but is nevertheless noteworthy because a compiled Cython module is much easier to integrate into existing Python codebases than PyPy. This makes Cython a compelling option for scenarios where one small module is bottlenecking an otherwise efficient workflow.

  The CPython 3.14 JIT compiler, despite being in the early stages of development, already shows modest improvements over the standard CPython interpreter. The JIT compiler's performance is likely to improve in the future if it continues to be developed and optimized.

  == Limitations

  The benchmark presented in this paper is limited to a single algorithm (@sw:long) and a specific set of synthetic sequence scenarios, with a rather small maximum problem size (10,000 characters). Additionally, the benchmark focuses solely on runtime performance and does not consider other important factors such as memory usage. Moreover, the performance of the @copy_and_patch @jit compilers may vary drastically depending on the specific CPU architecture.
]
