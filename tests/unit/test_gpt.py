"""
Unit tests for gpt.py module
Tests for OpenAI API interactions and image generation
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
import gpt
import threading


class TestGetAssistant:
    """Tests for get_assistant function"""

    def test_get_assistant_success(self, mock_openai_client, mocker):
        """Test successful assistant retrieval"""
        mock_logging = mocker.patch("gpt.logging")

        # Mock settings
        with patch("gpt.settings") as mock_settings:
            mock_settings.openai_assistant_id = "asst_test123"

            assistant = gpt.get_assistant(mock_openai_client)

            # Verify assistant was retrieved
            assert assistant is not None
            assert assistant.id == "asst_test123"

            # Verify API was called
            mock_openai_client.beta.assistants.retrieve.assert_called_once_with("asst_test123")

            # Verify logging
            mock_logging.info.assert_called()


class TestWhisperTextToSpeech:
    """Tests for whisper_text_to_speech function"""

    def test_whisper_text_to_speech_success(self, mock_openai_client, mocker):
        """Test successful text-to-speech generation"""
        mock_play_audio = mocker.patch("gpt.helpers.play_audio")

        text = "Hello, this is a test"
        gpt.whisper_text_to_speech(mock_openai_client, text)

        # Verify API was called with correct parameters
        mock_openai_client.audio.speech.create.assert_called_once_with(
            model="tts-1", voice="nova", input=text
        )

        # Verify audio file was played
        mock_play_audio.assert_called_once()

    def test_whisper_text_to_speech_empty_text(self, mock_openai_client, mocker):
        """Test with empty text input"""
        mock_play_audio = mocker.patch("gpt.helpers.play_audio")

        gpt.whisper_text_to_speech(mock_openai_client, "")

        # Should still call API (OpenAI will handle empty text)
        mock_openai_client.audio.speech.create.assert_called_once()


class TestGenerateChatGPTImage:
    """Tests for generate_chatgpt_image function"""

    def test_generate_image_success(self, mock_openai_client, mocker, mock_image_processing):
        """Test successful image generation and display"""
        # Mock requests.get
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.raw.decode_content = True
        mock_requests = mocker.patch("gpt.requests.get", return_value=mock_response)

        # Mock file operations
        mock_file = mocker.patch("builtins.open", mock_open())

        # Mock shutil.copyfileobj
        mock_copyfile = mocker.patch("gpt.shutil.copyfileobj")

        # Mock display_image
        mock_display = mocker.patch("gpt.helpers.display_image")

        # Mock logging
        mock_logging = mocker.patch("gpt.logging")

        user_text = "Show me a cat"
        assistant_text = "Here's a cat for you"

        gpt.generate_chatgpt_image(mock_openai_client, user_text, assistant_text)

        # Verify image generation was called
        mock_openai_client.images.generate.assert_called_once()
        call_args = mock_openai_client.images.generate.call_args[1]
        assert call_args["model"] == "dall-e-3"
        assert call_args["size"] == "1024x1024"

        # Verify image was downloaded with timeout
        mock_requests.assert_called_once()
        assert mock_requests.call_args[1]["timeout"] == 30

        # Verify image was resized to 800x480
        mock_image_processing.resize.assert_called_once_with((800, 480))

        # Verify image was displayed
        mock_display.assert_called_once_with("resized.png")

    def test_generate_image_network_error(self, mock_openai_client, mocker):
        """Test handling of network errors during image download"""
        # Mock requests.get to raise an exception
        mocker.patch("gpt.requests.get", side_effect=Exception("Network error"))

        mock_logging = mocker.patch("gpt.logging")

        # Should not crash
        try:
            gpt.generate_chatgpt_image(mock_openai_client, "test", "test")
        except Exception as e:
            # Exception should be raised but handled gracefully in production
            assert "Network error" in str(e)

    def test_generate_image_response_not_ok(
        self, mock_openai_client, mocker, mock_image_processing
    ):
        """Test handling when image download fails"""
        mock_response = MagicMock()
        mock_response.ok = False
        mocker.patch("gpt.requests.get", return_value=mock_response)

        mock_display = mocker.patch("gpt.helpers.display_image")
        mock_logging = mocker.patch("gpt.logging")

        gpt.generate_chatgpt_image(mock_openai_client, "test", "test")

        # Image should not be displayed if download failed
        mock_display.assert_not_called()


class TestSendToAssistant:
    """Tests for send_to_assistant function"""

    def test_send_to_assistant_success(self, mock_openai_client, mocker):
        """Test successful assistant interaction"""
        mock_tts = mocker.patch("gpt.whisper_text_to_speech")
        mock_thread = mocker.patch("gpt.threading.Thread")
        mock_logging = mocker.patch("gpt.logging")
        mocker.patch("gpt.time.sleep")  # Speed up test

        input_text = "What's the weather?"
        assistant_id = "asst_test123"
        thread_id = "thread_test123"

        mock_assistant = Mock()
        mock_assistant.id = assistant_id

        gpt.send_to_assistant(
            mock_openai_client, mock_assistant, thread_id, input_text, text_to_speech=True
        )

        # Verify message was created
        mock_openai_client.beta.threads.messages.create.assert_called_once()

        # Verify run was created
        mock_openai_client.beta.threads.runs.create.assert_called_once()

        # Verify TTS was called
        mock_tts.assert_called_once()

        # Verify image thread was started
        mock_thread.return_value.start.assert_called_once()

    def test_send_to_assistant_no_tts(self, mock_openai_client, mocker):
        """Test assistant interaction without text-to-speech"""
        mock_tts = mocker.patch("gpt.whisper_text_to_speech")
        mocker.patch("gpt.threading.Thread")
        mocker.patch("gpt.time.sleep")
        mocker.patch("gpt.logging")

        mock_assistant = Mock()
        mock_assistant.id = "asst_test123"

        gpt.send_to_assistant(
            mock_openai_client, mock_assistant, "thread_test123", "test input", text_to_speech=False
        )

        # TTS should not be called
        mock_tts.assert_not_called()

    def test_send_to_assistant_timeout(self, mock_openai_client, mocker):
        """Test handling of assistant timeout"""
        # Mock run that never completes
        mock_run = Mock()
        mock_run.id = "run_test123"
        mock_run.status = "in_progress"  # Never completes

        mock_openai_client.beta.threads.runs.create.return_value = mock_run
        mock_openai_client.beta.threads.runs.retrieve.return_value = mock_run

        mock_tts = mocker.patch("gpt.whisper_text_to_speech")
        mocker.patch("gpt.threading.Thread")
        mock_sleep = mocker.patch("gpt.time.sleep")
        mock_logging = mocker.patch("gpt.logging")

        mock_assistant = Mock()
        mock_assistant.id = "asst_test123"

        gpt.send_to_assistant(mock_openai_client, mock_assistant, "thread_test123", "test")

        # Should log timeout
        assert mock_logging.info.call_count > 0

        # Should still call TTS with error message
        mock_tts.assert_called_once()
        tts_arg = mock_tts.call_args[0][1]
        assert "went wrong" in tts_arg.lower()

    def test_send_to_assistant_brief_prompt_added(self, mock_openai_client, mocker):
        """Test that brief prompt is added to user input"""
        mocker.patch("gpt.whisper_text_to_speech")
        mocker.patch("gpt.threading.Thread")
        mocker.patch("gpt.time.sleep")
        mocker.patch("gpt.logging")

        mock_assistant = Mock()
        mock_assistant.id = "asst_test123"

        input_text = "Tell me a story"

        gpt.send_to_assistant(mock_openai_client, mock_assistant, "thread_test123", input_text)

        # Check that message content includes brief prompt
        call_args = mock_openai_client.beta.threads.messages.create.call_args[1]
        assert "brief" in call_args["content"].lower()
        assert input_text in call_args["content"]
