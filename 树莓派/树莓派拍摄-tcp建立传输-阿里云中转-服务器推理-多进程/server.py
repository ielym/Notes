# coding:utf-8
import socket
import struct
import multiprocessing
import threading
from queue import Queue
import random
import traceback
import time
import numpy as np

def recv_from_client(client_conn, queue_data, queue_error):
    try:
        while True:

            if not queue_error.empty():
                client_conn.close()
                return

            data_size = int(client_conn.recv(1024).decode('utf-8'))

            already = 0
            data_total = b''

            while already < data_size:
                buf = client_conn.recv(1024)
                data_total += buf
                already += len(buf)

            queue_data.put(data_total)

            client_conn.send('received'.encode('utf-8'))
    except Exception as e:
        print(e)
        queue_error.put(e)
        client_conn.close()
        return

def send_to_inference(inference_conn, queue_data, queue_error):

    try:
        while True:

            if not queue_error.empty():
                client_conn.close()
                return

            if queue_data.empty():
                continue

            data = queue_data.get()
            data_size = len(data)

            inference_conn.send(str(data_size).encode('utf-8'))



            already = 0
            while already < data_size:
                if already + 1024 > data_size:
                    buf = data[already:]
                    already += len(buf)
                else:
                    buf = data[already:already + 1024]
                    already += 1024
                inference_conn.sendall(buf)

            # 接收应答数据:
            response = inference_conn.recv(1024).decode('utf-8')

    except Exception as e:
        queue_error.put(e)
        inference_conn.close()
        return


def process_pair(client_conn, inference_conn):
    try:
        while True:


            # data_data_size = client_conn.recv(1024)
            # inference_conn.sendall(data_data_size)
            # data_size = int(data_data_size.decode('utf-8'))

            #  在 64-bit系统中，long是8字节，因此需要用 'i' 表示4字节
            buf_data_size = client_conn.recv(struct.calcsize('i'))
            data_size = struct.unpack('i', buf_data_size)[0]
            data_data_size = struct.pack('i', data_size)
            inference_conn.sendall(data_data_size)

            already = 0

            while already < data_size:
                buf = client_conn.recv(1024)
                inference_conn.sendall(buf)
                already += len(buf)

            response = inference_conn.recv(1024)
            client_conn.sendall(response)
    except Exception as e:
        print(e)
        client_conn.close()
        inference_conn.close()
        return


if __name__ == '__main__':

    inference_base_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    inference_base_socket.bind(('0.0.0.0', 5555))
    inference_base_socket.listen(128)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.bind(('0.0.0.0', 7777))
    client_socket.listen(128)

    inference_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    inference_socket.bind(('0.0.0.0', 6666))
    inference_socket.listen(128)

    while True:

        all_conns = []

        while True:
            try:
                print('Server for Inference Ready')
                inference_base_conn, inference_base_addr = inference_base_socket.accept()
                print('Inference base connection success :', inference_base_addr)
                break
            except Exception as e:
                print(e)

        while True:

            try:
                client_conn, client_addr = client_socket.accept()
                inference_base_conn.sendall('new'.encode('utf-8'))
                inference_conn, inference_addr = inference_socket.accept()

                inference_conn.sendall(str(client_addr).encode('utf-8'))

                all_conns.append(client_conn)
                all_conns.append(inference_conn)

                print('A New Pair established , client : ', client_addr, 'inference : ', inference_addr)
                process = multiprocessing.Process(target=process_pair, args=(client_conn, inference_conn,))
                process.start()

            except Exception as e:
                print(e)
                inference_base_conn.close()
                for conn in all_conns:
                    try:
                        conn.close()
                    except:
                        pass
                break


