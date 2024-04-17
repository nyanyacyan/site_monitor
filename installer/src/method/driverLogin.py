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
from method.utils import Logger
from method.errorNotify import ErrorDiscord

# ----------------------------------------------------------------------------------
####################################################################################


class AutoLogin:
    def __init__(self, chrome, discord_url, debug_mode=False):
        self.chrome = chrome
        self.discord_url = discord_url

        self.logger = self.setup_logger(debug_mode=debug_mode)

        self.error_discord = ErrorDiscord(chrome=self.chrome, discord_url=self.discord_url)



####################################################################################

# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# 対象のサイトを開く

    def open_site(self, url, by_pattern, check_path, field_name):

        # サイトを開く前にurlを確認
        self.logger.debug(f"{field_name} url: {url}")

        self.logger.info("対象のサイトを開く")

        self.chrome.get(url)
        current_url = self.chrome.current_url
        self.logger.debug(f"{field_name} URL: {current_url}")

        try:
            print(f'by_pattern: {by_pattern}')
            self.logger.debug(f"IDなどを入力 ができるかを確認")
            WebDriverWait(self.chrome, 10).until(EC.presence_of_element_located((self._locator_select(by_pattern), check_path)))
            self.logger.debug(f"{field_name}  入力準備 完了")

        except TimeoutException as e:
            self.logger.info(f"{field_name} 初回ロードに10秒以上かかってしまったためリロード: {e}")

            self.chrome.refresh()
            try:
                self.logger.debug(f"IDなどを入力 ができるかを確認")
                WebDriverWait(self.chrome, 10).until(EC.presence_of_element_located((self._locator_select(by_pattern), check_path)))
                self.logger.debug(f"{field_name}  入力準備 完了")

            except TimeoutException as e:
                self.logger.info(f"{field_name} 2回目のロードエラーのためタイムアウト: {e}")
                self.error_discord.process(
                    f"{field_name}: 2回目のロードエラーのためタイムアウト",
                    str(e)
                )

        except NoSuchElementException as e:
            self.logger.error(f" 要素が見つかりません: {by_pattern}: {check_path}, {e}")
            self.error_discord.process(
                f"{field_name}: 要素が見つかりません",
                str(e)
            )

        except WebDriverException as e:
            self.logger.error(f"{field_name} webdriverでのエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name}: webdriverでのエラーが発生",
                str(e)
            )

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name}: 処理中にエラーが発生",
                str(e)
            )

        time.sleep(2)


# ----------------------------------------------------------------------------------
# ロケーター選択→直接文字列で入れ込むことができない

    def _locator_select(self, locator):
        mapping = {
            'ID' : By.ID,
            'XPATH' : By.XPATH,
            'CLASS' : By.CLASS_NAME,
            'CSS' : By.CSS_SELECTOR,
            'TAG' : By.TAG_NAME,
            'NAME' : By.NAME,
            'LINK_TEXT': By.LINK_TEXT,  # リンクテキスト全体に一致する要素を見つける
            'PARTIAL_LINK_TEXT': By.PARTIAL_LINK_TEXT  # リンクテキストの一部に一致する要素を見つける
        }

        # 入力された文字を大文字に直して選択
        return mapping.get(locator.upper())



# ----------------------------------------------------------------------------------
#* Cookieを見つけて保存

    def save_cookies(self, cookies_file_name, field_name):
        # フルパスを定義
        full_path = self._get_full_path(cookies_file_name)

        # cookiesは、通常、複数のCookie情報を含む大きなリスト担っている
        # 各Cookieはキーと値のペアを持つ辞書（またはオブジェクト）として格納されてる
        cookies = self.chrome.get_cookies()

        try:
            if cookies:
                self.logger.debug(f"{field_name}: cookieを発見。")

                # Cookieの中身をテキストに保存
                self._save_cookies_to_text_file(cookies, full_path)
                # Cookieをバイナリデータにて保存
                self._save_cookies_to_pickle_file(cookies, full_path)
                self.logger.debug(f"{field_name}: 保存完了")

            else:
                self.logger.error(f"{field_name}: cookieが存在しません。")

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name}: 処理中にエラーが発生",
                str(e)
            )


# ----------------------------------------------------------------------------------
# Cookie用のフルパス生成

    def _get_full_path(self, file_name):

        # 事前にファイル名が反映してるのか確認
        self.logger.debug(f"file_name: {file_name}")

        # 親要素までのPathを取得（ファイル名をあと入力できるように）
        base_dir = os.path.dirname(os.path.abspath(__file__))

        full_path = os.path.join(base_dir, 'cookies', file_name)  # cookieのフルパス生成
        self.logger.debug(f"full_path: {full_path}")  # フルパス確認

        return full_path


# ----------------------------------------------------------------------------------
# Cookieを取得して保存期間をテキストにする

    def _save_cookies_to_text_file(self, cookies, full_path, field_name) -> None:
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
            self.error_discord.process(
                f"{field_name}: ファイルの書き込み中にエラーが発生しました",
                str(e)
            )
        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name}: 処理中にエラーが発生",
                str(e)
            )


# ----------------------------------------------------------------------------------
# Cookieをpickle化する

    def _save_cookies_to_pickle_file(self, cookies, full_path, field_name) -> None:
        try:
            # pickleデータを蓄積（ディレクトリがなければ作成）
            with open(full_path + '.pkl', 'wb') as file:
                pickle.dump(cookies, file)

            self.logger.debug(f"{field_name}: Cookie、保存完了。")

            with open(full_path + '.pkl', 'rb') as file:
                cookies = pickle.load(file)

            # 読み込んだデータを表示
            self.logger.debug(f"{field_name}: cookies: {cookies} \nCookieの存在を確認。"[:30])

        except pickle.PicklingError as e:
            self.logger.error(f"{field_name}: クッキーのpickle化中にエラーが発生しました: {e}")
            self.error_discord.process(
                f"{field_name}: クッキーのpickle化中にエラーが発生しました",
                str(e)
            )
        except Exception as e:
            self.logger.error(f"{field_name}: 予期せぬエラーが発生しました: {e}")
            self.error_discord.process(
                f"{field_name}: 予期せぬエラーが発生しました",
                str(e)
            )

# ----------------------------------------------------------------------------------
# pickleデータを読み込む

    def pickle_load(self, pickle_file_path, field_name) -> None:
        try:
            # Cookieファイルを展開
            self.logger.debug(f"{field_name}:  Cookie 読み込み 開始")
            with open(pickle_file_path, 'rb') as file:
                cookies = pickle.load(file)
            self.logger.debug(f"{field_name}:  Cookie 読み込み 完了")

        except FileNotFoundError as e:
            self.logger.error(f"ファイルが見つかりません:{e}")
            self.error_discord.process(
                f"{field_name}: ファイルが見つかりません",
                str(e)
            )

            # エラーのためCookiesは空を渡す
            cookies = []

        except Exception as e:
            self.logger.error(f"{field_name}: 処理中にエラーが起きました:{e}")
            self.error_discord.process(
                f"{field_name}: ファイルが見つかりません",
                str(e)
            )

            # エラーのためCookiesは空を渡す
            cookies = []

        return cookies


# ----------------------------------------------------------------------------------
# Cookieを使ってログイン

    def cookie_login(self, main_url, pickle_file_path, field_name) -> None:
        # cookiesを初期化
        cookies = []

        # urlを事前確認
        self.logger.info(f"{field_name}: main_url: {main_url}")

        # Cookieファイルを展開
        cookies = self.pickle_load(pickle_file_path)

        self.chrome.get(main_url)
        self.logger.info(f"{field_name}: メイン画面にアクセス")

        # Cookieを設定
        for c in cookies:
            self.chrome.add_cookie(c)

        self.chrome.get(main_url)
        self.logger.info(f"{field_name}: Cookieを使ってメイン画面にアクセス")


        if self.main_url != self.chrome.current_url:
            self.logger.info(f"{field_name}: Cookieでのログイン成功")

        else:
            self.logger.info("Cookieでのログイン失敗 sessionでのログインに変更")
            session = requests.Session()

            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

            response = session.get(self.main_url)

            if self.main_url != self.chrome.current_url:
                self.logger.info(f"{field_name}: sessionでのログイン成功")

            else:
                self.logger.error(f"{field_name}: sessionでのログイン 失敗")

            # テキスト化
            res_text = response.text
            self.logger.debug(f"res_text: {res_text}"[:30])


        try:
            # ログインした後のページ読み込みの完了確認
            WebDriverWait(self.chrome, 5).until(
            lambda driver: driver.execute_script('return document.readyState') == 'complete'
            )
            self.logger.debug(f"{field_name}: ログインページ読み込み 完了")

        except Exception as e:
            self.logger.error(f"{field_name}: ログイン処理中 にエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name}: ファイルが見つかりません",
                str(e)
            )

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------