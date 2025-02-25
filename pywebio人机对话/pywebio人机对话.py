import asyncio
from pywebio.input import *
from pywebio.output import *
from pywebio.session import *
from pywebio.pin import *
from pywebio.pin import _pin_output
from pywebio.utils import check_dom_name_value
from pywebio import start_server
from openai import OpenAI
from datetime import datetime
import time
import requests
import logging
import jwt
import warnings

warnings.filterwarnings('ignore')

# 创建一个handler，用于写入日志文件
logger = logging.getLogger('pywebio')
logger.setLevel(logging.DEBUG)
logger_error = logging.FileHandler('../pywebio.log')
logger_error.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger_error.setFormatter(formatter)
logger.addHandler(logger_error)

BUBBLE_STYLE = """
        border-radius: 0 8px 8px 8px; position: relative;text-align: left;
        padding: 15px;font-family: 'Arial', sans-serif;font-size: 14px;
        line-height: 1.4;box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        min-width: 10%;max-width: 80%; width: auto;word-wrap: break-word;
    """
PROXY = '10.116.6.100:9480'
HISTORY = []


def do_request(messages=None, *args, **kwargs):
    api_key = 'sk-KJkVrBU606vu6J2PW9Y3ZEBYU5npa3g833Of0VYjIThUs1BK'

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.cn/v1",
    )

    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=messages,
        temperature=0.3,
    )

    return completion.choices[0].message.content


def pin_on_change_(name: str, onchange=None, clear: bool = False, init_run: bool = False, **callback_options):
    assert not (onchange is None and clear is False), "When `onchange` is `None`, `clear` must be `True`"
    if onchange is not None:
        callback = lambda data: onchange(data)
        callback_id = pin.output_register_callback(callback, **callback_options)
        if init_run:
            onchange(pin[name])
    else:
        callback_id = None
    pin.send_msg('pin_onchange', spec=dict(name=name, callback_id=callback_id, clear=clear))


def add_assistant_msg(msg, position, is_request, **kwargs):
    """
    msg: [{'role': 'assistant', 'content': res, 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
    position: -2 倒数第二个位置
    is_request： 是否请求接口并loading
    """
    global HISTORY
    BUBBLE_LEFT_STYLE = f"""
            background-color:#4fd3c8;margin-right: 60px;{BUBBLE_STYLE}
        """
    if is_request:
        put_text('assistant', scope='main_scope_', position=position).style('margin: 0;text-align: left;')
        with put_loading(shape='grow', color='info', scope='main_scope_', position=position).style(
                'BUBBLE_LEFT_STYLE'):  # -2:倒数第2个，倒数第一个是<a></a>用于滚动条置底)
            try:
                # 请求接口
                res = do_request(HISTORY)
                HISTORY.append(
                    {'role': 'assistant', 'content': res, 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                put_markdown(res, scope='main_scope_', position=position).style(BUBBLE_LEFT_STYLE)
            except Exception as e:
                # 请求出错后把user的问题删除，重新加载对话页面
                toast(f'出错了:{repr(e)}', color='error')
                HISTORY = HISTORY[:-1]
                reload_conversation_page(clear_=False)
    else:
        # 不请求接口，直接渲染msg
        put_column(
            [
                put_text('assistant').style('margin: 0;text-align: left;'),
                put_markdown(msg).style(BUBBLE_LEFT_STYLE),
            ],
            size='30px calc(100% - 30px)',
            scope='main_scope_',
            position=position  # -2:倒数第2个，倒数第一个是<a></a>用于滚动条置底
        ).style('justify-items: left;')
        # put_text('assistant', scope='main_scope_', position=position).style('margin: 0;text-align: left;')
        # put_markdown(msg, scope='main_scope_', position=position).style(BUBBLE_LEFT_STYLE)


def add_user_msg(msg, position, is_request, **kwargs):
    """
    msg: [{'role': 'assistant', 'content': res, 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]
    position: -2 倒数第二个位置
    is_request: 是否请求接口并加入HISTORY
    """
    BUBBLE_RIGHT_STYLE = f"""
            background-color:#f6f7f9;margin-left: 60px;{BUBBLE_STYLE}
        """
    put_column(
        [
            put_text('user').style('margin: 0;text-align: right;'),
            put_markdown(msg).style(BUBBLE_RIGHT_STYLE)
        ],
        size='30px calc(100% - 30px)',
        scope='main_scope_',
        position=position  # -2:倒数第2个，倒数第一个是<a></a>用于滚动条置底
    ).style('justify-items: right;')
    if is_request:
        HISTORY.append({'role': 'user', 'content': msg, 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
    # put_text('user', scope='main_scope_', position=position).style('margin: 0;text-align: right;'),
    # put_markdown(msg, scope='main_scope_', position=position).style(BUBBLE_RIGHT_STYLE)


def add_conversation_msg(role, msg, is_request=False, position=-2, **kwargs):
    if role == 'assistant':
        add_assistant_msg(msg=msg, position=position, is_request=is_request, **kwargs)
    elif role == 'user':
        add_user_msg(msg=msg, position=position, is_request=is_request, **kwargs)
    else:
        put_markdown('')


def add_conversation_system_msg():
    add_conversation_msg('assistant', msg='**请在底部输入框中输入你的问题吧!**', position=OutputPosition.BOTTOM,
                         is_request=False)
    put_html("<div id='bottom_id'></div>", scope='main_scope_').style('height:30px;margin-top:50px')
    for history in HISTORY:
        add_conversation_msg(history['role'], msg=history['content'], is_request=False)
    run_js(f"document.getElementById('bottom_id').scrollIntoView()")  # 滚动到底部


def reload_conversation_page(clear_=True):
    """
    重新加载对话页面
    clear：是否删除历史记录
    """
    global HISTORY
    if clear_:
        HISTORY = []
    with use_scope('main_scope_', clear=True):
        add_conversation_system_msg()


def handler_enter_key(value):
    if value.endswith('\n'):
        handler_send()


def handler_send():
    value = pin.send
    if value.strip() == '':
        toast('请输入内容!', color='danger')
        return
    add_conversation_msg('user', msg=value, is_request=True)
    pin.send = None
    # unique_score = f'{int(time.time())}_{random.randint(100000, 999999)}'
    run_js(f"document.getElementById('bottom_id').scrollIntoView()")  # 滚动到底部
    add_conversation_msg('assistant', msg=None, is_request=True)
    run_js(f"document.getElementById('bottom_id').scrollIntoView()")  # 滚动到底部


def page_conversation_main():
    # content = put_column(
    #     [
    #         put_text('GLM-4').style('font-weight: 600;font-size: 20px;text-align: center;'),
    #         put_scrollable(
    #             [
    #                 put_scope('main_scope_', position=OutputPosition.TOP, content=[]).style(
    #                     'width: 80%;margin: 0 auto;padding:20px;')
    #             ],
    #             height=550,
    #             keep_bottom=True,
    #             border=False
    #         ),
    #         put_row(
    #             [
    #                 put_textarea('send', placeholder='请输入您的问题,回车换行,点击发送按钮发送', rows=1,
    #                              minlength=1).style('border-radius: .25rem 0 0 .25rem;'),
    #                 put_button(label='发 送', onclick=handler_send, color='primary').style(
    #                     'border-radius: 0;'),
    #                 put_button(label='清空记录', onclick=handler_clear_history, color='warning').style(
    #                     'border-radius: 0 .25rem .25rem 0;')
    #             ],
    #             size='75% 10% 15%',
    #             scope='main_scope'
    #         ).style('width: 80%; margin: 10px auto 0 auto;position:fix;bottom:200px')
    #     ],
    #     size='5vh 80vh 10vh',
    #     scope='main_scope'
    # )
    # pin_on_change_('send', onchange=handler_enter_key)
    pin_on_change('send', onchange=handler_enter_key)
    content = put_column(
        [
            put_text('GLM-4').style('font-weight: 600;font-size: 20px;text-align: center;'),
            put_scope('main_scope_', position=OutputPosition.TOP, content=[]).style(
                'border: 1px solid #00000029;width: 80%;margin: 0 auto;padding:20px;overflow-y: auto;overflow-x: hidden;'),
            put_row(
                [
                    put_textarea('send', placeholder='请输入您的问题,回车换行,点击发送按钮发送', rows=2,
                                 minlength=1).style('border-radius: .25rem 0 0 .25rem;'),
                    put_buttons(
                        [
                            {'label': '发 送', 'color': 'primary', 'value': '发 送'},
                            {'label': '清空记录', 'color': 'warning', 'value': '清空记录'}
                        ],
                        onclick=[handler_send, reload_conversation_page],
                        group=True,
                        small=True
                    ),
                    # put_button(label='发 送', onclick=handler_send, color='primary').style('border-radius: 0;'),
                    # put_button(label='清空记录', onclick=handler_clear_history, color='warning').style(
                    #     'border-radius: 0 .25rem .25rem 0;text-align: end;')
                ],
                size='80% 20%',
                scope='main_scope'
            ).style('width: 80%; margin: 10px auto;')
        ],
        size='5vh 80vh 10vh',
        scope='main_scope'
    )
    return content


def page_conversation():
    with use_scope('main_scope', clear=True):
        page_conversation_main()
    add_conversation_system_msg()


def page_think_main():
    return put_column(
        [
            put_text('这是思考页').style('font-weight: 600;font-size: 20px;')
        ],
        size='80px 60px 60px',
        scope='main_scope'
    )


def page_think():
    with use_scope('main_scope', clear=True):
        page_think_main()


def index():
    TOOLBAR_STYLE = """
                    border-block-color: #c1c4c9;
                    justify-content: center;
                    place-items: center;
                    padding-right: 20px;
                    grid-gap: 10px;
                    border-right: 1px solid #00000029;
                    """
    put_html(
        '''
            <style> 
                #output-container { max-width: 100%; } 
                .btn-light {width:200px}
                .footer {display: none;}
            </style>
        '''
    )
    global HISTORY
    HISTORY = []

    put_row(
        [
            # 左侧
            put_column(
                [
                    put_text('Service Brain').style('font-weight: 600;font-size: 20px;'),
                    put_button("会话", onclick=page_conversation, color='light'),
                    put_button("思考过程", onclick=page_think, color='light'),
                ],
                size='70px 50px 50px'
            ).style(css_style=TOOLBAR_STYLE),
            # 中间
            put_column(
                [put_scope('main_scope', page_conversation_main())],
                size='100%'
            ).style('padding: 0 30px 0 30px;'),
            # 右侧
            put_column(
                [put_scope('left_scope', [
                    put_grid([
                        [span(put_markdown('**·Title**'), col=1, row=1)],
                        [put_column([put_text('BBBBBBBBBBBB'), put_text('CCCCCCCCCCCCCCC')], size='20px 30px')],
                        [put_column([put_text('BBBBBBBBBBBB'), put_text('CCCCCCCCCCCCCCC')], size='20px 30px')],
                        [put_column([put_text('BBBBBBBBBBBB'), put_text('CCCCCCCCCCCCCCC')], size='20px 30px')],
                    ], cell_width='100%', cell_height='80px').style('padding:10px')
                ])],
                size='100%'
            ).style('border-left: 1px solid #00000029;'),
        ],
        size='15% 65% 20%',
    ).style('height: calc(100vh - 61px);')
    add_conversation_system_msg()


if __name__ == '__main__':
    start_server([index], auto_open_webbrowser=False, port=10086)
