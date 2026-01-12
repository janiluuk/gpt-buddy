"""
Unit tests for scheduled_image.py module
Tests for scheduled image generation functionality
"""
import pytest
from unittest.mock import Mock, patch, mock_open
import scheduled_image


class TestScheduledImage:
    """Tests for scheduled_image function"""
    
    def test_scheduled_image_success(self, mocker, mock_openai_client):
        """Test successful scheduled image generation"""
        # Mock file operations
        thread_id = "thread_test123"
        mock_file = mocker.patch(
            'builtins.open', 
            mock_open(read_data=thread_id)
        )
        mocker.patch('os.path.exists', return_value=True)
        
        # Mock OpenAI client creation
        mock_openai_class = mocker.patch('scheduled_image.OpenAI')
        mock_openai_class.return_value = mock_openai_client
        
        # Mock gpt functions
        mock_get_assistant = mocker.patch('scheduled_image.gpt.get_assistant')
        mock_assistant = Mock()
        mock_get_assistant.return_value = mock_assistant
        
        mock_send = mocker.patch('scheduled_image.gpt.send_to_assistant')
        
        # Mock settings
        mock_settings = mocker.patch('scheduled_image.settings')
        mock_settings.openai_api_key = "test_key"
        
        # Mock logging
        mock_logging = mocker.patch('scheduled_image.logging')
        
        # Mock prompts
        mock_prompts = mocker.patch('scheduled_image.prompts')
        mock_prompts.scheduled_image_prompt = "Test prompt"
        
        # Run the function
        scheduled_image.scheduled_image()
        
        # Verify file was read
        mock_file.assert_called()
        
        # Verify send_to_assistant was called with correct parameters
        mock_send.assert_called_once()
        call_args = mock_send.call_args[0]
        assert call_args[0] == mock_openai_client
        assert call_args[1] == mock_assistant
        assert call_args[2] == thread_id
        
        # Verify text_to_speech was False
        assert mock_send.call_args[1]['text_to_speech'] is False
    
    def test_scheduled_image_missing_file(self, mocker):
        """Test handling when assistant_thread.txt is missing"""
        # Mock os.path.exists to return False
        mocker.patch('os.path.exists', return_value=False)
        
        # Mock logging
        mock_logging = mocker.patch('scheduled_image.logging')
        
        # Run the function
        scheduled_image.scheduled_image()
        
        # Verify error was logged
        mock_logging.error.assert_called_once()
        assert "not found" in mock_logging.error.call_args[0][0].lower()
    
    def test_scheduled_image_empty_thread_id(self, mocker, mock_openai_client):
        """Test handling when thread file contains empty/whitespace-only content"""
        # Mock file with empty content
        mocker.patch('builtins.open', mock_open(read_data="  \n  "))
        mocker.patch('os.path.exists', return_value=True)
        
        # Mock OpenAI
        mock_openai_class = mocker.patch('scheduled_image.OpenAI')
        mock_openai_class.return_value = mock_openai_client
        
        mock_get_assistant = mocker.patch('scheduled_image.gpt.get_assistant')
        mock_send = mocker.patch('scheduled_image.gpt.send_to_assistant')
        
        # Mock logging
        mock_logging = mocker.patch('scheduled_image.logging')
        
        # Mock settings
        mock_settings = mocker.patch('scheduled_image.settings')
        mock_settings.openai_api_key = "test_key"
        
        # Run the function
        scheduled_image.scheduled_image()
        
        # Verify error was logged
        mock_logging.error.assert_called()
        assert "empty" in mock_logging.error.call_args[0][0].lower()
        
        # send_to_assistant should not be called
        mock_send.assert_not_called()
    
    def test_scheduled_image_strips_whitespace(self, mocker, mock_openai_client):
        """Test that thread ID whitespace is stripped"""
        thread_id = "thread_test123"
        thread_with_whitespace = f"  {thread_id}  \n"
        
        mocker.patch('builtins.open', mock_open(read_data=thread_with_whitespace))
        mocker.patch('os.path.exists', return_value=True)
        
        mock_openai_class = mocker.patch('scheduled_image.OpenAI')
        mock_openai_class.return_value = mock_openai_client
        
        mock_get_assistant = mocker.patch('scheduled_image.gpt.get_assistant')
        mock_assistant = Mock()
        mock_get_assistant.return_value = mock_assistant
        
        mock_send = mocker.patch('scheduled_image.gpt.send_to_assistant')
        
        mock_settings = mocker.patch('scheduled_image.settings')
        mock_settings.openai_api_key = "test_key"
        
        mocker.patch('scheduled_image.logging')
        
        mock_prompts = mocker.patch('scheduled_image.prompts')
        mock_prompts.scheduled_image_prompt = "Test"
        
        scheduled_image.scheduled_image()
        
        # Verify stripped thread ID was used
        call_args = mock_send.call_args[0]
        assert call_args[2] == thread_id  # Should be stripped
    
    def test_scheduled_image_api_error(self, mocker, mock_openai_client):
        """Test handling of API errors during scheduled image generation"""
        mocker.patch('builtins.open', mock_open(read_data="thread_test123"))
        mocker.patch('os.path.exists', return_value=True)
        
        mock_openai_class = mocker.patch('scheduled_image.OpenAI')
        mock_openai_class.return_value = mock_openai_client
        
        mock_get_assistant = mocker.patch('scheduled_image.gpt.get_assistant')
        mock_assistant = Mock()
        mock_get_assistant.return_value = mock_assistant
        
        # Make send_to_assistant raise an exception
        mock_send = mocker.patch(
            'scheduled_image.gpt.send_to_assistant',
            side_effect=Exception("API Error")
        )
        
        mock_settings = mocker.patch('scheduled_image.settings')
        mock_settings.openai_api_key = "test_key"
        
        mocker.patch('scheduled_image.logging')
        
        mock_prompts = mocker.patch('scheduled_image.prompts')
        mock_prompts.scheduled_image_prompt = "Test"
        
        # Should raise exception (would be handled by cronjob)
        with pytest.raises(Exception) as exc_info:
            scheduled_image.scheduled_image()
        
        assert "API Error" in str(exc_info.value)
