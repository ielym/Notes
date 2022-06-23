import struct
import cv2
import numpy as np
import socket
import pyttsx3
import time

from predict import Predict, draw_box_label

# from queue import Queue
import threading
import multiprocessing

class GRAY_DIFF():

    def __init__(self):
        self.former = 0

    def get(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.Canny(frame, 128, 128)
        diff = np.abs(frame - self.former)
        # diff = cv2.GaussianBlur(diff, (7, 7), -1, -1)
        # diff[diff < 50] = 0
        # diff[diff >= 50] = 255

        self.former = frame
        return diff

def recv_data(conn, buf_size, frame_queue, error_queue):

    try:
        while True:
            if not error_queue.empty():
                print('recv_data is closing')
                cv2.destroyAllWindows()
                return

            buf_data_size = conn.recv(struct.calcsize('l'))
            data_size = struct.unpack('l', buf_data_size)[0]

            already = 0
            data_total = b''

            while already < data_size:
                buf = conn.recv(buf_size)
                data_total += buf

                already += len(buf)

            nparr = np.frombuffer(data_total, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            frame_queue.put(frame)

            conn.send('received'.encode('utf-8'))
    except Exception as e:
        print(f'recv_data caused error : {e}')
        conn.close()
        error_queue.put(e)
        cv2.destroyAllWindows()
        return

def show_img(window_name, frame_queue, process_queue, error_queue):
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.namedWindow(f'{window_name}-diff', cv2.WINDOW_NORMAL)

    gray = GRAY_DIFF()
    stacks = []

    pre_time = 0
    try:
        while True:
            if not error_queue.empty():
                print('show_img is closing')
                cv2.destroyAllWindows()
                return

            if not frame_queue.empty():
                frame = frame_queue.get()

                frame_gray = gray.get(frame)
                stacks.append(frame_gray)
                if len(stacks) == 3:
                    frames = np.stack(stacks, axis=2)

                    diff = abs(frames[:, :, 0] * (-1 / 3) + frames[:, :, 1] * (2 / 3) + frames[:, :, 2] * (-1 / 3))
                    diff = cv2.medianBlur(diff.astype(np.uint8), 7)
                    stacks = []

                    cv2.imshow(f'{window_name}-diff', diff)

                    cur_time = time.time()
                    if np.mean(diff) > 0.05 and cur_time - pre_time > 0.5:
                        pre_time = cur_time
                        process_queue.put(frame)

                cv2.imshow(window_name, frame)
                cv2.waitKey(1)
    except Exception as e:
        print(f'show_img caused error : {e}')
        error_queue.put(e)
        cv2.destroyAllWindows()
        return

def detect(window_name, process_queue, error_queue):

    try:
        cv2.namedWindow(f'{window_name}-detect', cv2.WINDOW_NORMAL)

        pp = pyttsx3.init()
        predictor = Predict()

        while True:
            if not error_queue.empty():
                print('detect is closing')
                return

            if not process_queue.empty():

                frame = process_queue.get()
                results, categories_unique = predictor(frame)

                if 0 in categories_unique:
                    pp.say('检测到行人')

                for obj in results:
                    xmin, ymin, xmax, ymax, category_name, category, score = obj
                    frame = draw_box_label(frame, (xmin, ymin, xmax, ymax), text=category_name, line_color=category)

                cv2.imshow(f'{window_name}-detect', frame)
                cv2.waitKey(1)
                pp.runAndWait()

    except Exception as e:
        print(f'detect caused error : {e}')
        error_queue.put(e)
        return

def child_server(client_addr, conn, buf_size):
    print(f"New Connection : {client_addr}")

    frame_queue = multiprocessing.Queue()
    process_queue = multiprocessing.Queue()
    error_queue = multiprocessing.Queue()

    thread_recv_data = multiprocessing.Process(target=recv_data,args=(conn, buf_size, frame_queue, error_queue))
    thread_recv_data.start()

    thread_show_img = multiprocessing.Process(target=show_img, args=(f'{client_addr}', frame_queue, process_queue, error_queue))
    thread_show_img.start()

    thread_detect = multiprocessing.Process(target=detect, args=(f'{client_addr}', process_queue, error_queue))
    thread_detect.start()

    thread_recv_data.join()
    thread_show_img.join()
    thread_detect.join()





