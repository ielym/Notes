# coding:utf-8
import socket
import struct
import multiprocessing
import threading
from queue import Queue
import random
import traceback
import time

from each_client import child_server


if __name__ == '__main__':

    while True:

        server_base_addr = ('47.110.254.118', 5555)
        server_conn_addr = ('47.110.254.118', 6666)
        # server_base_addr = ('192.168.31.18', 5555)
        # server_conn_addr = ('192.168.31.18', 6666)

        try:
            socket_base = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_base.connect(server_base_addr)
            print('Connection with server success')
        except Exception as e:
            print(e)
            continue

        try:
            while True:
                data = socket_base.recv(1024)

                socket_inference = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_inference.settimeout(10)
                socket_inference.connect(server_conn_addr)

                client_addr = socket_inference.recv(1024).decode('utf-8')

                client_process = multiprocessing.Process(target=child_server, args=(client_addr, socket_inference, 1024))
                client_process.start()

        except Exception as e:
            socket_base.close()





