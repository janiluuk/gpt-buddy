import helpers
import prompts
import settings
import logging
import requests
import shutil
import threading
import time
from io import BytesIO
from PIL import Image
from pathlib import Path
from openai import OpenAI
from openai.types.beta.assistant import Assistant

# Constants
ASSISTANT_TIMEOUT_SECONDS = 10
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 480
NETWORK_TIMEOUT_SECONDS = 30


image_thread = None


def get_assistant(openai_client: OpenAI) -> Assistant:
    """
    Returns an already-created Assistant.
    """
    try:
        logging.info(f"Retrieving OpenAI Assistant: {settings.openai_assistant_id}")
        assistant = openai_client.beta.assistants.retrieve(settings.openai_assistant_id)
        logging.info(f"Successfully retrieved assistant: {assistant.id}")
        return assistant
    except Exception as e:
        logging.error(f"Failed to retrieve assistant: {e}")
        raise


def whisper_text_to_speech(openai_client: OpenAI, text_to_say: str) -> None:
    """
    Text to speech using OpenAI's Whisper API.
    """
    try:
        logging.info(f"Generating speech for text (length: {len(text_to_say)} chars)")
        speech_file_path = Path(__file__).parent / "speech.mp3"
        response = openai_client.audio.speech.create(model="tts-1", voice="nova", input=text_to_say)
        response.stream_to_file(speech_file_path)
        logging.info(f"Speech file saved to: {speech_file_path}")
        helpers.play_audio(speech_file_path)
    except Exception as e:
        logging.error(f"Failed to generate speech: {e}")
        raise


def generate_chatgpt_image(
    openai_client: OpenAI, user_text: str, assistant_output_text: str
) -> None:
    """
    Generates a dall-e image based on given text (usually the output of the
    GPT assistant)
    """
    try:
        logging.info("Starting DALL-E image generation")
        image_prompt = f"{prompts.assistant_image_prompt}\n{user_text}\n{assistant_output_text}"
        logging.debug(f"Image prompt: {image_prompt[:100]}...")

        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        logging.info(f"DALL-E image URL: {image_url}")

        # Download the image with timeout
        logging.info("Downloading generated image...")
        response = requests.get(image_url, stream=True, timeout=NETWORK_TIMEOUT_SECONDS)
        if response.ok:
            # Process image directly from stream without saving twice
            logging.info(f"Resizing image to {IMAGE_WIDTH}x{IMAGE_HEIGHT}")

            # Read image data into memory
            image_data = BytesIO()
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, image_data)
            image_data.seek(0)

            # Open and resize image from memory
            image = Image.open(image_data)

            # Save original for archival/sending
            image.save("dalle_image.png")

            # Resize for display
            resized_image = image.resize((IMAGE_WIDTH, IMAGE_HEIGHT))
            resized_image.save("resized.png")

            logging.info("Image downloaded, resized and saved")
            helpers.display_image("resized.png")
        else:
            logging.error(f"Failed to download image: HTTP {response.status_code}")
    except Exception as e:
        logging.error(f"Error generating DALL-E image: {e}", exc_info=True)


def send_to_assistant(
    openai_client: OpenAI,
    assistant: Assistant,
    assistant_thread_id: str,
    input_text: str,
    text_to_speech: bool = True,
) -> None:
    """
    Send text to an OpenAI Assistant and gets the response to pass to Whisper
    and Dall-E.
    """
    try:
        logging.info(f"Sending message to assistant. Thread: {assistant_thread_id}")

        # Encourage the GPT3 response to be brief. This is usually set on
        # the assistant prompt, however I've found responses can still be
        # rather long.
        brief_prompt = "Remember to keep responses brief."
        amended_input_text = f"{input_text}\n{brief_prompt}"

        logging.debug(f"Input text: {amended_input_text}")

        openai_client.beta.threads.messages.create(
            thread_id=assistant_thread_id, role="user", content=amended_input_text
        )

        logging.info("Creating assistant run...")
        run = openai_client.beta.threads.runs.create(
            thread_id=assistant_thread_id,
            assistant_id=assistant.id,
        )

        run_completed = False
        timeout_limit = ASSISTANT_TIMEOUT_SECONDS
        timeout_counter = 0
        while not run_completed:
            if timeout_counter >= timeout_limit:
                logging.warning(f"Assistant timeout exceeded ({timeout_limit}s)")
                break
            run = openai_client.beta.threads.runs.retrieve(
                thread_id=assistant_thread_id,
                run_id=run.id,
            )
            if run.status == "completed":
                run_completed = True
                logging.info("Assistant run completed successfully")
            time.sleep(1)
            timeout_counter += 1

        if timeout_counter >= timeout_limit:
            assistant_output = (
                "Sorry, it looks like something went wrong. Try again in a moment or two."
            )
        else:
            thread_messages = openai_client.beta.threads.messages.list(assistant_thread_id)
            # The most recent assistant's response will be the first item in the list
            assistant_output = thread_messages.data[0].content[0].text.value

        logging.info(f"Assistant response (length: {len(assistant_output)} chars)")
        logging.debug(f"Assistant output: {assistant_output}")

        global image_thread
        logging.info("Starting background image generation thread...")
        image_thread = threading.Thread(
            target=generate_chatgpt_image,
            args=(openai_client, input_text, assistant_output),
        )
        image_thread.start()

        if text_to_speech:
            whisper_text_to_speech(openai_client, assistant_output)
        else:
            logging.info("Skipping text-to-speech as requested")

    except Exception as e:
        logging.error(f"Error in send_to_assistant: {e}", exc_info=True)
        raise
