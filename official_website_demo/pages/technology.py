from pywebio.output import *
from official_website_demo.settings import BASE_DIR

image = BASE_DIR / 'staticfiles' / 'image'


def technology_page():
    scope = 'main_content'
    clear(scope)
    with use_scope(scope):
        style = """
            <style>
                @import url('https://cdn.jsdelivr.net/npm/@apple-oss/sf-font@1.0.0/sf-font.css');

                :root {
                    --black: #1D1D1F;
                    --gray-dark: #86868B;
                    --gray-light: #F5F5F7;
                    --blue: #0071E3;
                    --easing: cubic-bezier(0.28,0.11,0.32,1);
                }

                body {
                    font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont;
                    font-weight: 400;
                    line-height: 1.47059;
                    color: var(--black);
                    background: white;
                    -webkit-font-smoothing: antialiased;
                }

                /* Apple标准导航栏 */
                .nav-container {
                    height: 48px;
                    padding: 0 22px;
                    backdrop-filter: saturate(180%) blur(20px);
                    background: rgba(255,255,255,0.8);
                    border-bottom: 1px solid rgba(0,0,0,0.16);
                    position: fixed;
                    top:0;
                    width: 100%;
                    z-index: 9999;
                }

                .nav-content {
                    max-width: 1024px;
                    margin: 0 auto;
                    display: flex;
                    align-items: center;
                    height: 100%;
                }

                .nav-link {
                    font-size: 12px;
                    font-weight: 400;
                    letter-spacing: -0.01em;
                    padding: 0 10px;
                    transition: opacity 0.3s var(--easing);
                }

                /* Apple卡片规范 */
                .tech-module {
                    max-width: 80%;
                    margin: 80px auto;
                    padding: 0 22px;
                }

                .tech-card {
                    border-radius: 18px;
                    background: var(--gray-light);
                    background-color: #fff;
                    padding: 60px;
                    margin: 20px 0;
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
                    margin-bottom: 0.8em;
                }

                .tech-desc {
                    font-size: 24px;
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
                    padding-left: 20px;
                }

                .spec-value {
                    font-size: 28px;
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

        put_html(style)

        # 首屏内容（Apple式留白）
        with use_scope('hero', clear=True):
            put_row([
                put_column([
                    put_text("自动驾驶系统").style("font-size: 4rem; margin-bottom: 1rem;"),
                    put_text("由Apple Silicon芯片驱动的新一代智能驾驶平台，实现自然流畅的人车互动体验。").style("font-size: 1.5rem; margin-bottom: 2rem;"),
                ], size="1fr")
            ], size="1fr").style(
                "height: 30vh; display: flex; align-items: center; justify-content: center; flex-direction: column; text-align: left; padding: 2rem; background: #f5f5f7; color: #000;border-radius: 30px;font-weight: 600;max-width: 80%;")

        # 技术模块（Apple卡片布局）
        def create_tech_module(title, desc, specs):
            return put_html(f"""
                <div class="tech-module">
                    <div class="tech-card">
                        <h2 class="tech-title">{title}</h2>
                        <p class="tech-desc">{desc}</p>
                        <div class="spec-list">
                            {''.join([
                f'<div class="spec-item">'
                f'<div class="spec-value">{v}</div>'
                f'<div class="spec-label">{l}</div>'
                f'</div>'
                for v, l in specs
            ])}
                        </div>
                    </div>
                </div>
                """)

        # 自动驾驶模块
        create_tech_module(
            "Vision Pro 驾驶平台",
            "基于M2 Ultra芯片的端到端解决方案，每秒处理1.5万亿次操作",
            [
                ("A17 Pro 芯片", "神经网络引擎 35TOPS"),
                ("10,000nits HDR", "全天候视觉识别"),
                ("<20ms", "紧急响应延迟")
            ]
        )

        # 动力系统模块
        create_tech_module(
            "Apple Silicon 动力总成",
            "集成碳化硅逆变器的第四代电机系统，效率达业界领先的98%",
            [
                ("150kWh", "固态电池容量"),
                ("800km", "10分钟快充续航"),
                ("0.199Cd", "风阻系数")
            ]
        )

        # 交互系统模块
        create_tech_module(
            "CarPlay 2.0 生态系统",
            "与iPhone无缝协作的智能座舱系统，支持空间音频与手势控制",
            [
                ("6K Retina", "车载显示屏"),
                ("<100ms", "语音响应延迟"),
                ("18 个扬声器", "全景声音响")
            ]
        )

        # 新增技术对比模块
        put_html("""
            <div class="tech-module">
                <div class="tech-card">
                    <h2 class="tech-title">性能基准对比</h2>
                    <div class="comparison-grid">
                        <div class="spec-item">
                            <div class="spec-value">2.5x</div>
                            <div class="spec-label">能效比提升</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-value">150TOPS</div>
                            <div class="spec-label">神经网络算力</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-value">＜5cm</div>
                            <div class="spec-label">定位精度</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-value">99.999%</div>
                            <div class="spec-label">系统可靠性</div>
                        </div>
                    </div>
                </div>
            </div>
            """)

        # 新增技术演进时间线
        put_html("""
            <div class="tech-module">
                <div class="tech-card">
                    <h2 class="tech-title">技术演进</h2>
                    <div class="timeline-node">
                        <div class="spec-value">2024</div>
                        <div class="spec-label">固态电池量产 / 5nm制程芯片</div>
                    </div>
                    <div class="timeline-node">
                        <div class="spec-value">2026</div>
                        <div class="spec-label">全栈自研操作系统 / 全气候电池</div>
                    </div>
                    <div class="timeline-node">
                        <div class="spec-value">2028</div>
                        <div class="spec-label">L5自动驾驶 / 车云一体架构</div>
                    </div>
                </div>
            </div>
            """)

        # 新增可持续性模块
        put_html("""
            <div class="tech-module">
                <div class="tech-card">
                    <span class="badge">碳中和目标</span>
                    <h2 class="tech-title">环境责任</h2>
                    <div class="spec-list">
                        <div class="spec-item">
                            <svg class="progress-ring" viewBox="0 0 100 100">
                                <circle class="progress-ring-track" cx="50" cy="50" r="45"/>
                                <circle class="progress-ring-bar" cx="50" cy="50" r="45" 
                                        stroke-dasharray="283 283"
                                        stroke-dashoffset="113"/>
                            </svg>
                            <div>
                                <div class="spec-value">60%</div>
                                <div class="spec-label">再生铝使用率</div>
                            </div>
                        </div>
                        <!-- 更多可持续指标... -->
                    </div>
                </div>
            </div>
            """)
