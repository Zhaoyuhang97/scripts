import sys
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QDialog, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# 设置 matplotlib 支持中文字体
matplotlib.rcParams['font.family'] = 'SimHei'  # 使用黑体
matplotlib.rcParams['font.size'] = 10


class LineChartDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("折线图示例")
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 创建 Figure 对象和轴对象
        self.figure, self.ax = plt.subplots()

        # 创建 FigureCanvas 对象，用于在 PyQt 中显示图表
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # 绘制折线图
        self.plot()

    def plot(self):
        # 清除之前的图形
        self.ax.clear()

        # 绘制折线图
        x = [1, 2, 3, 4, 5]
        y = [2, 3, 5, 7, 11]
        self.ax.plot(x, y)

        # 设置标题和标签
        self.ax.set_title("简单折线图")
        self.ax.set_xlabel("X轴")
        self.ax.set_ylabel("Y轴")

        # 重新绘制
        self.canvas.draw()
