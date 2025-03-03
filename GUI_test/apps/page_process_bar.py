from PyQt5.QtWidgets import QApplication, QDialog, QProgressBar, QPushButton, QWidget, QVBoxLayout, QHBoxLayout

from .utils_process_bar import CircleProgressBar, ProgressBarDialog
from .task_work_thread import TestWorkerThread


class LoadingQDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("loading...")
        self.resize(400, 300)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # 进度条
        self.top_bar = QHBoxLayout()
        self.progress_circle = CircleProgressBar(self)
        self.progress_circle.setFixedHeight(80)
        self.top_bar.addWidget(self.progress_circle)

        # 添加弹性空间，占1个单元
        self.layout.addStretch(1)
        # 按钮
        self.bar = QHBoxLayout()

        self.button_1 = QPushButton("开始转动", self)
        # self.button_1.setGeometry(50, 100, 200, 25)
        self.button_1.clicked.connect(self.start_circle)

        self.button_2 = QPushButton("Start Loading", self)
        # self.button_2.setGeometry(50, 100, 200, 25)
        self.button_2.clicked.connect(self.start_loading)

        self.bar.addWidget(self.button_1)
        self.bar.addWidget(self.button_2)

        self.layout.addLayout(self.bar)
        # 添加弹性空间，占1个单元
        self.layout.addStretch(1)

    def start_loading(self):
        """启动任务并显示进度条"""
        self.progress_dialog = ProgressBarDialog(parent=self, worker_class=TestWorkerThread,
                                                 data=[i for i in range(100)])
        self.progress_dialog.start_progress()
        self.progress_dialog.exec_()  # 显示模态对话框

    def start_circle(self):
        if self.button_1.text() == '开始转动':
            self.progress_circle.start_animation()
            self.button_1.setText('结束')
        else:
            self.progress_circle.stop_animation()
            self.button_1.setText('开始转动')

    def closeEvent(self, event):
        self.progress_circle.stop_animation()  # 停止动画线程‌:ml-citation{ref="3,5" data="citationList"}
        event.accept()
