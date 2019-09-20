#!/usr/bin/python3
# coding: utf-8

import tornado
import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer


from api.logger import logger
from urls import urls

LISTEN_PORT = 8000

logger.info("启动端口号: {}".format(LISTEN_PORT))

class Application(tornado.web.Application):
    def __init__(self):
        handlers = urls
        super(Application, self).__init__(handlers, debug=False)

def make_app():
    return Application()

def main():
    application = make_app()
    HTTPServer(application)
    application.listen(LISTEN_PORT)
    logger.info('server is running....!!')
    print('server is running....!!')
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

