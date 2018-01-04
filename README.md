# OfficeControl
A script for controlling the actions to be preformed when the button at our door is pressed

## Hardware and setup
The script is intended to run on a Raspberry PI, the button have to be connected to GIPO pin 24(BCM)

## Dependencies
Tested with Python 2.7, but sould run with newer versions as well.

The voice files are generated with gTTS which uses Google TTS to generate mp3 files. Install with:
`pip install gtts`

## Executing 
Start the system by running: `python door-button.py`
