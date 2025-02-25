import time
from datetime import datetime, timedelta
from gensim.models.word2vec import Word2Vec
from sklearn.feature_extraction.text import TfidfTransformer, TfidfVectorizer, CountVectorizer

from collections import Counter
import json
import pickle
import pandas as pd
import numpy as np
import jieba
import os

base_dir = os.path.dirname(__file__)
# user_words_path = os.path.join(base_dir, 'utils', 'calc_user_words')
user_words_path = os.path.join(base_dir, 'utils', 'user_words')
stop_words_path = os.path.join(base_dir, 'utils', 'stop_words')
vocab_label_path = os.path.join(base_dir, 'utils', 'vocab_label.json')
word2vec_model_path = os.path.join(base_dir, 'utils', 'word2vec.model')
tfidf_model_path = os.path.join(base_dir, 'utils', 'tfidf.pickle')
knowledge_path = os.path.join(base_dir, 'local_data', 'knowledge.json')
tfidf_words_score_path = os.path.join(base_dir, 'local_data', 'tfidf_score.xlsx')

jieba.load_userdict(open(user_words_path, 'r', encoding='utf-8'))

KNOWLEDGE_TITLE_COL = 'short_description'
KNOWLEDGE_DESC_COL = 'description'
KNOWLEDGE_BS_COL = 'business_service_id'


class DataProcess:

    def __init__(self, stop_words=None):
        self.stop_words = stop_words if stop_words else []

    @staticmethod
    def generator_cut_words(data):
        """
        data:["我是一棵小草", "我爱北京天安门"...]
        return iterator[list]
        """
        for row in data:
            # yield list(jieba.cut(row.lower()))
            yield list(jieba.cut(row.lower(), use_paddle=True))
            # yield list(jieba.cut_for_search(row.lower()))

    def cut_words(self, data, min_len=2) -> list:
        """
        data:["我是一棵小草", "我爱北京天安门"...]
        min_len:切开的最小长度
        return [["我","是","一棵","小草"],["我","爱","北京","天安门"]]
        """
        final_words = [[word for word in row if word and (not word.isdigit()) and (word not in self.stop_words) and (
                len(set(word)) >= min_len)] for row in self.generator_cut_words(data)]
        return final_words

    def row_cut_words(self, data, split_: bool = False):
        """
        data:["我是一棵小草", "我爱北京天安门"...]
        split_: bool
        return:
        if split_:
            return ["我 是 一棵 小草","我 爱 北京 天安门"]
        else:
            return [["我","是","一棵","小草"],["我","爱","北京","天安门"]]
        """
        if split_:
            words_list = self.cut_words(data)
            words_list = [' '.join(i) for i in words_list]
        else:
            words_list = self.cut_words(data)
        return words_list


class TfidfModel:

    def __init__(self, stop_words=None):
        self.tfidf_model_path = tfidf_model_path
        self.tfidf_words_score_path = tfidf_words_score_path
        self.stop_words = stop_words if stop_words else []

    def train(self, text):
        # 训练
        tv_model = TfidfVectorizer(token_pattern=r"(?u)\S+", max_df=1.0, min_df=1, stop_words=self.stop_words)
        tv_model.fit(text)
        pickle.dump(tv_model, open(self.tfidf_model_path, "wb"))
        return tv_model

    def get_model(self):
        return pickle.load(open(self.tfidf_model_path, 'rb'))

    def save_word_p(self, df_knowledge_data, col, model):
        # 保存每个词在某个文章下的tfidf分数,返回bs下每个kw对应tfidf分数
        # col评分列名
        def make_score(value):
            row_words_list = [i for i in value.split(' ') if i in model.vocabulary_]
            row_words_split = ' '.join(row_words_list)
            tfidf_value = model.transform([row_words_split]).toarray()[0]
            row_words_set = set(row_words_list)
            data = {kw: tfidf_value[model.vocabulary_[kw]] for kw in row_words_set}
            sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)
            return sorted_data

        df_knowledge_data['score'] = df_knowledge_data[col].apply(make_score)
        df_knowledge_data.to_excel(self.tfidf_words_score_path, index=False)
        return df_knowledge_data


def gen_knowledge_cols(df_knowledge, stop_words=None):
    data_process = DataProcess(stop_words=stop_words)
    # short和desc拼接在一起
    df_knowledge_desc = df_knowledge.description.str.replace(r'<.*?>|&nbsp;', '')
    df_knowledge['words'] = df_knowledge.short_description + '.' + df_knowledge_desc
    # bs和title和title逗号切词
    df_knowledge[f'cut_words_vec'] = data_process.row_cut_words(df_knowledge['words'].to_list())
    df_knowledge['cut_words_tfidf'] = df_knowledge['cut_words_vec'].apply(lambda x: ' '.join(x))
    # 相同bs的words放在一起
    series_group_by_bs = df_knowledge.groupby(by=[KNOWLEDGE_BS_COL]).apply(
        lambda x: ' '.join(x['cut_words_tfidf'].to_list()))
    return df_knowledge, series_group_by_bs


if __name__ == '__main__':
    with open(stop_words_path, 'r', encoding='utf-8') as f:
        stop_words_ = f.read().split('\n')
    df_knowledge_ = pd.read_json(knowledge_path)
    df_knowledge_, series_group_by_bs_ = gen_knowledge_cols(df_knowledge=df_knowledge_, stop_words=stop_words_)
    ############ 训练 ############
    tf_idf = TfidfModel(stop_words=stop_words_)
    tf_idf.train(series_group_by_bs_.tolist())
    ############ 评分 ############
    tf_idf_ = TfidfModel()
    tf_idf_model_ = tf_idf_.get_model()
    df_tf_idf = tf_idf_.save_word_p(df_knowledge_, col='cut_words_tfidf', model=tf_idf_model_)
