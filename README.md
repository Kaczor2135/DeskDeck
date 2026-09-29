# DeskDeck

DeskDeck is a physical desktop controller built with an Arduino Uno, an 8x8 MAX7219 LED matrix, a potentiometer and a push button.

## Features

- 5 profiles: Gaming, Coding, School, Earning and YouTube
- 4-game gaming menu: CS2, Minecraft, Fortnite and GTA V
- 8x8 LED icons
- Active-profile border
- Potentiometer profile/game selection
- Potentiometer Windows volume control while active
- 3-second long press to close an active mode
- Serial communication between Arduino and Python
- Automatic opening of selected applications and websites
- CS2 launching through Steam

## Hardware

- Arduino Uno
- MAX7219 8x8 LED matrix
- Push button
- Potentiometer

### Pinout

| Component | Arduino |
|---|---:|
| MAX7219 DIN | D11 |
| MAX7219 CLK | D13 |
| MAX7219 CS | D10 |
| Button | D2 |
| Potentiometer | A0 |

## Software

- Arduino IDE
- Python 3
- `pyserial`
- `pycaw`
- Google Chrome
- Visual Studio Code
- Steam

## Project structure

```text
DeskDeck/
├── README.md
├── deskdeck.ino
└── deskdeck.py
```

## Installation

Install the Python dependencies:

```bash
pip install pyserial pycaw
```

Upload `deskdeck.ino` to the Arduino Uno using Arduino IDE.

Then check the COM port in `deskdeck.py`:

```python
COM_PORT = "COM5"
BAUDRATE = 115200
```

Change `COM5` if Windows assigned another port.

Run the controller with:

```bash
python deskdeck.py
```

## How it works

The Arduino handles the physical controls and LED matrix. The potentiometer selects profiles when inactive and controls volume when a profile is active. The button activates profiles, opens the gaming menu and closes active modes.

The Python application handles Windows-side actions and communicates with the Arduino over serial at 115200 baud.

## Current limitations

Only CS2 is currently configured to launch. Minecraft, Fortnite and GTA V are present as menu entries but are not configured to launch.

The Coding profile opens VS Code but does not close it when the profile is closed.

## License

No open-source license has been specified in the repository yet.
