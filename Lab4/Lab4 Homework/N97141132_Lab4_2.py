import RPi.GPIO as GPIO
import time

# 設定使用 BCM 編號系統
GPIO.setmode(GPIO.BCM)

# 超音波模組的 TRIG_y 與 ECHO_r 引腳設定
TRIG_y = 14  # GPIO14
ECHO_r = 15  # GPIO15

# 設定引腳輸出入模式
GPIO.setup(TRIG_y, GPIO.OUT)
GPIO.setup(ECHO_r, GPIO.IN)


def measure_distance():
    # 確保發射端是關閉的，並稍作延遲讓感測器穩定
    GPIO.output(TRIG_y, False)
    time.sleep(0.5)

    # 發送 10 微秒的高電位脈衝來觸發超音波
    GPIO.output(TRIG_y, True)
    time.sleep(0.00001)
    GPIO.output(TRIG_y, False)

    # 等待 ECHO_r 高電位 (1)，並記錄起始時間
    timeout_start = time.monotonic()

    while GPIO.input(ECHO_r) == 0:
        if time.monotonic() - timeout_start > 0.04:
            raise TimeoutError("等待 ECHO 高電位逾時，請檢查接線")

    pulse_start = time.monotonic()

    # 等待 ECHO_r 變回低電位 (0)，並記錄結束時間
    while GPIO.input(ECHO_r) == 1:
        if time.monotonic() - pulse_start > 0.04:
            raise TimeoutError("等待 ECHO 低電位逾時，請檢查接線")

    pulse_end = time.monotonic()

    # 計算脈衝持續時間，並根據音速轉換為距離（公分）
    # 距離 = (時間 * 聲速 34300 cm/s) / 2
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance


try:
    print("程式啟動，按 Ctrl+C 可以停止測試...")

    while True:

        # LAB4-2
        try:
            # 取得目前測量距離
            distance = measure_distance()

            # 顯示目前距離
            print(f"目前距離：{distance:.2f} cm")

            # 判斷距離是否小於 20 cm
            if distance < 20:
                print("注意！！！")
            else:
                print("沒事")

        except TimeoutError as err:
            print(f"測量失敗：{err}")

        time.sleep(0.1)  # 稍微停一下，避免畫面跳太快

except KeyboardInterrupt:
    # 當按下 Ctrl+C 時，會執行這裡
    print("\n停止測量中...")

finally:
    # 清除 GPIO 設定
    GPIO.cleanup()
    print("GPIO 已清理，程式結束。")