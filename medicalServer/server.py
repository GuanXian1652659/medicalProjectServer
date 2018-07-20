# coding: utf-8
import socket
import struct
import hashlib,base64
import threading
import time

# channels没用过，

'''""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
请求格式
+-+-+-+-+-------+-+-------------+-------------------------------+
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |   (if payload len==126/127)   |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+ - - - - - - - - - - - - - - - +
|     Extended payload length continued, if payload len == 127  |
+ - - - - - - - - - - - - - - - +-------------------------------+
|                               | Masking-key, if MASK set to 1 |
+-------------------------------+-------------------------------+
| Masking-key (continued)       |          Payload Data         |
+-------------------------------- - - - - - - - - - - - - - - - +
:                     Payload Data continued ...                :
+ - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - +
|                     Payload Data continued ...                |
+---------------------------------------------------------------+
'''""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

connectionlist = {} 
g_code_length = 0
g_header_length = 0 
PRINT_FLAG = True

def get_datalength(msg):
    global g_code_length
    global g_header_length
    g_code_length = msg[1] & 127
    if g_code_length == 126:
        g_code_length = struct.unpack('>H', msg[2:4])[0]
        g_header_length = 8
    elif g_code_length == 127:
        g_code_length = struct.unpack('>Q', msg[2:10])[0]
        g_header_length = 14
    else:  
        g_header_length = 6  
    g_code_length = int(g_code_length)
    return g_code_length  

def parse_data(msg):
    global g_code_length
    g_code_length = msg[1] & 127
    if g_code_length == 126:
        g_code_length = struct.unpack('>H', msg[2:4])[0]
        masks = msg[4:8]
        data = msg[8:]
    elif g_code_length == 127:
        g_code_length = struct.unpack('>Q', msg[2:10])[0]
        masks = msg[10:14]
        data = msg[14:]
    else:
        masks = msg[2:6]
        data = msg[6:]
    en_bytes = b""
    cn_bytes = []
    for i, d in enumerate(data):
        nv = chr(d ^ masks[i%4])
        nv_bytes = nv.encode()
        nv_len = len(nv_bytes)
        if nv_len == 1:
            en_bytes += nv_bytes
        else:
            en_bytes += b'%s'
            cn_bytes.append(ord(nv_bytes.decode()))
    if len(cn_bytes) > 2:
        cn_str = ""
        clen = len(cn_bytes)
        count = int(clen / 3)
        for x in range(count):
            i = x * 3
            b = bytes([cn_bytes[i], cn_bytes[i + 1], cn_bytes[i + 2]])
            cn_str += b.decode()
        new = en_bytes.replace(b'%s%s%s', b'%s')
        new = new.decode()
        res = (new % tuple(list(cn_str)))
    else:
        res = en_bytes.decode()
    return res

def sendMessage(msg):
    global connectionlist
    send_msg = b""  
    send_msg += b"\x81"
    back_str = []
    back_str.append('\x81')
    data_length = len(msg.encode()) 
    if PRINT_FLAG:
        print("INFO: send message is %s and len is %d" % (msg, len(msg.encode('utf-8'))))
    if data_length <= 125:
        send_msg += str.encode(chr(data_length))
    elif data_length <= 65535:
        send_msg += struct.pack('b', 126)
        send_msg += struct.pack('>h', data_length)
    elif data_length <= (2^64-1):  
        send_msg += struct.pack('b', 127)
        send_msg += struct.pack('>q', data_length)
    else:
        print (u'太长了')
    send_message = send_msg + msg.encode('utf-8')

    for connection in connectionlist.values():
        if send_message != None and len(send_message) > 0:
            connection.send(send_message)

def deleteconnection(item):
    global connectionlist
    del connectionlist['connection'+item]

class WebSocket(threading.Thread):
    def __init__(self,conn,index,name,remote, path=""):
        threading.Thread.__init__(self)
        self.conn = conn
        self.index = index
        self.name = name
        self.remote = remote
        self.path = path
        self.GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        self.buffer = ""
        self.buffer_utf8 = b""
        self.length_buffer = 0

    def generate_token(self, WebSocketKey):
        WebSocketKey = WebSocketKey + self.GUID
        Ser_WebSocketKey = hashlib.sha1(WebSocketKey.encode(encoding='utf-8')).digest()
        WebSocketToken = base64.b64encode(Ser_WebSocketKey) 
        return WebSocketToken.decode('utf-8')
    
    def run(self):
        if PRINT_FLAG:
            print('Socket %s Start!' % self.index)
        global g_code_length
        global g_header_length
        self.handshaken = False 
        while True:
            if self.handshaken == False: 
                if PRINT_FLAG:
                    print('INFO: Socket {} Start Handshaken with {}!'.format(self.index,self.remote))
                self.buffer = self.conn.recv(1024).decode('utf-8') 
                if PRINT_FLAG:
                    print("INFO: Socket {} self.buffer is {}".format(self.index, self.buffer))
                if self.buffer.find('\r\n\r\n') != -1:
                    headers = {}
                    header, data = self.buffer.split('\r\n\r\n', 1)
                    for line in header.split("\r\n")[1:]: 
                        key, value = line.split(": ", 1)
                        headers[key] = value
                    try:
                        WebSocketKey = headers["Sec-WebSocket-Key"]
                    except KeyError:
                        print("Socket {} Handshaken Failed!".format(self.index))
                        deleteconnection(str(self.index))
                        self.conn.close()
                        break
                    WebSocketToken = self.generate_token(WebSocketKey)
                    headers["Location"] = ("ws://{}{}".format(headers["Host"], self.path))
                    handshake = "HTTP/1.1 101 Switching Protocols\r\n"\
                            "Connection: Upgrade\r\n"\
                            "Sec-WebSocket-Accept: " + WebSocketToken + "\r\n"\
                            "Upgrade: websocket\r\n\r\n"
                    self.conn.send(handshake.encode(encoding='utf-8'))
                    self.handshaken = True 
                    sendMessage("Welocomg " + self.name + " !")
                    g_code_length = 0
                else:
                    print("Socket {} Error2!".format(self.index))
                    deleteconnection(str(self.index))
                    self.conn.close()
                    break
            else:            

                '''""""""""""""""""""""""""""""""""""""""""""""""""""""""
                mm = self.conn.recv(128)
                #计算接受的长度，判断是否接收完，如未接受完需要继续接收
                if g_code_length == 0:
                    get_datalength(mm) # 调用此函数可以计算并修改全局变量g_code_length和g_header_length的值
                self.length_buffer += len(mm)
                self.buffer_utf8 += mm
                if self.length_buffer - g_header_length < g_code_length:
                    if PRINT_FLAG:
                        print("INFO: 数据未接收完,接续接受")
                    continue
                else:
                    if PRINT_FLAG:
                        print("g_code_length:", g_code_length)
                        print("INFO Line 204: Recv信息 %s,长度为 %d:" % (self.buffer_utf8, len(self.buffer_utf8)))
                    if not self.buffer_utf8:
                        continue
                    recv_message = parse_data(self.buffer_utf8)
                    if recv_message == "quit":
                        print("Socket %s Logout!" % (self.index))
                        nowTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
                        sendMessage("%s %s say: %s" % (nowTime, self.remote, self.name+" Logout"))
                        deleteconnection(str(self.index))
                        self.conn.close()
                        break
                    else:
                        nowTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
                        sendMessage("%s %s say: %s" % (nowTime, self.remote, recv_message))
                    g_code_length = 0
                    self.length_buffer = 0
                    self.buffer_utf8 = b
                    """"""""""""""""""""""""""""""""""""""""""""""""""""""'''

class WebSocketServer(object):
    def __init__(self):
        self.socket = None
        self.i = 0

    def begin(self):
        if PRINT_FLAG:
            print('WebSocketServer Start!')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = 'localhost'
        port = 9002
        if PRINT_FLAG:
            print("WebServer is listening {},{}".format(ip,port))
        self.socket.bind((ip,port))
        self.socket.listen(50)
        global connectionlist
        
        while True:
            connection, address = self.socket.accept()
            newSocket = WebSocket(connection,self.i,address[0],address)
            newSocket.start()
            connectionlist['connection'+str(self.i)]=connection
            self.i += 1
            
# for my test server
if __name__ == "__main__":

    server = WebSocketServer()
    server.begin()
