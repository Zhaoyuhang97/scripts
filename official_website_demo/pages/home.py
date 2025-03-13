from pywebio import start_server, config
from pywebio.output import *
from pywebio.session import run_js
from official_website_demo.settings import BASE_DIR, TOAST_ERROR_MSG


def technology_page():
    pass


def model_detail_page(a):
    pass


def show_page(page_name, model_name=None):
    clear()
    if page_name == 'models':
        home_page()
    elif page_name == 'technology':
        technology_page()
    elif page_name == 'model_detail_page' and model_name:
        model_detail_page(model_name)
    else:
        home_page()


def home_page():
    scope = 'main_content'
    models = [
        {"name": "EM7", "desc": "旗舰轿跑", "price": "¥268,000起",
         "img": open((BASE_DIR / 'media' / 'images' / '2.png').as_posix(), 'rb').read()},
        {"name": "ES5", "desc": "智能SUV", "price": "¥228,000起",
         "img": open((BASE_DIR / 'media' / 'images' / '3.png').as_posix(), 'rb').read()},
        {"name": "ET3", "desc": "城市精灵", "price": "¥168,000起",
         "img": open((BASE_DIR / 'media' / 'images' / '4.png').as_posix(), 'rb').read()},
    ]
    if not models:
        toast(TOAST_ERROR_MSG, color='error')
        return None
    with use_scope(scope, clear=True):  # 在 "main_content" 作用域中渲染内容
        put_row([
            put_column([
                put_text("未来，此刻启程").style("font-size: 4rem; margin-bottom: 1rem;"),
                put_text("体验新一代智能电动汽车").style("font-size: 1.5rem; margin-bottom: 2rem;"),
                put_button("探索车型", onclick=lambda: run_js("window.location.href = '/models';")).style(
                    "padding: 1rem 2rem; background: none; border: none; color: white;"
                    "border-radius: 20px; cursor: pointer; font-size: 1rem; transition: background 0.3s ease;"
                )
            ], size="1fr")
        ], size="1fr").style(
            "height: 60vh; display: flex; align-items: center; justify-content: center; flex-direction: column; text-align: center; padding: 2rem; background: #000; color: white;border-radius: 30px;")
        # 车型展示
        put_row([
            put_text("最新车型").style("text-align: center; margin: 4rem 0; font-size: 2rem;")
        ])

        put_grid([
            [put_column([
                put_image(model['img'], format='png', width='100%', height='100%').style(
                    f"height: 400px; object-fit: cover;transition: transform 0.3s, box-shadow 0.3s, opacity 0.3s;"),
                put_column([
                    put_text(model['name']).style("text-align: center; font-size: 1.5rem; margin-bottom: 0.5rem;"),
                    put_text(model['desc']).style("text-align: center; color: #666; margin: 0.5rem 0;"),
                    put_text(model['price']).style("text-align: center; font-weight: bold; margin-bottom: 1rem;"),
                    put_button("了解更多", onclick=lambda: run_js(f"window.location.href = '/model-detail/{model['name']}';")).style(
                        "margin-top: 1rem; border: none; color: #0071e3; padding: 0.5rem 0.5rem; border-radius: 20px; cursor: pointer;"
                    )
                ], size="auto").style("padding: 1rem;text-align: center;")
            ], size='1.3').style("border-radius: 12px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1);margin-right: 1rem;")
             for model in models]
        ], cell_width=f"{int(1 / len(models) * 100)}%")
        put_html("""
            <style>
                img:hover {
                    transform: scale(1.05);
                    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                    opacity: 0.7;
                }
            </style>
        """)
