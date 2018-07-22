# coding:utf-8

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
import os
import datetime
import json

from tornado.web import RequestHandler
from tornado.options import define, options
from tornado.websocket import WebSocketHandler
from tasks import add

define("port", default=8000, type=int)

taskIP={}

class IndexHandler(RequestHandler):
    def get(self):
        taskIP[self.request.remote_ip]=None
        mes={
            "hello":"world",
            "dbcourse":"design"
        }
        self.write(json.dumps(mes))

class TaskHandler(WebSocketHandler):

    def open(self):
        print("open")
        newTask=add.delay(3,4)
        taskIP[self.request.remote_ip]=newTask
        self.write("success")
 
    def on_message(self, message):
        if message=="open":
            self.write("success")
        else:
            task=taskIP[self.request.remote_ip]
            ans=task.get()
            self.write(ans)
            print(message)

    def on_close(self):
        pass
 
    def check_origin(self, origin):
        return True  # 允许WebSocket的跨域请求

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application([
            (r"/", IndexHandler),
            (r"/task", TaskHandler),
        ],
        #static_path = os.path.join(os.path.dirname(__file__), "static"),
        #template_path = os.path.join(os.path.dirname(__file__), "template"),
        debug = True
        )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

