from PyQt5.QtCore import QThread, pyqtSignal

import time


class TestWorkerThread(QThread):
    """工作线程，用于模拟耗时任务并更新进度条"""
    progress_signal = pyqtSignal(int)  # 用于发送进度信号

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.args = args  # 总步数
        self.kwargs = kwargs  # 每步的延迟时间

    def run(self, *args, **kwargs):
        data = self.kwargs['data']
        for i, da in enumerate(data):
            self.progress_signal.emit(int(100 * i / len(data)))  # 发送进度信号
            time.sleep(0.02)  # 模拟耗时操作
