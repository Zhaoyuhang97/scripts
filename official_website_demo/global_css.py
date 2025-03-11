# 公共CSS样式
global_css = """
<style>

    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    }

    a {
        text-decoration: none; /* 去掉默认的下划线 */
        color: inherit; /* 保持与父元素相同的颜色 */
    }

    a:hover {
        text-decoration: none; /* 鼠标悬浮时也不显示下划线 */
        color: inherit; /* 保持与父元素相同的颜色 */
    }

    nav {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        position: fixed;
        width: 100%;
        top: 0;
        z-index: 1000;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .nav-content {
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .hero-section {
        height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        text-align: center;
        padding: 2rem;
        background: #000;
        color: white;
    }

    .model-card {
        transition: transform 0.3s;
        cursor: pointer;
    }

    .model-card:hover {
        transform: scale(1.05);
    }

</style>
"""

global_css += """
<style>
    body {
        background: #f5f5f7 !important;
    }
    .container {
        max-width: 80%;
    }
</style>
"""
