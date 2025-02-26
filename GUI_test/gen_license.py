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

    def __init__(self, key=None, iv=None):
        self.key = key
        self.iv = iv

    def generate_license(self, expire_date):
        """生成License"""
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        data = f"expire_date={expire_date}".encode("utf-8")
        padded_data = self._pad(data)
        encrypted_data = cipher.encrypt(padded_data)
        return b64encode(encrypted_data).decode("utf-8")

    def validate_license(self, license_str):
        """校验License"""
        try:
            encrypted_data = b64decode(license_str)
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            decrypted_data = cipher.decrypt(encrypted_data)
            unpadded_data = self._unpad(decrypted_data)
            data = unpadded_data.decode("utf-8")
            expire_date_str = data.split("=")[1]
            expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d")
            return expire_date > datetime.now()
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


if __name__ == "__main__":
    # 初始化License管理器
    v = b'adminadminadmina'
    license_manager = LicenseManager(key=v, iv=b'adminadminadmina')
    # 模拟生成一个License（实际使用时应保存密钥和偏移量）
    expire_date = "2026-12-31"
    license_str = license_manager.generate_license(expire_date)
    print(f"Generated License: {license_str}")
