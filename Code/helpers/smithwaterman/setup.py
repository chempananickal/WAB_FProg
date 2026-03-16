from __future__ import annotations

import os
import sys
from pathlib import Path

from setuptools import Extension, setup

try:
    from Cython.Build import cythonize
except ImportError as exc:
    raise RuntimeError("Cython must be installed to build smith_waterman_cython.") from exc


def _extension_args() -> tuple[list[str], list[str]]:
    compile_args: list[str] = []
    link_args: list[str] = []

    if os.name == "nt":
        compile_args.append("/MT")
    else:
        link_args.append("-static-libgcc")
        if sys.platform == "darwin":
            link_args.clear()

    return compile_args, link_args


ROOT_DIR = Path(__file__).resolve().parents[2]
os.chdir(ROOT_DIR)

extra_compile_args, extra_link_args = _extension_args()

extensions = [
    Extension(
        name="helpers.smithwaterman.smith_waterman_cython",
        sources=["helpers/smithwaterman/smith_waterman_cython.pyx"],
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
]

setup(
    ext_modules=cythonize(extensions, language_level="3"),
)