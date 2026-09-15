"""Unit tests for Golden Benchmark Dataset Formulator and Validator (Module 10.1)."""

import json
import os
import pytest
from pydantic import ValidationError

from evaluation.eval_dataset import BenchmarkDatasetManager, BenchmarkQAPair


class TestBenchmarkQAPair:
    """Test suite for BenchmarkQAPair Pydantic model validation and constraints."""

    def test_valid_pair_creation(self):
        """Verifies successful instantiation and normalization of category."""
        pair = BenchmarkQAPair(
            id="TEST-001",
            category="FACTUAL",
            question="What is the gross margin for FY24?",
            expected_answer_keywords=["gross margin", "45%"],
            expected_page_numbers=[12, 14],
            should_answer=True,
        )
        assert pair.id == "TEST-001"
        assert pair.category == "factual"  # Normalized to lowercase
        assert pair.should_answer is True
        assert pair.expected_page_numbers == [12, 14]

    def test_invalid_category_raises_validation_error(self):
        """Verifies rejection of categories outside the 5 canonical classes."""
        with pytest.raises(ValidationError):
            BenchmarkQAPair(
                id="TEST-BAD-CAT",
                category="speculative",  # Invalid
                question="What will happen next year?",
            )

    def test_negative_page_number_raises_validation_error(self):
        """Verifies rejection of non-positive page numbers."""
        with pytest.raises(ValidationError):
            BenchmarkQAPair(
                id="TEST-BAD-PAGE",
                category="factual",
                question="What was the net sales?",
                expected_page_numbers=[0],  # Must be >= 1
            )

        with pytest.raises(ValidationError):
            BenchmarkQAPair(
                id="TEST-BAD-PAGE-NEG",
                category="factual",
                question="What was the net sales?",
                expected_page_numbers=[-5],  # Must be >= 1
            )


class TestBenchmarkDatasetManager:
    """Test suite for BenchmarkDatasetManager 50-pair dataset curation and serialization."""

    def test_curated_50_pairs_definition_of_done(self):
        """Verifies Definition of Done (DoD):

        Dataset passes Pydantic validation for all 50 items; exactly 5 categories distributed as specified.
        """
        pairs = BenchmarkDatasetManager.CURATED_50_PAIRS

        # 1. Total count is exactly 50
        assert len(pairs) == 50

        # 2. All 50 items are valid BenchmarkQAPair instances
        for pair in pairs:
            assert isinstance(pair, BenchmarkQAPair)
            assert len(pair.id) >= 3
            assert len(pair.question) >= 5

    def test_category_distribution_exact_counts(self):
        """Verifies exact distribution: 20 Factual, 10 Analytical, 10 Risk, 5 Comparative, 5 Negative."""
        distribution = BenchmarkDatasetManager.validate_distribution(BenchmarkDatasetManager.CURATED_50_PAIRS)

        assert distribution["factual"] == 20
        assert distribution["analytical"] == 10
        assert distribution["risk"] == 10
        assert distribution["comparative"] == 5
        assert distribution["negative"] == 5

    def test_negative_tests_invariants(self):
        """Verifies that all 5 negative tests enforce should_answer=False and no source pages."""
        negative_pairs = [p for p in BenchmarkDatasetManager.CURATED_50_PAIRS if p.category == "negative"]
        assert len(negative_pairs) == 5

        for p in negative_pairs:
            assert p.should_answer is False, f"Negative pair {p.id} must have should_answer=False"
            assert p.expected_page_numbers == [], f"Negative pair {p.id} must not have expected page numbers"

    def test_load_dataset_from_canonical_json(self):
        """Verifies that evaluation/benchmark_dataset.json loads and validates successfully."""
        json_path = os.path.join("evaluation", "benchmark_dataset.json")
        loaded_pairs = BenchmarkDatasetManager.load_dataset(json_path)

        assert len(loaded_pairs) == 50
        distribution = BenchmarkDatasetManager.validate_distribution(loaded_pairs)
        assert distribution == BenchmarkDatasetManager.EXPECTED_DISTRIBUTION

    def test_save_and_load_roundtrip(self, tmp_path):
        """Verifies saving and re-loading dataset preserves complete data integrity."""
        temp_file = os.path.join(tmp_path, "test_dataset.json")
        BenchmarkDatasetManager.save_dataset(temp_file)

        reloaded = BenchmarkDatasetManager.load_dataset(temp_file)
        assert len(reloaded) == 50

        for original, restored in zip(BenchmarkDatasetManager.CURATED_50_PAIRS, reloaded):
            assert original.id == restored.id
            assert original.category == restored.category
            assert original.question == restored.question
            assert original.expected_answer_keywords == restored.expected_answer_keywords
            assert original.expected_page_numbers == restored.expected_page_numbers
            assert original.should_answer == restored.should_answer

    def test_load_dataset_file_not_found(self):
        """Verifies FileNotFoundError on non-existent dataset path."""
        with pytest.raises(FileNotFoundError):
            BenchmarkDatasetManager.load_dataset("non_existent_path.json")

    def test_load_dataset_malformed_json(self, tmp_path):
        """Verifies ValueError when loading corrupted or invalid JSON."""
        corrupted_file = os.path.join(tmp_path, "corrupted.json")
        with open(corrupted_file, "w") as f:
            f.write("{ invalid_json: true ")

        with pytest.raises(ValueError, match="Failed to parse JSON"):
            BenchmarkDatasetManager.load_dataset(corrupted_file)

    def test_validate_distribution_deviation_raises_value_error(self):
        """Verifies ValueError when dataset count or category distribution deviates."""
        # Case 1: Incomplete list (< 50)
        incomplete = BenchmarkDatasetManager.CURATED_50_PAIRS[:40]
        with pytest.raises(ValueError, match="must contain exactly 50 pairs"):
            BenchmarkDatasetManager.validate_distribution(incomplete)

        # Case 2: 50 items but wrong distribution (e.g. 21 factual and 9 analytical)
        distorted = list(BenchmarkDatasetManager.CURATED_50_PAIRS)
        # Swap an analytical pair to factual
        distorted[20] = BenchmarkQAPair(
            id="EXTRA-FACT",
            category="factual",
            question="Extra factual question?",
            expected_answer_keywords=["123"],
            expected_page_numbers=[1],
            should_answer=True,
        )
        with pytest.raises(ValueError, match="count mismatch"):
            BenchmarkDatasetManager.validate_distribution(distorted)
