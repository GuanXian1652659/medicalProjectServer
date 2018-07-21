# !/usr/bin/python
# encoding=utf-8

import socket

s = socket.socket()  # 生成一个socket对象
server= '127.0.0.1'
port = 1234
s.connect((server, port))  # 连接服务器
s.setblocking(1)
str=s.recv(100)
print str
while True:
    print "select picture:"
    print "1. picture1"
    print "2. picture2"
    print "3. picture3"
    print "4. exit"
    print "Your selection:"
    sel=raw_input()
    if sel=='1':
        s.send('p1')
        mes=s.recv(100)
        print "position:"+mes[0:3]+" "+mes[3:6]+" type:"+mes[6:10]+" rate:"+mes[10:12]
    elif sel=='2':
        s.send('p2')
        mes = s.recv(100)
        print "position:" + mes[0:3] + " " + mes[3:6] + " type:" + mes[6:10] + " rate:" + mes[10:12]
    elif sel=='3':
        s.send('p3')
        mes = s.recv(100)
        print "position:" + mes[0:3] + " " + mes[3:6] + " type:" + mes[6:10] + " rate:" + mes[10:12]
    elif sel=='4':
        s.send('exit')
        break
    else:
        pass


s.close()  # 关闭连接