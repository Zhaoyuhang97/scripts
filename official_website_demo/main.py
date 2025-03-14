import tornado
from pywebio import start_server, config
from pywebio.output import *
from pywebio.session import run_js
from pywebio.platform.tornado import webio_handler

from official_website_demo.components import nav_bar, footer
from official_website_demo.global_css import global_css
from official_website_demo.pages import home_page, models_page, technology_page, service_page, news_page, model_detail
from official_website_demo.settings import BASE_DIR


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
                put_image(f"https://search-operate.cdn.bcebos.com/7e85570b817e17e8f3ae93134cc78451.gif",
                          format='jpeg').style(
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


def main(page):
    config(title="EV Motors 官网", css_style=global_css)
    clear()
    nav_bar()  # 页头
    put_scope("main_content")
    page()  # 主页
    footer()  # 页脚
    put_html(global_css)
    put_html("""<script type="text/javascript" src="/static/js/pywebio.min.js"></script>""")


def home():
    main(home_page)


def models():
    main(models_page)


def technology():
    main(technology_page)


def service():
    main(service_page)


def news():
    main(news_page)


def detail():
    main(model_detail)


def make_app():
    return tornado.web.Application([
        (r"/", webio_handler(home)),
        (r"/home", webio_handler(home)),
        (r"/models", webio_handler(models)),
        (r"/technology", webio_handler(technology)),
        (r"/service", webio_handler(service)),
        (r"/news", webio_handler(news)),
        # (r"/about-us", webio_handler(news)),
        (r"/model-detail/(.*)", webio_handler(detail)),
        # 配置静态文件路径
        # (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": static_path.as_posix()}),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8080)
    static_path = BASE_DIR / 'staticfiles'
    app.settings = {"static_path": static_path.as_posix()}
    tornado.ioloop.IOLoop.current().start()
    # start_server(main, port=8080, debug=True, static_dir='./staticfiles')
