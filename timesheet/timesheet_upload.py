import requests
import pandas as pd
from tqdm import tqdm
import time
import json

"""
1. 从网站中获取token粘贴到timesheet.json中；
2. 制作excel，需要将文本原样粘贴到对应的列中；
"""

config = json.load(open('timesheet.json', 'r'))
PROXIES = config.get('proxies', None)

TOKEN = config['token']
HEADERS = {
    'content-type': 'application/json;charset=UTF-8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'Authorization': f'Bearer {TOKEN}'
}


def upload(data):
    try:
        url = 'https://servicebrain-uat.astrazeneca.cn/service-bau-api/bau-time-sheet/addTimeSheet'
        res = requests.post(url, headers=HEADERS, json=data, proxies=PROXIES)
        if res.status_code != 200:
            return False, res.text
        return True, ''
    except Exception as e:
        return False, repr(e)


def get_code(flat='applicationList', code=''):
    try:
        if flat == 'applicationList':
            url = 'https://servicebrain-uat.astrazeneca.cn/service-bau-api/bau-application/applicationList'
        elif flat == 'categoryList':
            url = 'https://servicebrain-uat.astrazeneca.cn/service-bau-api/bau-category/categoryList'
        elif flat == 'applicationSubList':
            url = f'https://servicebrain-uat.astrazeneca.cn/service-bau-api/bau-application-sub/applicationSubList/{code}/'
        elif flat == 'categorySubListByCategoryCode':
            url = f'https://servicebrain-uat.astrazeneca.cn/service-bau-api/bau-category/categorySubListByCategoryCode/{code}/'
        else:
            url = ''
        res = requests.get(url, headers=HEADERS, proxies=PROXIES)
        if res.status_code != 200:
            return False, res.text
        return True, res.json()
    except Exception as e:
        return False, repr(e)


def read_file(file) -> pd.DataFrame:
    df = pd.read_excel(file)
    return df


def batch_upload(df: pd.DataFrame):
    df['workDate'] = df['workDate'].apply(lambda x: x.strftime('%Y-%m-%d'))
    data = df.to_dict(orient='records')
    count = 2
    for d in tqdm(data, desc='正在执行中...', position=0):
        state, msg = upload(d)
        if not state:
            print(f"第{count}行出现错误,{msg},请修改后，删除掉已成功的行后重新执行")
            break
        time.sleep(1)
        count += 1
    else:
        print('All Done.')


def get_column_code(df) -> dict:
    try:
        application_list = get_code(flat='applicationList', code='')
        application_mapping = {i['applicationName'].strip(): i['applicationCode'] for i in application_list[1]}
        category_list = get_code(flat='categoryList', code='')
        category_mapping = {i['category'].strip(): i['categoryCode'] for i in category_list[1]}
        application_sub_mapping = {}
        category_sub_mapping = {}
        for application_name in df['applicationCode'].unique():
            application_code = application_mapping[application_name]
            res = get_code(flat='applicationSubList', code=application_code)
            application_sub_mapping[application_code] = {i['applicationSubName']: i['applicationSubCode'] for i in
                                                         res[1]}
        for category_name in df['categoryCode'].unique():
            category_code = category_mapping[category_name]
            res = get_code(flat='categorySubListByCategoryCode', code=category_code)
            category_sub_mapping[category_code] = {i['subCategory']: i['subCategoryCode'] for i in res[1]}
        return application_mapping, category_mapping, application_sub_mapping, category_sub_mapping
    except Exception as e:
        raise ValueError(f"获取code失败请重试。{repr(e)}")


def gen_batch_data(df, path=None):
    """生成长时间数据"""
    # 不包含周末\
    start = '2024-12-10'
    end = '2024-12-31'
    ll = [i for i in pd.date_range(start, end) if i.weekday() not in (5, 6)]
    df_concat = pd.DataFrame()
    for i in ll:
        df_ = df.copy()
        df_['workDate'] = i
        df_concat = pd.concat([df_concat, df_])
    df_concat.to_excel(path, index=False)


if __name__ == "__main__":
    df = read_file(r'timesheet.xlsx')
    application_mapping, category_mapping, application_sub_mapping, category_sub_mapping = get_column_code(df)
    df['applicationCode'] = df['applicationCode'].map(application_mapping.get)
    df['categoryCode'] = df['categoryCode'].map(category_mapping.get)
    df['applicationSubCode'] = df.apply(
        lambda x: application_sub_mapping[x['applicationCode']][x['applicationSubCode']], axis=1)
    df['subCategoryCode'] = df.apply(lambda x: category_sub_mapping[x['categoryCode']][x['subCategoryCode']], axis=1)
    batch_upload(df)
    # # 生成
    # df = read_file(r'ttt.xlsx')
    # gen_batch_data(df, 'timesheet.xlsx')
