from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from helpers.smithwaterman import smith_waterman_score


MATCH_SCORE = 2
MISMATCH_SCORE = -1
GAP_SCORE = -2

SEQUENCE_A = "ACGTATCG"
SEQUENCE_B = "ACGTCCG"


@dataclass(frozen=True)
class AlignmentResult:
    sequence_a: str
    sequence_b: str
    score_matrix: np.ndarray
    traceback_path: list[tuple[int, int]]
    best_score: int
    best_position: tuple[int, int]
    aligned_a: str
    aligned_b: str
    alignment_markers: str
    alignment_score: int
    start_a: int
    end_a: int
    start_b: int
    end_b: int


def _pair_score(char_a: str, char_b: str) -> int:
    return MATCH_SCORE if char_a == char_b else MISMATCH_SCORE


def smith_waterman_traceback(sequence_a: str, sequence_b: str) -> AlignmentResult:
    rows = len(sequence_a) + 1
    columns = len(sequence_b) + 1
    score_matrix = np.zeros((rows, columns), dtype=int)
    best_score = 0
    best_position = (0, 0)

    for row in range(1, rows):
        for column in range(1, columns):
            diagonal = score_matrix[row - 1, column - 1] + _pair_score(
                sequence_a[row - 1], sequence_b[column - 1]
            )
            up = score_matrix[row - 1, column] + GAP_SCORE
            left = score_matrix[row, column - 1] + GAP_SCORE
            score = max(0, diagonal, up, left)
            score_matrix[row, column] = score
            if score > best_score:
                best_score = score
                best_position = (row, column)

    path: list[tuple[int, int]] = []
    aligned_a: list[str] = []
    aligned_b: list[str] = []
    markers: list[str] = []
    alignment_score = 0

    row, column = best_position
    while row > 0 and column > 0 and score_matrix[row, column] > 0:
        path.append((row, column))
        current_score = score_matrix[row, column]
        diagonal_score = score_matrix[row - 1, column - 1] + _pair_score(
            sequence_a[row - 1], sequence_b[column - 1]
        )
        up_score = score_matrix[row - 1, column] + GAP_SCORE
        left_score = score_matrix[row, column - 1] + GAP_SCORE

        if current_score == diagonal_score:
            char_a = sequence_a[row - 1]
            char_b = sequence_b[column - 1]
            aligned_a.append(char_a)
            aligned_b.append(char_b)
            markers.append("|" if char_a == char_b else ".")
            alignment_score += _pair_score(char_a, char_b)
            row -= 1
            column -= 1
            continue

        if current_score == up_score:
            aligned_a.append(sequence_a[row - 1])
            aligned_b.append("-")
            markers.append(" ")
            alignment_score += GAP_SCORE
            row -= 1
            continue

        aligned_a.append("-")
        aligned_b.append(sequence_b[column - 1])
        markers.append(" ")
        alignment_score += GAP_SCORE
        column -= 1

    start_row = row
    start_column = column
    path.reverse()

    aligned_a.reverse()
    aligned_b.reverse()
    markers.reverse()

    return AlignmentResult(
        sequence_a=sequence_a,
        sequence_b=sequence_b,
        score_matrix=score_matrix,
        traceback_path=path,
        best_score=best_score,
        best_position=best_position,
        aligned_a="".join(aligned_a),
        aligned_b="".join(aligned_b),
        alignment_markers="".join(markers),
        alignment_score=alignment_score,
        start_a=start_row,
        end_a=best_position[0],
        start_b=start_column,
        end_b=best_position[1],
    )


def validate_alignment(result: AlignmentResult) -> None:
    helper_score = smith_waterman_score(
        result.sequence_a,
        result.sequence_b,
        match_score=MATCH_SCORE,
        mismatch_score=MISMATCH_SCORE,
        gap_score=GAP_SCORE,
    )

    if helper_score != result.best_score:
        raise ValueError(
            f"Traceback score mismatch: helper returned {helper_score}, matrix produced {result.best_score}."
        )

    if result.alignment_score != result.best_score:
        raise ValueError(
            f"Alignment reconstruction mismatch: traceback sums to {result.alignment_score}, expected {result.best_score}."
        )


# ---------------------------------------------------------------------------
# Shared colours
# ---------------------------------------------------------------------------
_MATCH_COL    = "#74c69d"
_MISMATCH_COL = "#f4a261"
_GAP_COL      = "#d8e2dc"
_PATH_COL     = "#e63946"
_TEXT_DARK    = "#212529"
_TEXT_MID     = "#6c757d"
_TEXT_HEAD    = "#343a40"


def draw_alignment_panel(ax: plt.Axes, result: AlignmentResult) -> None:
    """
    Top panel: colour-coded character boxes for the optimal local alignment.
    Row A on top, match/mismatch markers in the middle, row B on the bottom.
    The legend sits in the empty space to the right of the boxes.
    """
    aligned_a = result.aligned_a
    aligned_b = result.aligned_b
    markers   = result.alignment_markers
    n = len(aligned_a)

    # Reserve ~2 data units on the right for the inline legend
    ax.set_xlim(-1.0, n + 2.2)
    ax.set_ylim(0.0, 3.0)
    ax.axis("off")

    Y_A, Y_MID, Y_B = 2.3, 1.5, 0.7
    BOX_W, BOX_H = 0.74, 0.60

    # Row labels
    for y, label in [(Y_A, "A"), (Y_B, "B")]:
        ax.text(-0.7, y, label, ha="center", va="center",
                fontsize=13, fontweight="bold", color=_TEXT_HEAD,
                fontfamily="DejaVu Sans Mono")

    for i in range(n):
        cx = i + 0.5
        ca, cb, mk = aligned_a[i], aligned_b[i], markers[i]

        if ca == "-" or cb == "-":
            bg = _GAP_COL
        elif ca == cb:
            bg = _MATCH_COL
        else:
            bg = _MISMATCH_COL

        for y, ch in [(Y_A, ca), (Y_B, cb)]:
            ax.add_patch(mpatches.FancyBboxPatch(
                (cx - BOX_W / 2, y - BOX_H / 2), BOX_W, BOX_H,
                boxstyle="round,pad=0.04",
                linewidth=0, facecolor=bg,
            ))
            ax.text(cx, y, ch, ha="center", va="center",
                    fontsize=13, fontweight="bold", color=_TEXT_DARK,
                    fontfamily="DejaVu Sans Mono")

        ax.text(cx, Y_MID, mk, ha="center", va="center",
                fontsize=11, color=_TEXT_MID,
                fontfamily="DejaVu Sans Mono")

    # Inline legend to the right of the last box
    lx = n + 0.55
    for y, (color, label) in zip(
        [Y_A, Y_MID, Y_B],
        [
            (_MATCH_COL,    f"Match (+{MATCH_SCORE})"),
            (_MISMATCH_COL, f"Mismatch ({MISMATCH_SCORE})"),
            (_GAP_COL,      f"Gap ({GAP_SCORE})"),
        ],
    ):
        ax.add_patch(mpatches.FancyBboxPatch(
            (lx, y - 0.20), 0.44, 0.40,
            boxstyle="round,pad=0.03",
            linewidth=0.6, edgecolor="#adb5bd", facecolor=color,
        ))
        ax.text(lx + 0.54, y, label, ha="left", va="center",
                fontsize=9, color=_TEXT_HEAD)

    ax.set_title(
        f"Optimal local alignment  \u00b7  score = {result.best_score}  \u00b7  "
        f"match = +{MATCH_SCORE}   mismatch = {MISMATCH_SCORE}   gap = {GAP_SCORE}",
        fontsize=11, loc="left", pad=8, color=_TEXT_HEAD,
    )


def draw_matrix_panel(ax: plt.Axes, result: AlignmentResult) -> None:
    """
    Bottom panel: DP score matrix rendered with imshow.
    The traceback is shown as a connected red line with circle waypoints
    and a diamond at the best-score cell.
    """
    matrix         = result.score_matrix
    n_rows, n_cols = matrix.shape
    traceback_set  = set(result.traceback_path)
    vmax           = max(1, int(matrix.max()))

    cmap = LinearSegmentedColormap.from_list(
        "sw", ["#f8f9fa", "#c7e9d0", "#52b788", "#1b4332"]
    )
    im = ax.imshow(
        matrix, cmap=cmap, vmin=0, vmax=vmax,
        aspect="auto", interpolation="nearest",
    )

    # Fine white grid separating cells
    ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.4, zorder=2)
    ax.tick_params(which="minor", length=0)

    # Annotate every cell with its score
    for i in range(n_rows):
        for j in range(n_cols):
            val     = int(matrix[i, j])
            in_path = (i, j) in traceback_set
            fg      = "white" if val / vmax > 0.58 else _TEXT_DARK
            ax.text(
                j, i, str(val),
                ha="center", va="center", fontsize=9, zorder=3,
                color=fg, fontweight="bold" if in_path else "normal",
            )

    # Traceback: line + open-circle waypoints + filled start + diamond end
    path = result.traceback_path
    if path:
        col_p = [c for _, c in path]
        row_p = [r for r, _ in path]

        ax.plot(col_p, row_p,
                color=_PATH_COL, linewidth=2.0,
                solid_capstyle="round", solid_joinstyle="round", zorder=5)

        ax.plot(col_p, row_p, "o",
                color=_PATH_COL, markersize=7,
                markerfacecolor="white", markeredgecolor=_PATH_COL,
                markeredgewidth=2.0, zorder=6)

        # Filled circle at the alignment start
        ax.plot(col_p[0], row_p[0], "o",
                markersize=8, zorder=7,
                markerfacecolor=_PATH_COL, markeredgewidth=0)

        # Diamond at the best-score (end) cell
        ax.plot(col_p[-1], row_p[-1], "D",
                markersize=9, zorder=7,
                markerfacecolor="white", markeredgecolor=_PATH_COL,
                markeredgewidth=2.2)

    # Sequence characters as tick labels (B along top, A along left).
    # set_ticks_position must come BEFORE set_xticklabels; calling it
    # afterwards recreates the Text objects and discards any colour changes.
    #
    # Only highlight rows/cols that appear in a *diagonal* traceback step
    # (match or mismatch).  Gap-only rows/cols are left in the default colour.
    diagonal_rows: set[int] = set()
    diagonal_cols: set[int] = set()
    path = result.traceback_path
    if path:
        # The first cell is always an aligned (non-gap) position.
        diagonal_rows.add(path[0][0])
        diagonal_cols.add(path[0][1])
    for k in range(1, len(path)):
        r1, c1 = path[k - 1]
        r2, c2 = path[k]
        if r2 - r1 == 1 and c2 - c1 == 1:
            diagonal_rows.add(r2)
            diagonal_cols.add(c2)

    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_label_position("top")
    ax.set_xlabel("Sequence B", fontsize=11, labelpad=10)
    ax.set_ylabel("Sequence A", fontsize=11, labelpad=10)

    ax.set_xticks(np.arange(n_cols))
    ax.set_xticklabels(
        ["-"] + list(result.sequence_b),
        fontfamily="DejaVu Sans Mono", fontsize=11, fontweight="bold",
    )
    ax.set_yticks(np.arange(n_rows))
    ax.set_yticklabels(
        ["-"] + list(result.sequence_a),
        fontfamily="DejaVu Sans Mono", fontsize=11, fontweight="bold",
    )
    ax.tick_params(which="major", length=0, pad=5)

    # Colour the tick labels that fall along diagonal traceback steps in blue.
    for j, lbl in enumerate(ax.get_xticklabels()):
        lbl.set_color("#1565c0" if j in diagonal_cols else _TEXT_HEAD)
    for i, lbl in enumerate(ax.get_yticklabels()):
        lbl.set_color("#1565c0" if i in diagonal_rows else _TEXT_HEAD)

    cbar = plt.colorbar(im, ax=ax, fraction=0.038, pad=0.02)
    cbar.set_label("Cell score", fontsize=9)
    cbar.ax.tick_params(labelsize=8)

    ax.set_title(
        "DP score matrix  \u00b7  red path = traceback  \u00b7  \u25c7 = best position",
        fontsize=11, pad=14, color=_TEXT_HEAD,
    )


def render_figure(result: AlignmentResult, output_path: Path) -> list[Path]:
    plt.rcParams.update({
        "font.family":        "DejaVu Sans",
        "figure.facecolor":   "white",
        "axes.facecolor":     "white",
        "savefig.facecolor":  "white",
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.spines.bottom": False,
        "axes.spines.left":   False,
    })

    figure, (ax_matrix, ax_align) = plt.subplots(
        2, 1,
        figsize=(10, 11),
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.18},
    )

    draw_alignment_panel(ax_align, result)
    draw_matrix_panel(ax_matrix, result)

    figure.suptitle(
        f"Smith\u2013Waterman local alignment example\n"
        f"A = {result.sequence_a}    B = {result.sequence_b}",
        fontsize=14, fontweight="bold", color="#1b2631",
    )
    figure.subplots_adjust(top=0.82)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path = output_path.with_suffix(".pdf")
    png_path = output_path.with_suffix(".png")
    figure.savefig(pdf_path, dpi=200, bbox_inches="tight")
    figure.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close(figure)
    return [pdf_path, png_path]


def main() -> None:
    result = smith_waterman_traceback(SEQUENCE_A, SEQUENCE_B)
    validate_alignment(result)

    output_path = (
        Path(__file__).resolve().parent / "Graphics" / "smith_waterman_alignment_example"
    )
    saved_paths = render_figure(result, output_path)

    for saved_path in saved_paths:
        print(f"Saved: {saved_path}")
    print(f"Alignment: {result.aligned_a}")
    print(f"           {result.alignment_markers}")
    print(f"           {result.aligned_b}")
    print(f"Score: {result.best_score}")


if __name__ == "__main__":
    main()