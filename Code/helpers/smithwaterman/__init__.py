import importlib
import importlib.machinery
import os
from pathlib import Path
import subprocess
import sys

from helpers.smithwaterman.smith_waterman_python import smith_waterman_score as _python_impl

EXECUTOR_ENV_VAR = "EXECUTOR"
_MODULE_NAME = "helpers.smithwaterman.smith_waterman_cython"
_MODULE_BASENAME = "smith_waterman_cython"

_VALID_EXECUTORS = frozenset({"default", "jit", "cython", "pypy"})


def _load_cython_module():
    try:
        return importlib.import_module(_MODULE_NAME)
    except ModuleNotFoundError as exc:
        if exc.name != _MODULE_NAME or _has_compiled_extension():
            raise

    _build_cython_extension()
    importlib.invalidate_caches()
    return importlib.import_module(_MODULE_NAME)


def _has_compiled_extension() -> bool:
    package_dir = Path(__file__).resolve().parent
    return any((package_dir / f"{_MODULE_BASENAME}{suffix}").exists() for suffix in importlib.machinery.EXTENSION_SUFFIXES)


def _build_cython_extension() -> None:
    setup_py = Path(__file__).parent / "setup.py"
    completed = subprocess.run(
        [sys.executable, str(setup_py), "build_ext", "--inplace"],
        cwd=Path(__file__).parent,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.returncode != 0:
        output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
        raise RuntimeError(
            "Unable to build helpers.smithwaterman.smith_waterman_cython automatically. "
            "Ensure the Python build requirements are installed and a working compiler toolchain is available.\n"
            f"{output}"
        )


def smith_waterman_score(
    sequence_a: str,
    sequence_b: str,
    match_score: int = 2,
    mismatch_score: int = -1,
    gap_score: int = -2,
) -> int:
    """Run Smith-Waterman using the executor selected by the EXECUTOR env var.

    EXECUTOR=default  Pure-Python (CPython)
    EXECUTOR=jit      Pure-Python with CPython JIT  (start Python with PYTHON_JIT=1)
    EXECUTOR=pypy     Pure-Python under PyPy        (run script with the PyPy interpreter)
    EXECUTOR=cython   Cython extension              (build first: python setup.py build_ext --inplace)
    """
    executor = os.environ.get(EXECUTOR_ENV_VAR, "default").lower().strip()

    if executor not in _VALID_EXECUTORS:
        raise ValueError(
            f"Unknown {EXECUTOR_ENV_VAR}={executor!r}. "
            f"Valid values: {', '.join(sorted(_VALID_EXECUTORS))}."
        )

    if executor == "cython":
        try:
            cython_module = _load_cython_module()
        except (ImportError, RuntimeError) as exc:
            raise ImportError(
                "Cython extension is unavailable and the automatic build failed. "
                "Run: python setup.py build_ext --inplace "
                "from Code/helpers/smithwaterman/."
            ) from exc
        return cython_module.smith_waterman_score_cython(
            sequence_a, sequence_b, match_score, mismatch_score, gap_score
        )

    # "default", "jit", and "pypy" all run the same pure-Python implementation.
    # The difference is in how you start the interpreter, not in this code.
    return _python_impl(sequence_a, sequence_b, match_score, mismatch_score, gap_score)

