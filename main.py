'''
Author: zhangzhikai zzkbean@163.com
Date: 2022-12-2 09:42:39
LastEditTime: 2022-12-28 11:49:37
FilePath: /raspi-python/main.py
Description: 小派全屋智能项目，包括
    人脸识别：张智凯；
    入侵、火灾自动报警：张章；
    语音交互控制家用设备：张致远 赵博垚；
    移动端集成：丁旭。

Copyright (c) 2022 by zhangzhikai zzkbean@163.com, All Rights Reserved. 
'''

import _thread
import face_detect
import device_remote
import speech

if __name__ == '__main__':
    face_detect.face_verify()