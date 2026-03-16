cpdef int smith_waterman_score_cython(
    str sequence_a,
    str sequence_b,
    int match_score=2,
    int mismatch_score=-1,
    int gap_score=-2,
):
    """Return the Smith-Waterman local-alignment score.

    Keep this recurrence in sync with the companion implementation so benchmark
    comparisons stay focused on runtime differences rather than algorithm drift.
    """
    cdef Py_ssize_t length_a = len(sequence_a)
    cdef Py_ssize_t length_b = len(sequence_b)
    cdef Py_ssize_t index_a
    cdef Py_ssize_t index_b
    cdef int diagonal_score
    cdef int up_score
    cdef int left_score
    cdef int cell_score
    cdef int best_score = 0
    cdef str char_a
    cdef str char_b
    cdef list previous_row
    cdef list current_row

    if length_a == 0 or length_b == 0:
        return 0

    previous_row = [0] * (length_b + 1)

    for index_a in range(length_a):
        char_a = sequence_a[index_a]
        current_row = [0] * (length_b + 1)
        for index_b in range(1, length_b + 1):
            char_b = sequence_b[index_b - 1]
            diagonal_score = previous_row[index_b - 1] + (
                match_score if char_a == char_b else mismatch_score
            )
            up_score = previous_row[index_b] + gap_score
            left_score = current_row[index_b - 1] + gap_score
            cell_score = diagonal_score
            if up_score > cell_score:
                cell_score = up_score
            if left_score > cell_score:
                cell_score = left_score
            if cell_score < 0:
                cell_score = 0
            current_row[index_b] = cell_score
            if cell_score > best_score:
                best_score = cell_score
        previous_row = current_row

    return best_score