#include <LedControl.h>

#define DIN_PIN 11
#define CLK_PIN 13
#define CS_PIN 10
#define BUTTON_PIN 2
#define POT_PIN A0

LedControl matrix(DIN_PIN, CLK_PIN, CS_PIN, 1);

int currentProfile = 0;
int currentGame = 0;

bool active = false;
bool gamingMenu = false;
bool lastButtonState = HIGH;

unsigned long buttonDownTime = 0;
unsigned long lastPotSend = 0;

int lastPotValue = -1;

const unsigned long POT_SEND_INTERVAL = 80;
const unsigned long LONG_PRESS_TIME = 3000;


byte iconGaming[8] = {
  B00011000,
  B01111110,
  B11111111,
  B11011011,
  B11111111,
  B01100110,
  B01000010,
  B00000000
};

byte iconCoding[8] = {
  B10000001,
  B11000011,
  B01100110,
  B00111100,
  B00111100,
  B01100110,
  B11000011,
  B10000001
};

byte iconSchool[8] = {
  B00011000,
  B00111100,
  B01111110,
  B11111111,
  B11111111,
  B11011011,
  B11011011,
  B11011011
};

byte iconMoney[8] = {
  B00111100,
  B01100110,
  B11000011,
  B11011011,
  B11011011,
  B11000011,
  B01100110,
  B00111100
};

byte iconYoutube[8] = {
  B00000000,
  B01111110,
  B11111111,
  B11011001,
  B11011110,
  B11111111,
  B01111110,
  B00000000
};


byte iconCS2[8] = {
  B00011000,
  B00111100,
  B01111110,
  B11011011,
  B11111111,
  B01111110,
  B00111100,
  B00011000
};

byte iconMinecraft[8] = {
  B11111111,
  B10000001,
  B10100101,
  B10000001,
  B10111101,
  B10011001,
  B10000001,
  B11111111
};

byte iconFortnite[8] = {
  B11111111,
  B11000000,
  B11000000,
  B11111110,
  B11000000,
  B11000000,
  B11000000,
  B11000000
};

byte iconGTA[8] = {
  B11111111,
  B00011000,
  B00110000,
  B01100000,
  B01100000,
  B00110000,
  B00011000,
  B11111111
};


void showIcon(byte icon[8]) {
  for (int row = 0; row < 8; row++) {
    matrix.setRow(0, row, icon[row]);
  }
}


void showActiveIcon(byte icon[8]) {
  for (int row = 0; row < 8; row++) {
    byte value = icon[row];

    if (row == 0 || row == 7) {
      value = B11111111;
    } else {
      value |= B10000001;
    }

    matrix.setRow(0, row, value);
  }
}


void updateGameDisplay() {
  switch (currentGame) {
    case 0:
      showIcon(iconCS2);
      break;

    case 1:
      showIcon(iconMinecraft);
      break;

    case 2:
      showIcon(iconFortnite);
      break;

    case 3:
      showIcon(iconGTA);
      break;
  }
}


void updateDisplay() {
  if (gamingMenu) {
    updateGameDisplay();
    return;
  }

  switch (currentProfile) {
    case 0:
      active ? showActiveIcon(iconGaming) : showIcon(iconGaming);
      break;

    case 1:
      active ? showActiveIcon(iconCoding) : showIcon(iconCoding);
      break;

    case 2:
      active ? showActiveIcon(iconSchool) : showIcon(iconSchool);
      break;

    case 3:
      active ? showActiveIcon(iconMoney) : showIcon(iconMoney);
      break;

    case 4:
      active ? showActiveIcon(iconYoutube) : showIcon(iconYoutube);
      break;
  }
}


int getProfileFromPot(int value) {
  if (value < 205) return 0;
  if (value < 410) return 1;
  if (value < 615) return 2;
  if (value < 820) return 3;
  return 4;
}


int getGameFromPot(int value) {
  if (value < 256) return 0;
  if (value < 512) return 1;
  if (value < 768) return 2;
  return 3;
}


void readPotentiometer() {
  int value = analogRead(POT_PIN);

  if (gamingMenu) {
    int newGame = getGameFromPot(value);

    if (newGame != currentGame) {
      currentGame = newGame;
      updateGameDisplay();

      Serial.print("GAME_SELECT:");
      Serial.println(currentGame);
    }

    return;
  }

  if (!active) {
    int newProfile = getProfileFromPot(value);

    if (newProfile != currentProfile) {
      currentProfile = newProfile;
      updateDisplay();

      Serial.print("PROFILE:");
      Serial.println(currentProfile);
    }

    return;
  }

  if (millis() - lastPotSend < POT_SEND_INTERVAL) {
    return;
  }

  if (lastPotValue == -1 || abs(value - lastPotValue) >= 4) {
    Serial.print("POT:");
    Serial.println(value);

    lastPotValue = value;
    lastPotSend = millis();
  }
}


void readButton() {
  bool buttonState = digitalRead(BUTTON_PIN);

  if (buttonState == LOW && lastButtonState == HIGH) {
    buttonDownTime = millis();
  }

  if (buttonState == HIGH && lastButtonState == LOW) {
    unsigned long pressTime = millis() - buttonDownTime;

    if (gamingMenu) {
      if (pressTime >= LONG_PRESS_TIME) {
        gamingMenu = false;
        currentGame = 0;
        updateDisplay();
        Serial.println("GAME_MENU_CLOSE");
      } else {
        Serial.print("GAME:");
        Serial.println(currentGame);
      }
    } else if (active) {
      if (pressTime >= LONG_PRESS_TIME) {
        Serial.println("CLOSE");
      }
    } else {
      if (pressTime < LONG_PRESS_TIME) {
        if (currentProfile == 0) {
          gamingMenu = true;
          currentGame = 0;
          updateGameDisplay();
          Serial.println("GAME_MENU");
        } else {
          Serial.println("CLICK");
        }
      }
    }
  }

  lastButtonState = buttonState;
}


void readSerial() {
  if (!Serial.available()) {
    return;
  }

  String command = Serial.readStringUntil('\n');
  command.trim();

  if (command == "GET_PROFILE") {
    Serial.print("PROFILE:");
    Serial.println(currentProfile);
  } else if (command == "STATUS:ON") {
    active = true;
    gamingMenu = false;
    lastPotValue = -1;
    lastPotSend = 0;
    updateDisplay();
  } else if (command == "STATUS:OFF") {
    active = false;
    gamingMenu = false;
    lastPotValue = -1;
    lastPotSend = 0;
    updateDisplay();
  } else if (command == "PING") {
    Serial.println("PONG");
  } else if (command == "REDRAW") {
    updateDisplay();
    Serial.println("DISPLAY_OK");
  }
}


void setup() {
  Serial.begin(115200);
  Serial.setTimeout(20);

  pinMode(BUTTON_PIN, INPUT_PULLUP);

  matrix.shutdown(0, false);
  matrix.setIntensity(0, 5);
  matrix.clearDisplay(0);

  updateDisplay();

  Serial.println("READY");

  Serial.print("PROFILE:");
  Serial.println(currentProfile);
}


void loop() {
  readPotentiometer();
  readButton();
  readSerial();

  delay(10);
}
