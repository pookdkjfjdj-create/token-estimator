"""Tests for token_estimator."""

from __future__ import annotations

from token_estimator import COMPLEXITY_MULTIPLIERS, KEYWORDS, estimate, format_report


class TestEstimate:
    """Token estimation tests."""

    def test_basic_estimate(self) -> None:
        """Happy path: simple task gives reasonable estimate."""
        est = estimate("What is a list in Python?")
        assert est.input_tokens > 0
        assert est.output_tokens > 0
        assert est.total_tokens == est.input_tokens + est.output_tokens
        assert est.total_cost > 0

    def test_code_generation_detected(self) -> None:
        """Code generation tasks should be classified correctly."""
        est = estimate("Create a FastAPI endpoint with auth")
        assert est.complexity == "code_generation"

    def test_debugging_multipier(self) -> None:
        """Debugging should use appropriate multiplier."""
        est_debug = estimate("Fix the database connection error")
        est_qa = estimate("What is recursion?")
        assert est_debug.total_tokens > est_qa.total_tokens

    def test_all_models_work(self) -> None:
        """Estimation should work for all supported models."""
        task = "Write a Python script to parse CSV files"
        for model in ["gpt-4.1", "gpt-4o", "claude-sonnet-4-6", "gemini-2.5-flash"]:
            est = estimate(task, model=model)
            assert est.model == model
            assert est.total_cost > 0

    def test_unknown_model_raises(self) -> None:
        """Unknown model should raise ValueError."""
        import pytest

        with pytest.raises(ValueError, match="Unknown model"):
            estimate("test", model="nonexistent-model")

    def test_few_shot_examples_increase_tokens(self) -> None:
        """Few-shot examples should increase input tokens."""
        base = estimate("Classify this text")
        with_examples = estimate(
            "Classify this text",
            few_shot_examples=["Example 1: positive", "Example 2: negative"],
        )
        assert with_examples.input_tokens > base.input_tokens

    def test_format_report_contains_model(self) -> None:
        """Report should include model name."""
        est = estimate("test")
        report = format_report(est)
        assert est.model in report

    def test_complexity_keywords_match_categories(self) -> None:
        """All complexity categories should have keywords."""
        assert set(COMPLEXITY_MULTIPLIERS.keys()) == set(KEYWORDS.keys())
