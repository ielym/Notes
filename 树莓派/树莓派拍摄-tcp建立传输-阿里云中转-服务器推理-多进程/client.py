# coding:utf-8
import socket
import struct
import multiprocessing
import threading
from queue import Queue
import random
import traceback
import time
import cv2
import numpy as np

if __name__ == '__main__':

    buf_size = 1024


    while True:
        cap = None
        socket_client = None

        server_addr = ('47.110.254.118', 7777)
        # server_addr = ('192.168.31.18', 7777)

        try:
            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.settimeout(10)
            socket_client.connect(server_addr)
            print('Connection with server success')
        except Exception as e:
            print(e)
            continue

        try:

            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            while ret:

                img_encode = cv2.imencode('.jpg', frame)[1]
                data_encode = np.array(img_encode)
                data = data_encode.tobytes()
                data_size = len(data)

                # 报告data的大小 # 树莓派是32位系统，long是4字节
                data_data_size = struct.pack('l', data_size)
                socket_client.sendall(data_data_size)
                # socket_client.sendall(str(data_size).encode('utf-8'))

                already = 0
                while already < data_size:
                    if already + buf_size > data_size:
                        buf = data[already:]
                        already += len(buf)
                    else:
                        buf = data[already:already + buf_size]
                        already += buf_size
                    socket_client.sendall(buf)

                # 接收应答数据:
                response = socket_client.recv(1024).decode('utf-8')
                # print(response)

                ret, frame = cap.read()

        except Exception as e:
            if socket_client:
                socket_client.close()
            if cap:
                cap.release()





