#!/usr/bin/python3
# coding: utf-8

import json
from pypinyin import pinyin, lazy_pinyin

# https://github.com/melancholicwang/lic2019-information-extraction-baseline
TRAIN_DATA_FILE = '/home/gswyhq/github_projects/lic2019-information-extraction-baseline/data/train_data.json'
DEV_DATA_FILE = '/home/gswyhq/github_projects/lic2019-information-extraction-baseline/data/dev_data.json'
TEST_DATA_FILE = '/home/gswyhq/github_projects/lic2019-information-extraction-baseline/data/test_demo.json'

# https://github.com/crownpku/Information-Extraction-Chinese

SAVE_TRAIN_DATA_FILE = './data/train.txt'
SAVE_TEST_DATA_FILE = './data/test.txt'
SAVE_DEV_DATA_FILE = './data/dev.txt'

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

# BIOES   (B-begin，I-inside，O-outside，E-end，S-single)
#
# B 表示开始，I表示内部， O表示非实体 ，E实体尾部，S表示改词本身就是一个实体。

# BIO
# B 表示开始，I表示内部， O表示非实体

def format_tran(input_file, output_file, format='IOB'):
    with open(input_file) as f:
        line = f.readline()
        with open(output_file, 'a+', encoding='utf-8')as f2:
            while line:
                data = json.loads(line)
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
                    object = spo["object"]
                    subject = spo["subject"]
                    entity_dict.setdefault(subject.upper(), get_pinyin(subject_type, upper=True))
                    entity_dict.setdefault(object.upper(), get_pinyin(object_type, upper=True))

                for word_pos in postag:
                    word = word_pos.get('word').upper()
                    word = word.strip()
                    word_pinyin = entity_dict.get(word)
                    if word_pinyin:

                        word_len = len(word)
                        if format == 'BIOES':
                            if word_len == 1:
                                f2.write('{} S-{}\n'.format(word, word_pinyin))
                            elif word_len == 2:
                                f2.write('{} B-{}\n'.format(word[0], word_pinyin))
                                f2.write('{} E-{}\n'.format(word[-1], word_pinyin))
                            elif word_len > 2:
                                f2.write('{} B-{}\n'.format(word[0], word_pinyin))
                                for w in word[1:-1]:
                                    f2.write('{} I-{}\n'.format(w, word_pinyin))
                                f2.write('{} E-{}\n'.format(word[-1], word_pinyin))
                            else:
                                continue
                        else: # IOB格式
                            if word_len == 1:
                                f2.write('{} B-{}\n'.format(word, word_pinyin))
                            elif word_len == 2:
                                f2.write('{} B-{}\n'.format(word[0], word_pinyin))
                                f2.write('{} I-{}\n'.format(word[-1], word_pinyin))
                            elif word_len > 2:
                                f2.write('{} B-{}\n'.format(word[0], word_pinyin))
                                for w in word[1:]:
                                    f2.write('{} I-{}\n'.format(w, word_pinyin))
                            else:
                                continue
                    else:
                        for w in word:
                            f2.write('{} O\n'.format(w))

                f2.write('\n')

                line = f.readline()
            print('保存文件： {}'.format(output_file))


def main():
    for input_file, output_file in zip([TRAIN_DATA_FILE, DEV_DATA_FILE, TEST_DATA_FILE], [SAVE_TRAIN_DATA_FILE, SAVE_DEV_DATA_FILE, SAVE_TEST_DATA_FILE]):
        format_tran(input_file, output_file, format='IOB')


if __name__ == '__main__':
    main()


