import pandas as pd
import re
import os
from pathlib import Path
from urllib.parse import unquote
import requests

file_path = r'C:\Users\kmsj845\Downloads\机器人数据\标准问题文字 IT24.5.14.xlsx'
img_dir_path = r'C:\Users\kmsj845\Downloads\机器人数据\文字IT多媒体'
PROXY = 'azpzen.astrazeneca.net:9480'


# PROXY = '10.116.6.100:9480'

def sub_answer(value, img_name_list):
    src_ll = re.findall(r'<img\s+src="([^"]+)"', value)
    if src_ll:
        sys_media_path = r'/media/'
        for src in src_ll:
            # if src.startswith('http'):
            #     # url解码后获得文件后缀名
            #     img_suffix_name_lower = unquote(src).split('/')[-1].lower()
            # else:
            #     # 获得文件后缀名
            #     img_suffix_name_lower = src.split('/')[-1].lower()
            img_suffix_name_lower = unquote(src).split('/')[-1].lower().replace('+', ' ')
            # 如果文件后缀名没有格式，加上png
            if '.' not in img_suffix_name_lower:
                img_suffix_real_name_lower = f"{img_suffix_name_lower}.png"
            else:
                img_suffix_real_name_lower = img_suffix_name_lower
            # 查找本地文件名是否包含src中文件名
            img_full_names = [i.name for i in img_name_list if img_suffix_real_name_lower in i.name.lower()]
            if len(img_full_names) > 1:
                # 匹配多个只取大图
                img_full_names = [i for i in img_full_names if '__' not in i]
                if img_full_names:
                    img_full_name = img_full_names[0]
                    value = value.replace(src, f"{sys_media_path}{img_full_name}")
            elif len(img_full_names) == 1:
                img_full_name = img_full_names[0]
                value = value.replace(src, f"{sys_media_path}{img_full_name}")
            else:
                print(f'{src}::::没找到本地文件')
                if src.startswith('http'):
                    response = requests.get(src, proxies={'https': PROXY, 'http': PROXY})
                    download_img_name = Path(img_suffix_real_name_lower).resolve()
                    with open((img_dir_path / download_img_name).as_posix(), 'wb') as f:
                        f.write(response.content)
                    print(f'{src}::::已下载本地文件')
                    value = value.replace(src, f"{sys_media_path}{download_img_name.as_posix()}")
                else:
                    print('不是http的没办法了')
    return value


img_dir = Path(img_dir_path).resolve()
if img_dir.is_dir():
    img_names = [img_name for img_name in img_dir.iterdir()]
    df = pd.read_excel(file_path)
    df['final'] = df['回答'].apply(sub_answer, img_name_list=img_names)
    df.to_excel(Path(file_path).resolve().parent / 'final.xlsx', index=False)
    1
