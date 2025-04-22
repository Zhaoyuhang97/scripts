import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.metrics.pairwise import cosine_similarity
from text2vec import SentenceModel
from tqdm.auto import tqdm
import json
import os
import torch

if torch.cuda.is_available():
    device = 'cuda'  # 输出True表示CUDA可用
else:
    device = 'cpu'
with open('stop_words', 'r', encoding='utf-8') as f:
    stop_words = f.read().split('\n')
text2vec_model = SentenceModel('text2vec-bge-large-chinese', device=device)

config = json.load(open('config.json', 'r', encoding='utf-8'))


class ProcessData:
    def __init__(self, output=True):
        self.is_valid_field = '是否有效'
        self.is_valid_content_field = '人工标记'
        self.output = output  # 输出每个文件是否有效

        self.file_dir = 'input'
        self.output_file_dir = 'output'
        filename_config = config['filename']
        self.incident_filename = filename_config['incident']
        self.interaction_filename = filename_config['interaction']
        self.request_filename = filename_config['request']
        self.d2d_incident_filename = filename_config['d2d_incident']
        self.d2d_request_filename = filename_config['d2d_request']

    def process_incident(self):
        file_path = os.path.join(self.file_dir, self.incident_filename)
        l1_caller_is_valid_field = '无效(L1 Caller)'
        resolution_code_is_valid_field = '无效(Resolution code)'
        contact_type_is_valid_field = '无效(Contact Type)'
        if not os.path.exists(file_path):
            return pd.DataFrame()
        else:
            df = pd.read_excel(file_path)
            df.rename(columns={'Channel': 'Contact type', 'User ID': 'PRID', 'Service': 'Business Service',
                               'Manager': 'Caller Manager', 'Manager.1': 'Opened by Manager'}, inplace=True)
            # L1 Caller(无效条件)
            df[l1_caller_is_valid_field] = (
                    (df['Caller Manager'].str.lower().str.strip() == 'louis chen') +
                    (df['PRID'].str.lower().str.strip().isin(['ksxs502', 'kgwj612']))
            ).astype(int)
            # Resolution code(无效条件)
            df[resolution_code_is_valid_field] = 0
            df.loc[
                df[
                    df['Assignment group'].str.lower().str.strip().isin(
                        ['srvcdesk-china-shanghai', 'srvcdesk-asiapac', 'srvcdesk-dalian'])
                    & df['Resolution code'].str.lower().str.strip().isin(
                        ['duplicate', 'incident misreported', 'resolved by request'])
                    ].index,
                resolution_code_is_valid_field
            ] = 1
            # Contact Type(无效条件)
            df[contact_type_is_valid_field] = 0
            df.loc[
                df[
                    df['Owned by'].str.lower().str.strip().isin(['srvcdesk-china-shanghai', 'srvcdesk-asiapac'])
                    & ~(df['Contact type'].str.lower().str.strip().isin(['phone', 'email', 'chat']))
                    ].index,
                contact_type_is_valid_field
            ] = 1
            # 是否有效,以上三个条件，只要有一个无效，本字段即为无效
            df[self.is_valid_field] = 1
            df.loc[
                df[[contact_type_is_valid_field, resolution_code_is_valid_field, l1_caller_is_valid_field]].any(axis=1),
                self.is_valid_field
            ] = 0
            # 无效的原因
            conditions = [
                df[l1_caller_is_valid_field] == 1,
                df[resolution_code_is_valid_field] == 1,
                df[contact_type_is_valid_field] == 1,
            ]
            df[self.is_valid_content_field] = np.select(
                conditions,
                [l1_caller_is_valid_field, resolution_code_is_valid_field, contact_type_is_valid_field],
                default=''
            )  # 添加'a'列，根据'b', 'c', 'd'列的值来设置内容
            # 输出
            if self.output:
                df.to_excel(os.path.join(self.output_file_dir, os.path.basename(file_path)), index=False)
        return df.drop(columns=[contact_type_is_valid_field, resolution_code_is_valid_field, l1_caller_is_valid_field])

    def process_interaction(self):
        file_path = os.path.join(self.file_dir, self.interaction_filename)
        l1_caller_is_valid_field = '无效(L1 Caller)'
        contact_type_is_valid_field = '无效(Contact Type)'
        closed_abandoned_is_valid_field = '无效(State非"Closed Abandoned")'
        short_description_is_valid_field = '无效(ShortDescription不包含"[#]")'
        state_reason_is_valid_field = '无效(Abn Reason非Wrong Number、User Abandoned、Junk Email、Insufficient Information to Progress)'
        caller_is_valid_field = '无效(Caller 非K账号)'
        if not os.path.exists(file_path):
            return pd.DataFrame()
        else:
            df = pd.read_excel(file_path)
            df.rename(columns={'Type': 'Contact type', 'User ID': 'PRID', 'State Reason': 'Call type(非技术类型)',
                               'Manager': 'Caller Manager', 'Manager.1': 'Opened by Manager'}, inplace=True)
            # L1 Caller(无效条件)
            df[l1_caller_is_valid_field] = (
                    (df['Caller Manager'].str.lower().str.strip() == 'louis chen') +
                    (df['PRID'].str.lower().str.strip().isin(['ksxs502', 'kgwj612']))
            ).astype(int)
            # Contact Type(无效条件)
            df[contact_type_is_valid_field] = 0
            df.loc[
                df[
                    df['Owned by'].str.lower().str.strip().isin(['srvcdesk-china-shanghai', 'srvcdesk-asiapac'])
                    & ~(df['Contact type'].str.lower().str.strip().isin(['phone', 'email', 'chat']))
                    ].index,
                contact_type_is_valid_field
            ] = 1
            # State非"Closed Abandoned"(无效条件)
            df[closed_abandoned_is_valid_field] = 0
            df.loc[
                df[(df['State'].str.lower().str.strip() != 'closed abandoned')].index,
                closed_abandoned_is_valid_field
            ] = 1
            # ShortDescription不包含"[#]"(无效条件)
            df['Short description'] = df['Short description'].fillna('')
            df[short_description_is_valid_field] = 0
            df.loc[
                df[~(df['Short description'].str[:3].str.contains('#', regex=True))].index,
                short_description_is_valid_field
            ] = 1
            # Abn Reason非Wrong Number、User Abandoned、Junk Email、Insufficient Information to Progress(无效条件)
            df[state_reason_is_valid_field] = 0
            df.loc[
                df[
                    ~df['Call type(非技术类型)'].str.lower().str.strip().isin(
                        ['wrong number', 'user abandoned', 'junk email', 'insufficient information to progress']
                    )
                ].index,
                state_reason_is_valid_field
            ] = 1
            # Caller 非K账号(无效条件)
            df[caller_is_valid_field] = 0
            df.loc[
                df[~(df['PRID'].str.lower().str.contains('^k[a-z0-9]{6}', regex=True))].index,
                caller_is_valid_field
            ] = 1
            # 是否有效,以上三个条件，只要有一个无效，本字段即为无效
            df[self.is_valid_field] = 1
            df.loc[
                df[[contact_type_is_valid_field, closed_abandoned_is_valid_field, l1_caller_is_valid_field,
                    short_description_is_valid_field, state_reason_is_valid_field, caller_is_valid_field]].any(axis=1),
                self.is_valid_field
            ] = 0
            # 输出
            if self.output:
                df.to_excel(os.path.join(self.output_file_dir, os.path.basename(file_path)), index=False)
            # df['all'] = df[[l1_caller_is_valid_field, contact_type_is_valid_field, closed_abandoned_is_valid_field,
            #                 short_description_is_valid_field, state_reason_is_valid_field, caller_is_valid_field]].sum(
            #     axis=1)
            df.drop(index=df[df[closed_abandoned_is_valid_field] == 1].index, inplace=True)
            df.drop(columns=[closed_abandoned_is_valid_field], inplace=True)
            # 无效的原因(删除closed_abandoned_is_valid_field列所以output在前)
            conditions = [
                df[l1_caller_is_valid_field] == 1,
                df[contact_type_is_valid_field] == 1,
                # df[closed_abandoned_is_valid_field] == 1,
                df[short_description_is_valid_field] == 1,
                df[state_reason_is_valid_field] == 1,
                df[caller_is_valid_field] == 1,
            ]
            df[self.is_valid_content_field] = np.select(
                conditions,
                [
                    l1_caller_is_valid_field,
                    contact_type_is_valid_field,
                    # closed_abandoned_is_valid_field,
                    short_description_is_valid_field,
                    state_reason_is_valid_field,
                    caller_is_valid_field],
                default=''
            )  # 添加'a'列，根据'b', 'c', 'd'列的值来设置内容

        return df.drop(columns=[l1_caller_is_valid_field, contact_type_is_valid_field,
                                short_description_is_valid_field, state_reason_is_valid_field,
                                caller_is_valid_field]).reset_index(drop=True)

    def process_request(self):
        file_path = os.path.join(self.file_dir, self.request_filename)
        l1_caller_is_valid_field = '无效(L1 Caller)'
        contact_type_is_valid_field = '无效(Contact Type)'
        if not os.path.exists(file_path):
            return pd.DataFrame()
        else:
            df = pd.read_excel(file_path)
            df.rename(
                columns={'User ID': 'PRID', 'Configuration item': 'Business Service', 'Contact Type': 'Contact type',
                         'Manager': 'Caller Manager', 'Manager.1': 'Opened by Manager'}, inplace=True)
            # L1 Caller(无效条件)
            df[l1_caller_is_valid_field] = (
                    (df['Caller Manager'].str.lower().str.strip() == 'louis chen') +
                    (df['PRID'].str.lower().str.strip().isin(['ksxs502', 'kgwj612']))
            ).astype(int)
            # Contact Type(无效条件)
            df[contact_type_is_valid_field] = 0
            df.loc[
                df[
                    df['Owned by'].str.lower().str.strip().isin(['srvcdesk-china-shanghai', 'srvcdesk-asiapac'])
                    & ~(df['Contact type'].str.lower().str.strip().isin(['phone', 'email', 'agent chat']))
                    ].index,
                contact_type_is_valid_field
            ] = 1
            # 是否有效,以上三个条件，只要有一个无效，本字段即为无效
            df[self.is_valid_field] = 1
            df.loc[
                df[[contact_type_is_valid_field, l1_caller_is_valid_field]].any(axis=1),
                self.is_valid_field
            ] = 0
            # 无效的原因
            conditions = [
                df[l1_caller_is_valid_field] == 1,
                df[contact_type_is_valid_field] == 1,
            ]
            df[self.is_valid_content_field] = np.select(
                conditions,
                [l1_caller_is_valid_field, contact_type_is_valid_field],
                default=''
            )  # 添加'a'列，根据'b', 'c', 'd'列的值来设置内容
            # 输出
            if self.output:
                df.to_excel(os.path.join(self.output_file_dir, os.path.basename(file_path)), index=False)
        return df.drop(columns=['State', contact_type_is_valid_field, l1_caller_is_valid_field])

    def process_d2d_incident(self):
        file_path = os.path.join(self.file_dir, self.d2d_incident_filename)
        follow_up_l1_is_valid_field = '无效(D2D Followup SD L1开单)'
        if not os.path.exists(file_path):
            return pd.DataFrame()
        else:
            df = pd.read_excel(file_path)
            df.rename(
                columns={'User ID': 'PRID', 'Service': 'Business Service', 'Channel': 'Contact type',
                         'Watch list': 'D2D Watch', 'Manager': 'Caller Manager', 'Manager.1': 'Opened by Manager'},
                inplace=True)
            # 无效(D2D Followup SD L1开单）(无效条件)
            df[follow_up_l1_is_valid_field] = (
                df['Owned by'].str.lower().str.strip().isin(
                    ['srvcdesk-china-shanghai', 'srvcdesk-asiapac', 'SrvcDesk-Dalian'])
            ).astype(int)
            # 是否有效,以上三个条件，只要有一个无效，本字段即为无效
            df[self.is_valid_field] = 1
            df.loc[
                df[[follow_up_l1_is_valid_field]].any(axis=1),
                self.is_valid_field
            ] = 0
            # 无效的原因
            conditions = [
                df[follow_up_l1_is_valid_field] == 1
            ]
            df[self.is_valid_content_field] = np.select(
                conditions,
                [follow_up_l1_is_valid_field],
                default=''
            )  # 添加'a'列，根据'b', 'c', 'd'列的值来设置内容
            # 输出
            if self.output:
                df.to_excel(os.path.join(self.output_file_dir, os.path.basename(file_path)), index=False)
        return df.drop(columns=[follow_up_l1_is_valid_field])

    def process_d2d_request(self):
        file_path = os.path.join(self.file_dir, self.d2d_request_filename)
        follow_up_l1_is_valid_field = '无效(D2D Followup SD L1开单)'
        if not os.path.exists(file_path):
            return pd.DataFrame()
        else:
            df = pd.read_excel(file_path)
            df.rename(
                columns={'User ID': 'PRID', 'Configuration item': 'Business Service', 'Contact Type': 'Contact type',
                         'Watch list': 'D2D Watch'},
                inplace=True)
            # 无效(D2D Followup SD L1开单）(无效条件)
            df[follow_up_l1_is_valid_field] = (
                df['Owned by'].str.lower().str.strip().isin(
                    ['srvcdesk-china-shanghai', 'srvcdesk-asiapac', 'SrvcDesk-Dalian'])
            ).astype(int)
            # 是否有效,以上三个条件，只要有一个无效，本字段即为无效
            df[self.is_valid_field] = 1
            df.loc[
                df[[follow_up_l1_is_valid_field]].any(axis=1),
                self.is_valid_field
            ] = 0
            # 无效的原因
            conditions = [
                df[follow_up_l1_is_valid_field] == 1
            ]
            df[self.is_valid_content_field] = np.select(
                conditions,
                [follow_up_l1_is_valid_field],
                default=''
            )  # 添加'a'列，根据'b', 'c', 'd'列的值来设置内容
            # 输出
            if self.output:
                df.to_excel(os.path.join(self.output_file_dir, os.path.basename(file_path)), index=False)
        return df.drop(columns=[follow_up_l1_is_valid_field])

    def get_dataframe(self):
        df = pd.DataFrame()
        for i in ['process_incident', 'process_interaction', 'process_request', 'process_d2d_incident',
                  'process_d2d_request']:
            df_branch = getattr(self, i)()
            df = pd.concat([df, df_branch])
        return df.fillna('').reset_index(drop=True)


def process_data(df):
    df_ = df.copy()
    df_['desc'] = df_['Short description'].str.lower()
    # 日期
    df_['Opened_date'] = pd.to_datetime(df_['Opened']).dt.date
    return df_


def compare(df_simple):
    if df_simple.shape[0] == 1:
        df_simple['result'] = '-'
        return df_simple
    dd = df_simple.reset_index(drop=True)

    embeddings = text2vec_model.encode(dd['desc'])
    similarity = cosine_similarity(embeddings, embeddings)

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
                aa.append(f"{dd.loc[j, 'Number']}:{str(round(value, 4))}")
        sorted_sim.append(' '.join(aa))
    df_simple['result'] = sorted_sim
    return df_simple


def run():
    df_data = ProcessData().get_dataframe()
    df_data_valid = df_data[df_data['是否有效'] == 1].reset_index(drop=True)
    df_data_invalid = df_data[df_data['是否有效'] == 0].reset_index(drop=True)
    df_process = process_data(df_data_valid)
    df_result = df_process.groupby(['PRID', 'Opened_date']).progress_apply(compare).reset_index(drop=True)
    df_final = pd.concat([df_result, df_data_invalid]).reset_index(drop=True)
    df_final.drop(columns=['desc', 'Opened_date']).to_excel(
        f'output/result_{datetime.now().strftime("%Y%m%d%H%M%S")}.xlsx', index=False)


if __name__ == '__main__':
    try:
        print(f"开始: {datetime.now()}")
        tqdm.pandas(desc="Processing texts")  # 设置进度条描述
        run()
        print(f"完成: {datetime.now()}")
    except Exception as e:
        print(repr(e))
    finally:
        input('输入任意键关闭...')
