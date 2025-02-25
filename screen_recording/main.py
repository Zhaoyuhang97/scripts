from screeninfo import get_monitors
import pyautogui
import imageio
import numpy as np
import time

# 设置录制参数
fps = 10  # 帧率
duration = 3  # 录制时长（秒）
output_file = "screen_recording.mp4"  # 输出文件名

# 获取屏幕分辨率
screen_width, screen_height = pyautogui.size()


# 获取所有显示器的信息
monitors = get_monitors()

for monitor in monitors:
    print(f"Monitor: {monitor.name}")
    print(f"  Width: {monitor.width}")
    print(f"  Height: {monitor.height}")
    print(f"  X: {monitor.x}")
    print(f"  Y: {monitor.y}")
screen_no = 0
screen_region = (monitors[screen_no].x, monitors[screen_no].y, monitors[screen_no].width, monitors[screen_no].height)
# 初始化视频写入器
with imageio.get_writer(output_file, fps=fps) as writer:
    for _ in range(fps * duration):
        # 截取屏幕
        frame = pyautogui.screenshot(region=screen_region)
        # 将截图转换为 NumPy 数组
        frame = np.array(frame)
        # 写入帧
        writer.append_data(frame)

print(f"录制完成，视频已保存到 {output_file}")
