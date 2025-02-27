
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLabel, QDialog, QSpacerItem, QSizePolicy
)
from validation import LicenseDialog, LicenseManager
from PyQt5.QtCore import Qt
from settings import DB_NAME
from apps.knowledge import DocumentDialog
from pathlib import Path
import sqlite3
import os
import sys


class MainManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("小工具大全")
        self.resize(600, 450)
        self.init_db()
        self.init_ui()

    def init_db(self):
        """初始化数据库"""
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                create_time TEXT NOT NULL,
                file_path TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def init_ui(self):
        """初始化主页面布局"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 设置全局样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0; /* 浅灰色背景 */
            }
            QLabel {
                font-family: Arial, sans-serif;
                font-size: 24px;
                font-weight: bold;
                color: #333; /* 深灰色文字 */
            }
            QPushButton {
                font-family: Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
                background-color: #007BFF; /* 蓝色按钮 */
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #0056b3; /* 按钮悬停时变深 */
            }
            QDialog {
                background-color: white;
            }
        """)

        # 添加弹性空间，占据窗口高度的1/4
        self.layout.addStretch(1)

        # 标题
        self.title_label = QLabel("欢迎使用管理系统")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # 添加弹性空间，占1个单元
        self.layout.addStretch(1)

        # 按钮布局
        self.button_layout1 = QHBoxLayout()
        self.button_layout2 = QHBoxLayout()

        # 文档管理按钮
        self.doc_management_button = QPushButton("文档管理")
        self.doc_management_button.clicked.connect(self.open_document_management)
        self.doc_management_button.setFixedSize(200, 50)
        self.button_layout1.addWidget(self.doc_management_button)

        # 人员管理按钮
        self.staff_management_button = QPushButton("人员管理")
        self.staff_management_button.clicked.connect(self.open_staff_management)
        self.staff_management_button.setFixedSize(200, 50)
        self.button_layout1.addWidget(self.staff_management_button)

        # 信息管理按钮
        self.info_management_button = QPushButton("信息管理")
        self.info_management_button.clicked.connect(self.open_info_management)
        self.info_management_button.setFixedSize(200, 50)
        self.button_layout2.addWidget(self.info_management_button)

        # 报表生成按钮
        self.report_generation_button = QPushButton("报表生成")
        self.report_generation_button.clicked.connect(self.open_report_generation)
        self.report_generation_button.setFixedSize(200, 50)
        self.button_layout2.addWidget(self.report_generation_button)

        self.button_layout1.setAlignment(Qt.AlignCenter)
        self.button_layout2.setAlignment(Qt.AlignCenter)


        self.layout.addLayout(self.button_layout1)
        self.layout.addLayout(self.button_layout2)
        # 添加弹性空间，占2个单元
        self.layout.addStretch(1)
        # 设置布局的间距和对齐方式
        self.layout.setAlignment(Qt.AlignCenter)


    def open_document_management(self):
        """打开文档管理页面"""
        self.show_page(DocumentDialog)

    def open_staff_management(self):
        """打开人员管理页面"""
        self.show_page(DocumentDialog)

    def open_info_management(self):
        """打开信息管理页面"""
        self.show_page(DocumentDialog)

    def open_report_generation(self):
        """打开报表生成页面"""
        self.show_page(DocumentDialog)

    def show_page(self, dialog):
        """弹出对应的页面"""
        d = dialog()
        d.exec_()


if __name__ == "__main__":
    sys.path.append(Path(__file__).resolve().parent.as_posix())
    license_manager = LicenseManager()
    app = QApplication(sys.argv)
    # key
    key_path = "secret.key"
    # check license
    if not license_manager.validate_license():
        # file license valid failed
        license_dialog = LicenseDialog(license_manager, key_path=key_path)
        if license_dialog.exec_() == QDialog.Accepted:
            # input license valid success
            window = MainManager()
            window.show()
            sys.exit(app.exec_())
    else:
        # file license valid success
        window = MainManager()
        window.show()
        sys.exit(app.exec_())
