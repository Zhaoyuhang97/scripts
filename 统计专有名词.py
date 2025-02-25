import jieba
from collections import Counter
from itertools import chain
import math
import pandas as pd
import os
import re

base_dir = os.path.dirname(__file__)
knowledge_path = os.path.join(base_dir, 'local_data', 'knowledge.json')
stop_words_path = os.path.join(base_dir, 'utils', 'stop_words_fuhao')
calc_user_words_path = os.path.join(base_dir, 'utils', 'calc_user_words')
df_knowledge_ = pd.read_json(knowledge_path)

with open(stop_words_path, 'r', encoding='utf-8') as f:
    stop_words = f.read().split('\n')


def load_documents():
    # 这里模拟加载文档数据，实际应用中应从文件或数据库加载
    return df_knowledge_.description.str.replace(r'<.*?>|&nbsp;|\r|\n', '').str.lower().to_list()


def get_words(documents, user_words=None):
    # 使用jieba进行分词
    for i in user_words:
        jieba.add_word(i)
    words = [[w for w in jieba.cut(doc, use_paddle=True) if (w not in stop_words) and (not w.isdigit())] for doc in
             documents]
    return list(chain(*words))


def get_bigrams(words):
    # 生成bigram列表
    return [(words[i], words[i + 1]) for i in range(len(words) - 1)]


def calculate_pmi(bigrams, word_count, min_count=5):
    # 计算每个bigram的PMI
    bigram_count = Counter(bigrams)
    total = sum(word_count.values())
    pmi = {}
    for bigram, freq in bigram_count.items():
        if freq >= min_count:  # 过滤低频bigrams
            word1, word2 = bigram
            prob_word1 = word_count[word1] / total
            prob_word2 = word_count[word2] / total
            prob_bigram = freq / total
            pmi[bigram] = math.log(prob_bigram / (prob_word1 * prob_word2), 2)
    return pmi


def main(user_words):
    documents = load_documents()
    words = get_words(documents, user_words)
    word_count = Counter(words)
    bigrams = get_bigrams(words)
    pmi = calculate_pmi(bigrams, word_count)
    maybe_words = []
    # 输出PMI值较高的bigrams
    for bigram, value in sorted(pmi.items(), key=lambda x: x[1], reverse=True):
        # print(f"{bigram}: {value}")
        concat_words = ''.join(bigram)
        if re.match(r'[a-zA-Z]*', concat_words).group() == concat_words:
            # 纯英文用空格间隔
            maybe_words.append(' '.join(bigram))
        else:
            maybe_words.append(concat_words)
    return maybe_words


if __name__ == "__main__":
    # ll = []
    # count = 5
    # while count:
    #     ll.extend(main(tuple(ll)))
    #     count -= 1
    # sort_ll = sorted(set(ll))
    # with open(calc_user_words_path, 'w', encoding='utf-8') as f:
    #     f.write('\n'.join([f"{i} owner" for i in sort_ll]))
    def num_2_letter1(n):
        init = ord('A') - 1
        char = ''
        while n:
            y = n % 26
            char += chr(y + init)
            n //= 26
        return char


    def num_2_letter2(mult, remainder):
        init = ord('A') - 1
        char = ''
        if mult >= 1 and remainder:
            new_remainder, new_mult = mult % 26, mult // 26
            char += chr(remainder + init)
            char += num_2_letter(new_mult, new_remainder)
            return char
        elif remainder:
            char += chr(remainder + init)
            return char
        else:
            pass


    num = 12020
    a = num_2_letter2(num // 26, num % 26)
    print(a[::-1])
    b = num_2_letter1(num)
    print(b[::-1])
