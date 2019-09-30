import os
import re
import codecs
import copy
import random
from data_utils import create_dico, create_mapping, zero_digits
from data_utils import iob2, iob_iobes, get_seg_features

def data_augmentation(sentences):
    """
    数据增强
    通过中文标点，新增一些数据；
    随机查找一个字符，若是非实体，则删除掉。
    :param sentences: [[['查', 'O'], ['尔', 'O'], ['斯', 'O'], ['·', 'O'], ['阿', 'O'], ['兰', 'O'], ['基', 'O'], ['斯', 'O'], ['（', 'O'], ['C', 'O'], ['H', 'O'], ['A', 'O'], ['R', 'O'], ['L', 'O'], ['E', 'O'], ['S', 'O'], ['$', 'O'], ['A', 'O'], ['R', 'O'], ['Á', 'O'], ['N', 'O'], ['G', 'O'], ['U', 'O'], ['I', 'O'], ['Z', 'O'], ['）', 'O'], ['，', 'O'], ['1', 'B-DATE'], ['9', 'I-DATE'], ['8', 'I-DATE'], ['9', 'I-DATE'], ['年', 'I-DATE'], ['4', 'I-DATE'], ['月', 'I-DATE'], ['1', 'I-DATE'], ['7', 'I-DATE'], ['日', 'I-DATE'], ['出', 'O'], ['生', 'O'], ['于', 'O'], ['智', 'O'], ['利', 'O'], ['圣', 'O'], ['地', 'O'], ['亚', 'O'], ['哥', 'O'], ['，', 'O'], ['智', 'O'], ['利', 'O'], ['职', 'O'], ['业', 'O'], ['足', 'O'], ['球', 'O'], ['运', 'O'], ['动', 'O'], ['员', 'O'], ['，', 'O'], ['司', 'O'], ['职', 'O'], ['中', 'O'], ['场', 'O'], ['，', 'O'], ['效', 'O'], ['力', 'O'], ['于', 'O'], ['德', 'O'], ['国', 'O'], ['足', 'O'], ['球', 'O'], ['甲', 'O'], ['级', 'O'], ['联', 'O'], ['赛', 'O'], ['勒', 'O'], ['沃', 'O'], ['库', 'O'], ['森', 'O'], ['足', 'O'], ['球', 'O'], ['俱', 'O'], ['乐', 'O'], ['部', 'O']]]
    :return:
    """
    SPLIT_CHARS = '，。！？；,;?'
    augment_datas = []
    for sentence in sentences:
        if len(sentence) < 10:
            continue
        split_indexs = [_index for _index, ws in enumerate(sentence[:-1]) if ws[0] in SPLIT_CHARS and ws[1] == 'O']
        if not split_indexs:
            continue
        sentence = copy.deepcopy(sentence)
        data =[]
        data.append(sentence[:split_indexs[0]+1])
        if len(split_indexs) > 1:
            data.extend([sentence[i+1: split_indexs[_index+1]+1] for _index, i in enumerate(split_indexs[:-1])])
        data.append(sentence[split_indexs[-1]+1:])
        data = [ws for ws in data if any(w for w in ws if w[1] != 'O')]
        for t in data:
            _index = random.choice(range(len(t)))
            if t[_index][1] == 'O':
                t = copy.deepcopy(t)
                del t[_index]
                augment_datas.append(t)
        augment_datas.extend(data)
    return sentences + augment_datas

def load_sentences(path, lower, zeros, data_augment=True):
    """
    读取训练数据
    数据文件格式如下：
    如/O 何/O 演/O 好/O 自/O 己/O 的/O 角/O 色/O ，/O 请/O 读/O 《/O 演/O 员/O 自/O 我/O 修/O 养/O 》/O
    :param path: 数据文件
    :param lower:
    :param zeros:
    :param data_augment: 是否需要数据增强；
    :return:
    """
    sentences = []
    for line in codecs.open(path, 'r', 'utf8'):
        line = zero_digits(line.rstrip()) if zeros else line.rstrip()
        sentence = [[word[0], word[2:]] for word in line.split() if word[1] == '/']
        if sentence:
            sentences.append(sentence)
    if data_augment:
        sentences = data_augmentation(sentences)
    return sentences


def update_tag_scheme(sentences, tag_scheme):
    """
    Check and update sentences tagging scheme to IOB2.
    Only IOB1 and IOB2 schemes are accepted.
    """
    for i, s in enumerate(sentences):
        tags = [w[-1] for w in s]
        # Check that tags are given in the IOB format
        if not iob2(tags):
            s_str = '\n'.join(' '.join(w) for w in s)
            raise Exception('Sentences should be given in IOB format! ' +
                            'Please check sentence %i:\n%s' % (i, s_str))
        if tag_scheme == 'iob':
            # If format was IOB1, we convert to IOB2
            for word, new_tag in zip(s, tags):
                word[-1] = new_tag
        elif tag_scheme == 'iobes':
            new_tags = iob_iobes(tags)
            for word, new_tag in zip(s, new_tags):
                word[-1] = new_tag
        else:
            raise Exception('Unknown tagging scheme!')


def char_mapping(sentences, lower):
    """
    创建字典和单词映射，按频率排序。
    """
    chars = [[x[0].lower() if lower else x[0] for x in s] for s in sentences]
    dico = create_dico(chars)  # 词频统计；
    dico["<PAD>"] = 10000001
    dico['<UNK>'] = 10000000
    char_to_id, id_to_char = create_mapping(dico)  # 词及其词id
    print("Found %i unique words (%i in total)" % (
        len(dico), sum(len(x) for x in chars)
    ))
    return dico, char_to_id, id_to_char


def tag_mapping(sentences):
    """
    Create a dictionary and a mapping of tags, sorted by frequency.
    """
    tags = [[char[-1] for char in s] for s in sentences]
    dico = create_dico(tags)
    tag_to_id, id_to_tag = create_mapping(dico)
    print("Found %i unique named entity tags" % len(dico))
    return dico, tag_to_id, id_to_tag


def prepare_dataset(sentences, char_to_id, tag_to_id, lower=False, train=True):
    """
    Prepare the dataset. Return a list of lists of dictionaries containing:
        - word indexes
        - word char indexes
        - tag indexes
    """

    none_index = tag_to_id["O"]

    def f(x):
        return x.lower() if lower else x
    data = []
    for s in sentences:
        string = [w[0] for w in s]
        chars = [char_to_id[f(w) if f(w) in char_to_id else '<UNK>']
                 for w in string]
        segs = get_seg_features("".join(string))
        if train:
            tags = [tag_to_id[w[-1]] for w in s]
        else:
            tags = [none_index for _ in chars]
        data.append([string, chars, segs, tags])

    return data


def augment_with_pretrained(dictionary, ext_emb_path, chars):
    """
    用预先训练好的嵌入词增强词典的功能。
     如果`words'为None，我们添加每个具有预训练嵌入的单词
     到字典中，否则，我们只添加由
     单词（通常是开发和测试集中的单词）。
    """
    print('Loading pretrained embeddings from %s...' % ext_emb_path)
    assert os.path.isfile(ext_emb_path)

    # Load pretrained embeddings from file
    pretrained = set([
        line.rstrip().split()[0].strip()
        for line in codecs.open(ext_emb_path, 'r', 'utf-8')
        if len(ext_emb_path) > 0
    ])

    # We either add every word in the pretrained file,
    # or only words given in the `words` list to which
    # we can assign a pretrained embedding
    if chars is None:
        for char in pretrained:
            if char not in dictionary:
                dictionary[char] = 0
    else:
        for char in chars:
            if any(x in pretrained for x in [
                char,
                char.lower(),
                re.sub('\d', '0', char.lower())
            ]) and char not in dictionary:
                dictionary[char] = 0

    word_to_id, id_to_word = create_mapping(dictionary)
    return dictionary, word_to_id, id_to_word


def save_maps(save_path, *params):
    """
    Save mappings and invert mappings
    """
    pass
    # with codecs.open(save_path, "w", encoding="utf8") as f:
    #     pickle.dump(params, f)


def load_maps(save_path):
    """
    Load mappings from the file
    """
    pass
    # with codecs.open(save_path, "r", encoding="utf8") as f:
    #     pickle.load(save_path, f)

