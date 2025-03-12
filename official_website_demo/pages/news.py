from pywebio.output import *
from official_website_demo.settings import BASE_DIR

image = BASE_DIR / 'staticfiles' / 'image'


def news_page():
    scope = 'main_content'
    clear(scope)
    with use_scope(scope):
        style = """
            :root {
                --apple-dark: #1d1d1f;
                --apple-blue: #0071e3;
                --timeline-width: 4px;
            }
            body { background: #fafafa; }
            .apple-nav {
                background: var(--apple-dark); 
                padding: 1rem 10%;
                position: sticky;
                top:0;
                z-index: 1000;
            }
            .hero-carousel {
                height: 50vh;
                width: 70%;
                margin: 2rem auto;
                overflow: hidden;
                position: relative;
                border-radius: 18px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }
            .carousel-slide {
                position: absolute;
                width: 100%;
                height: 100%;
                opacity: 0;
                transition: opacity 1s ease;
            }
            .carousel-active { opacity: 1; }
            .carousel-slide img {
                width: 100%;
                height: 100%;
                object-fit: cover;
                object-position: center;
            }
            .slide-content {
                position: absolute;
                left: 50%;
                transform: translateX(-50%);
                bottom: 1%;
                text-align: center;
                background: rgba(0, 0, 0, 0.8);
                padding: 1.5rem 3rem;
                border-radius: 12px;
                max-width: 800px;
                width: 60%;
            }
           
            .timeline {
                position: relative;
                padding: 0 2rem 5% 2rem;
            }
            .timeline::before {
                content: '';
                position: absolute;
                left: 50%;
                transform: translateX(-50%);
                width: var(--timeline-width);
                height: 100%;
                background: var(--apple-blue);
            }

            /* 基础项样式 */
            .timeline-item {
                display: flex;
                margin: 4rem 0;
                width: 50%;
                position: relative;
            }

            /* 奇数项（左侧） */
            .timeline-item:nth-child(odd) {
                left: 0;
                flex-direction: row;
                justify-content: flex-start;
            }
            .timeline-item:nth-child(odd) .timeline-content {
                margin-right: 1rem;
            }
            .timeline-item:nth-child(odd) .timeline-content::before {
                right: -30px;
                left: auto;
            }

            /* 偶数项（右侧） */
            .timeline-item:nth-child(even) {
                left: 49%;
                flex-direction: row-reverse;
                justify-content: flex-end;
            }
            .timeline-item:nth-child(even) .timeline-content {
                margin-right: 2rem;
                right: -3%;
            }
            .timeline-item:nth-child(even) .timeline-content::before {
                left: -16px;
            }
            
            /* 左侧日期定位 */
            .timeline-item:nth-child(odd) .timeline-date {
                transform: translateX(30px); /* 调整日期与圆圈的间距 */
            }
            
            /* 右侧日期定位 */
            .timeline-item:nth-child(even) .timeline-date {
                transform: translateX(-30px);
            }

            .timeline-date {
                width: 120px;
                padding: 1rem 2rem 1rem 1rem;
                font-weight: bold;
                color: var(--apple-blue);
                text-align: center;
            }
            
            .timeline-content {
                width: calc(100% - 140px);
                background: white;
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                position: relative;
            }
            .timeline-content::before {
                content: '';
                position: absolute;
                top: 24px;
                width: 20px;
                height: 20px;
                background: var(--apple-blue);
                border-radius: 50%;
            }
            """

        put_html(f"<style>{style}</style>")

        # 轮播图
        put_html("""
            <div class="hero-carousel">
                <div class="carousel-slide carousel-active">
                    <img src="https://img1.baidu.com/it/u=570677140,1778679078&fm=253&fmt=auto&app=120&f=JPEG?w=1422&h=800">
                    <div class="slide-content">
                        <h2 style="color:white;margin:0 0 1rem">全新智能电动平台发布</h2>
                        <p style="color:rgba(255,255,255,0.9);line-height:1.4">集成新一代电池技术与自动驾驶系统</p>
                    </div>
                </div>
                <div class="carousel-slide">
                    <img src="https://img2.baidu.com/it/u=3465534984,1044890142&fm=253&fmt=auto&app=138&f=JPEG?w=981&h=500">
                    <div class="slide-content">
                        <h2 style="color:white;margin:0 0 1rem">品牌成立10周年庆典</h2>
                        <p style="color:rgba(255,255,255,0.9);line-height:1.4">回顾创新历程，展望未来愿景</p>
                    </div>
                </div>
            </div>
            """)

        # 时间轴新闻
        with use_scope('timeline', clear=True):
            timeline_data = [
                {'date': '2024.03', 'title': '日内瓦车展全球首发',
                 'content': '全新概念车首次公开亮相', 'image': 'https://img1.baidu.com/it/u=168329613,3765512422&fm=253&fmt=auto&app=120&f=JPEG?w=889&h=500'},
                {'date': '2024.02', 'title': '电池技术突破',
                 'content': '发布新一代固态电池技术，充电速度提升40%', 'image': 'https://img0.baidu.com/it/u=1360493130,1455459260&fm=253&fmt=auto&app=120&f=JPEG?w=607&h=291'},
                {'date': '2024.01', 'title': '年度销量冠军',
                 'content': '2023年全球电动汽车销量突破百万', 'image': 'https://img0.baidu.com/it/u=1801300892,994619241&fm=253&fmt=auto&app=120&f=JPEG?w=636&h=500'}
            ]

            timeline_html = '<div class="timeline">'
            for item in timeline_data:
                timeline_html += f"""
                    <div class="timeline-item">
                        <div class="timeline-date">{item['date']}</div>
                        <div class="timeline-content">
                            <img src="{item['image']}" style="width:100%;height:200px;object-fit:cover;border-radius:8px">
                            <h3>{item['title']}</h3>
                            <p>{item['content']}</p>
                        </div>
                    </div>
                    """
            timeline_html += '</div>'
            put_html(timeline_html)

        # 轮播自动切换脚本
        put_html("""
            <script>
            let currentSlide = 0;
            const slides = document.querySelectorAll('.carousel-slide');

            setInterval(() => {
                slides[currentSlide].classList.remove('carousel-active');
                currentSlide = (currentSlide + 1) % slides.length;
                slides[currentSlide].classList.add('carousel-active');
            }, 5000);
            </script>
            """)