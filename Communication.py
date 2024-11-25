import numpy as np
import socket
import os

def connect_unity(host, port):
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock = socket.socket()
    sock.connect((host, port))
    print('连接已建立')


def send_to_unity(arr):
    arr_list = arr.flatten().tolist()  # numpy数组转换为list类型
    data = '' + ','.join([str(elem) for elem in arr_list]) + ''  # 每个float用,分割
    sock.sendall(bytes(data, encoding="utf-8"))  # 发送数据
    print("向unity发送：", arr_list)


def rec_from_unity():
    data = sock.recv(1024)
    data = str(data, encoding='utf-8')
    data = data.split(',')
    new_data = []
    for d in data:
        new_data.append(float(d))
    print('从环境接收：', new_data)
    return new_data


# 生成随机数据
output_data = np.random.default_rng().random((1,20))

host = '127.0.0.1'
port = 5005

connect_unity(host, port)

for i in range(output_data.shape[0]):
    send_to_unity(output_data[i])
    rec_from_unity()  # Unity接收数据后再发送下一个