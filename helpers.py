import vlc
import subprocess
import time
import logging
import os


# Track the fbi process for better cleanup
_fbi_process = None


def play_audio(audio_file_path):
    """
    Plays a given audio file and waits until it's finished playing
    """
    if not os.path.exists(audio_file_path):
        logging.error(f"Audio file not found: {audio_file_path}")
        return
    
    try:
        logging.info(f"Playing audio: {audio_file_path}")
        player = vlc.MediaPlayer(audio_file_path)
        player.play()
        time.sleep(1)
        # Ensure the program doesn't cut off the text to speech
        while player.is_playing():
            time.sleep(1)
        logging.debug("Audio playback completed")
    except Exception as e:
        logging.error(f"Error playing audio: {e}")


def display_image(image_file_path):
    """
    Displays an image to the console framebuffer imageviewer (fbi)
    """
    global _fbi_process
    
    # Validate that the file exists and is within allowed directories
    if not os.path.exists(image_file_path):
        logging.error(f"Image file not found: {image_file_path}")
        return
    
    try:
        # Get absolute path to prevent directory traversal
        abs_path = os.path.abspath(image_file_path)
        logging.info(f"Displaying image: {abs_path}")
        
        # Remove the current image by terminating tracked process
        if _fbi_process and _fbi_process.poll() is None:
            # Process is still running, terminate it
            logging.debug(f"Terminating existing fbi process (PID: {_fbi_process.pid})")
            _fbi_process.terminate()
            try:
                _fbi_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                logging.warning("fbi process did not terminate, killing it")
                _fbi_process.kill()
        
        # Display the new image and track the process
        _fbi_process = subprocess.Popen(
            ["sudo", "fbi", "-T", "1", abs_path, "--noverbose"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        logging.debug(f"Started new fbi process (PID: {_fbi_process.pid})")
    except Exception as e:
        logging.error(f"Error displaying image: {e}")


def cleanup_display():
    """Clean up the fbi display process on shutdown"""
    global _fbi_process
    if _fbi_process and _fbi_process.poll() is None:
        logging.info("Cleaning up display process...")
        try:
            _fbi_process.terminate()
            _fbi_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            _fbi_process.kill()
        except Exception as e:
            logging.error(f"Error cleaning up display: {e}")
