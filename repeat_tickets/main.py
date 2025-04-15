import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from text2vec import SentenceModel
from tqdm.auto import tqdm
import torch

if torch.cuda.is_available():
    device = 'cuda'  # 输出True表示CUDA可用
else:
    device = 'cpu'
with open('stop_words', 'r', encoding='utf-8') as f:
    stop_words = f.read().split('\n')
text2vec_model = SentenceModel('text2vec-bge-large-chinese', device=device)


def desc_delete_id(x):
    # 处理description中的字符串
    if x:
        lines = str(x).split('\n')
        da_list = [line for line in lines if (
            not line.strip().startswith('#id'))
                   and not line.strip().startswith('id')
                   # and not 'prid' in line.strip()
                   and line.strip() != ''
                   ]
        da = '\n'.join(da_list)
        for i in stop_words:
            da = da.replace(i, '')
        return da
    return x


def get_data(path):
    df = pd.read_csv(path)
    return df


def process_data(df):
    df_ = df[df['description'].notna()].reset_index(drop=True)
    # 拼接待比较的列
    split_desc = df_['description'].str.split('Problem Description:', expand=True)
    df_['desc'] = split_desc[1].str.lower()
    df_.loc[df_[df_['desc'].isna()].index, 'desc'] = split_desc[0].str.lower()
    # df_['desc'] = df_['short_description'] + df_['desc']

    df_['desc'] = df_['desc'].apply(desc_delete_id)
    df_['desc'] = df_['short_description'].str.lower() + df_['desc']
    # 日期
    df_['create_date'] = pd.to_datetime(df_['create_time']).dt.date
    return df_


def compare(df_simple):
    if df_simple.shape[0] == 1:
        df_simple['result'] = ''
        return df_simple
    dd = df_simple.reset_index(drop=True)

    embeddings = text2vec_model.encode(dd['desc'])
    similarity = cosine_similarity(embeddings, embeddings)

    # batch_input = list(itertools.product(dd['desc'], repeat=2))
    # results = similarity_pipeline(input=batch_input)
    # reshape_results = [i['scores'][1] for i in results]
    # similarity = np.array(reshape_results).reshape(dd.shape[0], dd.shape[0])

    # embeddings_1 = model.encode(df_simple['desc'].tolist(),
    #                         batch_size=12,
    #                         max_length=8192, # If you don't need such a long length, you can set a smaller value to speed up the encoding process.
    #                         )['dense_vecs']
    # embeddings_2 = model.encode(df_simple['desc'].tolist())['dense_vecs']
    # similarity = embeddings_1 @ embeddings_2.T

    np.fill_diagonal(similarity, -1)  # 自己的相似度置为-1
    # 每行按照数值从大到小排列，返回索引
    sorted_indices = np.argsort(-similarity, axis=1)
    sorted_sim = []
    # 打印结果
    for i, row_indices in enumerate(sorted_indices):
        aa = []
        for j in row_indices:
            value = similarity[i, j]
            if value != -1:
                aa.append(f"{dd.loc[j, 'ticket_id']}:{str(round(value, 4))}")
        sorted_sim.append(' '.join(aa))
    df_simple['result'] = sorted_sim
    return df_simple


if __name__ == '__main__':
    tqdm.pandas(desc="Processing texts")  # 设置进度条描述
    df_data = get_data('ticket.csv')
    df_process = process_data(df_data)
    df_final = df_process.groupby(['creator_id', 'create_date']).progress_apply(compare).reset_index(drop=True)
    df_final.to_excel(f'result_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx', index=False)
    print('Completed.')
