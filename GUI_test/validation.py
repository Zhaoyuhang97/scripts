import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox, QDialog, QLineEdit
)
from PyQt5.QtCore import Qt
from datetime import datetime
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from typing import Any
from settings import VERSION
import os


class LicenseManager:
    """管理License的生成和校验"""

    def __init__(self, key=b'adminadminadmina', iv=b'adminadminadmina'):
        self.key = key
        self.iv = iv

    def validate_license(self, license_str=None) -> dict:
        """校验License"""
        try:
            if license_str is None:
                if os.path.exists('secret.key'):
                    with open('secret.key', 'r') as f:
                        license_str = f.readline()
                else:
                    return {}
            encrypted_data = b64decode(license_str)
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            decrypted_data = cipher.decrypt(encrypted_data)
            unpadded_data = self._unpad(decrypted_data)
            data = eval(unpadded_data.decode("utf-8"))
            expire_date_str = data.get('expire_date', None)
            version = data.get('version', None)
            if datetime.strptime(expire_date_str, "%Y-%m-%d") <= datetime.now() or version != VERSION:
                return {}
            return data
        except Exception as e:
            print(f"License validation error: {e}")
            return {}

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
        decode_key, status = self._validate_license(license_str)
        if status == 0:
            QMessageBox.critical(self, "校验失败", "License无效！")
        elif status == 2:
            QMessageBox.critical(self, "校验失败", "License已过期！")
        else:
            QMessageBox.information(self, "校验成功", decode_key['title'])
            self.accept()

    def _validate_license(self, license_str: str) -> tuple[Any, int]:
        decode_key = self.license_manager.validate_license(license_str)
        expire_date_str = decode_key.get('expire_date', None)
        if expire_date_str:
            expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d")
            if expire_date > datetime.now():
                with open(r'secret.key', 'w') as f:
                    f.write(license_str)
                return decode_key, 1
            else:
                return None, 2
        else:
            return None, 0
