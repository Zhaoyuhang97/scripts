from pywebio import start_server, config
from pywebio.output import *
from pywebio.session import run_js

from official_website_demo.components import nav_bar, footer
from official_website_demo.global_css import global_css
from official_website_demo.pages import home_page


def model_detail_page(model_name):
    clear()
    nav_bar()
    put_scope("main_content")  # 创建作用域
    with use_scope("main_content"):  # 在作用域中渲染内容
        details = {
            "EM7": {
                "specs": [
                    {"name": "续航里程", "value": "680km"},
                    {"name": "百公里加速", "value": "3.9s"},
                    {"name": "最大功率", "value": "480kW"}
                ],
                "features": ["智能空气悬架", "L4级自动驾驶", "4D沉浸式座舱"]
            }
        }

        put_row([
            put_column([
                put_image(f"https://search-operate.cdn.bcebos.com/7e85570b817e17e8f3ae93134cc78451.gif", format='jpeg').style(
                    "width: 100%; border-radius: 12px;")
            ], size="1fr"),
            put_column([
                put_text(model_name).style("font-size: 2rem; margin-bottom: 1.5rem;"),
                put_row([
                    put_text("核心参数").style("font-size: 1.5rem; margin-bottom: 1rem;")
                ]),
                put_grid([
                    [put_text(f"{item['name']}").style("margin-right: 1rem;"),
                     put_text(item['value']).style("font-weight: bold;")] for item in
                    details.get(model_name, {}).get('specs', [])
                ], cell_width='auto'),
                put_row([
                    put_text("亮点功能").style("font-size: 1.5rem; margin: 2rem 0 1rem;")
                ]),
                put_grid([
                    [put_text(f"✓ {feature}").style("padding: 0.5rem 0;")] for feature in
                    details.get(model_name, {}).get('features', [])
                ], cell_width='auto'),
                put_button("预约试驾", onclick=lambda: None).style(
                    "margin-top: 2rem; background: #0071e3; color: white; padding: 1rem 2rem; border: none; border-radius: 30px; cursor: pointer;")
            ], size="1fr")
        ], size="1fr 1fr", style="max-width: 1200px; margin: 2rem auto; padding: 0 2rem;")

    footer()
    put_button("返回首页", onclick=lambda: home_page())


def technology_page():
    clear()
    nav_bar()
    put_scope("main_content")
    with use_scope("main_content"):
        put_row([
            put_text("核心技术").style("font-size: 2rem;")
        ])
        put_grid([
            [put_column([
                put_text("智能驾驶").style("font-size: 1.5rem; margin-bottom: 1rem;"),
                put_text("全栈自研的自动驾驶系统，配备12个摄像头和5个毫米波雷达").style("color: #666;")
            ], size="1fr"),
                put_column([
                    put_text("电池技术").style("font-size: 1.5rem; margin-bottom: 1rem;"),
                    put_text("自主研发的固态电池技术，能量密度提升40%").style("color: #666;")
                ], size="1fr"),
                put_column([
                    put_text("智能座舱").style("font-size: 1.5rem; margin-bottom: 1rem;"),
                    put_text("全场景语音交互，多屏联动智能生态系统").style("color: #666;")
                ], size="1fr")]
        ], cell_width='1fr')
    footer()
    put_button("返回首页", onclick=lambda: home_page())


def main():
    config(title="EV Motors 官网", css_style=global_css)
    clear()
    nav_bar()  # 页头
    put_scope("main_content")
    home_page()  # 主页
    footer()  # 页脚
    put_html(global_css)


if __name__ == '__main__':
    start_server(main, port=8080, debug=True)
