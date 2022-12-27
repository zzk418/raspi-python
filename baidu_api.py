'''
Author: zhangzhikai zzkbean@163.com
Date: 2022-12-27 07:03:57
LastEditors: zhangzhikai zzkbean@163.com
LastEditTime: 2022-12-27 07:13:38
FilePath: /raspi-python/baidu_api.py
Description: [Edit]

Copyright (c) 2022 by zhangzhikai zzkbean@163.com, All Rights Reserved. 
'''
import base64
import os
import re

import requests

# 百度云api连接参数
baidu_config = {
    'APP_ID': '28833160',
    'API_KEY': 'cqnAOIksYK6mFkwToYpRpjil',
    'SECRET_KEY': '4ssnT8EZceyvDuDCXtxk0jpCzBS6O86w'
}

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

# 语音识别
def Speech(access_token):
    global detector
    request_url = "http://vop.baidu.com/server_api"
    headers = {'Content-Type': 'application/json'}
    WAVE_FILE = "beginSpeech.wav"
    # begin Speech
    answers = ["我在, 请说话.", "来了,我来了!", ",哥,我是小派!", "我是小派,有何指示?"]
    baidu_tts(answers[randomNumber(answers)])
    print("小派开始录音了,录音时间3s!")
    cmdmsg = run_cmd('arecord -d 3 -r 16000 -f S16_LE -D "plughw:1,0" beginSpeech.wav')  # 采集音频
    print(cmdmsg)
    print("录音结束,语音识别中...")
    f = open(WAVE_FILE, "rb")  # 以二进制读模式打开输入音频
    speech = base64.b64encode(f.read())  # 读音频文件并使用base64编码
    size = os.path.getsize(WAVE_FILE)  # 获取文件大小(字节)
    data_json = json.dumps(
        {"format": "wav", "rate": 16000, "channel": 1, "cuid": "zhl", "token": access_token,
         "speech": speech, "len": size}, cls=MyEncoder, indent=4)  # 请求数据格式
    response = requests.post(request_url, data=data_json,
                             headers=headers)  # 发起requests post请求
    if response.json().get('err_msg') == 'success.':  # 处理返回数据
        words = response.json().get('result')[0]
        print("您说的是:" + words)
        if re.findall('[温湿度]', words):
            temperature, humidity = getDHT11Data()
            words = "哥,室内温度:" + str(temperature) + ",室内湿度:" + str(humidity)
            baidu_tts(words)
        elif re.findall('开.*灯', words):
            led1.set_on()
            baidu_tts("哥,灯已打开.")
        elif re.findall('关.*灯', words):
            led1.set_off()
            baidu_tts("哥,灯已关闭.")
        elif re.findall('开.*[风扇]', words):
            fan.set_off()
            baidu_tts("哥,风扇已打开.")
        elif re.findall('关.*[风扇]', words):
            fan.set_on()
            baidu_tts("哥,风扇已关闭.")
        else:
            baidu_tts("我没有理解您说的",words)
    else:
        baidu_tts("对不起,小派没有听清.")


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

def run_cmd(cmd):
    """
    run command by using subprocess,
    raise exception when error has happened
    return standard output and standard error
    """
    cp = sp.run(cmd,shell=True,capture_output=True,encoding="utf-8")
    if cp.returncode != 0:
        error = f"""Something wrong has happened when running command [{cmd}]:
         {cp.stderr}"""
        raise Exception(error)
    return cp.stdout, cp.stderr

    # 生成随机数
def randomNumber(str):
    length = len(str)
    num = random.randint(0, length - 1)
    return num