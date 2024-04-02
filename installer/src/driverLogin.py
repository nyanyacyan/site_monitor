# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/3/29更新

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
                                        WebDriverException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select

# 自作モジュール
from auto_login.solve_recaptcha import RecaptchaBreakthrough
from logger.debug_logger import Logger
from spreadsheet.read import Read

# ----------------------------------------------------------------------------------


class AutoLogin:
    def __init__(self, chrome, debug_mode=False):
        self.chrome = chrome

        self.logger = self.setup_logger(debug_mode=debug_mode)


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------

# 対象のサイトを開く

    def open_site(self, **kwargs):

        #* 引数
        url = kwargs.get('url')
        print(url)
        by_pattern = kwargs.get('by_pattern')
        userid_path = kwargs.get('userid_path')

        self.logger.info("対象のサイトを開く")

        self.chrome.get(url)
        current_url = self.chrome.current_url
        self.logger.debug(f"URL: {current_url}")

        try:
            self.logger.debug(f"IDなどを入力 ができるかを確認")
            WebDriverWait(self.chrome, 10).until(EC.presence_of_element_located((by_pattern, userid_path)))
            self.logger.debug(f" 入力準備 完了")

        except TimeoutException as e:
            self.logger.error(f" ロードに10秒以上かかってしまったためタイムアウト: {e}")

        except NoSuchElementException as e:
            self.logger.error(f" 要素が見つかりません: {by_pattern}: {userid_path}, {e}")

        except WebDriverException as e:
            self.logger.error(f" webdriverでのエラーが発生: {e}")

        except Exception as e:
            self.logger.error(f" 処理中にエラーが発生: {e}")

        time.sleep(2)


# ----------------------------------------------------------------------------------
#* Cookieを見つけて保存

    def save_cookies(self, **kwargs):
        #* 引数
        cookies_file_name = kwargs.get('cookies_file_name')
        cookie_text_path = kwargs.get('cookie_text_path')

        # フルパスを定義
        full_path = self._get_full_path(cookie_text_path, cookies_file_name)

        # cookiesは、通常、複数のCookie情報を含む大きなリスト担っている
        # 各Cookieはキーと値のペアを持つ辞書（またはオブジェクト）として格納されてる
        cookies = self.chrome.get_cookies()

        try:
            self.logger.debug(" Cookieの取得 完了")

            if cookies:
                self.logger.debug(" クッキーが存在します。")

                self._save_cookies_to_text_file(cookies, full_path)
                self._save_cookies_to_pickle_file(cookies, full_path)

            else:
                self.logger.error(f" にはクッキーが存在しません。")

        except Exception as e:
            self.logger.error(f"予期せぬエラーが発生しました: {e}")


# ----------------------------------------------------------------------------------
# フルパス生成

    def _get_full_path(self, **kwargs):
        #* 引数
        cookies_file_name = kwargs.get('cookies_file_name')
        cookie_text_path = kwargs.get('cookie_text_path')

        if not os.path.isabs(cookie_text_path):
            self.logger.debug(" フルパスではないため生成 開始")
            base_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_dir, cookie_text_path, cookies_file_name)
            self.logger.debug(" フルパスではないため生成 終了")

        # フルパスだったらファイル名を足すだけ
        else:
            full_path = os.path.join(cookie_text_path, cookies_file_name)

        return full_path


# ----------------------------------------------------------------------------------
# Cookieを取得して保存期間をテキストにする

    def _save_cookies_to_text_file(self, **kwargs):
        #* 引数
        cookies = kwargs.get('cookies')
        full_path = kwargs.get('full_path')

        try:
            with open(f'{full_path}_cookie.txt', 'w', encoding='utf-8') as file:
                for cookie in cookies:
                    if 'expiry' in cookie:
                        expiry_timestamp = cookie['expiry']

                        # UNIXタイムスタンプを datetime オブジェクトに変換
                        expiry_datetime = datetime.utcfromtimestamp(expiry_timestamp)

                        # 専用テキストに書き込めるようにクリーニング
                        cookie_expiry_timestamp = f"Cookie: {cookie['name']} の有効期限は「{expiry_datetime}」\n"
                        file.write(cookie_expiry_timestamp)

        except (IOError, OSError) as e:
            self.logger.error(f"ファイルの書き込み中にエラーが発生しました: {e}")

        except Exception as e:
            self.logger.error(f"予期せぬエラーが発生しました: {e}")


# ----------------------------------------------------------------------------------
# Cookieをpickle化する

    def _save_cookies_to_pickle_file(self, **kwargs):
        #* 引数
        cookies = kwargs.get('cookies')
        full_path = kwargs.get('full_path')

        try:
            # pickleデータを蓄積（ディレクトリがなければ作成）
            with open(full_path + '.pkl', 'wb') as file:
                pickle.dump(cookies, file)

            self.logger.debug(f" Cookie、保存完了。")

            with open(full_path + '.pkl', 'rb') as file:
                cookies = pickle.load(file)

            # 読み込んだデータを表示
            self.logger.debug(f"cookies: {cookies} \nCookieの存在を確認。"[:30])

        except pickle.PicklingError as e:
            self.logger.error(f"クッキーのpickle化中にエラーが発生しました: {e}")

        except Exception as e:
            self.logger.error(f"予期せぬエラーが発生しました: {e}")


# ----------------------------------------------------------------------------------
# pickleデータを読み込む

    def pickle_load(self, pickle_file_path):
        try:
            # Cookieファイルを展開
            self.logger.debug(" Cookie 読み込み 開始")
            with open(pickle_file_path, 'rb') as file:
                cookies = pickle.load(file)
            self.logger.debug(" Cookie 読み込み 完了")

        except FileNotFoundError as e:
            self.logger.error(f"ファイルが見つかりません:{e}")
            cookies = []

        except Exception as e:
            self.logger.error(f"処理中にエラーが起きました:{e}")
            cookies = []

        return cookies


# ----------------------------------------------------------------------------------
# Cookieを使ってログイン

    def cookie_login(self, **kwargs):
        #* 引数
        main_url = kwargs.get('main_url')
        pickle_file_path = kwargs.get('pickle_file_path')

        cookies = []

        # Cookieファイルを展開
        cookies = self.pickle_load(pickle_file_path)

        self.chrome.get(main_url)
        self.logger.info("メイン画面にアクセス")

        # Cookieを設定
        for c in cookies:
            self.chrome.add_cookie(c)

        self.chrome.get(main_url)
        self.logger.info("Cookieを使ってメイン画面にアクセス")


        if self.main_url != self.chrome.current_url:
            self.logger.info("Cookieでのログイン成功")

        else:
            self.logger.info("Cookieでのログイン失敗 sessionでのログインに変更")
            session = requests.Session()

            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

            response = session.get(self.main_url)

            if self.main_url != self.chrome.current_url:
                self.logger.info("sessionでのログイン成功")

            else:
                self.logger.error("sessionでのログイン 失敗")

            # テキスト化
            res_text = response.text
            self.logger.debug(f"res_text: {res_text}"[:30])


        try:
            # ログインした後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(" ログインページ読み込み 完了")

        except Exception as e:
            self.logger.error(f" ログイン処理中 にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------