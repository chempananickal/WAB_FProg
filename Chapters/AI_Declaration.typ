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
    system: [GitHub Copilot 1],
    prompt: [I want you to write some tests Comparing the Python 3.14 JIT Compiler, PyPy, and Cython implementations of the Smith-Waterman algorithm.],
    usage: [Created a test suite that benchmarks the Python 3.14 JIT Compiler, PyPy, and Cython implementations of the Smith-Waterman algorithm.],
  ),
  (
    system: [GitHub Copilot 2],
    prompt: [Put the test code in Code/, and use Python 3.15 instead of 3.14.],
    usage: [Added a runtime-generated Smith-Waterman validation and benchmarking suite in Code and retargeted the project text from Python 3.14 to Python 3.15.],
  ),
  (
    system: [GitHub Copilot 3],
    prompt: [Okay, use python 3.14. 3.15 is still in pre-release. I've created the conda env named smith and installed the packages],
    usage: [Retargeted the Smith-Waterman suite and Exposé references back to Python 3.14 and validated the project against the configured environment.],
  ),
)
