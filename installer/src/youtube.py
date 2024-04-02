# coding: utf-8
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
import asyncio
import functools
import os
import logging
import pickle
import time
import requests
import pyperclip
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException,
                                        UnexpectedAlertPresentException,
                                        NoAlertPresentException,
                                        WebDriverException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from webdriver_manager.chrome import ChromeDriverManager


# 自作モジュール
from logger.debug_logger import Logger
from auto_login.getCookie import GetCookie
from driverLogin import AutoLogin
from driverBase import Base
from errorNotify import ErrorDiscord


load_dotenv()
# logging.basicConfig(level=logging.INFO)

# ----------------------------------------------------------------------------------


# メインメソッド
#* ログインした状態でwebdriver起動
# →Youtubeにアクセス
# →コメントにアクセス
# →コピペ
# →コメントボタンクリック


# ----------------------------------------------------------------------------------
# 使うベースクラス

class SiteLogin(AutoLogin):
    def __init__(self, chrome, debug_mode=False):
        super().__init__(chrome, debug_mode)


    def open_site(self, **kwargs):
        # kwargs['by_pattern'] = 'By.XPATH'
        return super().open_site(**kwargs)


    def save_cookies(self, **kwargs):
        return super().save_cookies(**kwargs)


    def _get_full_path(self, **kwargs):
        return super()._get_full_path(**kwargs)


    def _save_cookies_to_text_file(self, **kwargs):
        return super()._save_cookies_to_text_file(**kwargs)


    def _save_cookies_to_pickle_file(self, **kwargs):
        return super()._save_cookies_to_pickle_file(**kwargs)



# ----------------------------------------------------------------------------------


class SiteProgram(Base):
    def __init__(self, chrome, discord_url, screenshot_dir, debug_mode=False):
        super().__init__(chrome, discord_url, screenshot_dir, debug_mode)


    def input_write(self, **kwargs):
        return super().input_write(**kwargs)


    def btn_click(self, **kwargs):
        return super().btn_click(**kwargs)


    def _display_none_unlock(self):
        return super()._display_none_unlock()


    def _handle_wait_loadpage(self):
        return super()._handle_wait_loadpage()


    def _handle_wait_next_page(self, xpath):
        return super()._handle_wait_next_page(xpath)


# ----------------------------------------------------------------------------------
# インスタンス化する

class Main:
    def __init__(self, debug_mode=False):
        # 引数渡す
        self.userid_path = ""
        self.comment_input = ""

        # スクショに必要な引数
        discord_url = os.getenv('DISCORD_BOT_URL')
        screenshot_dir = os.getenv('SCREENSHOT_DIR')

        # インスタンス化
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.chrome = self.setup_chrome()
        print(self.chrome)


        # インスタンス化
        self.auto_login = SiteLogin(chrome=self.chrome)
        self.driver_base = SiteProgram(chrome=self.chrome, discord_url=discord_url, screenshot_dir=screenshot_dir)


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# # Chromeセットアップ（動かす箇所にしか配置しない）(要初期化)

    def setup_chrome(self):
        try:
            chrome_options = Options()
            # chrome_options.add_argument("--headless")  # ヘッドレスモードで実行

            chrome_options.add_argument("--window-size=1200,1000")  # ウィンドウサイズの指定

            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            # chrome_options.add_argument("--user-data-dir=/Users/nyanyacyan/Library/Application Support/Google/Chrome/")
            # chrome_options.add_argument("--profile-directory=Profile 5")
            chrome_options.add_extension('data/uBlock-Origin.crx')  # iframe対策の広告ブロッカー
            chrome_options.add_extension('data/hlifkpholllijblknnmbfagnkjneagid.crx')


            service = Service(ChromeDriverManager().install())
            # service.log_path = '/Users/nyanyacyan/Desktop/ProgramFile/project_file/tiktok_project/chromedriver.log'  # ログファイルのパス

            print("ChromeDriverのインスタンス化を開始...")
            chrome = webdriver.Chrome(service=service, options=chrome_options)
            print("ChromeDriverのインスタンス化に成功しました。")

            # result = subprocess.run([service, '--version'], capture_output=True, text=True)
            # print(result.stdout)
            print(f"chrome: {chrome}")
            return chrome

        except WebDriverException as e:
            self.logger.error(f"webdriverでのエラーが発生: {e}")

        except Exception as e:
            self.logger.error(f"インスタンス化に失敗: {e}")


# ----------------------------------------------------------------------------------


    def main(self):
        # サイトへアクセス
        self.auto_login.open_site(
            # chrome=self.chrome,
            url=os.getenv("LOGIN_URL"),
            by_pattern='by.XPATH',
            userid_path=self.userid_path  # そのサイトへ移動できてるかの確認
        )

        # display:noneを解除
        self.driver_base._display_none_unlock()

        # コメントへのアクセスから書き込み
        self.driver_base.input_write(
            xpath=self.comment_input,
            input_value=os.getenv("COMMENT_1"),
            field_name="site_comment"
        )


# ----------------------------------------------------------------------------------

if __name__ == '__main__':
    main_inst = Main()
    main_inst.main()
