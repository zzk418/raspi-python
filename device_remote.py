'''
Author: zhangzhang
Date: 2022-12-2 07:49:04
LastEditTime: 2022-12-28 06:06:22
FilePath: /raspi-python/device_remote.py
Description: 火灾燃气安全报警时打开通风系统，发送至移动端报警

Copyright (c) 2022 by zhangzhang, All Rights Reserved. 
'''
import _thread
import json
import os
import time

import Adafruit_DHT
import aliyunsdkiotclient.AliyunIotMqttClient as iot  # 阿里云平台mqtt连接
import RPi.GPIO as GPIO

from init import Init, Light  # GPIO初始化
from MyEncoder import MyEncoder  # 自定义json序列化

# 阿里云物联网平台mqtt连接参数
aliyun_config = {
    'productKey': 'i0n2di0c8Cc',
    'deviceName': 'raspi',
    'deviceSecret': '7a924ec27ace79225364db7b66caf9fb',
    'port': 1883,
    'host': 'i0n2di0c8Cc.iot-as-mqtt.cn-shanghai.aliyuncs.com'
}

# mqtt topic
topicHead = '/' + aliyun_config['productKey'] + \
            '/' + aliyun_config['deviceName']
topics = {
    'topic1': topicHead + '/user/setDevice',
    'topic2': topicHead + '/user/sendDHT11',
    'topic3': topicHead + '/user/putHumanMonitor',
    'topic4': topicHead + '/user/putSmokeStatus'
}

def on_mjpegstreamer_start():
    os.system("sh /home/pi/mjpg-streamer/mjpg-streamer-experimental/start.sh")

# mqtt连接
def on_mqtt_connect():
    mqttClient.on_connect = on_connect
    mqttClient.on_disconnect = on_disconnect
    mqttClient.on_message = on_message
    mqttClient.connect(
        host=aliyun_config['host'], port=aliyun_config['port'], keepalive=100)
    mqttClient.loop_forever()

def on_connect(mqttClient, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    mqttClient.subscribe(topics['topic1'], 0)  # 接收指定服务器的消息


def on_disconnect(mqttClient, userdata, flags, rc):
    print("Disconnected.")


# 收到订阅消息
def on_message(mqttClient, userdata, msg):
    msg = str(msg.payload, encoding='utf8')
    # print(msg)
    setjson = json.loads(msg)
    # print(setjson)
    ledChecked0 = setjson['ledList'][0]['ledChecked0']
    ledChecked1 = setjson['ledList'][1]['ledChecked1']
    fanChecked0 = setjson['fanList'][0]['fanChecked0']
    led1.set_on() if ledChecked1 == 1 else led1.set_off()
    led2.set_on() if ledChecked0 == 1 else led2.set_off()
    fan.set_off() if fanChecked0 == 1 else fan.set_on()

# 热释电红外传感器监控
def humanMonitoring():
    if human.is_on():  
        print("热释电红外监测到有人靠近")
        led2.blink()  # alarm
        mqttClient.publish(topics['topic3'], json.dumps(
            {"human": 1}), 0)  
    else:
        pass

# MQ-2烟雾传感器监控
def smokeMonitoring():
    print("MQ-2烟雾传感器working")
    if smoke.is_off():  # 监测高电平则表示MQ-2烟雾传感器检测到有害气体
        print("working")
        led2.blink()  
        mqttClient.publish(topics['topic4'], json.dumps(
            {"smoke": 1}), 0)  
    else:
        pass

# dht11数据发布IOT
dht11 = [0, 0]
def getDHT11Data():
    print("dht11温湿度传感器working")
    GPIO.setmode(GPIO.BCM)
    humidity, temperature = Adafruit_DHT.read_retry(
        Adafruit_DHT.DHT11, 12)
    if humidity is not None and temperature is not None:
        global dht11
        dht11 = [temperature, humidity]
        print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
        # MQTT发布至阿里云物联网平台
        mqttClient.publish(topics['topic2'], json.dumps(
            {"temperature": temperature, "humidity": humidity}), 0)
        return temperature, humidity
    else:
        return 0

def thread_human():
    while 1:
        humanMonitoring()
        time.sleep(1)


def thread_smoke():
    while 1:
        smokeMonitoring()
        time.sleep(0.5)


def thread_dht11():
    while 1:
        getDHT11Data()
        time.sleep(2)

def thread_video():
    on_mjpegstreamer_start()

def thread_mqtt():
    on_mqtt_connect()

led1 = Light(18)  # led1 
led2 = Light(5)  # led1 
fan = Init(22)  # 风扇 
dht = Init(12)  # dht11 
smoke = Init(20)  # 烟雾传感器 
human = Init(17)  # 热释电红外传感器 

mqttClient = iot.getAliyunIotMqttClient(aliyun_config['productKey'], aliyun_config['deviceName'],
                                            aliyun_config['deviceSecret'],
                                            secure_mode=3)


if __name__ == '__main__':
    _thread.start_new_thread(thread_human, ())
    _thread.start_new_thread(thread_smoke, ())
    _thread.start_new_thread(thread_dht11, ())
    _thread.start_new_thread(thread_video, ())
    _thread.start_new_thread(thread_mqtt, ())
    
    time.sleep(120)