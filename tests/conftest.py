# Test configuration and shared fixtures
import pytest
import os
import sys
from unittest.mock import Mock, MagicMock

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing"""
    client = MagicMock()

    # Mock assistant
    mock_assistant = Mock()
    mock_assistant.id = "asst_test123"
    client.beta.assistants.retrieve.return_value = mock_assistant

    # Mock thread
    mock_thread = Mock()
    mock_thread.id = "thread_test123"
    client.beta.threads.create.return_value = mock_thread

    # Mock message
    mock_message = Mock()
    client.beta.threads.messages.create.return_value = mock_message

    # Mock run
    mock_run = Mock()
    mock_run.id = "run_test123"
    mock_run.status = "completed"
    client.beta.threads.runs.create.return_value = mock_run
    client.beta.threads.runs.retrieve.return_value = mock_run

    # Mock thread messages
    mock_content = Mock()
    mock_content.text.value = "Test response from assistant"
    mock_thread_message = Mock()
    mock_thread_message.content = [mock_content]
    mock_messages = Mock()
    mock_messages.data = [mock_thread_message]
    client.beta.threads.messages.list.return_value = mock_messages

    # Mock TTS
    mock_speech_response = Mock()
    mock_speech_response.stream_to_file = Mock()
    client.audio.speech.create.return_value = mock_speech_response

    # Mock image generation
    mock_image_data = Mock()
    mock_image_data.url = "https://example.com/test-image.png"
    mock_image_response = Mock()
    mock_image_response.data = [mock_image_data]
    client.images.generate.return_value = mock_image_response

    return client


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings module"""
    monkeypatch.setattr("settings.openai_api_key", "test_openai_key")
    monkeypatch.setattr("settings.openai_assistant_id", "asst_test123")
    monkeypatch.setattr("settings.pvporcupine_api_key", "test_porcupine_key")
    monkeypatch.setattr("settings.stable_diffusion_api", "192.168.1.1")
    monkeypatch.setattr("settings.stable_diffusion_port", "7860")
    monkeypatch.setattr("settings.apprise_services", [])


@pytest.fixture
def temp_test_dirs(tmp_path):
    """Create temporary test directories"""
    saved_images = tmp_path / "saved_images"
    audio = tmp_path / "audio"
    assistant_images = tmp_path / "assistant_images"

    saved_images.mkdir()
    audio.mkdir()
    assistant_images.mkdir()

    # Create some test files
    (audio / "test.mp3").write_text("test audio")
    (assistant_images / "listening.png").write_text("test image")

    return {
        "saved_images": str(saved_images),
        "audio": str(audio),
        "assistant_images": str(assistant_images),
    }


@pytest.fixture
def mock_vlc_player(mocker):
    """Mock VLC media player"""
    mock_player = MagicMock()
    mock_player.play = Mock()
    mock_player.is_playing = Mock(side_effect=[True, True, False])

    mock_vlc = mocker.patch("vlc.MediaPlayer")
    mock_vlc.return_value = mock_player

    return mock_player


@pytest.fixture
def mock_subprocess(mocker):
    """Mock subprocess calls"""
    mock_call = mocker.patch("subprocess.call")
    mock_popen = mocker.patch("subprocess.Popen")

    return {
        "call": mock_call,
        "popen": mock_popen,
    }


@pytest.fixture
def mock_image_processing(mocker):
    """Mock PIL Image processing"""
    mock_image = MagicMock()
    mock_image.resize = Mock(return_value=mock_image)
    mock_image.save = Mock()

    mock_open = mocker.patch("PIL.Image.open")
    mock_open.return_value = mock_image

    return mock_image
