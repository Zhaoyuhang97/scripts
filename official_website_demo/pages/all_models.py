from pywebio.pin import put_input

from official_website_demo.settings import BASE_DIR
from pywebio.output import *
from pywebio.pin import pin, pin_on_change
from pywebio.session import run_js

import base64
import math


def get_data(name=None):
    data = [
        {"name": "EM7", "desc": "旗舰轿跑", "price": "¥268,000起",
         "img": open((BASE_DIR / 'media' / 'images' / '2.png').as_posix(), 'rb').read()},
        {"name": "ES5", "desc": "智能SUV", "price": "¥228,000起",
         "img": open((BASE_DIR / 'media' / 'images' / '3.png').as_posix(), 'rb').read()},
        {"name": "ET3", "desc": "城市精灵", "price": "¥168,000起",
         "img": open((BASE_DIR / 'media' / 'images' / '4.png').as_posix(), 'rb').read()},
        {"name": "EX9", "desc": "豪华SUV", "price": "¥328,000起",
         "img": open((BASE_DIR / 'media' / 'images' / '1.png').as_posix(), 'rb').read()},
        {"name": "EV1", "desc": "微型电动车", "price": "¥128,000起",
         "img": open((BASE_DIR / 'media' / 'images' / '2.png').as_posix(), 'rb').read()},
        {"name": "EC6", "desc": "轿跑SUV", "price": "¥298,000起",
         "img": open((BASE_DIR / 'media' / 'images' / '3.png').as_posix(), 'rb').read()},
        {"name": "ET3", "desc": "城市精灵", "price": "¥168,000起",
         "img": open((BASE_DIR / 'media' / 'images' / '4.png').as_posix(), 'rb').read()},
    ]
    if name:
        data = [i for i in data if name.lower() in i['name'].lower()]
    return data


def search_handler():
    value = pin.search
    data = get_data(name=value)
    clear('main_content_modal_cards')
    all_models_card(data)


def all_models_card(data):
    with use_scope('main_content_modal_cards', clear=True):
        if not data:
            return
        items_per_row = 5  # 每行显示5个元素

        # 创建网格布局
        grid_content = []

        # 按行分组数据
        for i in range(0, len(data), items_per_row):
            row_data = data[i:i + items_per_row]

            # 创建当前行的内容
            row_content = []
            for model in row_data:
                item = put_column([
                    put_image(model['img'], format='png', width='100%', height='100%').style(
                        "height: 200px; object-fit: cover; transition: transform 0.3s, box-shadow 0.3s, opacity 0.3s; border-radius: 12px;"),
                    put_column([
                        put_text(model['name']).style("text-align: center; font-size: 1.5rem; margin-bottom: 0.5rem;"),
                        put_text(model['desc']).style("text-align: center; color: #666; margin: 0.5rem 0;"),
                        put_text(model['price']).style("text-align: center; font-weight: bold; margin-bottom: 1rem;"),
                        put_button("了解更多", onclick=lambda: run_js(
                            f"window.location.href = '/model-detail/{model['name']}';")).style(
                            "margin-top: 1rem; border: none; color: #0071e3; padding: 0.5rem 0.5rem; border-radius: 20px; cursor: pointer;"
                        )
                    ], size='20% 20% 20% 40%').style("padding: 1rem;text-align: center;")
                ], size='1fr').style(
                    "border-radius: 12px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin: 1rem;")
                row_content.append(item)  # 整行
            # , size = " ".join(['1fr' for i in range(items_per_row)])
            # 添加当前行到网格内容
            grid_content.append(row_content)  # 多行
        put_grid(grid_content, cell_widths=" ".join(['1fr' for i in range(items_per_row)]))  # 渲染多行

        # 添加 CSS 样式
        put_html("""
                <style>
                    img:hover {
                        transform: scale(1.05);
                        box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                        opacity: 0.7;
                    }
                </style>
                <script>
                    document.querySelector('input').addEventListener("keydown", e => {
                        if (e.key === "Enter") {
                            pywebio_js.js_run_js("search_handler()");
                        }
                    });
                </script>
                """)


def models_page():
    scope = 'main_content'
    clear(scope)
    data = get_data()

    with use_scope(scope):  # 在 "main_content" 作用域中渲染内容
        # 页面标题
        put_row([
            put_text("所有车型").style("text-align: center; margin: 2rem 0; font-size: 2rem; color: #333;")
        ])

        icon = base64.b64encode(
            open((BASE_DIR / 'staticfiles' / 'icon' / 'search.png').as_posix(), 'rb').read()).decode()
        put_html('''
        <style>
                input {
                    width: 100%;
                    padding: 12px;
                    border: 1px solid #ccc;  /* 默认灰色边框 */
                    border-radius: 4px;
                    font-size: 16px;
                    outline: none;
                    padding-right: 6% !important;
                }
                input:focus {
                    border-color: #007bff;  /* 聚焦时蓝色边框‌ */
                }
                .icon {
                    position: absolute;
                    right: 5px;
                    top: 50%;
                    transform: translateY(-50%);
                    pointer-events: none;
                    background-image: url("data:image/png;base64, ''' + icon + '''");
                    background-repeat: no-repeat;
                    width: 10%;
                    height: 100%;
                    background-position: right;
                    cursor: pointer;
                }
                </style>
            ''')

        # put_html(f'''<div class="search-container">
        #                  <div class="search-box">
        #                      <div class="icon"></div>
        #                      <input class="search-input" type="text" placeholder=" " onkeydown="searchHandleEnter(event)">
        #                      <label class="placeholder-label">搜索关键词</label>
        #                  </div>
        #              </div>
        #     ''')

        put_row(
            [
                put_text(''),
                put_input(name='search', label='', placeholder='搜索关键词').style('margin: 0;'),
                put_button('搜索', color='info', outline=False, onclick=search_handler),
                # put_html(f'''<div class="icon"></div>''').onclick(lambda x:x),
                # put_image(src=f"data:image/png;base64, {icon}").style('margin-right: 20%;'),
            ], size='8% 80% 15%'
        ).style('margin: 0 auto;position: relative; width: 50%; margin-bottom: 3vh')
        # pin_on_change('search', search_handler)
        put_scope('main_content_modal_cards')
        all_models_card(data)
