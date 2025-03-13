from pywebio.output import *
from pywebio.input import *
from pywebio.pin import put_input, put_select, put_textarea
from official_website_demo.settings import BASE_DIR
from pywebio.session import run_js
import base64


# 技术模块（Apple卡片布局）
def create_module(title, desc, specs):
    hh = ''.join([
        f'<div class="spec-item">'
        f'<div class="spec-value">{v}</div>'
        f'<div class="spec-label">{l}</div>'
        f'</div>'
        for v, l in specs
    ])
    return put_html(f"""
                <div class="tech-module">
                    <div class="tech-card">
                        <h2 class="tech-title">{title}</h2>
                        <p class="tech-desc">{desc}</p>
                        {("<div class='spec-list'>" + hh + "</div>") if specs else ''}
                    </div>
                </div>
                """)


def service_page():
    scope = 'main_content'
    # icon1 = base64.b64encode(
    #     open((BASE_DIR / 'staticfiles' / 'icon' / 'customer-feedback.png').as_posix(), 'rb').read()).decode()
    with use_scope(scope, clear=True):
        put_html(
            """
            <style>
            /* Apple卡片规范 */
                    .tech-module {
                        width: 100%;
                        margin: 40px auto;
                        padding: 0 10px;
                        height: 330px;
                    }
    
                    .tech-card {
                        border-radius: 18px;
                        background: var(--gray-light);
                        background-color: #fff;
                        padding: 20px;
                        margin: 10px 0;
                        height: 100%;
                        transition: transform 0.32s var(--easing),
                                    box-shadow 0.32s var(--easing);
                    }
    
                    .tech-card:hover {
                        transform: scale(1.008);
                        box-shadow: 0 8px 30px rgba(0,0,0,0.04);
                    }
    
                    .tech-title {
                        font-family: 'SF Pro Display';
                        font-size: 40px;
                        line-height: 1.1;
                        font-weight: 700;
                        letter-spacing: -0.015em;
                        border: none !important;
                    }

                    .tech-desc {
                        font-size: 15px;
                        line-height: 1.41667;
                        color: var(--gray-dark);
                        margin-bottom: 1.2em;
                    }
    
                    /* Apple规范列表 */
                    .spec-list {
                        display: grid;
                        grid-template-columns: repeat(3,1fr);
                        gap: 40px;
                    }
    
                    .spec-item {
                        border-left: 1px solid rgba(0,0,0,0.1);
                        padding-left: 10px;
                    }
    
                    .spec-value {
                        font-size: 18px;
                        font-weight: 600;
                        letter-spacing: -0.003em;
                        margin-bottom: 0.4em;
                    }
    
                    .spec-label {
                        font-size: 17px;
                        color: var(--gray-dark);
                    }
            </style>
            """
        )
        # 自动驾驶模块
        put_row([put_text('专业呵护,维修保养').style("font-size: 3rem; font-weight: 400;")], size='1fr'),
        put_row(
            [
                create_module(
                    "维修服务",
                    "针对车辆出现的故障，提供专业的诊断和维修服务，使用原厂配件，确保维修质量。",
                    [],
                ),
                create_module(
                    "零部件更换",
                    "提供原厂零部件更换服务，包括刹车片、轮胎、电池等常见零部件的更换。",
                    []
                ),
                create_module(
                    "常规保养",
                    "包括机油更换、空气滤清器更换、车辆检查等基础保养项目。建议每5000公里或6个月进行一次。",
                    []
                ),
                create_module(
                    "深度保养",
                    "包括常规保养项目，以及刹车系统、传动系统、电气系统等深度检查和维护。建议每10000公里或12个月进行一次",
                    []
                ),
            ], size='1fr 1fr 1fr 1fr'
        )
        put_row([put_text('全天候守护,道路救援').style("font-size: 3rem; font-weight: 400;margin-top: 10vh;")], size='1fr'),
        put_row(
            [
                create_module(
                    "及时响应",
                    "无论您在何时何地遇到车辆故障，我们的道路救援团队将迅速响应，提供拖车、换胎、送油、充电等紧急救援服务，确保您和您的车辆安全无虞。",
                    [],
                ),
                create_module(
                    "拨打救援电话",
                    "救援热线：400-123-4567",
                    []
                ),
                create_module(
                    "定位车辆位置",
                    "通过车辆定位系统或您提供的位置信息，快速锁定您的位置。",
                    []
                ),
                create_module(
                    "救援团队出发",
                    "救援团队在接到请求后，将在最短时间内出发前往您的位置",
                    []
                ),
                create_module(
                    "现场救援服务",
                    "到达现场后，救援人员将迅速进行故障诊断，并提供相应的救援服务。",
                    []
                ),
                create_module(
                    "后续跟进服务",
                    "救援完成后，我们将继续跟进您的车辆情况，确保问题得到彻底解决。",
                    []
                ),
            ], size='1fr 1fr 1fr 1fr 1fr 1fr'
        )

        #
        # # 客户反馈
        # put_row([
        #     None,
        #     put_column([
        #         put_image(open(r'C:\Users\yidatec\Downloads\customer-feedback.png', 'rb').read()).style('width:100%; max-width:500px;'),
        #         put_text('倾听心声：客户反馈').style('font-size:24px; font-weight:bold; margin-top:20px;'),
        #         put_text(
        #             '您的满意是我们不断前进的动力。我们诚挚邀请您分享使用我们的服务及售后体验，您的反馈将帮助我们改进和完善服务。').style(
        #             'margin-top:15px; line-height:1.6;'),
        #         # 反馈表单
        #         put_row([
        #             put_input(name='feedback_name', label='姓名', placeholder='请输入您的姓名'),
        #             put_input(name='feedback_phone', label='联系方式', placeholder='请输入您的联系方式', type=TEXT)
        #         ]),
        #         put_textarea(name='feedback_content', label='反馈内容', placeholder='请输入您的反馈内容'),
        #         put_button('提交反馈', onclick=lambda: toast('感谢您的反馈！我们将认真对待您的意见。'))
        #     ]).style('padding:50px 0;'),
        #     None
        # ], size='1 10 1')
