import traceback
import json
import copy
from tornado import gen
import tornado.web
from api.logger import logger
from api.ner import ner

class NerHandler(tornado.web.RequestHandler):

    @gen.coroutine
    def get(self):
        self.write("请使用post方法！")

    @gen.coroutine
    def post(self):

        result = {
            'msg': '请求失败！',
            'code': 1,
            'data': {}
        }
        try:
            # logger.info('request.body : %s' % self.request.body, no_uid=True)
            _ip = self.request.headers.get('X-Forwarded-For') or self.request.headers.get(
                'X-Real-IP') or self.request.remote_ip  # 有可能是nginx代理； proxy_set_header X-Forwarded-For  $remote_addr;
            # content_type = self.request.headers.get("Content-Type", "")
            # args_data = {}
            # if 'application/json' in content_type.lower():
            body_data = self.request.body
            if isinstance(body_data, bytes):
                body_data = self.request.body.decode('utf8')
            data = json.loads(body_data)

            data['ip'] = _ip
            logger.info("传入参数： {}".format(data), no_uid=True)
            question = data['question']
            json_data_ret = ner.evaluate_line(question)
            if json_data_ret:
                result = {
                    "msg": "请求成功",
                    "code": 0,
                    "data": json_data_ret
                }
            result_str = json.dumps(result, ensure_ascii=False)

            logger.info("返回数据：{}".format(result_str), no_uid=True)

            self.write(result_str)
            self.write("\n")
        except Exception as e:
            logger.info("解析参数出错： {}".format(e), no_uid=True, exc_info=True)
            logger.info("错误详情： {}".format(traceback.print_exc()), no_uid=True)
            result_str = json.dumps(result, ensure_ascii=False)
            self.write(result_str)
            self.write("\n")

