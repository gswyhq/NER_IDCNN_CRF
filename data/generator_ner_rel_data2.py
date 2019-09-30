#!/usr/bin/python3
# coding: utf-8

import json
import csv
import re
import random
from pypinyin import pinyin, lazy_pinyin

DATA_FILE = './data/all_node_rel.csv'
# CALL apoc.export.csv.query("MATCH (n)-[r]->() return n.name, type(r)", "/var/lib/neo4j/data/all_node_rel.csv", {})
# -133:~/data/neo4j$ docker cp three_tuple_all_50_schemas_neo4j_7476:/var/lib/neo4j/data/all_node_rel.csv .

SAVE_LABEL_ENTITY_DICT_FILE = './data/label_entity_dict.json'

EXAMPLE_QUESTION_FILE = './data/属性对应的问句样例.csv'

SAVE_TRAIN_DATA_FILE = './data/train5.txt'
SAVE_TEST_DATA_FILE = './data/test5.txt'
SAVE_DEV_DATA_FILE = './data/dev5.txt'

SAVE_TRAIN_DATA_FILE2 = './data/rel_train2.txt'
SAVE_TEST_DATA_FILE2 = './data/rel_test2.txt'
SAVE_DEV_DATA_FILE2 = './data/rel_dev2.txt'

# 下面常用到的几个国家的Unicode编码范围
# u4e00-u9fa5 (中文)
# x0400-x052f (俄语)
# xAC00-xD7A3 (韩文)
# u0800-u4e00 (日文)

NOT_ZH_EN_WORDS_PATTERN = '[^\u0800-\u9fa5A-Za-z]' # 非中英日文字符
NOT_ZH_EN_WORDS_PATTERN_COMPILE = re.compile(NOT_ZH_EN_WORDS_PATTERN)

LIMIT_NUM = 939225

ALL_SUBJECT_TYPE = {'书籍',
 '人物',
 '企业',
 '历史人物',
 '国家',
 '图书作品',
 '地点',
 '学科专业',
 '影视作品',
 '景点',
 '机构',
 '歌曲',
 '生物',
 '电视综艺',
 '网络小说',
 '行政区',
 '疾病', '术语'
 }

REL_SUBJECT_TYPE = {'占地面积': '地点',
 '连载网站': '图书作品',
 '预防措施': '疾病',
 '编剧': '影视作品',
 '导演': '影视作品',
 '忌吃食物': "疾病",
 '改编自': "影视作品",
 '主演': "影视作品",
 '定义': "术语",
 '概念': "术语",
 '字': "人物",
 '出版社': "书籍",
 '作曲': "歌曲",
 '简称': "术语",
 '药品详情': "疾病",
 '推荐药品': "疾病",
 '出品公司': "影视作品",
 '气候': "地点",
 '官方语言': "国家",
 '邮政编码': "行政区",
 '身高': "人物",
 '歌手': "歌曲",
 '并发疾病': "疾病",
 '简介': "术语",
 '治疗费用': "疾病",
 '治疗方式': "疾病",
 '创始人': "企业",
 '嘉宾': "电视综艺",
 '修业年限': "学科专业",
 '传染性': "疾病",
 '主持人': "电视综艺",
 '治疗科室': "疾病",
 '易感人群': "疾病",
 '治愈概率': "疾病",
 '出生地': "人物",
 '目': "生物",
 '母亲': "人物",
 '总部地点': "企业",
 '所属专辑': "歌曲",
 '治疗周期': "疾病",
 '诊断检查项目': "疾病",
 '专业代码': "学科专业",
 '症状': "疾病",
 '人口数量': "行政区",
 '分类': "疾病",
 '首都': "国家",
 '丈夫': "人物",
 '主角': "影视作品",
 '发病率': "疾病",
 '宜吃食物': "疾病",
 '民族': "人物",
 '制片人': "影视作品",
 '所在城市': "机构",
 '病因': "疾病",
 '作者': "书籍",
 '基本医疗保险': "疾病",
 '毕业院校': "人物",
 '号': "人物",
 '常用药品': "疾病",
 '妻子': "人物",
 '父亲': "人物",
 '祖籍': "人物",
 '面积': "地点",
 '作词': "歌曲",
 '成立日期': "机构",
 '出生日期': "人物",
 '注册资本': "企业",
 '国籍': "人物",
 '朝代': "历史人物",
 '推荐食谱': "疾病",
 '董事长': "企业",
 '海拔': "景点",
 '上映时间': "影视作品"}



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

def read_entity_words(file_name, save_entity_file):
    '''
    从三元组文件中提取实体及其属性；
    :param file_name:
    :param save_entity_file:
    :return:
    '''
    num = 0
    label_entity_dict = {}
    with open(file_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')

        for row in spamreader:
            subject_name, relationship = row
            if re.search(NOT_ZH_EN_WORDS_PATTERN_COMPILE, subject_name):
                continue
            label_entity_dict.setdefault(relationship, [])
            # if subject_name not in label_entity_dict[relationship]:
            label_entity_dict[relationship].append(subject_name)
            num += 1

    print(len(label_entity_dict))
    with open(save_entity_file, 'w')as f:
        json.dump(label_entity_dict, f, ensure_ascii=False)

# BIOES   (B-begin，I-inside，O-outside，E-end，S-single)
#
# B 表示开始，I表示内部， O表示非实体 ，E实体尾部，S表示改词本身就是一个实体。

# BIO
# B 表示开始，I表示内部， O表示非实体

def write_iob(f2, rel, word, rel_example_question_dict):
    question = random.choice(rel_example_question_dict[rel])
    word_flag = []
    for w in question:
        if w == '$':
            subject_type = REL_SUBJECT_TYPE[rel]
            word_pinyin = get_pinyin(subject_type, upper=True)
            word_len = len(word)

            if word_len == 1:
                word_flag.append([word, 'B-{}'.format(word_pinyin)])
            elif word_len >= 2:
                word_flag.append([word[0], 'B-{}'.format(word_pinyin)])
                for w in word[1:]:
                    word_flag.append([w, 'I-{}'.format(word_pinyin)])
            else:
                continue
        else:
            word_flag.append([w, 'O'])

    f2.write('{}\n'.format(' '.join('/'.join(w) for w in word_flag)))

def format_tran(rel_example_question_dict, data_file,
                save_train_data_file, save_test_data_file, save_dev_data_file, train_dev_test_split, format='IOB'):
    """
    生成命名实体识别训练数据
    :param rel_example_question_dict:
    :param data_file:
    :param save_train_data_file:
    :param save_test_data_file:
    :param save_dev_data_file:
    :param train_dev_test_split:
    :param format:
    :return:
    """
    assert sum(train_dev_test_split) == 1, "训练、校验、测试集的分配比例和应该为1."
    count = 0
    limit_num = LIMIT_NUM
    limit_num_class = {}
    with open(save_train_data_file, 'w', encoding='utf-8')as train_f:
        with open(save_dev_data_file, 'w', encoding='utf-8')as dev_f:
            with open(save_test_data_file, 'w', encoding='utf-8')as test_f:
                with open(data_file, newline='') as csvfile:
                    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')

                    for row in spamreader:
                        count += 1
                        if count%10000==0:
                            print('已完成：', count)

                        subject_name, relationship = row

                        if limit_num_class.get(relationship, 0) >= (limit_num / (1 + len(limit_num_class))) * 1.5:
                            # 某个类别的数据量太多，也忽略
                            continue

                        if re.search(NOT_ZH_EN_WORDS_PATTERN_COMPILE, subject_name):
                            continue

                        num = random.random()
                        if num < train_dev_test_split[0]:
                            write_iob(train_f, relationship, subject_name, rel_example_question_dict)
                        elif num < sum(train_dev_test_split[:2]):
                            write_iob(dev_f, relationship, subject_name, rel_example_question_dict)
                        else:
                            write_iob(test_f, relationship, subject_name, rel_example_question_dict)

                        if count > limit_num:
                            break
                        limit_num_class.setdefault(relationship, 0)
                        limit_num_class[relationship] += 1

def write_rel(f2, rel, word, rel_example_question_dict):
    question = random.choice(rel_example_question_dict[rel])
    question = question.replace('$', word)
    f2.write('{}\t{}\n'.format(question, rel))

def format_tran_rel(rel_example_question_dict, data_file,
                save_train_data_file, save_test_data_file,
                    save_dev_data_file, train_dev_test_split):
    """
    生成意图识别训练数据；
    :param rel_example_question_dict:
    :param data_file:
    :param save_train_data_file:
    :param save_test_data_file:
    :param save_dev_data_file:
    :param train_dev_test_split:
    :return:
    """
    assert sum(train_dev_test_split) == 1, "训练、校验、测试集的分配比例和应该为1."
    count = 0
    limit_num = LIMIT_NUM
    limit_num_class = {}
    with open(save_train_data_file, 'w', encoding='utf-8')as train_f:
        with open(save_dev_data_file, 'w', encoding='utf-8')as dev_f:
            with open(save_test_data_file, 'w', encoding='utf-8')as test_f:
                with open(data_file, newline='') as csvfile:
                    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')

                    for row in spamreader:
                        count += 1
                        if count%10000==0:
                            print('已完成：', count)
                        subject_name, relationship = row

                        if limit_num_class.get(relationship, 0) >= (limit_num / (1 + len(limit_num_class))) * 1.5:
                            # 某个类别的数据量太多，也忽略
                            continue

                        if re.search(NOT_ZH_EN_WORDS_PATTERN_COMPILE, subject_name):
                            continue

                        num = random.random()
                        if num < train_dev_test_split[0]:
                            write_rel(train_f, relationship, subject_name, rel_example_question_dict)
                        elif num < sum(train_dev_test_split[:2]):
                            write_rel(dev_f, relationship, subject_name, rel_example_question_dict)
                        else:
                            write_rel(test_f, relationship, subject_name, rel_example_question_dict)
                        if count > limit_num:
                            break

                        limit_num_class.setdefault(relationship, 0)
                        limit_num_class[relationship] += 1

def read_example_question(file_name=EXAMPLE_QUESTION_FILE):
    rel_example_question_dict = {}
    with open(file_name, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')

        for row in spamreader:
            row = [r for r in row if r]
            rel_example_question_dict.setdefault(row[0], row[1:])
    return rel_example_question_dict

def main():

    # CALL apoc.export.csv.query("match (n) where (n)-->() return n.name, labels(n)", "/var/lib/neo4j/data/all_nodes_20190930_1023.csv", {})

    # for input_file, output_file in zip([TRAIN_DATA_FILE, DEV_DATA_FILE, TEST_DATA_FILE], [SAVE_TRAIN_DATA_FILE, SAVE_DEV_DATA_FILE, SAVE_TEST_DATA_FILE]):
    #     format_tran(input_file, output_file, format='IOB')
    # read_entity_words(DATA_FILE, SAVE_LABEL_ENTITY_DICT_FILE)
    rel_example_question_dict = read_example_question(EXAMPLE_QUESTION_FILE)
    # print(rel_example_question_dict)

    format_tran(rel_example_question_dict, DATA_FILE, SAVE_TRAIN_DATA_FILE, SAVE_TEST_DATA_FILE, SAVE_DEV_DATA_FILE,
                train_dev_test_split=[0.8, 0.1, 0.1],
                format='IOB')

    format_tran_rel(rel_example_question_dict, DATA_FILE,
                    SAVE_TRAIN_DATA_FILE2, SAVE_TEST_DATA_FILE2, SAVE_DEV_DATA_FILE2, train_dev_test_split=[0.8, 0.1, 0.1]
                    )



if __name__ == '__main__':
    main()


