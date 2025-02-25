import datetime
from collections import namedtuple
from nicegui import ui, run as nicegui_run
from queue import Queue
import asyncio
import json
import logging
import os
import requests
import jwt
import threading
import time
import wave
import tempfile
import numpy as np

# 创建一个handler，用于写入日志文件
logger = logging.getLogger('nicegui')
logger.setLevel(logging.DEBUG)
logger_error = logging.FileHandler('nicegui_run.log')
logger_error.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger_error.setFormatter(formatter)
logger.addHandler(logger_error)
# icon = 'https://www.wp2.cn/material_icons/'
data = [
    {'role': 'assistant', 'content': 'Hi请说出你的故事...', 'datetime': '2024-05-14 09:19:21'},
    {'role': 'user', 'content': 'jashdkjashdkjas', 'datetime': '2024-05-16 19:19:21'},
    {'role': 'assistant', 'content': 'jashdkjashdkjas\njashdkjashdkjasjashdkjashdkjas',
     'datetime': '2024-05-16 09:19:21'},
    {'role': 'user', 'content': '阿三大苏打实打实', 'datetime': '2024-05-14 09:19:21'},
    {'role': 'assistant', 'content': '可累计安装量肯德基ask了大家阿斯利康大家', 'datetime': '2024-05-17 09:19:21'},
    {'role': 'user', 'content': '啊书法大赛顶顶顶顶顶顶顶顶顶顶顶顶顶顶', 'datetime': '2024-05-14 09:19:21'},
    {'role': 'assistant', 'content': '啊书法大赛顶顶顶顶顶顶顶顶顶顶顶顶顶顶', 'datetime': '2024-05-17 11:14:21'},
]

PROXY = '10.116.6.100:9480'
SENT_STYLE = 'display: flex; width: 100%; justify-content: flex-end;'


def do_request(messages=None, *args, **kwargs):
    api_key = '261152645fcf6e37acf1c0be1d8082dd.nahqDpoCFcp9bpNt'
    token = jwt.encode(
        {
            'api_key': api_key.split('.')[0],
            'exp': int(round(time.time() * 1000)) + 1000 * 60 * 60,
            'timestamp': int(round(time.time() * 1000))
        },
        api_key.split('.')[1],
        algorithm='HS256',
        headers={'alg': 'HS256', 'sign_type': 'SIGN'}
    )
    data = {
        'model': 'glm-4',
        'messages': messages,
        'stream': False,
        'temperature': 0.1,
        'top_p': 0.1
    }

    response = requests.post(
        url='https://open.bigmodel.cn/api/paas/v4/chat/completions',
        json=data,
        headers={'Content-Type': 'application/json', 'Authorization': token},
        proxies={'http': PROXY, 'https': PROXY},
        verify=False,
        stream=True
    )
    return response


def calc_time_utils(t):
    if isinstance(t, str):
        t = datetime.datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
    elif isinstance(t, datetime.datetime):
        pass
    else:
        return None
    now = datetime.datetime.now()
    diff = (now - t)
    if diff.days == 0:
        if diff.seconds <= 600:
            return '刚刚'
        elif 600 < diff.seconds <= 3600:
            return f'{diff.seconds // 60} 分钟之前'
        else:
            return f'{diff.seconds // 3600} 小时之前'
    elif diff.days == 1:
        return f'昨天 {t.strftime("%H:%M:%S")}'
    else:
        return t.strftime("%Y-%m-%d %H:%M:%S")


def send_user_message_(e, history_message=[]):
    value = e.sender.value
    # 发送事件
    if value.strip() == '':
        ui.notify('内容不能为空', position='top', type='warning')
        return
    di_id = render_chat_message(role='user', message=value)  # 获取生成的robot对话id，用于定位到最底部
    history_message.append({'role': 'user', 'content': value})
    value_ = '...'

    @ui.refreshable
    def number_ui() -> None:
        render_chat_message(role='assistant', message=value_)

    number_ui()

    ui.run_javascript(f"document.getElementById('{di_id}').scrollIntoView()")
    res = do_request(history_message)

    value_ = ''
    for i in res.iter_lines():
        # 有值后渲染
        if i:
            i = i.decode('utf-8')
            i = json.loads(i)
            value_ += i['choices'][0]['message']['content']

            number_ui.refresh()
    history_message.append({'role': 'assistant', 'content': value_})


def render_chat_message(role, message, dt=None) -> str:
    di_id = ''
    if role == 'assistant':
        with ui.chat_message(name='assistant', stamp=calc_time_utils(dt)):
            label = ui.markdown(message)
            di_id = f"c{label.id}"
    elif role == 'user':
        with ui.chat_message(name='user', sent=True).style(SENT_STYLE):
            label = ui.label(message)
            di_id = f"c{label.id}"
            # ui.markdown('This is **Markdown**.')
            # ui.html('This is <strong>HTML</strong>.')
    else:
        pass
    return di_id


@ui.page('/')
def main():
    ui.label(text="Welcome come to Our WebPage!").style(
        """
            margin-top: 100px;
            text-align: center;
            color: #6E93D6;
            font-size: 300%;
            font-weight: 350;
            width: 100%;
        """
    )
    with ui.row().style('width: 100%; justify-content: center;align-items: center;margin-top: 150px;font-size: 100%;'):
        ui.label(text='页面将于')
        knob = ui.knob(
            value=5, max=5, min=0, step=1, show_value=True, size='lg',
            on_change=lambda x: ui.open('/conversion_page') if x.value == 0 else None,
        )
        ui.timer(interval=1.0, callback=lambda: knob.set_value(knob.value - 1))
        ui.label(text='秒后跳转,如果跳转失败请点击')
        ui.link('index', '/conversion_page').style("""color: #6E93D6;font-size: 150%;font-weight: 350;""")
        ui.label(text='跳转')


async def send_user_message(e):
    await nicegui_run.io_bound(send_user_message_, e.sender.value, timeout=30)
    ui.notify(f'OK')


@ui.page('/conversion_page')
async def conversion_page():
    CENTER_STYLE = 'align-content:center;justify-content:center;align-items:center;'
    HEADER_STYLE = f'background-color:#001529;height:48px;{CENTER_STYLE}'
    LOGO_STYLE = f'padding:16px;gap:6%;{CENTER_STYLE}'
    MAIN_STYLE = 'width:100%;height:100%;'
    MAIN_LEFT_STYLE = f'width:80%;height:calc(100vh - 80px);padding:16px;border-radius:2px;align-items: none;' \
                      f'background-color:#f6f7f9;place-items:center;align-items:center;'
    CONVERSATION_STYLE = f'width:80%;height:calc(100vh - 180px);padding:16px;border-radius:20px;padding-bottom:45px;{CENTER_STYLE}'
    MAIN_RIGHT_STYLE = f'width:16%;height:calc(100vh - 80px);padding:6px;{CENTER_STYLE}'

    INPUT_STYLE = 'width:50%;position: fixed;bottom:50px;border-radius:12px;'

    history_message = []

    with ui.header(elevated=True, bordered=True).style(HEADER_STYLE):
        ui.icon('face', size='xl')

    with ui.column().classes('w-full text-xl').style(MAIN_STYLE):
        with ui.splitter(value=10).classes('w-full h-156') as splitter:
            # 左侧
            with splitter.before:
                # logo
                with ui.row().classes('w-full text-xl').style(LOGO_STYLE):
                    ui.icon('insert_emoticon', size='md')
                    ui.label('ServiceBrain').classes('font-bold')
                # 标签
                with ui.tabs().props('vertical').classes('w-full') as tabs:
                    conversation = ui.tab('对话', icon='support_agent')
                    reason = ui.tab('思考过程', icon='psychology')
            # 右侧
            with splitter.after:
                with ui.row().style(MAIN_STYLE):
                    # 对话框
                    with ui.column().style(MAIN_LEFT_STYLE).classes('border'):
                        with ui.tab_panels(tabs, value=conversation).props('vertical').classes('w-full h-full').style(
                                CONVERSATION_STYLE):
                            # 对话页
                            with ui.tab_panel(conversation):
                                # 对话框
                                for i in data:
                                    render_chat_message(role=i['role'], message=i['content'], dt=i['datetime'])
                                # 发送
                                with ui.input(placeholder='请输入你的问题,回车发送').props("outlined dense").style(
                                        INPUT_STYLE) as input_ele:
                                    input_ele.on('keydown.enter', send_user_message_)
                                    # input_ele.on('keydown.enter',
                                    #              lambda e: send_user_message(e.sender.value, history_message),
                                    #              )

                            # 思考页
                            with ui.tab_panel(reason).style(CENTER_STYLE):
                                ui.label('Alarms').classes('text-h4')
                                ui.label('Content of alarms')

                    # 右侧待定
                    with ui.column().style(MAIN_RIGHT_STYLE):
                        ui.label('待定...').classes('text-h5')


# class WebPage(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#         self.asnyc = asyncio
#         self.asnyc.set_event_loop(asyncio.new_event_loop())
#         self.loop = self.asnyc.get_event_loop()
#
#     def run(self):
#         ui.run(title='conversion', port=10086, host='0.0.0.0', reload=False, show=False)
#
#
# thread1 = WebPage()
# # 开启新线程
# thread1.start()
# thread1.join()

ui.run(title='conversion', port=10086, host='0.0.0.0', reload=False, show=False)
