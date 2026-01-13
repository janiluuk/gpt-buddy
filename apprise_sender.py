import apprise
import settings
from typing import List


def send(title: str, message: str, image_path: str) -> None:
    """
    Sends a message using Apprise
    :param title: The string for the title of the notification
    :param message: The string of the message to send
    :param image_path: Path to the image file to attach
    """
    if settings.apprise_services:
        # Create an Apprise instance
        app = apprise.Apprise()
        for service in settings.apprise_services:
            app.add(service)

        app.notify(
            body=message,
            title=title,
            attach=image_path
        )


if __name__ == "__main__":
    send("", "", "dalle_image.png")
