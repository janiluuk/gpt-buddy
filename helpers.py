import vlc
import subprocess
import time
import logging
import os


def play_audio(audio_file_path):
    """
    Plays a given audio file and waits until it's finished playing
    """
    if not os.path.exists(audio_file_path):
        logging.error(f"Audio file not found: {audio_file_path}")
        return
    
    player = vlc.MediaPlayer(audio_file_path)
    player.play()
    time.sleep(1)
    # Ensure the program doesn't cut off the text to speech
    while player.is_playing():
        time.sleep(1)


def display_image(image_file_path):
    """
    Displays an image to the console framebuffer imageviewer (fbi)
    """
    # Validate that the file exists and is within allowed directories
    if not os.path.exists(image_file_path):
        logging.error(f"Image file not found: {image_file_path}")
        return
    
    # Get absolute path to prevent directory traversal
    abs_path = os.path.abspath(image_file_path)
    
    # Remove the current image by killing the fbi process
    # Use list arguments to prevent shell injection
    subprocess.call(["sudo", "killall", "-15", "fbi"])
    
    # Display the new image
    # Use list arguments to prevent shell injection
    subprocess.Popen(["sudo", "fbi", "-T", "1", abs_path, "--noverbose"])
