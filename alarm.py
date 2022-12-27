'''
Author: zhangzhikai zzkbean@163.com
Date: 2022-12-27 07:49:04
LastEditors: zhangzhikai zzkbean@163.com
LastEditTime: 2022-12-27 07:51:50
FilePath: /raspi-python/alarm.py
Description: [Edit]

Copyright (c) 2022 by zhangzhikai zzkbean@163.com, All Rights Reserved. 
'''

# 热释电红外传感器监控
def humanMonitoring():
    if human.is_on():  
        print("监测到有人靠近...开始人脸检测...")
        img = get_picture()  # 摄像头采集图像
        result = monitorSearch(img, access_token)  # 将采集到的图像上传百度云人脸库搜索
        if result == 1:  # 图像搜索不到则表示陌生物体靠近
            led2.blink()  # 红灯警告
            # ftp_upload()  # 上传FTP服务器
            mqttClient.publish(topics['topic3'], json.dumps(
                {"human": 1}), 0)  # 发布MQTT消息到阿里云物联网平台
            # send_shortMessage()  # 发送告警短信到用户手机
    else:
        pass
   
   test

# MQ-2烟雾传感器监控
def smokeMonitoring():
    if smoke.is_off():  # 监测高电平则表示MQ-2烟雾传感器检测到有害气体
        print("working")
        led2.blink()  # 红灯警告
        mqttClient.publish(topics['topic4'], json.dumps(
            {"smoke": 1}), 0)  # 发布MQTT消息到阿里云物联网平台
        # send_shortMessage()  # 发送告警短信到用户手机
    else:
        pass

# dht11数据发布IOT
def getDHT11Data():
    humidity, temperature = Adafruit_DHT.read_retry(
        Adafruit_DHT.DHT11, 12)
    if humidity is not None and temperature is not None:
        global dht11
        dht11 = [temperature, humidity]
        print('dht11', dht11[0], dht11[1])
        # MQTT发布至阿里云物联网平台
        mqttClient.publish(topics['topic2'], json.dumps(
            {"temperature": temperature, "humidity": humidity}), 0)
        return temperature, humidity
    else:
        return 0