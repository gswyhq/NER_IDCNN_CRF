
import tornado.web
from api.ner_handler import NerHandler

class MyFile(tornado.web.StaticFileHandler):

    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")
        self.set_header("Content-Type", "text/plain; charset=utf-8")  # 若是HTML文件，用浏览器访问时，显示所有的文件内容
        # self.set_header("Content-Type", "text/html; charset=utf-8")  # 若是HTML文件，用浏览器访问时，仅仅显示body部分；

urls = [
        (r'/', NerHandler),
        (r'/parser', NerHandler),
        (r'/api', NerHandler),
        (r"/myfile/(.*)", MyFile, {"path": "./output/"})# 提供静态文件下载； 如浏览器打开‘http://192.168.3.145:8000/myfile/place.pdf’即可访问‘./output/place.pdf’文件
]
