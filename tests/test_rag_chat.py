import sys
import unittest
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agents.chat_agent import ChatAgent  # noqa: E402


class SessionStateMock(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


def completion(text="answer"):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=text))]
    )


def make_agent():
    agent = ChatAgent.__new__(ChatAgent)
    agent.model_name = ChatAgent.MODEL_NAME
    agent.client = Mock()
    agent.client.chat.completions.create.return_value = completion()
    agent._contextualize_query = Mock(side_effect=lambda query, history: query)
    return agent


class ChatAgentRetrievalTests(unittest.TestCase):
    def test_retrieved_report_chunks_are_sent_in_final_model_prompt(self):
        agent = make_agent()
        retriever = Mock()
        retriever.invoke.return_value = [
            SimpleNamespace(page_content="Hemoglobin: 13.5 g/dL; reference 12–15 g/dL")
        ]
        vectorstore = Mock()
        vectorstore.as_retriever.return_value = retriever

        result = agent.get_response("What is my hemoglobin?", vectorstore, [])

        self.assertEqual(result, "answer")
        vectorstore.as_retriever.assert_called_once_with(search_kwargs={"k": 3})
        retriever.invoke.assert_called_once_with("What is my hemoglobin?")
        final_user_message = agent.client.chat.completions.create.call_args.kwargs[
            "messages"
        ][-1]["content"]
        self.assertIn("Hemoglobin: 13.5 g/dL", final_user_message)
        self.assertIn("What is my hemoglobin?", final_user_message)

    def test_missing_retrieved_evidence_is_explicit_and_has_no_fake_context(self):
        agent = make_agent()
        retriever = Mock()
        retriever.invoke.return_value = []
        vectorstore = Mock()
        vectorstore.as_retriever.return_value = retriever

        answer = agent.get_response("What is my hemoglobin?", vectorstore, [])

        self.assertIn("couldn't find a relevant passage", answer)
        agent.client.chat.completions.create.assert_not_called()

    def test_retrieval_exception_fails_closed_without_calling_model(self):
        agent = make_agent()
        retriever = Mock()
        retriever.invoke.side_effect = RuntimeError("internal index details")
        vectorstore = Mock()
        vectorstore.as_retriever.return_value = retriever

        answer = agent.get_response("question", vectorstore, [])

        self.assertIn("couldn't find a relevant passage", answer)
        agent.client.chat.completions.create.assert_not_called()

    def test_empty_report_cannot_be_indexed_as_placeholder_evidence(self):
        agent = make_agent()

        with self.assertRaises(ValueError):
            agent.initialize_vector_store("  \n")


class ReportIndexIsolationTests(unittest.TestCase):
    def test_same_report_text_uses_separate_index_for_each_session(self):
        from services import ai_service

        state = SessionStateMock(
            analysis_agent=object(),
            chat_agent=Mock(),
            current_session={"id": "guest-session-a", "guest": True},
        )
        state.chat_agent.initialize_vector_store.side_effect = [object(), object()]
        state.chat_agent.get_response.return_value = "answer"

        with patch.object(ai_service.st, "session_state", state), patch.object(
            ai_service.st, "spinner", side_effect=lambda *args, **kwargs: nullcontext()
        ):
            ai_service.get_chat_response("question", "same synthetic report", [])
            key_a = state.vector_store_key
            index_a = state.vector_store
            state.current_session = {"id": "guest-session-b", "guest": True}
            ai_service.get_chat_response("question", "same synthetic report", [])

        self.assertNotEqual(key_a, state.vector_store_key)
        self.assertIsNot(index_a, state.vector_store)
        self.assertEqual(state.chat_agent.initialize_vector_store.call_count, 2)

    def test_empty_context_does_not_reuse_cached_or_assistant_analysis_text(self):
        from services import ai_service

        state = SessionStateMock(
            analysis_agent=object(),
            chat_agent=Mock(),
            current_session={"id": "guest-session", "guest": True},
            vector_store=object(),
            vector_store_key="old-report-key",
        )
        history = [{"role": "assistant", "content": "A" * 200}]

        with patch.object(ai_service.st, "session_state", state):
            ai_service.get_chat_response("question", "", history)

        self.assertIsNone(state.chat_agent.get_response.call_args.args[1])
        self.assertNotIn("vector_store", state)
        self.assertNotIn("vector_store_key", state)


if __name__ == "__main__":
    unittest.main()
