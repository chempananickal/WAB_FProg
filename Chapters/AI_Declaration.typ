#let ai_declaration_intro = [
  The usage of AI tools within this project is documented here. I declare that I have documented all interactions with AI tools, including the prompts used and the outputs received.
]

#let ai_declaration_entries = (
  (
    system: [GitHub Copilot 1],
    prompt: [I want you to rewrite my template from LaTeX to Typst, and make it look like it did before.],
    usage: [Recreated the template in Typst, maintaining the original appearance.],
  ),
  (
    system: [GitHub Copilot 2],
    prompt: [I want you to write some tests Comparing the Python 3.14 JIT Compiler, PyPy, and Cython implementations of the Smith-Waterman algorithm.],
    usage: [Created a test suite that benchmarks the Python 3.14 JIT Compiler, PyPy, and Cython implementations of the Smith-Waterman algorithm.],
  ),
  (
    system: [GitHub Copilot 3],
    prompt: [Put the test code in Code/, and use Python 3.15 instead of 3.14.],
    usage: [Added a runtime-generated Smith-Waterman validation and benchmarking suite in Code and retargeted the project text from Python 3.14 to Python 3.15.],
  ),
  (
    system: [GitHub Copilot 4],
    prompt: [Okay, use python 3.14. 3.15 is still in pre-release. I've created the conda env named smith and installed the packages],
    usage: [Retargeted the Smith-Waterman suite and Exposé references back to Python 3.14 and validated the project against the configured environment.],
  ),
  (
    system: [GitHub Copilot 5],
    prompt: [I think the warmup runs should be timed too. We can and should somehow separate it in the final summary though.],
    usage: [Modified the runtime worker to time each warmup repetition individually. Added a `per_run_times.csv` output that records every run's time with an `is_warmup` flag, keeping warmup and timed runs clearly separated in the data.],
  ),
  (
    system: [GitHub Copilot 6],
    prompt: [It'd also be interesting to see how the performance evolves across runs per algorithm, so make a plot of that.],
    usage: [Added a `run_convergence.pdf` plot showing runtime relative to each case's stable median across all run indices, with the warmup region shaded, faceted by problem size.],
  ),
  (
    system: [GitHub Copilot 7],
    prompt: [The runtime distributions per case and algorithm would also be interesting to see, maybe as a box plot?],
    usage: [Added a `runtime_distributions.pdf` box plot showing the distribution of runtimes per case and algorithm, faceted by problem size.],
  ),
  (
    system: [GitHub Copilot 8],
    prompt: [Add a power law fit of the runtime scaling with input size, and plot the empirical scaling exponent.],
    usage: [Added an empirical scaling exponent plot (`scaling_exponent.pdf`) fitting $t prop n^alpha$ via OLS in log-log space with 95% CI error bars, and a warmup penalty plot. The warmup penalty plot was subsequently removed for being too confusing to interpret.],
  ),
  (
    system: [GitHub Copilot 9],
    prompt: [Move the run convergence plotting stuff to a new jupyter notebook. I might need to isolate that to singular scenarios too. Also move the scaling exponent plotting code in there.],
    usage: [Created `Code/plotting.ipynb` with interactive controls for both the run convergence and empirical scaling exponent plots. Both sections have filter controls for scenario, problem size, and algorithm, and the scaling exponent can be faceted per scenario to compare behaviour across input types.],
  ),
)
