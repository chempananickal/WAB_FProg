from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


BG = "#ffffff"
TEXT = "#1f2933"
MUTED = "#5b6570"
FILE_FILL = "#fffdf8"
PROC_FILL = "#eef4f0"
TOOL_FILL = "#eef2f7"
EDGE = "#cfc6b8"
ARROW = "#34495e"
FILE_ACCENT = "#c98a36"
PROC_ACCENT = "#4c956c"
TOOL_ACCENT = "#577590"


def _draw_document(ax: plt.Axes, x: float, y: float, width: float, height: float, title: str, detail: str) -> None:
    outer = mpatches.FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.01,rounding_size=0.03",
        facecolor=FILE_FILL,
        edgecolor=EDGE,
        linewidth=1.0,
        zorder=2,
    )
    ax.add_patch(outer)
    ax.add_patch(
        mpatches.Rectangle((x, y + height - 0.18), width, 0.18, facecolor=FILE_ACCENT, edgecolor="none", zorder=3)
    )
    ax.text(x + width / 2, y + height - 0.28, title, ha="center", va="top", fontsize=10.0, fontweight="bold", color=TEXT)
    ax.text(x + width / 2, y + 0.30, detail, ha="center", va="center", fontsize=7.9, color=MUTED, family="DejaVu Sans Mono")


def _draw_process(
    ax: plt.Axes,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str,
    detail: str,
    accent: str = PROC_ACCENT,
    fill: str = PROC_FILL,
) -> None:
    box = mpatches.Rectangle(
        (x, y),
        width,
        height,
        facecolor=fill,
        edgecolor=EDGE,
        linewidth=1.0,
        zorder=2,
    )
    ax.add_patch(box)
    ax.add_patch(mpatches.Rectangle((x, y + height - 0.16), width, 0.16, facecolor=accent, edgecolor="none", zorder=3))
    ax.text(x + width / 2, y + height - 0.26, title, ha="center", va="top", fontsize=9.8, fontweight="bold", color=TEXT)
    ax.text(x + width / 2, y + 0.26, detail, ha="center", va="center", fontsize=7.9, color=MUTED)


def _arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float], text: str | None = None, rad: float = 0.0) -> None:
    patch = mpatches.FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=12,
        linewidth=1.6,
        color=ARROW,
        connectionstyle=f"arc3,rad={rad}",
        zorder=5,
    )
    ax.add_patch(patch)
    if text:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        ax.text(mid_x, mid_y + 0.12, text, ha="center", va="bottom", fontsize=8.0, color=MUTED)


def render_figure(output_base: Path) -> list[Path]:
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": BG,
            "savefig.facecolor": BG,
            "font.family": "DejaVu Sans",
        }
    )

    fig, ax = plt.subplots(figsize=(8.6, 7.8))
    fig.subplots_adjust(left=0.06, right=0.97, top=0.92, bottom=0.06)
    ax.set_xlim(0, 8.6)
    ax.set_ylim(0, 8.1)
    ax.axis("off")

    fig.suptitle("Cython build pipeline", fontsize=18, fontweight="bold", color=TEXT, y=0.975)

    ax.text(4.30, 7.55, "Main transformation path", ha="center", va="center", fontsize=9.2, color=MUTED)

    _draw_document(ax, 2.85, 6.45, 2.90, 0.90, ".pyx source", "smith_waterman_cython.pyx")
    _draw_process(ax, 2.85, 5.00, 2.90, 0.92, "cythonize", "generate C from .pyx")
    _draw_document(ax, 2.85, 3.55, 2.90, 0.90, "generated C", "smith_waterman_cython.c")
    _draw_process(ax, 2.85, 2.10, 2.90, 0.92, "build_ext --inplace", "build native extension")
    _draw_document(ax, 2.85, 0.65, 2.90, 0.90, "compiled extension", "smith_waterman_cython.pyd / .so")

    _draw_document(ax, 0.25, 4.99, 1.95, 0.94, "setup.py", "Extension +\ncythonize")
    _draw_process(ax, 6.85, 2.10, 1.50, 0.82, "GCC / MSVC", "compiler", accent=TOOL_ACCENT, fill=TOOL_FILL)
    _draw_process(ax, 6.55, 0.68, 1.80, 0.82, "import", "helpers.\nsmithwaterman", accent=TOOL_ACCENT, fill=TOOL_FILL)

    _arrow(ax, (4.30, 6.42), (4.30, 5.95))
    _arrow(ax, (4.30, 4.98), (4.30, 4.48))
    _arrow(ax, (4.30, 3.52), (4.30, 3.05))
    _arrow(ax, (4.30, 2.08), (4.30, 1.58))

    _arrow(ax, (2.22, 5.46), (2.82, 5.46), "config")
    _arrow(ax, (6.83, 2.50), (5.77, 2.50), "compile")
    _arrow(ax, (5.77, 1.10), (6.53, 1.10), "use")

    output_base.parent.mkdir(parents=True, exist_ok=True)
    pdf_path = output_base.with_suffix(".pdf")
    png_path = output_base.with_suffix(".png")
    fig.savefig(pdf_path, dpi=300, bbox_inches="tight")
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return [pdf_path, png_path]


def main() -> None:
    output_base = Path(__file__).resolve().parent / "Graphics" / "cython_transpilation_workflow"
    saved_paths = render_figure(output_base)
    for path in saved_paths:
        print(f"Saved Cython workflow figure to {path}")


if __name__ == "__main__":
    main()