import RPi.GPIO as GPIO
import time

# BOARD = Raspberry Pi 實體腳位編號
GPIO.setmode(GPIO.BOARD)

LED_PIN = 11       # 實體 Pin 11 = GPIO17
BUZZER_PIN = 13    # 實體 Pin 13 = GPIO27

GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# 蜂鳴器 PWM
voice = GPIO.PWM(BUZZER_PIN, 523)

# Morse code 時間
SHORT = 0.2
LONG = SHORT * 3
GAP = 0.2
LETTER_GAP = 0.6


def signal(duration):
    """LED 和蜂鳴器同時動作"""
    GPIO.output(LED_PIN, GPIO.HIGH)
    voice.start(50)

    time.sleep(duration)

    GPIO.output(LED_PIN, GPIO.LOW)
    voice.stop()

    time.sleep(GAP)


def S():
    signal(SHORT)
    signal(SHORT)
    signal(SHORT)


def O():
    signal(LONG)
    signal(LONG)
    signal(LONG)


try:
    # S = ...
    S()

    time.sleep(LETTER_GAP)

    # O = ---
    O()

    time.sleep(LETTER_GAP)

    # S = ...
    S()

finally:
    voice.stop()
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()
