"""
在线词典服务端
"""
"""
Web server
    【1】 接收客户端（浏览器）请求
    【2】 解析客户端发送的请求
    【3】 根据请求组织数据内容
    【4】 将数据内容形成http响应格式返回给浏览器
要求
    【1】 采用IO并发，可以满足多个客户端同时发起请求情况
    【2】 通过类接口形式进行功能封装
    【3】 做基本的请求解析，根据具体请求返回具体内容，同时处理客户端的非网页请求行为
"""
from socket import *
from select import *
import re
import pymysql


class DictionaryServer:
    def __init__(self, dir=None, host='0.0.0.0', port=9527, ):
        self.host = host
        self.port = port
        # 初始服务端
        self.__create_socket()
        self.__bind()
        # 初始请求回复头协议

        # 初始select监控 IO阻塞对象列表
        self.__rl = []
        self.__wl = []
        self.__xl = []
    def _connect_database(self):
        self.db = pymysql.connect(host='176.198.113.11',
                                  port=3306,
                                  user='root',
                                  password='123456',
                                  database='dict',
                                  charset='utf8')


    def __create_socket(self):
        """
        设置TCP套接字，IO非阻塞
        """
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setblocking(False)

    def __bind(self):
        """
        绑定服务地址
        """
        self.address = (self.host, self.port)
        self.sock.bind((self.host, self.port))
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    def __get_request(self, connfd: socket):
        # 接收客户端（浏览器）请求,返回请求行的请求内容，没有就返回空字符
        request = connfd.recv(1024 * 10)
        # 解析客户端发送的请求
        # request = request.decode().split(' ', 3)[1]
        pattern = r''
        try:
            info = re.match(pattern, request.decode()).group('info')
            # print("请求内容", info)
            return info
        except:
            return ''

    def __send_responseOK_msg(self, connfd, data):
        # 请求内容存在，组织协议格式，发送存在内容，关闭连接
        msg = self._OkHead.encode() + data
        connfd.send(msg)

    def __send_NoFound(self, connfd: socket):
        # 请求内容不存在，发送不存在，关闭连接
        msg = self._NotFound
        connfd.send(msg.encode())

    def close_connect(self, connfd: socket):
        # 关闭连接，移除IO阻塞监控
        self.__rl.remove(connfd)
        connfd.close()

    def handle(self, connfd: socket):
        """
        根据请求类型，发送处理请求
        """
        request = self.__get_request(connfd)

        if request == '/':  # 默认根目录
            self.html = self.dir + '/index.html'
        else:
            self.html = self.dir + request
        # 【4】 将数据内容形成http响应格式返回给浏览器

        try:
            with open(self.html, 'rb') as f:
                data = f.read()
        except:
            # 请求内容不存在
            self.__send_NoFound(connfd)
            self.close_connect(connfd)
        else:
            self.__send_responseOK_msg(connfd, data)
            self.close_connect(connfd)

    def start(self):
        """
        启动服务端
        """
        self.__rl.append(self.sock)
        self.sock.listen(5)
        print('Listen the port %d' % self.port)

        while True:
            # 获取IO阻塞监控列表
            rs, ws, xs = select(self.__rl,
                                self.__wl,
                                self.__xl)
            for item in rs:  # 遍历列表监控的就绪事件
                if item is self.sock:  # 判断列表返回就绪的事件，是否是监听套接字
                    connfd, addr = self.sock.accept()
                    print('{}connetted'.format(addr))
                    # 有客户端连接，添加连接事件到IO监控列表
                    connfd.setblocking(False)
                    self.__rl.append(connfd)

                # elif item is connfd:                   # 判断就绪事件 是否为链接套接字
                else:
                    self.handle(item)


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 9521
    dir = './static'
    httpfd = DictionaryServer(dir, host, port)
    httpfd.start()
