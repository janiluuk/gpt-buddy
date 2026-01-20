# ChatGPT Buddy

![Tests](https://github.com/janiluuk/gpt-buddy/actions/workflows/test.yml/badge.svg)
![Code Quality](https://github.com/janiluuk/gpt-buddy/actions/workflows/lint.yml/badge.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A ChatGPT assistant connected to a small Raspberry Pi display, with voice activation (using [porcupine](https://github.com/Picovoice/porcupine))
and image generation (using Dall-E and local Stable Diffusion).

## Overview and features
- Hotword activation is handled offline by [porcupine](https://github.com/Picovoice/porcupine).  Saying the default hotword, "Porcupine",
activates the display and starts listening for input.
- Speech is then recognised by Google text to speech.
- The speech input is sent to the ChatGPT Assistant API if none of local service keywords are not given
- The ChatGPT output is sent to the OpenAI Whisper API, to get high quality speech synthesis. This is then played on the display's speakers.
- Meanwhile, both the user input and ChatGPT output is sent to Dall-E 3. 
- Make specific image with local Stable Diffusion by giving prompt "make image about XXXX"
- Saying an included "cancel" command will stop the display listening to user input and revert back to waiting for hotword activation.
- Saying an included "Send that to me" 
- Saying an included "Show me a random picture" command will choose an image from the saved_images directory at random and display to the user.

Optionally, you can also run the **scheduled_image.py** file on a cronjob and it will create an image based on the topics you've talked about with
ChatGPT in the current session.  Sessions are recreated on application restarts.

## Installation
This project is intended to be installed onto a Raspberry Pi using Raspberry PI OS-Lite (terminal-only mode with no desktop environment).  As such, I had to
install the following global packages
```
sudo apt-get install python3-dev
sudo apt-get install portaudio19-dev python-pyaudio python3-pyaudio
sudo apt-get install fbi
```

Next, clone the project and install the dependencies into a python virtual environment:
```
# Clone the repository
$ git clone git@github.com:janiluuk/gpt-buddy.git

# Create a python virtual environment
$ python3 -m venv venv

# Activate the virtual environment
$ source venv/bin/activate

# Install the python dependencies using the requirements.txt file provided
(venv) $ pip install -r requirements.txt
```

Configure your API keys by copying the example settings file:
```
# Copy the example settings file
(venv) $ cp settings.py.example settings.py

# Edit settings.py with your favorite editor and add your API keys
(venv) $ nano settings.py
```

Enter your Open AI, your ChatGPT Assistant `assistant_id`, and porcupine API keys into settings.py in the designated sections. Optionally, you can also provide a chat service (such as Telegram)
if you want to be able to send generated images to yourself.  

**SECURITY WARNING: Never commit your settings.py file with real API keys. The .gitignore file is configured to exclude it.**

Start the program:
```
(venv) $ python main.py
```
Say "Porcupine" to activate the display to start listening to input.

## Development

### Running Tests

Tests are automatically run on every push via GitHub Actions. To run tests locally:

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests with coverage
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Quality

The project uses automated code quality checks:

```bash
# Format code with black
black .

# Lint code
flake8 .

# Security analysis
bandit -r .
```

### CI/CD Workflows

This project includes GitHub Actions workflows for:

- **Tests** (`test.yml`): Runs test suite on Python 3.11, 3.12, and 3.13
- **Code Quality** (`lint.yml`): Checks formatting, linting, and security with Python 3.13
- **Release** (`release.yml`): Automatically creates releases when main branch is updated

See [.github/workflows/README.md](.github/workflows/README.md) for detailed workflow documentation.

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure tests pass: `pytest`
5. Ensure code is formatted: `black .`
6. Submit a pull request

Pull requests will automatically run tests and code quality checks.

## Based On

Based partly on https://github.com/AlanCunningham/chatgpt-assistant

# gpt-buddy
