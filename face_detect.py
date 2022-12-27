'''
Author: zhangzhikai zzkbean@163.com
Date: 2022-12-27 09:52:58
LastEditors: zhangzhikai zzkbean@163.com
LastEditTime: 2022-12-27 09:57:14
FilePath: /raspi-python/face_detect.py
Description: [Edit]

Copyright (c) 2022 by zhangzhikai zzkbean@163.com, All Rights Reserved. 
'''
import base64
import time
import urllib
from http.client import IncompleteRead, RemoteDisconnected
from urllib.error import HTTPError, URLError  # URLError与HTTPError的异常处理


def verify(access_token):
    baidu_tts("您好，进门前请进行身份认证")
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
    except HTTPError as e:  # HTTP响应异常处理
        print(e.reason)
    except URLError as e:  # 一定要放到HTTPError之后，因为它包含了前者
        print(e.reason)
    except IncompleteRead or RemoteDisconnected as e:
        if num_retries == 0:  # 重连机制
            return
        else:
            requestImg(num_retries - 1)
    # 打开图片并转码  rb以二进制格式打开一个文件用于只读
    f = open('people.jpg', 'rb')
    img = base64.b64encode(f.read())
    return img

# 人脸搜索返回处理
def faceSearch(img, access_token):
    output = getsearchMessage(img, access_token)
    if output['error_msg'] == 'SUCCESS':
        user_list = output['result']['user_list']
        print(user_list)
        score = user_list[0]['score']
        user = user_list[0]['user_id']
        if user == 'zhangzhikai':
            words = "认证成功,张智凯" + "相似度为百分之" + \
                    str(round(score, 2)) + ",快来唤醒小派吧!"
            baidu_tts(words)

    else:
        print(output['error_msg'])
        baidu_tts("对不起,认证失败!")
        time.sleep(1) 
        baidu_tts("当前处于测试模式，可以直接唤醒小派！")


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