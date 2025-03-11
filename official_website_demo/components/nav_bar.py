from pywebio.output import *
from official_website_demo.pages import all_models_page, home_page


def nav_bar():
    with use_scope('nav_bar', clear=True):
        put_row([
            put_column([
                put_text("EV Motors").style("font-size: 1.5rem;").onclick(home_page)  # 标题样式
            ], size="auto"),
            put_column([
                put_text('车型').onclick(all_models_page),
                put_text('技术').onclick(all_models_page),
                put_text('服务').onclick(all_models_page),
                put_text('新闻').onclick(all_models_page),
                put_text('关于我们').onclick(all_models_page),
            ], size="auto").style("display: flex; gap: 2rem;color: #78c2ad;")
        ], size='1fr').style("backdrop-filter: blur(10px); padding: 1rem 2rem;align-items: center;height: 8vh;")


__all__ = [
    'nav_bar',
]
