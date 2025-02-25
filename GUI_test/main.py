from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from db import init_db

import sqlite3


class KnowledgeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('知识库 - 2025版')
        self.setGeometry(300, 200, 800, 600)
        self.setup_ui()
        self.apply_styles()
        self.load_data()
        self.btn_add.clicked.connect(self.add_article)
        self.btn_edit.clicked.connect(self.edit_article)
        self.btn_delete.clicked.connect(self.delete_article)
        self.table.doubleClicked.connect(self.show_article_detail)

    def setup_ui(self):
        # 搜索区域
        self.search_input = QLineEdit(placeholderText="🔍 输入关键词搜索...")
        self.search_input.textChanged.connect(self.search_articles)

        # 数据表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['ID', '标题', '创建时间'])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 操作按钮
        self.btn_add = QPushButton('新建知识')
        self.btn_edit = QPushButton('编辑条目')
        self.btn_delete = QPushButton('删除条目')
        # 按钮信号连接...

        # 布局管理
        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.btn_add)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.table)
        footer_layout = QHBoxLayout()
        footer_layout.addWidget(self.btn_edit)
        footer_layout.addWidget(self.btn_delete)
        main_layout.addLayout(footer_layout)
        self.setLayout(main_layout)

    def apply_styles(self):
        self.setStyleSheet('''
            QWidget {
                background-color: #f5f7fb;
                font-family: "Segoe UI";
            }
            QTableWidget {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #4f46e5;
                color: white;
                padding: 12px;
            }
            QPushButton {
                background-color: #4f46e5;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QLineEdit {
                border: 2px solid #e0e7ff;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }
        ''')

    # 数据库操作装饰器
    def db_operation(func):
        def wrapper(self, *args, **kwargs):
            with sqlite3.connect('knowledge.db') as conn:
                cursor = conn.cursor()
                try:
                    return func(self, cursor, *args, **kwargs)
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"数据库操作失败: {str(e)}")
                finally:
                    conn.commit()

        return wrapper

    @db_operation
    def add_article(self, *args, **kwargs):
        self._add_article(*args, **kwargs)

    def _add_article(self, cursor, ok):
        print(ok)
        title, ok = QInputDialog.getText(self, '新建知识', '请输入标题:')
        if ok and title:
            content, ok = QInputDialog.getMultiLineText(self, '内容输入', '详细内容:')
            if ok:
                cursor.execute('INSERT INTO articles (title, content) VALUES (?, ?)', (title, content))
                self._load_data(cursor=cursor)

    @db_operation
    def delete_article(self, *args, **kwargs):
        self._delete_article(*args, **kwargs)

    def _delete_article(self, cursor, ok):
        selected = self.table.selectedItems()
        if selected:
            article_ids = set([(self.table.item(i.row(), 0).text()) for i in selected])
            # article_id = self.table.item(selected.row(), 0).text()
            cursor.execute(f'''DELETE FROM articles WHERE id in ({','.join("?" * len(article_ids))})''',
                           tuple(article_ids))
            cursor.execute(f'''select 1 from articles''')
            self._load_data(cursor=cursor)

    @db_operation
    def load_data(self, *args, **kwargs):
        self._load_data(*args, **kwargs)

    def _load_data(self, cursor=None, search_key=None):
        """动态加载数据并支持搜索过滤"""
        query = '''SELECT id, title, strftime('%Y-%m-%d', created_at) FROM articles'''
        params = ()
        if search_key:
            query += " WHERE title LIKE ? OR content LIKE ?"
            params = (f'%{search_key}%', f'%{search_key}%')

        cursor.execute(query, params)
        data = cursor.fetchall()

        self.table.setRowCount(len(data))
        for row, (art_id, title, date) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(str(art_id)))
            self.table.setItem(row, 1, QTableWidgetItem(title))
            self.table.setItem(row, 2, QTableWidgetItem(date))
            # 设置不可编辑
            self.table.item(row, 0).setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)

    # 搜索功能
    def search_articles(self):
        """实时搜索优化（防抖处理）"""
        search_text = self.search_input.text()
        self.load_data(search_key=search_text)

    # 编辑功能
    @db_operation
    def edit_article(self, cursor, ok):
        """智能编辑对话框"""
        selected = self.table.currentRow()
        if selected >= 0:
            art_id = self.table.item(selected, 0).text()
            cursor.execute("SELECT title,content FROM articles WHERE id=?", (art_id,))
            title, content = cursor.fetchone()

            # 自定义编辑对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("知识编辑器")
            dialog.setFixedSize(600, 400)

            # 使用QTextEdit支持Markdown格式（2025新特性）
            title_edit = QLineEdit(title)
            content_edit = QTextEdit()
            content_edit.setMarkdown(content)

            # 布局与样式
            dialog.setStyleSheet(self.styleSheet())
            layout = QVBoxLayout()
            layout.addWidget(QLabel("标题:"))
            layout.addWidget(title_edit)
            layout.addWidget(QLabel("内容（支持Markdown）:"))
            layout.addWidget(content_edit)

            btn_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
            btn_box.accepted.connect(dialog.accept)
            btn_box.rejected.connect(dialog.reject)
            layout.addWidget(btn_box)

            dialog.setLayout(layout)
            if dialog.exec_() == QDialog.Accepted:
                cursor.execute('''UPDATE articles SET title=?, content=? WHERE id=?''',
                               (title_edit.text(), content_edit.toMarkdown(), art_id))
                self._load_data(cursor=cursor)

    # 详情查看
    def show_article_detail(self):
        """响应式详情展示"""
        row = self.table.currentRow()
        if row >= 0:
            art_id = self.table.item(row, 0).text()
            with sqlite3.connect('knowledge.db') as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT content FROM articles WHERE id=?", (art_id,))
                content = cursor.fetchone()

                # 使用QWebEngineView展示富文本（需额外导入）
                preview = QDialog(self)
                preview.setWindowTitle("知识详情")
                preview.resize(800, 600)

                webview = QTextBrowser()
                webview.setHtml(f"<div style='padding:2em;max-width:800px;margin:0 auto'>{''.join(content)}</div>")

                layout = QVBoxLayout()
                layout.addWidget(webview)
                preview.setLayout(layout)
                preview.exec_()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    init_db()
    window = KnowledgeApp()
    window.show()
    sys.exit(app.exec_())
