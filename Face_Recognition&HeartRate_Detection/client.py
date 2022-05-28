import os
import socket
import cv2
import time
from PIL import Image
import numpy as np


def getFramFromCamera():
    url = '172.20.10.5'  # 局域网ip
    port = 81  # 固定端口
    http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    http_sock.connect((url, port))
    request_url = 'GET /stream HTTP/1.1\r\nHost: 172.20.10.5\r\nConnection: close\r\n\r\n'
    http_sock.send(request_url.encode())
    http_sock.recv(1)
    http_sock.close()

    port = 8888
    pic_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pic_sock.connect((url, port))
    arrayLength = int(pic_sock.recv(32))
    pic_sock.send('I'.encode())
    image = open("test.jpg", "wb")
    for i in range(0, arrayLength):
        data = pic_sock.recv(1)
        image.write(bytes(data))
    pic_sock.close()
    image.close()
    return cv2.imread("test.jpg")


def take_picture():
    url = '172.20.10.5'  # 局域网ip
    port = 81  # 固定端口
    http_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    http_sock.connect((url, port))
    request_url = 'GET /stream HTTP/1.1\r\nHost: 172.20.10.5\r\nConnection: close\r\n\r\n'
    http_sock.send(request_url.encode())
    http_sock.recv(1)
    http_sock.close()

    port = 8888
    pic_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pic_sock.connect((url, port))
    arrayLength = int(pic_sock.recv(32))
    pic_sock.send('I'.encode())
    image = open("test.jpg", "wb")
    for i in range(0, arrayLength):
        data = pic_sock.recv(1)
        image.write(bytes(data))
    pic_sock.close()
    image.close()
