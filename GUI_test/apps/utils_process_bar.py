import time
from PyQt5.QtWidgets import QApplication, QDialog, QProgressBar, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor


class ProgressBarDialog(QDialog):
    """进度条对话框"""

    def __init__(self, parent=None, worker_class=None, *args, **kwargs):
        super().__init__(parent)
        self.setWindowTitle("进度条")
        self.setModal(True)  # 设置为模态窗口，禁止父窗口操作

        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        layout = QVBoxLayout(self)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        # self.label = QLabel("正在处理，请稍候...", self)
        # layout.addWidget(self.label)

        self.worker = worker_class(*args, **kwargs)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished.connect(self.close)

    def start_progress(self):
        """启动进度条"""
        self.worker.start()

    def update_progress(self, value):
        """更新进度条值"""
        self.progress_bar.setValue(value)


class CircleProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.hide()

    def start_animation(self):
        """启动动画"""
        self.timer.start(20)  # 开始定时器
        self.show()
        self.update()

    def stop_animation(self):
        """停止动画"""
        self.timer.stop()
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(37, 162, 208), 4)
        painter.setPen(pen)
        # 绘制动态圆环（从顶部开始，顺时针旋转）
        painter.drawArc(20, 20, 40, 40, self.angle * 16, 270 * 16)

    def update_angle(self):
        self.angle = (self.angle + 5) % 360
        self.update()
