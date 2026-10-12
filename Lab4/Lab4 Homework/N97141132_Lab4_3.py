import serial
import time
from pathlib import Path
from tm1637 import TM1637

# =====================================
# Lab4-3 UART 串列通訊
# =====================================

# 判斷樹莓派型號，選擇 UART
model = Path("/proc/device-tree/model").read_text(
    errors="ignore"
)

if "Raspberry Pi 5" in model:
    SERIAL_PORT = "/dev/ttyAMA0"
else:
    SERIAL_PORT = "/dev/serial0"

# 設定 UART
ser = serial.Serial(
    port=SERIAL_PORT,
    baudrate=9600,
    timeout=1
)

# 設定 TM1637 LED 顯示器
CLK = 3
DIO = 2

tm = TM1637(CLK, DIO)
tm.brightness(1)

# 傳送的數字
counter = 0

try:
    print("UART 程式啟動")
    print("按 Ctrl+C 停止")
    print("--------------------")

    while True:

        # 將數字轉成四位數字字串
        data = f"{counter:04d}"

        # UART 傳送資料
        ser.write((data + "\n").encode("utf-8"))

        print(f"已傳送：{data}")

        # UART 接收資料
        received = ser.readline().decode(
            "utf-8", errors="ignore"
        ).strip()

        if len(received) == 4 and received.isdigit():

            print(f"收到資料：{received}")

            # 將接收到的數字顯示在 LED
            tm.show(received)

            print(f"LED 顯示：{received}")

        else:
            print("未收到有效資料")

        print("--------------------")

        # 更新傳送數字
        counter = (counter + 1) % 10000

        time.sleep(1)

except KeyboardInterrupt:
    print("\n程式停止")

finally:
    ser.close()
    print("UART 已關閉")