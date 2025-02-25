# -*- coding: utf-8 -*-
import logging
from logging import handlers
from datetime import datetime, timedelta
import shutil
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import socket

"""
1.安装driver并解压到r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'
https://googlechromelabs.github.io/chrome-for-testing/
2.添加环境变量r'C:\Program Files\Google\Chrome\Application
"""

# driver_path = r'C:\Program Files\Google\Chrome\Application\chromedriver.exe'

# 创建一个handler，用于写入日志文件
logger = logging.getLogger('spa_download')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
time_logger = handlers.TimedRotatingFileHandler(filename='spa_download.log', when='W1', backupCount=12,
                                                encoding='utf-8')
time_logger.setFormatter(formatter)
logger.addHandler(time_logger)

# TARGET_HOME = SALES_EVENT_CONFIG['TARGET_HOST']
# TARGET_URI = SALES_EVENT_CONFIG['TARGET_URI']
TARGET_URL = 'https://azc-t.procurement.sapariba.cn/'


# REPORT_NAME = SALES_EVENT_CONFIG['REPORT_NAME']
# DAYS_DATE = SALES_EVENT_CONFIG['days_date']


class EventExtra:
    def __init__(self):
        self.count = 0
        self.error_count = 10
        error_count = self.error_count
        while error_count:
            try:
                self.web_driver = self.driver_initial()
                break
            except Exception as e:
                msg = f'页面渲染失败-正在重试...{self.error_count - error_count + 1}'
                print(msg)
                logger.error(msg)
                error_count -= 1

    def wait_ele_xpath(self, bro, xpath, waitime=60):
        ele = WebDriverWait(bro, waitime).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return ele

    def wait_ele_name(self, bro, name, waitime=60):
        ele = WebDriverWait(bro, waitime).until(EC.presence_of_element_located((By.NAME, name)))
        return ele

    def wait_ele_id(self, bro, id_, waitime=60):
        ele = WebDriverWait(bro, waitime).until(EC.presence_of_element_located((By.ID, id_)))
        return ele

    def check_port(self, address, port):
        # 创建套接字对象
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 检查端口是否占用
        result = sock.connect_ex((address, port))
        # 关闭套接字
        sock.close()
        # 返回结果
        return result == 0

    def driver_initial(self):
        # chrome_options = Options()
        # prefs = {
        #     'profile.default_content_settings.popups': 0,
        # }
        # chrome_options.add_experimental_option('prefs', prefs)
        # chrome_options.add_argument('log-level=3')
        # # chrome_options.add_argument('--headless')
        # driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
        # driver.get(TARGET_URL)

        port = 9230
        if not self.check_port(address='localhost', port=port):
            # 需要把driver_path路径中chrome.exe的父级目录添加到环境变量
            cmd = f'chrome --remote-debugging-port={port} ' \
                  '--disable-gpu ' \
                  f'{TARGET_URL}'
            os.popen(cmd)

        chrome_options = Options()
        chrome_options.add_argument(f'--remote-debugging-port={port}')
        chrome_options.add_experimental_option('debuggerAddress', f'127.0.0.1:{port}')
        driver = webdriver.Chrome(
            options=chrome_options,
            # executable_path=driver_path
        )
        driver.maximize_window()
        driver.get(TARGET_URL)
        return driver

    def customer_click(self, ele, actions):
        time.sleep(1)
        try:
            ele.click()
        except Exception as e:
            actions.click(ele).perform()

    # def login(self):
    #     actions = ActionChains(self.web_driver)
    #     another_user = self.wait_ele_xpath(self.web_driver, '//*[@id="otherTileText"]')
    #     self.customer_click(another_user, actions)
    #     email_element = self.wait_ele_xpath(self.web_driver, '//*[@id="i0116"]')
    #     email_element.send_keys(USERNAME, Keys.ENTER)
    #     # pwd_element = self.wait_ele_id(self.web_driver, 'i0118')
    #     pwd_element = self.web_driver.find_element_by_id('i0118')
    #     pwd_element.send_keys(PASSWORD, Keys.ENTER)
    #     time.sleep(3)
    #     a = self.web_driver.find_element_by_xpath('//*[@id="idSIButton9"]')
    #     a.click()

    def save_report(self):
        error_count = self.error_count
        # now = datetime.now()
        # filename = rf"{PENDING_TICKETS_CONFIG['data_type']}_{now.strftime('%Y%m%d%H%M%S')}.csv"
        # save_file_path = os.path.join(TEMP_FILES_PATH, filename)
        state = True
        while error_count:
            try:
                state = True
                # 执行右键
                actions = ActionChains(self.web_driver)
                ops = self.wait_ele_xpath(self.web_driver, '//*[@id="_1eckkc"]')
                self.customer_click(ops, actions=actions)
                ops_order = self.wait_ele_xpath(self.web_driver, '//*[@id="_k3m2lb"]')
                self.customer_click(ops_order, actions=actions)
                # 输入框
                order_id_input = self.wait_ele_xpath(self.web_driver, '//*[@id="_icg$nd"]')
                time.sleep(5)
                order_id_input.send_keys('7000176259')
                # 搜索
                search = self.wait_ele_xpath(self.web_driver, '//*[@id="_4opwwd"]')
                self.customer_click(search, actions=actions)
                # 表格
                tbody = self.wait_ele_xpath(self.web_driver, '//*[@id="_3lftt"]/tbody')
                tbody_elements = tbody.find_elements_by_css_selector("tbody > tr:not(:first-child)")

                # 遍历并处理 tbody 中的 tr 元素
                for tr in tbody_elements:
                    # 你的逻辑代码
                    order_id = tr.find_element_by_xpath('td[3]/span/table/tbody/tr/td/a')
                    self.customer_click(order_id, actions=actions)
                    download_btn = self.wait_ele_xpath(self.web_driver, '/html/body/div[6]/div[2]/table/tbody/tr/td[1]/table/tbody/tr[2]/td/table/tbody/tr/td[2]/div/div/div/form/table[1]/tbody/tr[4]/td/div/div[2]/div/div/div[8]/div[2]/div/div[1]/table/tbody/tr[2]/td/table/tbody/tr[2]/td/div/table/tbody/tr[2]/td[1]/span/table/tbody/tr/td/a[2]')
                    self.customer_click(download_btn, actions=actions)
                    break
                time.sleep(5)
                self.web_driver.close()
                break
            except Exception as e:
                state = False
                msg = f'页面操作失败-正在重试...{self.error_count - error_count + 1}'
                print(msg)
                logger.error(msg)
                self.web_driver.get(TARGET_URL)
                error_count -= 1
        return state


def run(start='07:30:00', end='23:00:00'):
    now = datetime.now()
    now_str = now.strftime('%Y%m%d%H%M%S')
    now_format = now.strftime('%H:%M:%S')
    # 浏览器下载的文件路径
    save_file_path = r'C:\Users\kmsj845\Downloads\task.csv'
    new_save_file_path = rf"C:\Users\kmsj845\Downloads\pendingTickets_{now.strftime('%Y%m%d%H%M%S')}.csv"
    try:
        if end > now_format > start:
            e = EventExtra()
            state = e.save_report()
            if not state:
                raise ValueError('10次内没有导出excel')
            # os.rename(save_file_path, new_save_file_path)
            # os.remove(new_save_file_path)
            # shutil.move(save_file_path, move_file_path)
            res = 'save and move succeed.'
            msg = f"{new_save_file_path} {res}."
            print(msg)
            logger.info(msg)
    except Exception as e:
        msg = f"{now_str}:{repr(e)}."
        print(msg)
        logger.error(msg)


if __name__ == '__main__':
    run()
    # m = PENDING_TICKETS_CONFIG['run_minutes']
    # print(f'每{m}分钟开始...')
    # scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    # # ('year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second')
    # # scheduler.add_job(run, 'cron', hour=m, minute='1', misfire_grace_time=60)
    # scheduler.add_job(run, 'interval', minutes=m, misfire_grace_time=60)
    # scheduler.start()
