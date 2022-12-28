'''
Author: zhangzhikai zzkbean@163.com
Date: 2022-12-2 09:52:58
LastEditTime: 2022-12-28 12:16:30
FilePath: /raspi-python/face_detect.py
Description: 人脸识别成功开门, 人脸识别失败入侵报警信息和入侵者抓拍发送到移动端

Copyright (c) 2022 by zhangzhikai zzkbean@163.com, All Rights Reserved. 
'''
import base64
import os
import time
import urllib
# from http.client import IncompleteRead, RemoteDisconnected
from urllib.error import HTTPError, URLError  # URLError与HTTPError的异常处理

import requests  # 百度语音sdk
from aip import AipSpeech

# 百度云api连接参数
baidu_config = {
    'APP_ID': '28833160',
    'API_KEY': 'cqnAOIksYK6mFkwToYpRpjil',
    'SECRET_KEY': '4ssnT8EZceyvDuDCXtxk0jpCzBS6O86w'
}
client = AipSpeech(
        baidu_config['APP_ID'], baidu_config['API_KEY'], baidu_config['SECRET_KEY'])

# 获取百度云token
def getaccess_token():
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=cqnAOIksYK6mFkwToYpRpjil&client_secret=4ssnT8EZceyvDuDCXtxk0jpCzBS6O86w'
    header_1 = {
        'Content-Type': 'application/json; charset=UTF-8', 
    }
    request = requests.post(host, headers=header_1)
    access_token = request.json()['access_token']
    # print(access_token)
    return access_token

access_token = "24.9750ed527e2ecf5dd4d7dd0a9a235c3d.2592000.1673324251.282335-28833160"

def face_verify(access_token=access_token):
    print("开始认证...")
    img = get_picture()
    faceSearch(img, access_token)

# 摄像头拍照
def get_picture(num_retries=3):
    img_url = 'http://192.168.137.162:8080/?action=snapshot'  # 此刻摄像头采集的图片地址
    # Request类可以使用给定的header访问URL
    req = urllib.request.Request(url=img_url)  # 请求访问图片地址
    try:
        response = urllib.request.urlopen(req)  # 请求包装处理
        filename = 'people.jpg'
        with open(filename, "wb") as f:
            content = response.read()  # 获得图片
            f.write(content)  # 保存图片
            response.close()
    # except HTTPError as e:  # HTTP响应异常处理
    #     print(e.reason)
    except URLError as e:  # 放到HTTPError之后，因为它包含了前者
        print(e.reason)
    # except IncompleteRead or RemoteDisconnected as e:
    #     if num_retries == 0:  # 重连机制
    #         return
    #     else:
    #         requestImg(num_retries - 1)
    # 打开图片并转码  rb以二进制格式打开一个文件用于只读
    f = open('people.jpg', 'rb')
    img = base64.b64encode(f.read())
    return img

# 人脸识别接口请求
def getsearchMessage(img, access_token):
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
    params = {"image": img, "image_type": "BASE64", "group_id_list": "face_list", "quality_control": "LOW",
              "liveness_control": "NORMAL"}
    request_url = request_url + "?access_token=" + access_token
    response = requests.post(request_url, data=params)
    return response.json()

# 人脸搜索返回处理
err_count = 0
def faceSearch(img, access_token):
    output = getsearchMessage(img, access_token)
    if output['error_msg'] == 'SUCCESS':
        user_list = output['result']['user_list']
        print(user_list)
        score = user_list[0]['score']
        user = user_list[0]['user_id']

        baidu_tts("您好，进门前请进行身份认证")

        if user == 'zhangzhikai':
            words = "认证成功,张智凯" + "相似度百分之" + \
                    str(round(score, 2)) + "...请进！"
            baidu_tts(words)
    else:
        print(output['error_msg'])
        global err_count
        err_count += 1
        baidu_tts("对不起,认证失败!,请重新刷脸")
        time.sleep(1) 
        if err_count < 3:
            face_verify(access_token)
        else:
            baidu_tts("已报警！")
        

# 监控人脸认证
def monitorSearch(img, access_token):
    output = getsearchMessage(img, access_token)
    if output['error_msg'] != 'SUCCESS':
        return 1
    else:
        pass

# 百度语音合成 test to speech
def baidu_tts(words):
    # pereference 3 度逍遥
    result = client.synthesis(words, 'zh', 1, {'vol': 5, 'per': 3})  
    if not isinstance(result, dict):  # 识别正确返回语音二进制 错误则返回dict
        with open('audio.mp3', 'wb') as f:  # wb表示二进制写入
            f.write(result)
        os.system('mplayer audio.mp3')
    else:
        print(result)

if __name__ == '__main__':
    face_verify(access_token)