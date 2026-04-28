#let results_content = [
  = Results

  == Runtime by Scenario and Problem Size

  @runtime_by_scenario_plot measures the median runtime (in milliseconds) for each runtime, grouped by scenario and plotted over the tested problem sizes. Each panel corresponds to one synthetic sequence scenario, and the vertical axis is shown on a logarithmic scale so that differences across the full size range remain visible in the same figure.

  #figure(
    image("../Code/Results/plots/runtime_by_scenario.pdf", width: 80%),
    caption: [Median runtime by scenario and problem size for the four tested Python execution modes.],
  ) <runtime_by_scenario_plot>

  == Speedup Relative to CPython

  @speedup_plot measures runtime speedup relative to the CPython baseline. A value above 1 indicates that the runtime is faster than CPython, while a value below 1 indicates that it is slower.
  #figure(
    image("../Code/Results/plots/speedup_vs_cpython.pdf", width: 80%),
    caption: [Speedup relative to CPython across scenarios and problem sizes.],
  ) <speedup_plot>

  == Runtime Distribution Across Cases

  @boxplot_plot measures the spread of per-case median runtimes for each runtime at each tested problem size. Unlike the previous figure, which aggregates by scenario and size, this plot emphasizes the distribution across all generated cases at a given problem size (including the scenarios with unbalanced A and B lengths). The vertical axis is logarithmic, and each box summarizes the variability over the case-level medians.

  #figure(
    image("../Code/Results/plots/runtime_boxplot.pdf", width: 80%),
    caption: [Distribution of per-case median runtimes by runtime and problem size.],
  ) <boxplot_plot>

  == Throughput

  @throughput_plot measures computational throughput in millions of dynamic-programming cells per second. A higher throughput indicates that the runtime is able to process more of the dynamic-programming matrix per unit time.

  #figure(
    image("../Code/Results/plots/throughput_by_size.pdf", width: 80%),
    caption: [Throughput in millions of dynamic-programming cells per second across scenarios and problem sizes.],
  ) <throughput_plot>

  == Empirical Scaling Exponent

  @scaling_plot summarizes how strongly the measured runtime increases as the input size increases, specifically for the "random uniform" scenario (although the plot looks almost identical for all tested scenarios). The plot fits a power-law model of the form $t(n) = c n^alpha$, where $t$ is runtime, $c$ is a constant factor, and $alpha$ is the scaling exponent. In the implemented analysis, $n$ is not the nominal problem size $p$ directly, but the effective alignment size

  $
    n = sqrt(l e n(A) * l e n(B)),
  $

  so that unequal sequence lengths (as seen in the contained fragment and indel disruption scenarios) are still represented by a single size variable.

  Taking logarithms turns the power law into a linear relation:

  $
    log t = log c + alpha log n.
  $

  Defining $x_i = log n_i$ and $y_i = log t_i$, $hat(alpha)$ denotes the estimated scaling exponent, obtained by fitting a linear regression to the log-log data points @powerlaw:

  $
    hat(alpha) = (sum_i (x_i - overline(x))(y_i - overline(y))) / (sum_i (x_i - overline(x))^2).
  $

  The bars therefore report fitted growth rates rather than raw runtimes, and the dotted reference line marks the theoretical quadratic case $alpha = 2$.

  #figure(
    image("../Code/Results/plots/scaling_exponent.pdf", width: 100%),
    caption: [Empirical scaling exponent derived from log-log fits of runtime against problem size.],
  ) <scaling_plot>
]
