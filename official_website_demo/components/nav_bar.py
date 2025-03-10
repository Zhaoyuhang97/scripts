from pywebio.output import *


def nav_bar():
    with use_scope('nav_bar', clear=True):
        put_row([
            put_column([
                put_text("EV Motors").style("font-size: 1.5rem;")  # 标题样式
            ], size="auto"),
            put_column([
                put_link("车型", url='#').style("text-decoration: none; color: inherit;"),
                put_link("技术", url='#').style(
                    "text-decoration: none; color: inherit;"),
                put_link("服务", url='#').style("text-decoration: none; color: inherit;"),
                put_link("关于我们", url='#').style("text-decoration: none; color: inherit;")
            ], size="auto").style("display: flex; gap: 2rem;color: #78c2ad;")
        ], size="1fr").style("backdrop-filter: blur(10px); padding: 1rem 2rem;align-items: center;height: 8vh;")


__all__ = [
    'nav_bar',
]
