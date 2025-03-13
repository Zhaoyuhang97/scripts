from pywebio.pin import put_input

from official_website_demo.settings import BASE_DIR
from pywebio.output import *
from pywebio.session import run_js
from pywebio.pin import pin, pin_on_change, put_checkbox
import random

img = open((BASE_DIR / 'media' / 'images' / '2.png').as_posix(), 'rb').read()

# 模拟数据源
vehicle_images = ["img_url1", "img_url2", "img_url3"]  # 图片地址列表，请替换为真实的链接
vehicle_info = {
    'name': 'Model S',
    'description': '''特斯拉 Model S是一款全尺寸高性能电动轿车，
                   它不仅拥有令人惊叹的速度和加速度性能,
                   同时也具备长距离续航里程''',
}
specifications = [
    {"label": "电池容量", "value": "75 kWh"},
    {"label": "最大功率", "value": "480 kW"},
    {"label": "加速时间(0-100km/h)", "value": "<3.2 秒"},
]


def model_detail():
    scope = 'main_content'
    with use_scope(scope, clear=True):  # 在 "main_content" 作用域中渲染内容

        put_html("""
        <style>

        <style>
        """)

        main_image_scope = 'main_image'

        def change_main_image(img):
            def inner():
                """用于更新主显示图片"""
                with use_scope(name=main_image_scope, clear=True):
                    put_image(img, width='90%').style("border: 8px #fff solid; border-radius: 25px;")
            return inner

        # 车辆信息
        vehicle_info = {
            'name': 'Model Y',
            'intro': '车辆经过重新设计，以实现效率最大化，更有效地使用每一度电。更新后的悬架、轮毂和轮胎使驾乘体验更流畅、更安静。',
            'performance': {'马力': '300hp', '扭矩': '400Nm', '加速': '0-100km/h in 4.3s'},
            'configuration': ['大容量储物空间', '全新内饰', '沉浸式音效']
        }

        # 图片列表
        images = [
            'https://img1.baidu.com/it/u=570677140,1778679078&fm=253&fmt=auto&app=120&f=JPEG?w=1422&h=800',
            'https://img2.baidu.com/it/u=3465534984,1044890142&fm=253&fmt=auto&app=138&f=JPEG?w=981&h=500',
            'https://img1.baidu.com/it/u=570677140,1778679078&fm=253&fmt=auto&app=120&f=JPEG?w=1422&h=800',
            'https://img2.baidu.com/it/u=3465534984,1044890142&fm=253&fmt=auto&app=138&f=JPEG?w=981&h=500',
            'https://img1.baidu.com/it/u=570677140,1778679078&fm=253&fmt=auto&app=120&f=JPEG?w=1422&h=800',
            'https://img2.baidu.com/it/u=3465534984,1044890142&fm=253&fmt=auto&app=138&f=JPEG?w=981&h=500',
            'https://img1.baidu.com/it/u=570677140,1778679078&fm=253&fmt=auto&app=120&f=JPEG?w=1422&h=800',
        ]

        put_row([
            # 左侧
            put_column([
                put_scope(main_image_scope).style("text-align: center;height: 50vh;"),
                put_row(
                    [
                        put_image(img).style(
                            "border: 5px #fff solid; border-radius: 10px;transform: scale(1.05); box-shadow: 0 8px 16px rgba(0,0,0,0.2); opacity: 1;margin:0 10px;height:50px;").onclick(
                            change_main_image(img)
                        )
                        for img in images
                    ]
                ).style("justify-self: center;width: 80%;justify-items: center;gap: 20px;")
            ], size='3fr 1fr').style(""),
            # 留白
            put_column(),
            # 右侧
            put_column([
                put_text(vehicle_info['name']).style("font-size: 2rem;"),
                put_text(vehicle_info['intro']).style("color: darkgray;"),
                put_markdown("### 性能参数"),
                put_table([
                    ['参数', '值'],
                    ['马力', vehicle_info['performance']['马力']],
                    ['扭矩', vehicle_info['performance']['扭矩']],
                    ['加速', vehicle_info['performance']['加速']]
                ]),
                put_markdown("### 配置"),
                put_table([
                    vehicle_info['configuration']
                ]),
            ], size='auto')
        ], size='60% 5% 35%')

        main_image = images[0]  # 默认主图
        change_main_image(main_image)()
