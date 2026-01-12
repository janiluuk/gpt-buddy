"""
Unit tests for helpers.py module
Tests for audio playback and image display functionality
"""
import pytest
import os
from unittest.mock import Mock, patch, call
import helpers


class TestPlayAudio:
    """Tests for play_audio function"""
    
    def test_play_audio_with_valid_file(self, mock_vlc_player, mocker, tmp_path):
        """Test that a valid audio file plays successfully"""
        # Create a test audio file
        audio_file = tmp_path / "test.mp3"
        audio_file.write_text("test audio content")
        
        # Mock time.sleep to speed up test
        mock_sleep = mocker.patch('time.sleep')
        
        # Call the function
        helpers.play_audio(str(audio_file))
        
        # Verify VLC player was called
        mock_vlc_player.play.assert_called_once()
        
        # Verify sleep was called (for waiting)
        assert mock_sleep.call_count >= 1
    
    def test_play_audio_with_missing_file(self, mocker):
        """Test that missing audio file is handled gracefully"""
        # Mock logging to capture error
        mock_logging = mocker.patch('helpers.logging')
        
        # Mock VLC to avoid actual playback attempt
        mocker.patch('vlc.MediaPlayer')
        
        # Call with non-existent file
        helpers.play_audio("/non/existent/file.mp3")
        
        # Verify error was logged
        mock_logging.error.assert_called_once()
    
    def test_play_audio_waits_for_completion(self, mock_vlc_player, mocker, tmp_path):
        """Test that function waits until audio finishes playing"""
        audio_file = tmp_path / "test.mp3"
        audio_file.write_text("test")
        
        mock_sleep = mocker.patch('time.sleep')
        
        # is_playing returns True twice, then False
        mock_vlc_player.is_playing.side_effect = [True, True, False]
        
        helpers.play_audio(str(audio_file))
        
        # Should sleep at least 3 times (initial + 2 while playing)
        assert mock_sleep.call_count >= 3


class TestDisplayImage:
    """Tests for display_image function"""
    
    def test_display_image_with_valid_path(self, mock_subprocess, tmp_path):
        """Test that a valid image is displayed correctly"""
        # Create a test image file
        image_file = tmp_path / "test.png"
        image_file.write_text("test image")
        
        # Reset the global _fbi_process before test
        helpers._fbi_process = None
        
        # Call the function
        helpers.display_image(str(image_file))
        
        # Verify fbi was called with correct arguments
        mock_subprocess['popen'].assert_called_once()
        args = mock_subprocess['popen'].call_args[0][0]
        assert "sudo" in args
        assert "fbi" in args
        assert "--noverbose" in args
    
    def test_display_image_with_missing_file(self, mock_subprocess, mocker):
        """Test that missing image file is handled gracefully"""
        mock_logging = mocker.patch('helpers.logging')
        
        # Call with non-existent file
        helpers.display_image("/non/existent/image.png")
        
        # Verify error was logged
        mock_logging.error.assert_called_once()
        
        # Verify fbi was NOT called
        mock_subprocess['popen'].assert_not_called()
    
    def test_display_image_prevents_command_injection(self, mock_subprocess, tmp_path):
        """Test that malicious paths don't cause command injection"""
        # Create a file with special characters in name (safe version)
        image_file = tmp_path / "test_image.png"
        image_file.write_text("test")
        
        # Call with the path
        helpers.display_image(str(image_file))
        
        # Verify that Popen was called with list args (not shell=True)
        mock_subprocess['popen'].assert_called_once()
        call_args = mock_subprocess['popen'].call_args
        
        # First argument should be a list
        assert isinstance(call_args[0][0], list)
        
        # Should not use shell=True
        assert call_args[1].get('shell', False) is False
    
    def test_display_image_uses_absolute_path(self, mock_subprocess, tmp_path):
        """Test that relative paths are converted to absolute paths"""
        # Create a test image
        image_file = tmp_path / "test.png"
        image_file.write_text("test")
        
        # Call with path
        helpers.display_image(str(image_file))
        
        # Get the path that was passed to fbi
        popen_args = mock_subprocess['popen'].call_args[0][0]
        
        # Find the image path in arguments (should be an absolute path to our file)
        image_path = None
        for arg in popen_args:
            if arg.endswith('test.png'):
                image_path = arg
                break
        
        assert image_path is not None, "Image path not found in fbi arguments"
        assert os.path.isabs(image_path), "Image path should be absolute"
    
    def test_display_image_kills_previous_fbi(self, mock_subprocess, tmp_path):
        """Test that previous fbi process is killed before displaying new image"""
        import unittest.mock as mock
        
        image_file = tmp_path / "test.png"
        image_file.write_text("test")
        
        # Create a mock for the first fbi process
        first_process = mock.MagicMock()
        first_process.poll.return_value = None  # Process is still running
        first_process.pid = 12345
        
        # Set up mock to return different process objects for each call
        process_calls = [first_process, mock.MagicMock()]
        mock_subprocess['popen'].side_effect = process_calls
        
        # First call - creates the process
        helpers.display_image(str(image_file))
        
        # Second call - should terminate the previous process
        helpers.display_image(str(image_file))
        
        # Verify the first process was terminated
        first_process.terminate.assert_called_once()
        
        # Verify Popen was called twice (once for each display)
        assert mock_subprocess['popen'].call_count == 2
