# OfficeControl
A script for controlling the actions to be preformed when the button at our door is pressed

## Hardware and setup
The script is intended to run on a Raspberry PI, the button have to be connected to GIPO pin (BCM) as specified in the config.yaml

### Config
The config file should be self explanatory:
```yaml
gpio:
  pin: 24 # the Bcm pin to connect the button to 
ical:
  - name: # A name for the user a calender belongs to
    url: # An http(s) url to an ical calendar
  - name: ..
    url: .. 
messages:
  - # messages to play randomly at button presses
sound: 
  freq: 24000     # audio CD quality 
  bitsize: -16    # unsigned 16 bit
  channels: 1     # 1 is mono, 2 is stereo
  ```

IF NOT ON Raspberry Pi you will need to comment out GPIO:
```yaml
#gpio:
#  pin: 24 # the Bcm pin to connect the button to
```

## Dependencies
Tested with Python 3, but sould run with newer versions as well.

The voice files are generated with gTTS which uses Google TTS to generate mp3 files. Install with:
`pip install gtts`
The project requires pygame:
`pip install pygame`
The project requires yaml:
`pip install pyyaml`
The project requires icalendar:
`pip install icalendar`



## Executing 
Start the system by running: `python door_button.py`
