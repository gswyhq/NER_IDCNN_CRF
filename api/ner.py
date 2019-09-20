import traceback
from api.logger import logger
import copy
import json
import pickle
import tensorflow as tf
from model import Model
from utils import load_config

from utils import create_model

from data_utils import load_word2vec, input_from_line

flags = tf.app.flags

flags.DEFINE_string("ckpt_path",    "ckpt",      "Path to save model")
flags.DEFINE_string("map_file",     "maps.pkl",     "file for maps")
flags.DEFINE_string("config_file",  "config_file",  "File for config")

FLAGS = tf.app.flags.FLAGS

class Ner():
    def __init__(self):
        self.config = load_config(FLAGS.config_file)
        # limit GPU memory
        self.tf_config = tf.ConfigProto()
        self.tf_config.gpu_options.allow_growth = True
        with open(FLAGS.map_file, "rb") as f:
            self.char_to_id, self.id_to_char, self.tag_to_id, self.id_to_tag = pickle.load(f)
        graph = tf.Graph()
        with graph.as_default():
            self.sess = tf.Session(config=self.tf_config)
            self.model = create_model(self.sess, Model, FLAGS.ckpt_path, load_word2vec, self.config, self.id_to_char,
                                      logger, False)
            self.trans = self.model.trans.eval(self.sess)

    def evaluate_line(self, line: str):

        inputs = input_from_line(line, self.char_to_id)
        lengths, scores = self.model.run_step(self.sess, False, inputs)
        batch_paths = self.model.decode(scores, lengths, self.trans)
        tags = [self.id_to_tag[idx] for idx in batch_paths[0]]
        # print('tags={}'.format(tags))
        ret = self.result_to_json(inputs[0][0], tags)
        # result = self.model.evaluate_line(self.sess, input_from_line(line, self.char_to_id), self.id_to_tag)

        logger.info("问句`{}`实体识别的结果：{}".format(line, ret))
        return ret

    def result_to_json(self, string, tags):
        entity_name = ""
        datas = []
        for char, tag in zip(string, tags):
            if tag[0] == "S":
                datas.append([char, tag[2:]])
            elif tag[0] == "B":
                entity_name += char
            elif tag[0] == "I":
                entity_name += char
            elif tag[0] == "E":
                entity_name += char
                datas.append([entity_name, tag[2:]])
                entity_name = ""
            else:
                entity_name = ""
        return datas

ner = Ner()

def main():
    ner = Ner()
    ret = ner.evaluate_line('姚明有多高')
    print(ret)


if __name__ == "__main__":
    # tf.app.run(main)
    main()

# docker run -e 'POST={"question": "姚明有多高", "pid": "123456", "extract_tags": true}' -it --rm -t devth/alpine-bench -t 60 -c 30 http://192.168.3.164:8000/parser
