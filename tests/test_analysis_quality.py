import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agents.model_manager import ModelManager  # noqa: E402
from config.prompts import SPECIALIST_PROMPTS  # noqa: E402


class AnalysisQualityPromptTests(unittest.TestCase):
    def setUp(self):
        self.prompt = SPECIALIST_PROMPTS["comprehensive_analyst"]

    def test_prompt_separates_transcribed_facts_from_interpretation(self):
        self.assertLess(
            self.prompt.index("### Report facts"),
            self.prompt.index("### What the reported ranges suggest"),
        )
        self.assertIn("List only the test values and units visible in the report", self.prompt)
        self.assertIn("Keep extraction separate from interpretation", self.prompt)
        self.assertIn("Do not list tests that are absent", self.prompt)

    def test_prompt_requires_only_reported_ranges_and_handles_strict_limits(self):
        self.assertIn("Do not substitute a range from memory", self.prompt)
        self.assertIn("a value equal to a stated '<' limit is not below that limit", self.prompt)
        self.assertIn("cannot be classified from this report", self.prompt)
        self.assertIn("identify the discrepancy", self.prompt)

    def test_prompt_rejects_unsupported_diagnoses_risk_levels_and_retest_schedules(self):
        self.assertIn("You do not diagnose", self.prompt)
        self.assertIn("Do not diagnose conditions or assign cardiovascular or other risk levels", self.prompt)
        self.assertIn("state that this report is insufficient", self.prompt)
        self.assertIn("Do not recommend a specific retesting date", self.prompt)
        self.assertIn("Do not infer", self.prompt)

    def test_model_request_preserves_only_supplied_report_data_as_json(self):
        manager = ModelManager.__new__(ModelManager)
        client = Mock()
        client.chat.completions.create.return_value = Mock(
            choices=[Mock(message=Mock(content="analysis"))]
        )
        manager.clients = {"groq": client}
        manager.initialization_error = None
        supplied = {
            "report": "LDL: 100 mg/dL (Reference: <100)",
        }

        result = manager.generate_analysis(supplied, self.prompt)

        self.assertTrue(result["success"])
        messages = client.chat.completions.create.call_args.kwargs["messages"]
        self.assertEqual(messages[0]["content"], self.prompt)
        self.assertIn('"LDL: 100 mg/dL (Reference: <100)"', messages[1]["content"])
        self.assertNotIn("patient_age", messages[1]["content"])
        self.assertNotIn("Reference: 70-100", messages[1]["content"])


if __name__ == "__main__":
    unittest.main()
