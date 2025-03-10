from pywebio.output import *
from pywebio.session import run_js


def footer():
    with use_scope('footer', clear=True):
        put_row([
            put_column([
                put_text("© 2023 EV Motors. All rights reserved.").style("text-align: center;color: #888"),
                put_row([
                    put_column([
                        put_link("隐私政策", "#").style("text-decoration: none; color: inherit;")
                    ]),
                    put_column([
                        put_link("使用条款", "#").style("text-decoration: none; color: inherit;")
                    ]),
                    put_column([
                        put_link("销售政策", "#").style("text-decoration: none; color: inherit;")
                    ])
                ], size="auto").style("margin-top: 1rem; display: flex; gap: 1rem; justify-content: center;")
            ], size="auto").style("max-width: 1200px; margin: 0 auto; text-align: center;color: #78c2ad")
        ]).style("background: #f5f5f7; padding: 2rem; margin-top: 4rem;")
    run_js('''document.querySelector('.footer').style.display = 'none';''')
