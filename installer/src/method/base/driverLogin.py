# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/3/29更新

# ----------------------------------------------------------------------------------
import os
import pickle
import time
import requests
from datetime import datetime



from selenium.common.exceptions import (NoSuchElementException,
                                        WebDriverException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# 自作モジュール
from .utils import Logger
from .driver_utils import Wait

# ----------------------------------------------------------------------------------
####################################################################################


class AutoLogin:
    def __init__(self, chrome, debug_mode=False):
        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        self.chrome = chrome
        self.driver_wait = Wait(chrome=self.chrome, debug_mode=debug_mode)



####################################################################################
# ----------------------------------------------------------------------------------
# 対象のサイトを開く

    def open_site(self, url, by_pattern, check_path, field_name):

        # サイトを開く前にurlを確認
        self.logger.debug(f"{field_name} url: {url}")
        self.logger.debug(f"{field_name} by_pattern: {by_pattern} , check_path: {check_path}")

        self.logger.info("対象のサイトを開く")

        self.chrome.get(url)
        current_url = self.chrome.current_url
        self.logger.debug(f"{field_name} URL: {current_url}")

        try:
            print(f'by_pattern: {by_pattern}')
            self.logger.debug(f"IDなどを入力 ができるかを確認")

            self.driver_wait._element_clickable(by_pattern=by_pattern, element_path=check_path, field_name=field_name)

            self.logger.debug(f"{field_name}  入力準備 完了")

        except TimeoutException as e:
            self.logger.info(f"{field_name} 初回ロードに10秒以上かかってしまったためリロード: {e}")

            self.chrome.refresh()
            try:
                self.logger.debug(f"IDなどを入力 ができるかを確認")
                self.driver_wait._element_clickable(by_pattern=by_pattern, element_path=check_path, field_name=field_name)
                self.logger.debug(f"{field_name}  入力準備 完了")

            except TimeoutException as e:
                self.logger.info(f"{field_name} 2回目のロードエラーのためタイムアウト: {e}")


        except NoSuchElementException as e:
            self.logger.error(f" 要素が見つかりません: {by_pattern}: {check_path}, {e}")


        except WebDriverException as e:
            self.logger.error(f"{field_name} webdriverでのエラーが発生: {e}")


        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")


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
                self._save_cookies_to_text_file(cookies=cookies, full_path=full_path, field_name=field_name)
                # Cookieをバイナリデータにて保存
                self._save_cookies_to_pickle_file(cookies=cookies, full_path=full_path, field_name=field_name)
                self.logger.debug(f"{field_name}: 保存完了")

            else:
                self.logger.error(f"{field_name}: cookieが存在しません。")

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")



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

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")


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

        except Exception as e:
            self.logger.error(f"{field_name}: 予期せぬエラーが発生しました: {e}")


# ----------------------------------------------------------------------------------
# pickleデータを読み込む

    def _pickle_load(self, pickle_file_path, field_name) -> None:
        try:
            # Cookieファイルを展開
            self.logger.debug(f"{field_name}:  Cookie 読み込み 開始")
            with open(pickle_file_path, 'rb') as file:
                cookies = pickle.load(file)
            self.logger.debug(f"{field_name}: Cookie 読み込み 完了")
            self.logger.debug(f"{field_name}: Cookie: {cookies}")


        except FileNotFoundError as e:
            self.logger.error(f"ファイルが見つかりません:{e}")


            # エラーのためCookiesは空を渡す
            cookies = []

        except Exception as e:
            self.logger.error(f"{field_name}: 処理中にエラーが起きました:{e}")


            # エラーのためCookiesは空を渡す
            cookies = []

        return cookies


# ----------------------------------------------------------------------------------
# Cookieを使ってログイン

    def cookie_login(self, main_url, file_name, field_name):
        # cookiesを初期化
        cookies = []

        # Cookieのフルパス
        pickle_file_path = self._get_full_path(file_name=file_name)

        # urlを事前確認
        self.logger.debug(f"{field_name}: main_url: {main_url}")

        # Cookieファイルを展開
        cookies = self._pickle_load(pickle_file_path=pickle_file_path, field_name=field_name)

        self.logger.debug(f"{field_name} cookies: {cookies}")

        self.chrome.get(main_url)
        self.logger.info(f"{field_name}: メイン画面にアクセス")


        # Cookieを設定
        for c in cookies:
            self.chrome.add_cookie(c)

        self.chrome.get(main_url)
        self.logger.info(f"{field_name}: Cookieを使ってメイン画面にアクセス")

        time.sleep(60)

        current_url = self.chrome.current_url
        self.logger.info(f"{field_name}: current_url: {current_url}")


        if main_url == current_url:
            self.logger.info(f"{field_name}: Cookieでのログイン成功")

        else:
            self.logger.warning("Cookieでのログイン失敗 sessionでのログインに変更")
            session = requests.Session()


# セッションでのログイン
# 項目はその時に応じて変更が必要
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])


            self.logger.debug(f"name{cookie['name']},{cookie['value']},{cookie['domain']}")

            response = session.get(main_url)

            print(f"status_code:{response.status_code} {response.text}")

            time.sleep(60)


            if main_url == self.chrome.current_url:
                self.logger.info(f"{field_name}: sessionでのログイン成功")

            else:
                self.logger.error(f"{field_name}: sessionでのログイン 失敗")
                raise

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


# ----------------------------------------------------------------------------------
# サイトを閉じる

    def close_chrome(self):
        self.chrome.quit()


# ----------------------------------------------------------------------------------
# ログインできたかを確認する

    def login_checker(self, timeout, by_pattern, xpath):
        # サイトの状態がコンプリート状態になってるか確認
        self.driver_wait._js_page_checker(timeout=timeout, field_name='login_checker')

        # 指定の要素がDOM上に存在するまで待機
        self.driver_wait._dom_checker(by_pattern=by_pattern, xpath=xpath, field_name='login_checker', timeout=timeout)

# ----------------------------------------------------------------------------------
# Cookieを使ってログイン

    def cookie_login2(self, main_url, file_name, field_name):
        # cookiesを初期化
        cookies = []

        # Cookieのフルパス
        pickle_file_path = self._get_full_path(file_name=file_name)

        # urlを事前確認
        self.logger.debug(f"{field_name}: main_url: {main_url}")

        # Cookieファイルを展開
        cookies = self._pickle_load(pickle_file_path=pickle_file_path, field_name=field_name)

        self.logger.debug(f"{field_name} cookies: {cookies}")

        self.chrome.get(main_url)

        for c in cookies:
            self.chrome.add_cookie(c)

        self.chrome.get(main_url)

        time.sleep(60)

        self.logger.info(f"{field_name}: Cookieを使ってメイン画面にアクセス")


        current_url = self.chrome.current_url
        self.logger.info(f"{field_name}: current_url: {current_url}")


        if main_url == current_url:
            self.logger.info(f"{field_name}: Cookieでのログイン成功")

        else:
            self.logger.warning("Cookieでのログイン失敗 sessionでのログインに変更")
            session = requests.Session()


# セッションでのログイン
# 項目はその時に応じて変更が必要
            cookie = cookies[0]
            session.cookies.set(
                name=cookie['name'],
                value=cookie['value'],
                domain=cookie['domain'],
                path=cookie['path'],
                # expires=cookie['expiry'],
                # secure=cookie['secure'],
                # rest={'HttpOnly': cookie['httpOnly'], 'SameSite': cookie['sameSite']}
            )

            self.logger.debug(f"name{cookie['name']},{cookie['value']},{cookie['domain']},{cookie['path']}")

            response = session.get(main_url)

            if main_url == self.chrome.current_url:
                self.logger.info(f"{field_name}: sessionでのログイン成功")

            else:
                self.logger.error(f"{field_name}: sessionでのログイン 失敗")
                raise

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


# ----------------------------------------------------------------------------------


    def switch_window(self, main_url):
        self.logger.info(f"********** switch_window 開始 **********")
        self.logger.debug(f"main_url: {main_url}")

        try:
            self.chrome.execute_script("window.open('');")
            # ウィンドウハンドルの数をチェック
            if len(self.chrome.window_handles) > 1:
                self.chrome.switch_to.window(self.chrome.window_handles[1])
                self.chrome.get(main_url)
            else:
                self.logger.error("2つ目のウィンドウが存在しません。")
        except Exception as e:
            self.logger.error(f"ウィンドウの切り替え中にエラーが発生しました: {e}")
        finally:
            self.logger.info("********** switch_window 終了 **********")



# ----------------------------------------------------------------------------------
# 対象のサイトを開く

    def sever_open_site(self, url, by_pattern, check_path, notify_func, field_name):

        # サイトを開く前にurlを確認
        self.logger.debug(f"{field_name} url: {url}")
        self.logger.debug(f"{field_name} by_pattern: {by_pattern} , check_path: {check_path}")

        self.logger.info("対象のサイトを開く")

        time.sleep(2)

        self.chrome.get(url)
        current_url = self.chrome.current_url
        self.logger.debug(f"{field_name} URL: {current_url}")

        self.logger.critical(f'ここを確認する: {url}')
        self.driver_wait._js_page_checker(field_name=field_name)

        try:
            self.driver_wait._sever_element_clickable(by_pattern=by_pattern, element_path=check_path, notify_func=notify_func , field_name=field_name)

            self.logger.debug(f"{field_name}  入力準備 完了")

        except TimeoutException as e:
            self.logger.info(f"{field_name} 初回ロードに10秒以上かかってしまったためリロード: {e}")

            self.chrome.refresh()
            try:
                self.logger.debug(f"IDなどを入力 ができるかを確認")
                self.driver_wait._element_clickable(by_pattern=by_pattern, element_path=check_path, field_name=field_name)
                self.logger.debug(f"{field_name}  入力準備 完了")

            except TimeoutException as e:
                self.logger.info(f"{field_name} 2回目のロードエラーのためタイムアウト: {e}")


        except NoSuchElementException as e:
            self.logger.error(f" 要素が見つかりません: {by_pattern}: {check_path}, {e}")


        except WebDriverException as e:
            self.logger.error(f"{field_name} webdriverでのエラーが発生: {e}")


        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")


        time.sleep(2)


# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------