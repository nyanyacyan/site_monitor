# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/3/27更新

#! webdriverをどこが開いているのかを確認しながら実装が必要。
# ----------------------------------------------------------------------------------
import asyncio
import functools
import os
import pickle
import time
import requests
import pyperclip
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


from dotenv import load_dotenv

from selenium import webdriver
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException,
                                        UnexpectedAlertPresentException,
                                        NoAlertPresentException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

# 自作モジュール
from auto_login.solve_recaptcha import RecaptchaBreakthrough
from logger.debug_logger import Logger
from spreadsheet.read import Read
from errorNotify import ErrorDiscord


# ----------------------------------------------------------------------------------
# エラー時にdiscordにて通知

class Error(ErrorDiscord):
    def __init__(self, chrome, discord_url, screenshot_dir, debug_mode=False):
        super().__init__(chrome, discord_url, screenshot_dir, debug_mode)


# ----------------------------------------------------------------------------------
# オーバーライド

    def error_screenshot_discord(self, screenshot_title, **kwargs):
        return super().error_screenshot_discord(screenshot_title, **kwargs)


# ----------------------------------------------------------------------------------

class Base:
    def __init__(self, chrome, discord_url, screenshot_dir, debug_mode=False):
        self.chrome = chrome
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.error_discord = ErrorDiscord(chrome, discord_url, screenshot_dir)


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------

# 要素を探して入力

    def input_write(self, discord_url, screenshot_dir, **kwargs):
        # 引数
        xpath = kwargs.get('xpath')
        input_value = kwargs.get('input_value')
        field_name = kwargs.get('field_name')

        try:
            # 要素を探す
            self.logger.debug(f"{field_name} を捜索 開始")
            field = self.chrome.find_element(By.XPATH, xpath)
            self.logger.debug(f"{field_name} を捜索 終了")

            # 要素に入力する
            self.logger.debug(f"{field_name} 入力 開始")
            field.send_keys(input_value)
            self.logger.debug(f"{field_name} 入力 終了")

        except NoSuchElementException as e:
            self.logger.error(f"{field_name} の要素が見つからない: {e}")

            # エラー時にスクショ＆報告
            self.error_discord.error_screenshot_discord(
                discord_url,screenshot_dir,
                screenshot_title='input_write',
                comment='要素がみつからない',
                error_message='要素がみつからない',
            )

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# 要素を探してクリック

    def btn_click(self, **kwargs):
        # 引数
        xpath = kwargs.get('xpath')
        field_name = kwargs.get('field_name')

        try:
            # btn要素を探してクリックできる状態になるまで待機
            self.logger.debug(f"{field_name} を捜索 開始")
            btn = WebDriverWait(self.chrome, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            self.logger.debug(f"{field_name} を捜索 終了")

            # 要素に入力する
            self.logger.debug(f"{field_name} クリック 開始")
            btn.click()
            self.logger.debug(f"{field_name} クリック 終了")

        except ElementNotInteractableException:
            self.logger.debug(f"{field_name} JavaScriptを使用してクリック実行 開始")
            self.chrome.execute_script("arguments[0].click();", btn)
            self.logger.debug(f"{field_name} JavaScriptを使用してクリック実行 終了")

        except NoSuchElementException as e:
            self.logger.error(f"{field_name} の要素が見つからない: {e}")
        except TimeoutException as e:
            self.logger.error(f"{field_name} のクリック操作またはページ読み込みでタイムアウト: {e}")
        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")

        finally:
            try:
                # ログインした後のページ読み込みの完了確認
                WebDriverWait(self.chrome, 10).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
                )
                self.logger.debug(f"{field_name} ログインページ読み込み完了")

            except TimeoutException as e:
                self.logger.error(f"{field_name} ページの読み込み完了待機中にタイムアウト: {e}")


# ----------------------------------------------------------------------------------
# display:noneを解除

    def _display_none_unlock(self):
        try:
            self.logger.debug(" display:noneを解除 開始")
            self.chrome.execute_script("document.getElementById('ui-id-2').style.display = 'block';")
            self.logger.debug(" display:noneを解除 完了開始")

        except NoSuchElementException as e:
            self.logger.error(" display:none の要素が見つかりません。")


# ----------------------------------------------------------------------------------
# ページがちゃんと表示されるまで待機

    def _handle_wait_loadpage(self):
        try:
            WebDriverWait(self.chrome, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            self.logger.debug("ページは完全に表示されている")

        except TimeoutException as e:
            self.logger.error(f"ページが表示されません: {e}")


# ----------------------------------------------------------------------------------
# ページが切り替わった際に特定の要素が出るまで待機

    def _handle_wait_next_page(self, xpath):
        try:
            WebDriverWait(self.chrome, 10).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            self.logger.debug(f"{self.site_name} ボタンDOMの読み込みは完了してる")

        except TimeoutException as e:
            self.logger.error(f"10秒待機してもページが表示されません: {e}")


# ----------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------