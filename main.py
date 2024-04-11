import apprise_sender
import gpt
import helpers
import logging
import os
import random
import settings
import shutil
import speech_recognition
import time
import pvporcupine
from pvrecorder import PvRecorder
from openai import OpenAI
import webuiapi
from PIL import Image

# create API client
api = webuiapi.WebUIApi()

# create API client with custom host, port
current_prompt=""



def main():
    client = OpenAI(api_key=settings.openai_api_key)
    assistant = gpt.get_assistant(client)
    assistant_thread = client.beta.threads.create()
    images = os.listdir("saved_images")
    random_image = random.choice(images)
    helpers.display_image(f"saved_images/{random_image}")
    current_image = random_image

    # Save the assistant thread to a text file, so we can use it in our
    # scheduled image cronjob
    with open("assistant_thread.txt", "w") as assistant_thread_file:
        assistant_thread_file.write(assistant_thread.id)

    # test_input = "An interesting fact"
    # send_to_assistant(client, assistant, assistant_thread, test_input)

    # List the recording devices
    for i, device in enumerate(PvRecorder.get_available_devices()):
        logging.info("Device %d: %s" % (i, device))

    running = True
    wait_for_hotword = True
    first_session_listen = True
    current_prompt = None
    prompt = None

    while running:
        if wait_for_hotword:
            if first_session_listen:
                # Hotword setup
                logging.info(pvporcupine.KEYWORDS)
                pvporcupine_api_key = settings.pvporcupine_api_key
                handle = pvporcupine.create(
                    access_key=pvporcupine_api_key, keywords=["porcupine"]
                )

                hotword_recorder = PvRecorder(
                    frame_length=handle.frame_length, device_index=1
                )
                hotword_recorder.start()

                logging.info("Waiting for hotword...")
                first_session_listen = False

            # Wait for the hotword
            pcm = hotword_recorder.read()
            result = handle.process(pcm)
            if result >= 0:
                # Hotword detected
                logging.info("Detected!")
                wait_for_hotword = False
                hotword_recorder.delete()
                handle.delete()
        else:
            # Hotword detected, continue with speech recognition
            hotword_responses = [
                "audio/what.mp3",
                "audio/yes_question.mp3",
            ]
            helpers.play_audio(random.choice(hotword_responses))
            helpers.display_image("assistant_images/listening.png")
            microphone = speech_recognition.Microphone()
            speech_result = speech_recognition.Recognizer()

            logging.info("Ready for input:")
            with microphone as source:
                audio = speech_result.listen(source, phrase_time_limit=10)
            try:
                recognised_speech = speech_result.recognize_google(audio)
                logging.info(f"Recognised speech: {recognised_speech}")
                wait_for_hotword = True
                first_session_listen = True

                # List of phrases to cancel the conversation before making
                # requests to ChatGPT
                cancel_phrases = [
                    "nevermind",
                    "thanks",
                    "never mind",
                    "stop",
                    "cancel that",
                    "cancel",
                    "nothing",
                    "forget it",
                ]

                # List of phrases to send the dall-e image to telegram
                send_image_phrases = [
                    "send",
                    "telegram",
                ]

                # List of phrases to display a random image from the saved
                # images folder.
                show_random_image_phrases = [
                    "random",
                ]
                # List of phrases to display a random image from the saved
                # images folder.
                show_ai_image_phrases = [
                    "make image",
                ]
                make_another_phrases = [
                    "make another",
                    "make more"
                ]


                if any(
                    cancel_phrase in recognised_speech
                    for cancel_phrase in cancel_phrases
                ):
                    # Cancel the conversation
                    end_conversation_phrases = [
                        "audio/oh_ok.mp3",
                        "audio/alright_then.mp3",
                    ]
                    helpers.play_audio(random.choice(end_conversation_phrases))
                    helpers.display_image("resized.png")

                elif any(
                    send_image_phrase in recognised_speech
                    for send_image_phrase in send_image_phrases
                ):

                    # Send the last created dall-e image to Telegram
                    helpers.display_image("resized.png")
                    helpers.play_audio("audio/sending_image.mp3")
                    apprise_sender.send("", "", "dalle_image.png")

                    # Save the image to the saved images folder
                    filename = time.strftime("%Y%m%d-%H%M%S")
                    shutil.copyfile("resized.png", f"saved_images/{filename}.png")

                elif any(
                    make_another_phrase in recognised_speech
                    for make_another_phrase in make_another_phrases
                ):
                    api = webuiapi.WebUIApi(host='192.168.2.22', port=7860, steps=8)
                    end_conversation_phrases = [
                        "audio/oh_ok.mp3",
                        "audio/alright_then.mp3",
                    ]
                    helpers.play_audio(random.choice(end_conversation_phrases))

                    filename = time.strftime("%Y%m%d-%H%M%S")
                    print(current_prompt)

                    result1 = api.txt2img(prompt=current_prompt,
                      negative_prompt="ugly, out of frame",
                      styles=["anime"],
                      width=800,
                      height=480,
                      save_images=True,
                      cfg_scale=2
                    )
                    file_path = "saved_images/{filename}.png"
                    result1.image.save(file_path)
                    helpers.display_image(file_path)
                    current_image = file_path

                elif any(
                    show_random_image_phrase in recognised_speech
                    for show_random_image_phrase in show_random_image_phrases
                ):
                    # Pick a random saved image and display it on the screen
                    images = os.listdir("saved_images")
                    if current_image:
                        images.remove(current_image)
                    random_image = random.choice(images)
                    helpers.display_image(f"saved_images/{random_image}")
                    current_image = random_image
                elif any(
                    show_ai_image_phrase in recognised_speech
                    for show_ai_image_phrase in show_ai_image_phrases
                ):
                    # Pick a random saved image and display it on the screen
                    api = webuiapi.WebUIApi(host='192.168.2.22', port=7860, steps=8)
                    filename = time.strftime("%Y%m%d-%H%M%S")
                    end_conversation_phrases = [
                        "audio/oh_ok.mp3",
                        "audio/alright_then.mp3",
                    ]
                    helpers.play_audio(random.choice(end_conversation_phrases))

                    current_prompt = ""+recognised_speech.replace("make image", "")
                    result1 = api.txt2img(prompt=current_prompt,
                      negative_prompt="ugly, out of frame",
                      width=800,
                      height=480,
                      styles=["lcmxl"],
                      save_images=True,
                      cfg_scale=2
                    )
                    file_path = "saved_images/{filename}.png"
                    result1.image.save(file_path)
                    helpers.display_image(file_path)
                    current_image = file_path

                else:
                    print(recognised_speech)

                    helpers.display_image("assistant_images/thinking.png")
                    helpers.play_audio("audio/hmm.mp3")
                    gpt.send_to_assistant(
                        client, assistant, assistant_thread.id, recognised_speech
                    )
                    wait_for_hotword = False

            except speech_recognition.UnknownValueError:
                logging.info("Could not understand audio")
                helpers.display_image("resized.png")
                wait_for_hotword = True
                first_session_listen = True
            except speech_recognition.RequestError as e:
                logging.info(f"Error: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(filename)s %(lineno)d - %(message)s",
        level=logging.INFO,
        handlers=[
            logging.FileHandler("/tmp/gpt_assistant.log"),
            logging.StreamHandler(),
        ],
    )

    main()
