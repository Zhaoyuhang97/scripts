import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox, QDialog, QLineEdit
)
from PyQt5.QtCore import Qt
from datetime import datetime
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os


class LicenseManager:
    """管理License的生成和校验"""

    def __init__(self, key=b'adminadminadmina', iv=b'adminadminadmina'):
        self.key = key
        self.iv = iv

    def generate_license(self, expire_date):
        """生成License"""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        data = f"expire_date={expire_date}".encode("utf-8")
        padded_data = self._pad(data)
        encrypted_data = cipher.encrypt(padded_data)
        return b64encode(encrypted_data).decode("utf-8")

    def validate_license(self, license_str=None):
        """校验License"""
        try:
            if license_str is None:
                if os.path.exists('secret.key'):
                    with open('secret.key', 'r') as f:
                        license_str = f.readline()
                else:
                    return False
            encrypted_data = b64decode(license_str)
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            decrypted_data = cipher.decrypt(encrypted_data)
            unpadded_data = self._unpad(decrypted_data)
            data = unpadded_data.decode("utf-8")
            expire_date_str = data.split("=")[1]
            expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d")
            return expire_date
        except Exception as e:
            print(f"License validation error: {e}")
            return False

    @staticmethod
    def _pad(data):
        """PKCS7填充"""
        padding_len = 16 - (len(data) % 16)
        padding = bytes([padding_len] * padding_len)
        return data + padding

    @staticmethod
    def _unpad(data):
        """去除PKCS7填充"""
        padding_len = data[-1]
        return data[:-padding_len]


class LicenseDialog(QDialog):
    """License校验对话框"""

    def __init__(self, license_manager, parent=None, key_path=None):
        super().__init__(parent)
        self.resize(300, 100)
        self.setWindowTitle("License校验")
        self.layout = QVBoxLayout(self)

        self.label = QLabel("请输入License：")
        self.layout.addWidget(self.label)

        self.license_input = QLineEdit()
        self.layout.addWidget(self.license_input)

        self.validate_button = QPushButton("校验")
        self.license_manager = license_manager
        self.validate_button.clicked.connect(lambda: self.validate_license())
        self.layout.addWidget(self.validate_button)

    def validate_license(self):
        """校验License"""
        license_str = self.license_input.text()
        expire_date = self._validate_license(license_str)
        if expire_date == 0:
            QMessageBox.critical(self, "校验失败", "License无效！")
        elif expire_date == 2:
            QMessageBox.critical(self, "校验失败", "License已过期！")
        else:
            QMessageBox.information(self, "校验成功", f"License有效期至{expire_date.strftime('%Y-%m-%d')}")
            self.accept()


    def _validate_license(self, license_str: str):
        if expire_date := self.license_manager.validate_license(license_str):
            if expire_date > datetime.now():
                with open(r'secret.key', 'w') as f:
                    f.write(license_str)
                return expire_date
            else:
                return 2
        else:
            return 0


class ValidationWindow(QMainWindow):
    """主窗口"""

    def __init__(self, license_manager):
        super().__init__()
        self.license_manager = license_manager
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel("欢迎使用文档管理系统！")
        self.layout.addWidget(self.label)

        self.doc_manager_button = QPushButton("进入文档管理")
        self.doc_manager_button.clicked.connect(self.open_document_manager)
        self.layout.addWidget(self.doc_manager_button)

    def open_document_manager(self):
        """打开文档管理系统"""
        # 在这里可以初始化你的文档管理系统
        QMessageBox.information(self, "提示", "文档管理系统已启动！")

    def check_license(self):
        """校验License"""
        license_dialog = LicenseDialog(self.license_manager, self)
        if license_dialog.exec_() == QDialog.Accepted:
            return True
        else:
            return False


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 初始化License管理器
    license_manager = LicenseManager()

    # 模拟生成一个License（实际使用时应保存密钥和偏移量）
    expire_date = "2026-12-31"
    license_str = license_manager.generate_license(expire_date)
    print(f"Generated License: {license_str}")

    # 启动主窗口
    window = ValidationWindow(license_manager)
    window.check_license()
    sys.exit(app.exec_())
