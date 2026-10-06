#!/usr/bin/env python3

from time import sleep, localtime
import sys

# tm1637.py 位於隔壁的 7segment_display/raspberrypi-tm1637
sys.path.append('../7segment_display/raspberrypi-tm1637')

import tm1637

# BCM GPIO
CLK = 23
DIO = 24

# 建立 TM1637 顯示器
tm = tm1637.TM1637(clk=CLK, dio=DIO)
tm.brightness(1)

# 控制中間冒號
colon = True

while True:
    # 取得目前系統時間
    now = localtime()

    # 顯示 HH:MM
    tm.numbers(now.tm_hour, now.tm_min, colon)

    # 每秒切換冒號亮/滅
    colon = not colon

    sleep(1)
