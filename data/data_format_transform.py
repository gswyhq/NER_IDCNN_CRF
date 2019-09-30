#!/usr/bin/python3
# coding: utf-8

from tqdm import tqdm_notebook as tqdm
import json
from pypinyin import pinyin, lazy_pinyin

# https://github.com/melancholicwang/lic2019-information-extraction-baseline
ORIGINAL_TRAIN_FILE = '/home/gswyhq/github_projects/lic2019-information-extraction-baseline/data/train_data.json'
ORIGINAL_DEV_FILE = '/home/gswyhq/github_projects/lic2019-information-extraction-baseline/data/dev_data.json'
ORIGINAL_TEST_FILE = '/home/gswyhq/github_projects/lic2019-information-extraction-baseline/data/test_demo.json'

JIBING_DATA_FILE = '/home/gswyhq/kg_fusion/data/百科_词典_疾病.json'

# https://github.com/crownpku/Information-Extraction-Chinese

TRAIN_FILE = './data/train4.txt'
DEV_FILE = './data/dev4.txt'
TEST_FILE = './data/test4.txt'

SPLIT_CHARS = '，。！？；,;?'

def get_pinyin(text, upper=False):
    """
    返回文本的拼音，若upper为真则所有字母都大写，否则仅仅首字母大写
    :param text: 文本
    :return: Shuxing
    """

    if isinstance(text, str):
        if upper:
            return ''.join(lazy_pinyin(text)).upper()
        else:
            return ''.join(lazy_pinyin(text)).capitalize()
    return ''

SUBJECT_TYPE_SET = set()

# {'歌曲', '作品', '学校', 'Text', '地点', '机构', '出版社', '历史人物', '语言', '城市', 'Number', '图书作品', '书籍', '电视综艺',
# '生物', '景点', '企业', '影视作品', '气候', '国家', '目', '音乐专辑', '网站', '行政区', '人物', '学科专业', '网络小说', 'Date'}

def transform_format(input_file, output_file):
    with open(input_file) as f:
        line = f.readline()
        with open(output_file, 'w', encoding='utf-8')as f2:
            while line:
                data = json.loads(line)
                # {"postag": [{"word": "如何", "pos": "r"}, {"word": "演", "pos": "v"}, {"word": "好", "pos": "a"}, {"word": "自己", "pos": "r"}, {"word": "的", "pos": "u"}, {"word": "角色", "pos": "n"}, {"word": "，", "pos": "w"}, {"word": "请", "pos": "v"}, {"word": "读", "pos": "v"}, {"word": "《", "pos": "w"}, {"word": "演员自我修养", "pos": "nw"}, {"word": "》", "pos": "w"}, {"word": "《", "pos": "w"}, {"word": "喜剧之王", "pos": "nw"}, {"word": "》", "pos": "w"}, {"word": "周星驰", "pos": "nr"}, {"word": "崛起", "pos": "v"}, {"word": "于", "pos": "p"}, {"word": "穷困潦倒", "pos": "a"}, {"word": "之中", "pos": "f"}, {"word": "的", "pos": "u"}, {"word": "独门", "pos": "n"}, {"word": "秘笈", "pos": "n"}], "text": "如何演好自己的角色，请读《演员自我修养》《喜剧之王》周星驰崛起于穷困潦倒之中的独门秘笈", "spo_list": [{"predicate": "主演", "object_type": "人物", "subject_type": "影视作品", "object": "周星驰", "subject": "喜剧之王"}]}

                postag = data.get('postag', [])
                text = data['text']
                spo_list = data.get('spo_list', [])
                if not spo_list or not postag:
                    line = f.readline()
                    continue

                entity_dict = {}
                for spo in spo_list:
                    predicate = spo["predicate"]
                    object_type = spo["object_type"]
                    subject_type = spo["subject_type"]
                    SUBJECT_TYPE_SET.add(subject_type)
                    SUBJECT_TYPE_SET.add(object_type)
                    object = spo["object"]
                    subject = spo["subject"]
                    entity_dict.setdefault(subject.upper(), get_pinyin(subject_type, upper=True))
                    entity_dict.setdefault(object.upper(), get_pinyin(object_type, upper=True))

                entity_dict_sorted = sorted(entity_dict.items(), key=lambda x: len(x[0]), reverse=True)
                word_flag = []
                current_index = 0
                for _index, w in enumerate(text):
                    if _index < current_index:
                        continue
                    for word, word_pinyin in entity_dict_sorted:
                        if text[_index:].startswith(word):
                            word_len = len(word)
                            current_index = _index + word_len
                            if word_len == 1:
                                word_flag.append([word, 'B-{}'.format(word_pinyin)])
                            elif word_len >= 2:
                                word_flag.append([word[0], 'B-{}'.format(word_pinyin)])
                                for w in word[1:]:
                                    word_flag.append([w, 'I-{}'.format(word_pinyin)])
                            else:
                                continue
                            break
                    else:
                        word_flag.append([w, 'O'])

                if word_flag:
                    f2.write('{}\n'.format(' '.join('/'.join(w) for w in word_flag)))

                line = f.readline()
            print('保存文件： {}'.format(output_file))

    print('实体类型：{}'.format(SUBJECT_TYPE_SET))

def main():
    for input_file, output_file in zip([ORIGINAL_TRAIN_FILE, ORIGINAL_DEV_FILE, ORIGINAL_TEST_FILE], [TRAIN_FILE, DEV_FILE, TEST_FILE]):
        transform_format(input_file, output_file)


if __name__ == '__main__':
    main()