from typing import List, Optional


class TextSplitter:
    """Recursive character text splitter targeting semantic boundary preservation and optimal RAG chunk sizing.

    Technical Tasks:
    1. Hierarchical Recursive Splitting: Decomposes text along the hierarchy \n\n -> \n -> .  -> ;  -> ' ',
       accumulating segments into chunks targeting an 800-character window (650 to 850 characters).
    2. Minimum Chunk Threshold: Merges dangling fragments smaller than 100 characters into the preceding chunk
       to prevent sparse vectors in downstream embedding pipelines.
    """

    DEFAULT_SEPARATORS: List[str] = ["\n\n", "\n", ". ", "; ", " "]

    def __init__(
        self,
        target_chunk_size: int = 800,
        min_chunk_size: int = 100,
        separators: Optional[List[str]] = None,
    ):
        """Initializes the TextSplitter with target and minimum chunk thresholds.

        Args:
            target_chunk_size: Ideal character size for document chunks (default: 800).
            min_chunk_size: Minimum allowable character length for a standalone chunk (default: 100).
            separators: Priority list of separators for recursive decomposition.

        Raises:
            ValueError: If target_chunk_size is not positive, min_chunk_size is negative,
                        or min_chunk_size exceeds target_chunk_size.
        """
        if target_chunk_size <= 0:
            raise ValueError("target_chunk_size must be a positive integer.")
        if min_chunk_size < 0:
            raise ValueError("min_chunk_size cannot be negative.")
        if min_chunk_size > target_chunk_size:
            raise ValueError("min_chunk_size cannot exceed target_chunk_size.")

        self.target_chunk_size = target_chunk_size
        self.min_chunk_size = min_chunk_size
        self.separators = separators if separators is not None else list(self.DEFAULT_SEPARATORS)

    def _split_into_atomic_units(self, text: str, sep_index: int = 0) -> List[str]:
        """Recursively decomposes text into smaller atomic semantic units along the separator hierarchy.

        Args:
            text: Input text string to decompose.
            sep_index: Current separator index in self.separators.

        Returns:
            List of constituent strings retaining appropriate delimiter continuity.
        """
        if sep_index >= len(self.separators):
            # Fallback for unbroken token sequences exceeding target chunk size
            if len(text) > self.target_chunk_size:
                return [
                    text[i : i + self.target_chunk_size]
                    for i in range(0, len(text), self.target_chunk_size)
                ]
            return [text]

        sep = self.separators[sep_index]
        if sep not in text:
            return self._split_into_atomic_units(text, sep_index + 1)

        splits = text.split(sep)
        units: List[str] = []
        break_threshold = max(self.min_chunk_size, self.target_chunk_size // 2)

        for i, part in enumerate(splits):
            if not part:
                continue
            # Reattach separator to all except the trailing fragment if original didn't end with it
            part_with_sep = part + sep if i < len(splits) - 1 else part
            # If the fragment is still substantial, decompose it further along finer separators
            if len(part_with_sep) > break_threshold and sep_index + 1 < len(self.separators):
                units.extend(self._split_into_atomic_units(part_with_sep, sep_index + 1))
            else:
                units.append(part_with_sep)
        return units

    def split_text(self, text: str) -> List[str]:
        """Recursively splits text into target-sized character chunks.

        Follows the hierarchical priority: \n\n -> \n -> .  -> ;  -> ' '
        and merges any trailing or intermediate fragments under min_chunk_size
        into the adjacent chunk.

        Args:
            text: Raw narrative text string to split.

        Returns:
            List of cleaned string chunks satisfying target sizing criteria.
        """
        if not text or not text.strip():
            return []

        cleaned_text = text.strip()
        if len(cleaned_text) <= self.target_chunk_size:
            return [cleaned_text]

        # Decompose into atomic units respecting the separator hierarchy
        units = self._split_into_atomic_units(cleaned_text, 0)

        # Upper and lower bounds for greedy accumulation window
        upper_window = max(self.target_chunk_size, int(self.target_chunk_size * 1.0625))  # e.g., 850 for 800
        lower_window = int(self.target_chunk_size * 0.8125)  # e.g., 650 for 800
        fill_threshold = max(self.min_chunk_size, self.target_chunk_size // 4)

        raw_chunks: List[str] = []
        current: str = ""

        for unit in units:
            if not current:
                current = unit
            elif len(current) + len(unit) <= upper_window:
                current += unit
            elif len(current) < lower_window and len(unit) > fill_threshold:
                # Break large unit down using finer separators to fill current chunk
                finer_idx = min(3, len(self.separators) - 1)
                sub_units = self._split_into_atomic_units(unit, finer_idx)
                for su in sub_units:
                    if len(current) + len(su) <= upper_window:
                        current += su
                    else:
                        if current.strip():
                            raw_chunks.append(current.strip())
                        current = su
            else:
                if current.strip():
                    raw_chunks.append(current.strip())
                current = unit

        if current.strip():
            raw_chunks.append(current.strip())

        # Task 2: Merge dangling text fragments smaller than min_chunk_size
        merged_chunks: List[str] = []
        for chunk in raw_chunks:
            if not merged_chunks:
                merged_chunks.append(chunk)
            elif len(chunk) < self.min_chunk_size:
                merged_chunks[-1] = f"{merged_chunks[-1]} {chunk}"
            else:
                merged_chunks.append(chunk)

        # If the first chunk itself was smaller than min_chunk_size and other chunks follow, merge forward
        if len(merged_chunks) > 1 and len(merged_chunks[0]) < self.min_chunk_size:
            merged_chunks[1] = f"{merged_chunks[0]} {merged_chunks[1]}"
            merged_chunks.pop(0)

        return merged_chunks
