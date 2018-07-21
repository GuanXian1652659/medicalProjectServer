#!/usr/bin/python
# encoding=utf-8

from SocketServer import TCPServer, ThreadingMixIn, StreamRequestHandler



class Server(ThreadingMixIn, TCPServer):  # 自定义Server类
    pass


class MyHandler(StreamRequestHandler):

    def handle(self):  # 重载handle函数
        addr = self.request.getpeername()
        print 'Get connection from', addr  # 打印客户端地址
        self.request.send('connects success!')  # 发送信息
        while True:
            mes=self.request.recv(100)
            print mes
            if mes=='exit':
                break
            elif mes=='p1':
                self.request.send('125213good58')
            elif mes=='p2':
                self.request.send('145313bad 90')
            elif mes=='p3':
                self.request.send('855223good12')






host = '127.0.0.1'
port = 1234
server = Server((host, port), MyHandler)

server.serve_forever()  # 开始侦听并处理连接
