from __future__ import annotations

import os
import subprocess
import time

import serial
from pycaw.pycaw import AudioUtilities


COM_PORT = "COM5"
BAUDRATE = 115200

current_profile = 0
current_game = 0
active_profile = None

profile_processes = {
    0: [],
    1: [],
    2: [],
    3: [],
    4: [],
}

audio_device = None


def initialize_audio():
    global audio_device

    try:
        audio_device = AudioUtilities.GetSpeakers()
        print("Sterowanie głośnością: OK")
    except Exception as error:
        audio_device = None
        print("Nie udało się uruchomić sterowania głośnością:")
        print(error)


def set_volume_from_pot(pot_value: int):
    if audio_device is None:
        return

    volume = round((pot_value / 1023) * 100)
    volume = max(0, min(100, volume))

    try:
        audio_device.volume_percent = volume
        print(f"Głośność: {volume}%")
    except Exception as error:
        print("Błąd zmiany głośności:")
        print(error)


def find_chrome():
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(
            r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"
        ),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None


CHROME = find_chrome()
CHROME_PROFILE = os.path.join(os.environ["TEMP"], "DESKDECK_CHROME")


def open_chrome(urls: list[str]):
    if CHROME is None:
        print("Nie znaleziono Google Chrome.")
        return None

    command = [
        CHROME,
        f"--user-data-dir={CHROME_PROFILE}",
        "--start-maximized",
        "--new-window",
    ]
    command.extend(urls)

    try:
        return subprocess.Popen(command)
    except Exception as error:
        print("Błąd uruchamiania Chrome:")
        print(error)
        return None


def close_process(process):
    if process is None:
        return

    try:
        if process.poll() is None:
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception as error:
        print("Błąd zamykania procesu:")
        print(error)


def send_status(status: str):
    try:
        arduino.write(f"STATUS:{status}\n".encode())
    except Exception:
        pass


def launch_game(game: int):
    global current_game
    current_game = game

    if game == 0:
        print("\n=== CS2 ===")

        try:
            process = subprocess.Popen(
                ["cmd", "/c", "start", "", "steam://rungameid/730"],
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            profile_processes[0] = [process]
            print("CS2 -> uruchamianie")
            return True
        except Exception as error:
            print("Błąd uruchamiania CS2:")
            print(error)
            return False

    if game == 1:
        print("\n=== MINECRAFT ===")
        print("Minecraft -> jeszcze nie skonfigurowany.")
    elif game == 2:
        print("\n=== FORTNITE ===")
        print("Fortnite -> jeszcze nie skonfigurowany.")
    elif game == 3:
        print("\n=== GTA V ===")
        print("GTA V -> jeszcze nie skonfigurowane.")

    return False


def close_gaming():
    print("\n=== ZAMYKAM GAMING ===")
    subprocess.run(
        ["taskkill", "/IM", "cs2.exe", "/F"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    profile_processes[0] = []
    print("CS2 -> zamknięty")


def open_coding():
    print("\n=== CODING ===")

    try:
        subprocess.Popen(
            ["cmd", "/c", "start", "", "code"],
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        print("VS Code -> uruchomiony")
        return True
    except Exception as error:
        print("Nie udało się uruchomić VS Code:")
        print(error)
        return False


def close_coding():
    print("\n=== WYJŚCIE Z CODING ===")
    print("VS Code pozostaje otwarty.")


def open_school():
    print("\n=== SCHOOL ===")
    process = open_chrome(["https://portal.librus.pl/"])

    if process:
        profile_processes[2] = [process]
        print("Librus -> otwarty")
        return True

    return False


def close_school():
    print("\n=== ZAMYKAM SCHOOL ===")
    for process in profile_processes[2]:
        close_process(process)
    profile_processes[2] = []


def open_earning():
    print("\n=== EARNING ===")
    process = open_chrome(
        [
            "https://heycash.com/",
            "https://www.primeopinion.com/",
        ]
    )

    if process:
        profile_processes[3] = [process]
        print("HeyCash -> karta 1")
        print("Prime Opinion -> karta 2")
        return True

    return False


def close_earning():
    print("\n=== ZAMYKAM EARNING ===")
    for process in profile_processes[3]:
        close_process(process)
    profile_processes[3] = []


def open_youtube():
    print("\n=== YOUTUBE ===")
    process = open_chrome(["https://www.youtube.com/"])

    if process:
        profile_processes[4] = [process]
        print("YouTube -> otwarty")
        return True

    return False


def close_youtube():
    print("\n=== ZAMYKAM YOUTUBE ===")
    for process in profile_processes[4]:
        close_process(process)
    profile_processes[4] = []


def open_profile(profile: int):
    global active_profile

    if profile == 0:
        print("\nGaming -> menu gier")
        return

    success = False

    if profile == 1:
        success = open_coding()
    elif profile == 2:
        success = open_school()
    elif profile == 3:
        success = open_earning()
    elif profile == 4:
        success = open_youtube()

    if success:
        active_profile = profile
        send_status("ON")
        print(f"Profil {profile} -> ACTIVE")


def close_profile(profile: int):
    global active_profile

    if profile == 0:
        close_gaming()
    elif profile == 1:
        close_coding()
    elif profile == 2:
        close_school()
    elif profile == 3:
        close_earning()
    elif profile == 4:
        close_youtube()

    active_profile = None
    send_status("OFF")
    print("Tryb nieaktywny.")


def toggle_profile(profile: int):
    global active_profile

    if active_profile == profile:
        print("\nTen tryb jest już aktywny.")
        print("Przytrzymaj przycisk 3 sekundy, żeby go zamknąć.")
        return

    if active_profile is not None:
        close_profile(active_profile)

    open_profile(profile)


print("====================================")
print("             DESKDECK")
print("====================================\n")

initialize_audio()

print("\nŁączenie z Arduino...")

try:
    arduino = serial.Serial(COM_PORT, BAUDRATE, timeout=1)
except Exception as error:
    print("\nNIE UDAŁO SIĘ POŁĄCZYĆ Z ARDUINO\n")
    print(error)
    raise SystemExit

time.sleep(2)

print("Arduino połączone.")
arduino.write(b"GET_PROFILE\n")


while True:
    try:
        line = (
            arduino.readline()
            .decode("utf-8", errors="ignore")
            .strip()
        )

        if not line:
            continue

        print("Arduino >", line)

        if line.startswith("PROFILE:"):
            try:
                current_profile = int(line.split(":")[1])

                names = {
                    0: "GAMING",
                    1: "CODING",
                    2: "SCHOOL",
                    3: "EARNING",
                    4: "YOUTUBE",
                }

                print("Wybrano:", names.get(current_profile, "UNKNOWN"))
            except ValueError:
                print("Błędny numer profilu.")

        elif line == "GAME_MENU":
            print("\n====================")
            print("       GAME MENU")
            print("====================")
            print("Potencjometr -> wybór gry")
            print("Klik -> uruchomienie")
            print("3 sekundy -> wyjście")

        elif line.startswith("GAME_SELECT:"):
            try:
                current_game = int(line.split(":")[1])

                games = {
                    0: "CS2",
                    1: "Minecraft",
                    2: "Fortnite",
                    3: "GTA V",
                }

                print("Wybrana gra:", games.get(current_game, "UNKNOWN"))
            except ValueError:
                print("Błędny numer gry.")

        elif line.startswith("GAME:"):
            try:
                game = int(line.split(":")[1])
                success = launch_game(game)

                if success:
                    active_profile = 0
                    send_status("ON")
            except ValueError:
                print("Błędny numer gry.")

        elif line == "GAME_MENU_CLOSE":
            print("\nWyjście z menu gier.")

        elif line == "CLICK":
            print("\n>>> CLICK <<<")
            toggle_profile(current_profile)

        elif line.startswith("POT:"):
            if active_profile is not None:
                try:
                    pot_value = int(line.split(":")[1])
                    set_volume_from_pot(pot_value)
                except ValueError:
                    print("Nieprawidłowa wartość POT.")

        elif line == "CLOSE":
            print("\n>>> PRZYCISK PRZYTRZYMANY 3 SEKUNDY <<<")
            if active_profile is not None:
                close_profile(active_profile)

        elif line == "READY":
            print("Arduino -> READY")

        elif line == "PONG":
            print("Arduino -> PONG")

        elif line == "DISPLAY_OK":
            print("Matryca -> OK")

    except KeyboardInterrupt:
        print("\nZamykanie DeskDeck...")

        if active_profile is not None:
            close_profile(active_profile)

        try:
            arduino.close()
        except Exception:
            pass

        print("Gotowe.")
        break

    except Exception as error:
        print("\nBŁĄD:")
        print(error)
