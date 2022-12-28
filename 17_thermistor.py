'''
Author: zhangzhikai zzkbean@163.com
Date: 2022-12-27 13:57:31
LastEditors: zhangzhikai zzkbean@163.com
LastEditTime: 2022-12-27 14:33:11
FilePath: /raspi-python/17_thermistor.py
Description: [Edit]

Copyright (c) 2022 by zhangzhikai zzkbean@163.com, All Rights Reserved. 
'''
'''
Author: zhangzhikai zzkbean@163.com
Date: 2022-12-27 13:57:31
LastEditors: zhangzhikai zzkbean@163.com
LastEditTime: 2022-12-27 14:08:36
FilePath: /raspi-python/17_thermistor.py
Description: [Edit]

Copyright (c) 2022 by zhangzhikai zzkbean@163.com, All Rights Reserved. 
'''
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# －－－－湖南创乐博智能科技有限公司－－－－
#  文件名：17_thermistor.py
#  版本：V2.0
#  author: zhulin
# 说明：模拟温度传感器实验
#####################################################
import PCF8591 as ADC
import RPi.GPIO as GPIO
import time
import math

makerobo_DO = 13 # 温度传感器Do管脚
GPIO.setmode(GPIO.BCM) # 管脚映射，采用BCM编码

# 初始化设置
def makerobo_setup():
	ADC.setup(0x48)          # 设置PCF8591模块地址
	GPIO.setup(makerobo_DO, GPIO.IN) # 温度传感器DO端口设置为输入模式

# 打印出温度传感器的提示信息
def makerobo_Print(x):
	if x == 1:     # 正合适
		print ('')
		print ('***********')
		print ('* Better~ *')
		print ('***********')
		print ('')
	if x == 0:    # 太热
		print ('')
		print ('************')
		print ('* Too Hot! *')
		print ('************')
		print ('')

# 循环函数
def makerobo_loop():
	makerobo_status = 1   # 状态值
	makerobo_tmp = 1      # 当前值
	while True:
		makerobo_analogVal = ADC.read(0) # 读取AIN0上的模拟值
		makerobo_Vr = 5 * float(makerobo_analogVal) / 255 # 转换到5V范围
		makerobo_Rt = 10000 * makerobo_Vr / (5 - makerobo_Vr)
		makerobo_temp = 1/(((math.log(makerobo_Rt / 10000)) / 3950) + (1 / (273.15+25)))
		makerobo_temp = makerobo_temp - 273.15
		print ('temperature = ', makerobo_temp, 'C')
		
		makerobo_tmp = GPIO.input(makerobo_DO) # 读取温度传感器数字端口

		if makerobo_tmp != makerobo_status: # 判断状态值发生改变
			makerobo_Print(makerobo_tmp)    # 打印出温度传感器的提示信息
			makerobo_status = makerobo_tmp  # 把当前状态值设置为比较状态值，避免重复打印； 

		time.sleep(0.2)                     # 延时 200ms

# 程序入口
if __name__ == '__main__':
	try:
		makerobo_setup()  #初始化程序
		makerobo_loop()   #循环函数
	except KeyboardInterrupt:  
		pass	
