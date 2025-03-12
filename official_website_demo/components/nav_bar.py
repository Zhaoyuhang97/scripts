from pywebio.output import *
from pywebio.session import run_js


def nav_bar():
    with use_scope('nav_bar', clear=True):
        put_row([
            put_column([
                put_text("EV Motors").style("font-size: 1.5rem;").onclick(lambda: run_js("window.location.href = '/home';"))  # 标题样式
            ], size="auto"),
            put_column([
                put_text('首页').onclick(lambda: run_js("window.location.href = '/home';")),
                put_text('车型').onclick(lambda: run_js("window.location.href = '/models';")),
                put_text('技术').onclick(lambda: run_js("window.location.href = '/technology';")),
                put_text('服务').onclick(lambda: run_js("window.location.href = '/service';")),
                put_text('新闻').onclick(lambda: run_js("window.location.href = '/news';")),
                put_text('关于我们').onclick(lambda: run_js("window.location.href = '/models';")),
            ], size="auto").style("display: flex; gap: 2rem;color: #78c2ad;")
        ], size='1fr').style("backdrop-filter: blur(10px); padding: 1rem 2rem;align-items: center;height: 8vh; margin-bottom: 3vh")


__all__ = [
    'nav_bar',
]
