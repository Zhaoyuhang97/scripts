import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QMessageBox, QLabel, QComboBox, QAbstractItemView, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt
import sqlite3

DB_NAME = "demo2_knowledge.db"


class DocumentManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文档管理系统")
        self.resize(800, 600)
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
        """初始化界面"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # 顶部操作栏
        self.top_bar = QHBoxLayout()
        self.add_button = QPushButton("新增文档")
        self.add_button.clicked.connect(self.show_add_dialog)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索文档...")
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.search_documents)
        self.top_bar.addWidget(self.add_button)
        self.top_bar.addWidget(self.search_input)
        self.top_bar.addWidget(self.search_button)
        self.layout.addLayout(self.top_bar)

        # 文档列表
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["序号", "文档名称", "文档类型", "创建时间", "文件位置", "操作"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.layout.addWidget(self.table)
        self.load_documents()

        # 底部分页（暂未实现分页功能）
        self.page_label = QLabel("第1页/共1页")
        self.layout.addWidget(self.page_label)

    def load_documents(self):
        """加载文档列表"""
        self.cursor.execute("SELECT * FROM documents")
        rows = self.cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                if col_idx == 0:  # 序号
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(row_idx + 1)))
                elif col_idx == 4:  # file_path，显示在第4列（索引为3）
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))
                    container = QWidget()
                    layout = QHBoxLayout(container)
                    layout.setContentsMargins(0, 0, 0, 0)

                    modify_button = QPushButton("修改")
                    modify_button.clicked.connect(lambda checked, idx=row_idx: self.show_modify_dialog(idx))

                    delete_button = QPushButton("删除")
                    delete_button.clicked.connect(lambda checked, idx=row_idx: self.delete_document(idx))

                    detail_button = QPushButton("详情")
                    detail_button.clicked.connect(lambda checked, idx=row_idx: self.show_detail_dialog(idx))

                    layout.addWidget(modify_button)
                    layout.addWidget(delete_button)
                    layout.addWidget(detail_button)
                    self.table.setCellWidget(row_idx, 5, container)  # 操作列放在第5列
                else:
                    # 确保 file_path 被正确写入表格
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def show_add_dialog(self):
        """显示新增文档对话框"""
        dialog = AddDocumentDialog(self)
        if dialog.exec_() == AddDocumentDialog.Accepted:
            name, type_, file_path = dialog.get_data()
            self.add_document(name, type_, file_path)

    def show_detail_dialog(self, row_idx):
        """显示文档详情对话框"""
        try:
            doc_id = self.table.item(row_idx, 0).text()  # 序号
            doc_name = self.table.item(row_idx, 1).text()  # 文档名称
            doc_type = self.table.item(row_idx, 2).text()  # 文档类型
            create_time = self.table.item(row_idx, 3).text()  # 创建时间
            file_path = self.table.item(row_idx, 4).text()  # file_path 在第4列（索引为3）

            dialog = DetailDocumentDialog(doc_id, doc_name, doc_type, create_time, file_path, self)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法获取文档详情：{e}")

    def show_modify_dialog(self, row_idx):
        """显示修改文档对话框"""
        dialog = ModifyDocumentDialog(self)
        dialog.set_data(self.table.item(row_idx, 1).text(), self.table.item(row_idx, 2).text())
        if dialog.exec_() == ModifyDocumentDialog.Accepted:
            new_name, new_type = dialog.get_data()
            self.modify_document(row_idx, new_name, new_type)

    def add_document(self, name, type_, file_path):
        """添加文档到数据库"""
        from datetime import datetime
        create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            INSERT INTO documents (name, type, create_time, file_path) VALUES (?, ?, ?, ?)
        """, (name, type_, create_time, file_path))
        self.conn.commit()
        self.load_documents()

    def modify_document(self, row_idx, new_name, new_type):
        """修改文档信息"""
        doc_id = self.table.item(row_idx, 0).text()
        self.cursor.execute("""
            UPDATE documents SET name = ?, type = ? WHERE id = ?
        """, (new_name, new_type, doc_id))
        self.conn.commit()
        self.load_documents()

    def delete_document(self, row_idx):
        """删除文档"""
        doc_id = self.table.item(row_idx, 0).text()
        file_path = self.table.item(row_idx, 4).text()
        reply = QMessageBox.question(self, "确认删除", "确定要删除该文档吗？")
        if reply == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            self.conn.commit()
            os.remove(file_path)  # 删除文件
            self.load_documents()

    def search_documents(self):
        """搜索文档"""
        keyword = self.search_input.text()
        self.cursor.execute("""
            SELECT * FROM documents WHERE name LIKE ? OR type LIKE ?
        """, (f"%{keyword}%", f"%{keyword}%"))
        rows = self.cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                if col_idx == 0:  # 序号
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(row_idx + 1)))
                elif col_idx == 4:  # 操作列
                    # 创建一个 QWidget 容器
                    container = QWidget()
                    layout = QHBoxLayout(container)
                    layout.setContentsMargins(0, 0, 0, 0)  # 去掉布局的边距

                    # 修改按钮
                    modify_button = QPushButton("修改")
                    modify_button.clicked.connect(lambda checked, idx=row_idx: self.show_modify_dialog(idx))

                    # 删除按钮
                    delete_button = QPushButton("删除")
                    delete_button.clicked.connect(lambda checked, idx=row_idx: self.delete_document(idx))

                    # 将按钮添加到布局中
                    layout.addWidget(modify_button)
                    layout.addWidget(delete_button)

                    # 将容器设置到单元格中
                    self.table.setCellWidget(row_idx, col_idx, container)
                else:
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

    def closeEvent(self, event):
        """关闭窗口时关闭数据库连接"""
        self.conn.close()
        event.accept()


class AddDocumentDialog(QDialog):
    """新增文档对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新增文档")
        self.layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("文档名称")
        self.type_input = QComboBox()
        self.type_input.addItems(["TXT", "PDF", "Word", "Excel"])
        self.file_input = QPushButton("选择文件")
        self.file_input.clicked.connect(self.select_file)
        self.file_path = ""

        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.type_input)
        self.layout.addWidget(self.file_input)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def select_file(self):
        """选择文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*)")
        if file_path:
            self.file_path = file_path

    def get_data(self):
        """获取对话框数据"""
        return self.name_input.text(), self.type_input.currentText(), self.file_path


class ModifyDocumentDialog(QDialog):
    """修改文档对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("修改文档")
        self.layout = QVBoxLayout(self)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("文档名称")
        self.type_input = QComboBox()
        self.type_input.addItems(["TXT", "PDF", "Word", "Excel"])

        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.type_input)

        # 查看详情按钮
        self.detail_button = QPushButton("查看详情")
        self.detail_button.clicked.connect(self.show_detail)
        self.layout.addWidget(self.detail_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def show_detail(self):
        """显示当前文档的详情"""
        # 假设当前文档的索引存储在 self.row_idx 中
        row_idx = self.parent().table.currentRow()
        self.parent().show_detail_dialog(row_idx)

    def set_data(self, name, type_):
        """设置对话框初始数据"""
        self.name_input.setText(name)
        self.type_input.setCurrentText(type_)

    def get_data(self):
        """获取对话框数据"""
        return self.name_input.text(), self.type_input.currentText()


class DetailDocumentDialog(QDialog):
    """文档详情对话框"""

    def __init__(self, doc_id, doc_name, doc_type, create_time, file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("文档详情")
        self.layout = QVBoxLayout(self)

        # 显示文档基本信息
        self.info_label = QLabel(f"""
            <h3>文档详情</h3>
            <p><b>文档ID:</b> {doc_id}</p>
            <p><b>文档名称:</b> {doc_name}</p>
            <p><b>文档类型:</b> {doc_type}</p>
            <p><b>创建时间:</b> {create_time}</p>
            <p><b>文件路径:</b> {file_path}</p>
        """)
        self.layout.addWidget(self.info_label)

        # 如果是文本文件，显示内容
        if doc_type.lower() in ["txt"]:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                self.content_label = QLabel(f"<h4>文档内容：</h4><pre>{content}</pre>")
                self.content_label.setWordWrap(True)
                self.layout.addWidget(self.content_label)
            except Exception as e:
                self.error_label = QLabel(f"<p style='color:red'>无法读取文件内容：{e}</p>")
                self.layout.addWidget(self.error_label)

        # 按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Close)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DocumentManager()
    window.show()
    sys.exit(app.exec_())
