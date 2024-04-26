"""Test for functionality of openai_llm.py."""
import pytest
from llmpeg.openai_llm import OpenAILLMInterface


def test_missing_openai_api_key(monkeypatch):
    """Test the graceful exit path if OPENAI_API_KEY is not set.

    Args:
        monkeypatch (_pytest.monkeypatch.MonkeyPatch): A pytest fixture
    """
    # Temporarily unset OPENAI_API_KEY
    # raising=False makes this operation safe if the variable isn't set
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(SystemExit) as e:
        _ = OpenAILLMInterface("gpt-3.5-turbo-0125")
    assert e.type == SystemExit
    assert e.value.code == 1
