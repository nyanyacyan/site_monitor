# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/3/27更新

#! webdriverをどこが開いているのかを確認しながら実装が必要。
# ----------------------------------------------------------------------------------


import os
from dotenv import load_dotenv

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException,
                                        TimeoutException)

# 自作モジュール
from .utils import Logger


###############################################################


class Base:
    def __init__(self, chrome, discord_url, debug_mode=False):
        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        self.chrome = chrome
        self.discord_url = discord_url
        self.logger = self.setup_logger(debug_mode=debug_mode)



###############################################################
# ----------------------------------------------------------------------------------

# 要素を探して入力

    def input_write(self, xpath, input_value, field_name):
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
            self.error_discord.process(
                f"{field_name}: 要素がみつからない",
                str(e)
            )

        except Exception as e:
            self.error_discord.process(
                f"[error]{field_name}: 処理中にエラーが発生",
                str(e)
            )


# ----------------------------------------------------------------------------------
# 要素を探してクリック

    def btn_click(self, xpath, field_name):
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

        # 通常のクリックができないためJavaScriptにてクリック
        except ElementNotInteractableException:
            self.logger.debug(f"{field_name} JavaScriptを使用してクリック実行 開始")
            self.chrome.execute_script("arguments[0].click();", btn)
            self.logger.debug(f"{field_name} JavaScriptを使用してクリック実行 終了")

        except NoSuchElementException as e:
            self.logger.error(f"{field_name} の要素が見つからない: {e}")
            self.error_discord.process(
                f"{field_name}: 要素がみつからない",
                str(e)
            )

        except TimeoutException as e:
            self.logger.error(f"{field_name} のクリック操作またはページ読み込みでタイムアウト: {e}")
            self.error_discord.process(
                f"{field_name}: のクリック操作またはページ読み込みでタイムアウト",
                str(e)
            )

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name}: 処理中にエラーが発生",
                str(e)
            )

        finally:
            try:
                # ログインした後のページ読み込みの完了確認
                WebDriverWait(self.chrome, 10).until(
                lambda driver: driver.execute_script('return document.readyState') == 'complete'
                )
                self.logger.debug(f"{field_name} ログインページ読み込み完了")

            except TimeoutException as e:
                self.logger.error(f"{field_name} ページの読み込み完了待機中にタイムアウト: {e}")
                self.error_discord.process(
                    f"{field_name}: のクリック操作またはページ読み込みでタイムアウト",
                    str(e)
                )

            except Exception as e:
                self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")
                self.error_discord.process(
                    f"{field_name}: 処理中にエラーが発生",
                    str(e)
                )

# ----------------------------------------------------------------------------------
# display:noneを解除

    def _display_none_unlock(self, field_name):
        try:
            self.logger.debug(f"{field_name} display:noneを解除 開始")
            self.chrome.execute_script("document.getElementById('ui-id-2').style.display = 'block';")
            self.logger.debug(f"{field_name} display:noneを解除 完了開始")

        except NoSuchElementException as e:
            self.logger.error(" display:none の要素が見つかりません。")
            self.error_discord.process(
                f"{field_name}: 要素がみつからない",
                str(e)
            )

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name}: 処理中にエラーが発生",
                str(e)
            )

###############################################################


class Wait:
    def __init__(self, chrome, debug_mode=False):
        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        self.chrome = chrome


###############################################################
# ----------------------------------------------------------------------------------
# ページがちゃんと表示されるまで待機

    def _handle_wait_loadpage(self, field_name):
        try:
            WebDriverWait(self.chrome, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            self.logger.debug(f"{field_name} ページは完全に表示されている")

        except TimeoutException as e:
            self.logger.error(f"{field_name} ページが表示されません: {e}")
            self.error_discord.process(
                f"{field_name}: ページ読み込みでタイムアウト",
                str(e)
            )

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name}: 処理中にエラーが発生",
                str(e)
            )

# ----------------------------------------------------------------------------------
# ページが切り替わった際に特定の要素が出るまで待機

    def _handle_wait_next_page(self, xpath, field_name):
        try:
            WebDriverWait(self.chrome, 10).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            self.logger.debug(f"{field_name}: ボタンDOMの読み込みは完了してる")

        except TimeoutException as e:
            self.logger.error(f"10秒待機してもページが表示されません: {e}")
            self.error_discord.process(
                f"{field_name}: のクリック操作またはページ読み込みでタイムアウト",
                str(e)
            )

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name}: 処理中にエラーが発生",
                str(e)
            )


# ----------------------------------------------------------------------------------
# データのリストを取得

    def _get_element(self):
        try:
            self.logger.info(f"******** google_map_api_request start ********")

            self.logger.info(f"******** google_map_api_request end ********")

        except Exception as e:
            self.logger.error(f" google_map_api_request 処理中にエラーが発生: {e}")
