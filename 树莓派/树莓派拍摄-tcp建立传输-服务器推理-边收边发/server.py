import socket
import struct
import multiprocessing
import random

from each_client import child_server

def port_is_free(ip, port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((ip, int(port)))
        s.shutdown(2)
        return True
    except:
        return False

def get_port():

    port = random.randint(6000, 8000)

    while not port_is_free('127.0.0.1', port):
        port = random.randint(6000, 8000)
    return port

if __name__ == '__main__':

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', 5555))
    server_socket.listen(128)


    print("Server Ready")
    while True:

        new_conn, addr = server_socket.accept()

        # 接收传输时的 buf_size
        buf_data_size = new_conn.recv(struct.calcsize('l'))
        buf_size = struct.unpack('l', buf_data_size)[0]

        client_process = multiprocessing.Process(target=child_server, args=(addr, new_conn, buf_size))
        client_process.start()
