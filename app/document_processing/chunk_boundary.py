from typing import List


class BoundaryManager:
    """Manages cross-chunk contextual overlap and preserves structural table integrity.

    Technical Tasks:
    1. 150-Character Contextual Overlap: Prepends the trailing 150 characters of Chunk N
       to the beginning of Chunk N+1, preserving narrative coherence at boundaries.
    2. Table Integrity Lock: Prevents splitting mid-table up to the target window (850 characters)
       and ensures zero markdown tables are split across single cell rows.
    """

    def __init__(self, target_window: int = 850):
        """Initializes BoundaryManager with a target character window.

        Args:
            target_window: Maximum character window threshold for locking table rows together (default: 850).
        """
        if target_window <= 0:
            raise ValueError("target_window must be a positive integer.")
        self.target_window = target_window

    def apply_overlap(self, raw_chunks: List[str], overlap_size: int = 150) -> List[str]:
        """Applies backward overlap across chunk boundaries while respecting table rows.

        Args:
            raw_chunks: Sequential list of raw text chunks from the splitter.
            overlap_size: Number of characters from the trailing edge of Chunk N to prepend
                          to Chunk N+1 (default: 150).

        Returns:
            List of chunks with contextual overlap and preserved table integrity.

        Raises:
            ValueError: If overlap_size is negative.
        """
        if overlap_size < 0:
            raise ValueError("overlap_size cannot be negative.")
        if not raw_chunks:
            return []
        if len(raw_chunks) == 1:
            return list(raw_chunks)

        # Step 1: Repair any mid-cell table rows split across chunk boundaries
        repaired_chunks = self._repair_split_cell_rows(raw_chunks)

        # Step 2: Lock table rows together across chunks up to the target window
        locked_chunks = self._lock_table_rows(repaired_chunks)

        if overlap_size == 0 or len(locked_chunks) <= 1:
            return locked_chunks

        # Step 3: Apply backward overlap of exact overlap_size
        result: List[str] = []
        for i, chunk in enumerate(locked_chunks):
            if i == 0:
                result.append(chunk)
            else:
                prev = result[-1]
                overlap = prev[-overlap_size:] if len(prev) >= overlap_size else prev

                # If the chunk begins with a markdown table row, ensure newline separation so formatting holds
                if chunk.lstrip().startswith("|") and not overlap.endswith("\n"):
                    result.append(f"{overlap}\n{chunk}")
                else:
                    sep = " " if (not overlap.endswith((" ", "\n")) and not chunk.startswith((" ", "\n"))) else ""
                    result.append(f"{overlap}{sep}{chunk}")

        return result

    def _repair_split_cell_rows(self, chunks: List[str]) -> List[str]:
        """Detects and repairs any markdown table rows split mid-row across chunks.

        Ensures zero markdown tables are split across a single cell row.
        """
        repaired = list(chunks)
        i = 0
        while i < len(repaired) - 1:
            curr = repaired[i]
            nxt = repaired[i + 1]
            curr_lines = curr.splitlines()
            nxt_lines = nxt.splitlines()

            if curr_lines and nxt_lines:
                last_line = curr_lines[-1].rstrip()
                first_line = nxt_lines[0].lstrip()

                # If the last line started with '|' but was cut without a closing '|'
                # or if the first line is the tail end of that cell row
                if last_line.startswith("|") and (not last_line.endswith("|") or not first_line.startswith("|")):
                    # Check if combining them completes the cell row
                    combined_row = f"{last_line} {first_line}".strip()
                    if combined_row.startswith("|") and combined_row.endswith("|"):
                        curr_lines[-1] = combined_row
                        repaired[i] = "\n".join(curr_lines)
                        repaired[i + 1] = "\n".join(nxt_lines[1:])

            i += 1

        return [c for c in repaired if c.strip()]

    def _lock_table_rows(self, chunks: List[str]) -> List[str]:
        """Locks markdown table rows together across chunks up to the target window.

        If Chunk N ends with table rows and Chunk N+1 begins with table rows,
        they are kept together in a single chunk rather than being split mid-table.
        """
        result: List[str] = []
        for chunk in chunks:
            if not result:
                result.append(chunk)
                continue

            prev = result[-1]
            prev_lines = [l.strip() for l in prev.splitlines() if l.strip()]
            curr_lines = [l.strip() for l in chunk.splitlines() if l.strip()]

            prev_ends_table = bool(prev_lines and prev_lines[-1].startswith("|"))
            curr_starts_table = bool(curr_lines and curr_lines[0].startswith("|"))

            # If adjacent chunks divide a continuous table and fit within target_window, merge them
            if prev_ends_table and curr_starts_table and len(prev) + len(chunk) + 1 <= self.target_window:
                result[-1] = f"{prev}\n{chunk}"
            else:
                result.append(chunk)

        return result
