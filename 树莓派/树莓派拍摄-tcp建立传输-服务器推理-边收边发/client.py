import socket
import cv2
import numpy as np
import struct
import tqdm
import random

def connection(server_ip, init_port=5555, buf_size=1024):
    init_addr = (server_ip, 5555)

    try:
        socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_client.settimeout(10)
        socket_client.connect(init_addr)

        data_buf_size = struct.pack('l', buf_size)
        socket_client.send(data_buf_size)

        return socket_client
    except Exception as e:
        print(f'{e}, ReConnected')
        socket_client.close()
        return None

if __name__ == "__main__":

    server_ip = r'192.168.31.18'
    init_port = 5555
    buf_size = 1024

    while True:

        try:

            socket_client = None
            cap = None

            socket_client = connection(server_ip=server_ip, init_port=init_port, buf_size=buf_size)
            if not socket_client:
                raise Exception("socket_client error")
            print(f"Connection Success")

            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            while ret:

                img_encode = cv2.imencode('.jpg', frame)[1]
                data_encode = np.array(img_encode)
                data = data_encode.tobytes()
                data_size = len(data)

                # 报告data的大小
                data_data_size = struct.pack('l', data_size)
                socket_client.send(data_data_size)

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
            print(f'{e}, ReConnected')
            if socket_client:
                socket_client.close()
            if cap:
                cap.release()


