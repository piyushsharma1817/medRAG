import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agents.model_manager import ModelManager, ModelTier  # noqa: E402


class SessionStateMock(dict):
    """Small Streamlit session-state stand-in with mapping and attribute access."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


def completion(content="analysis"):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


class ModelManagerTests(unittest.TestCase):
    def test_client_uses_configured_key_with_bounded_sdk_retries(self):
        with patch("agents.model_manager.st.secrets", {"GROQ_API_KEY": "test-key"}), patch(
            "agents.model_manager.groq.Groq"
        ) as groq_client:
            manager = ModelManager()

        self.assertIsNotNone(manager.clients.get("groq"))
        self.assertEqual(groq_client.call_args.kwargs["api_key"], "test-key")
        self.assertEqual(groq_client.call_args.kwargs["max_retries"], 0)
        self.assertEqual(groq_client.call_args.kwargs["timeout"], 30.0)

    def test_current_primary_model_succeeds_without_fallback(self):
        manager = ModelManager.__new__(ModelManager)
        client = Mock()
        client.chat.completions.create.return_value = completion()
        manager.clients = {"groq": client}
        manager.initialization_error = None

        result = manager.generate_analysis({"report": "short"}, "prompt")

        self.assertTrue(result["success"])
        self.assertEqual(result["model_used"], "groq/openai/gpt-oss-120b")
        self.assertEqual(client.chat.completions.create.call_count, 1)
        self.assertEqual(
            client.chat.completions.create.call_args.kwargs["timeout"], 30.0
        )
        self.assertEqual(
            client.chat.completions.create.call_args.kwargs["max_completion_tokens"],
            2000,
        )

    def test_model_not_found_falls_back_once_to_active_alternate(self):
        manager = ModelManager.__new__(ModelManager)
        client = Mock()
        unavailable = RuntimeError("provider response must not be exposed")
        unavailable.status_code = 404
        client.chat.completions.create.side_effect = [unavailable, completion()]
        manager.clients = {"groq": client}
        manager.initialization_error = None

        result = manager.generate_analysis({"report": "short"}, "prompt")

        self.assertTrue(result["success"])
        self.assertEqual(result["model_used"], "groq/openai/gpt-oss-20b")
        self.assertEqual(client.chat.completions.create.call_count, 2)

    def test_auth_error_is_sanitized_and_does_not_retry_models(self):
        manager = ModelManager.__new__(ModelManager)
        client = Mock()
        rejected = RuntimeError("secret or response body must not appear")
        rejected.status_code = 401
        client.chat.completions.create.side_effect = rejected
        manager.clients = {"groq": client}
        manager.initialization_error = None

        result = manager.generate_analysis({"report": "short"}, "prompt")

        self.assertFalse(result["success"])
        self.assertIn("authentication failed", result["error"])
        self.assertNotIn("secret", result["error"])
        self.assertEqual(client.chat.completions.create.call_count, 1)

    def test_all_configured_model_ids_are_current_replacements(self):
        model_ids = {config["model"] for config in ModelManager._models()}

        self.assertEqual(
            model_ids, {"openai/gpt-oss-120b", "openai/gpt-oss-20b"}
        )
        self.assertEqual(len(ModelTier), 2)


class AnalysisInitializationTests(unittest.TestCase):
    def test_analysis_initialization_does_not_load_chat_embeddings(self):
        from services import ai_service

        state = SessionStateMock()
        with patch.object(ai_service.st, "session_state", state), patch.object(
            ai_service, "AnalysisAgent"
        ):
            ai_service.init_analysis_state()

        self.assertIn("analysis_agent", state)
        self.assertNotIn("chat_agent", state)


class ChatHistoryDisplayTests(unittest.TestCase):
    def test_skips_only_one_analysis_copy_and_preserves_history(self):
        from components.chat_history import messages_for_display

        analysis = "AI Generated Diagnosis\n\nGenerated with Groq"
        messages = [
            {"role": "assistant", "content": analysis},
            {"role": "user", "content": "What does this mean?"},
            {"role": "assistant", "content": "Follow-up response"},
            {"role": "assistant", "content": analysis},
        ]

        rendered = list(messages_for_display(messages, analysis))

        self.assertEqual(rendered, messages[1:])
        self.assertEqual(len(messages), 4)  # Display filtering does not mutate history.


if __name__ == "__main__":
    unittest.main()
