'''
Author: zhangzhikai zzkbean@163.com
Date: 2022-12-27 12:43:38
LastEditors: zhangzhikai zzkbean@163.com
LastEditTime: 2022-12-27 13:44:46
FilePath: /raspi-python/new_test.py
Description: [Edit]

Copyright (c) 2022 by zhangzhikai zzkbean@163.com, All Rights Reserved. 
'''
import Adafruit_DHT
import time
import RPi.GPIO as GPIO

makerobo_pin = 13  # DHT11 温湿度传感器管脚定义

# GPIO口定义
def makerobo_setup():
	global sensor
	sensor = Adafruit_DHT.DHT11

# 循环函数
def loop():
	humidity, temperature = Adafruit_DHT.read_retry(sensor, makerobo_pin)
	while True:
		if humidity is not None and temperature is not None:
			print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
		else:
			print('Failed to get reading. Try again!')
		time.sleep(1)                 # 延时1s

def destroy():
	GPIO.cleanup()                     # 释放资源

# 程序入口
if __name__ == '__main__':    
	makerobo_setup()
	try:
		loop()
	except KeyboardInterrupt:  # 当按下Ctrl+C时，将执行destroy()子程序。
		destroy()