"""
Unit tests for apprise_sender.py module
Tests for notification sending functionality
"""
import pytest
from unittest.mock import Mock, patch
import apprise_sender


class TestSend:
    """Tests for send function"""
    
    def test_send_with_configured_services(self, mocker):
        """Test sending notification with configured services"""
        # Mock apprise
        mock_apprise_instance = Mock()
        mock_apprise_class = mocker.patch('apprise_sender.apprise.Apprise')
        mock_apprise_class.return_value = mock_apprise_instance
        
        # Mock settings with services
        mock_settings = mocker.patch('apprise_sender.settings')
        mock_settings.apprise_services = [
            "tgram://test_token/test_chat",
            "discord://webhook_id/webhook_token"
        ]
        
        title = "Test Title"
        message = "Test Message"
        image_path = "test_image.png"
        
        apprise_sender.send(title, message, image_path)
        
        # Verify Apprise instance was created
        mock_apprise_class.assert_called_once()
        
        # Verify services were added
        assert mock_apprise_instance.add.call_count == 2
        mock_apprise_instance.add.assert_any_call("tgram://test_token/test_chat")
        mock_apprise_instance.add.assert_any_call("discord://webhook_id/webhook_token")
        
        # Verify notification was sent
        mock_apprise_instance.notify.assert_called_once_with(
            body=message,
            title=title,
            attach=image_path
        )
    
    def test_send_with_no_services(self, mocker):
        """Test that no notification is sent when no services configured"""
        mock_apprise_class = mocker.patch('apprise_sender.apprise.Apprise')
        
        # Mock settings with empty services
        mock_settings = mocker.patch('apprise_sender.settings')
        mock_settings.apprise_services = []
        
        apprise_sender.send("Test", "Message", "image.png")
        
        # Apprise should not be instantiated
        mock_apprise_class.assert_not_called()
    
    def test_send_with_none_services(self, mocker):
        """Test that no notification is sent when services is None"""
        mock_apprise_class = mocker.patch('apprise_sender.apprise.Apprise')
        
        # Mock settings with None
        mock_settings = mocker.patch('apprise_sender.settings')
        mock_settings.apprise_services = None
        
        apprise_sender.send("Test", "Message", "image.png")
        
        # Apprise should not be instantiated
        mock_apprise_class.assert_not_called()
    
    def test_send_with_empty_title_and_message(self, mocker):
        """Test sending with empty title and message (for image-only notifications)"""
        mock_apprise_instance = Mock()
        mock_apprise_class = mocker.patch('apprise_sender.apprise.Apprise')
        mock_apprise_class.return_value = mock_apprise_instance
        
        mock_settings = mocker.patch('apprise_sender.settings')
        mock_settings.apprise_services = ["tgram://test/test"]
        
        # Send with empty strings
        apprise_sender.send("", "", "image.png")
        
        # Should still call notify
        mock_apprise_instance.notify.assert_called_once()
        call_args = mock_apprise_instance.notify.call_args[1]
        assert call_args['body'] == ""
        assert call_args['title'] == ""
        assert call_args['attach'] == "image.png"
    
    def test_send_multiple_services(self, mocker):
        """Test adding multiple notification services"""
        mock_apprise_instance = Mock()
        mock_apprise_class = mocker.patch('apprise_sender.apprise.Apprise')
        mock_apprise_class.return_value = mock_apprise_instance
        
        mock_settings = mocker.patch('apprise_sender.settings')
        services = [
            "tgram://token1/chat1",
            "discord://webhook1/token1",
            "slack://tokenA/tokenB/tokenC"
        ]
        mock_settings.apprise_services = services
        
        apprise_sender.send("Test", "Message", "image.png")
        
        # Verify all services were added
        assert mock_apprise_instance.add.call_count == len(services)
        for service in services:
            mock_apprise_instance.add.assert_any_call(service)
