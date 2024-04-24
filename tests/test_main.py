"""Test for functionality of main.py."""
import pytest
from unittest.mock import patch
from llmpeg.main import LLMPEG


@pytest.fixture
def mock_llm_interface(mocker):
    """Fixture to create and configure a mock LLMInterface object.

    Args:
        mocker (pytest.fixture): The pytest mocker fixture.

    Returns:
        MagicMock: A mocked LLMInterface object with predefined return
            values.
    """
    # Create a mock LLMInterface object
    mock = mocker.patch("llmpeg.llm_interface.LLMInterface", autospec=True)
    # Configure the mock to avoid side effects and to specify return values
    mock_instance = mock.return_value
    mock_instance.invoke_model.return_value = '{"explanation": ["Test Explanation"], "command": "ffmpeg -i input.mp4 output.mp4"}'  # noqa: E501
    return mock_instance


def test_llmpeg_run_user_confirmation(mock_llm_interface):
    """Test LLMPEG run function with user confirming command execution.

    This test simulates user confirmation ('Y') and checks if the correct
    system command is executed as expected when user input is affirmative.

    Args:
        mock_llm_interface (MagicMock): Mocked LLMInterface provided by the
            fixture.
    """
    # Patching 'input' to simulate user inputs and 'subprocess.run' to
    # prevent actual command execution
    with patch("builtins.input", side_effect=["Y"]), patch(
        "subprocess.run"
    ) as mock_run:
        llmpeg = LLMPEG(llm_interface=mock_llm_interface)
        llmpeg.run("Convert video format")

        # Ensure that subprocess.run was called with the expected command
        mock_run.assert_called_with(
            "ffmpeg -i input.mp4 output.mp4", shell=True
        )


def test_llmpeg_run_user_abort(mock_llm_interface):
    """Test LLMPEG run function with user aborting command execution.

    This test verifies that no system command is executed when the user input
    indicates a decision to abort ('N').

    Args:
        mock_llm_interface (MagicMock): Mocked LLMInterface provided by the
            fixture.
    """
    # Patching 'input' to simulate user input declining to execute the command
    with patch("builtins.input", side_effect=["N"]), patch(
        "subprocess.run"
    ) as mock_run:
        llmpeg = LLMPEG(llm_interface=mock_llm_interface)
        llmpeg.run("Convert video format")

        # Ensure that subprocess.run was not called due to user cancellation
        specific_args = ("ffmpeg -i input.mp4 output.mp4",)
        assert not any(
            args == specific_args for args, _ in mock_run.call_args_list
        ), "subprocess.run was called with specific undesired arguments"


def test_llmpeg_initialization(mock_llm_interface):
    """Test the initialization of the LLMPEG class.

    Ensures that the LLMPEG class is correctly initialized with the provided
    LLMInterface mock.

    Args:
        mock_llm_interface (MagicMock): Mocked LLMInterface provided by the
            fixture.
    """
    llmpeg = LLMPEG(llm_interface=mock_llm_interface)
    assert llmpeg.llm_interface is mock_llm_interface


def test_llmpeg_chat(mock_llm_interface):
    """Test the chat function of the LLMPEG class.

    Verifies that the chat function returns correct explanations and commands
    based on the mock LLMInterface's behavior.

    Args:
        mock_llm_interface (MagicMock): Mocked LLMInterface provided by the
            fixture.
    """
    llmpeg = LLMPEG(llm_interface=mock_llm_interface)
    explanation, command = llmpeg.chat("Convert video format")
    assert "Test Explanation" in explanation
    assert "ffmpeg -i input.mp4 output.mp4" == command


def test_missing_ffmpeg_executable(mock_llm_interface):
    """Test the graceful exit path if ffmpeg is not found.

    Patches the behavior of shutil.which detects the ffmpeg executable
    to return None, which is the behavior if it doesn't find it.

    Args:
        mock_llm_interface (MagicMock): Mocked LLMInterface provided by the
            fixture.
    """
    with pytest.raises(SystemExit) as e, patch(
        "shutil.which", side_effect=[None]
    ):
        _ = LLMPEG(mock_llm_interface)
    assert e.type == SystemExit
    assert e.value.code == 1
