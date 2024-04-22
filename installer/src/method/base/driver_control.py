# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/3/27更新

#! webdriverをどこが開いているのかを確認しながら実装が必要。
# ----------------------------------------------------------------------------------


import os
import time
import random

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException,
                                        InvalidSelectorException,
                                        TimeoutException)

# 自作モジュール
from .utils import Logger, NoneChecker
from .driver_utils import Wait
from .errorNotify import ErrorDiscord


# ----------------------------------------------------------------------------------
####################################################################################


class Base:
    def __init__(self, chrome, discord_url, debug_mode=False):
        self.chrome = chrome
        self.discord_url = discord_url
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.none = NoneChecker(debug_mode=debug_mode)
        self.driver_wait = Wait(chrome=self.chrome, discord_url=self.discord_url, debug_mode=debug_mode)

        # 自作モジュールインスタンス化
        self.error_discord = ErrorDiscord(chrome=self.chrome, discord_url=self.discord_url, debug_mode=debug_mode)

####################################################################################

# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# 要素を探して入力

    def input_write(self, by_pattern, xpath, input_value, field_name) -> None:
        try:
            # 要素を探す
            self.logger.debug(f"{field_name} 捜索 開始")
            self.logger.debug(f"by_pattern: {by_pattern} xpath: {xpath}")
            field = self.chrome.find_element(self._locator_select(by_pattern), xpath)
            self.logger.debug(f"{field_name} 発見")

            # 要素に入力する
            self.logger.debug(f"input_value: {input_value}")
            self.logger.debug(f"{field_name} {input_value} 入力 開始")
            field.send_keys(input_value)
            self.logger.debug(f"{field_name} 入力 終了")

        except InvalidSelectorException as e:
            self.logger.error(f"{field_name} 選択したロケーターと要素が違う: {e}")
            self.error_discord.process(
                f"{field_name}: 要素がみつからない",
                str(e)
            )

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
# 要素を探して入力したあとにEnterKey

    def input_enterkey(self, by_pattern, xpath, input_value, field_name, timeout) -> None:
        try:

            # 要素を探す
            self.logger.debug(f"{field_name} 捜索 開始")
            self.logger.debug(f"by_pattern: {by_pattern} xpath: {xpath}")
            search_field = self.chrome.find_element(self._locator_select(by_pattern), xpath)

            self.logger.debug(f"{field_name} search_field: {search_field}")
            self.logger.debug(f"{field_name} 明示的な待機 開始")


            search_field = self.driver_wait._no_locator_clickable(
                variable_name=search_field,
                field_name=field_name,
                timeout=timeout
            )
            self.logger.debug(f"{field_name} 発見")
            self.logger.debug(f"{field_name} search_field 2回目: {search_field}")


            time.sleep(2)

            # 要素に入力する
            self.logger.debug(f"input_value: {input_value}")
            self.logger.debug(f"{field_name} {input_value} 入力 開始")
            search_field.send_keys(input_value)
            self.logger.debug(f"{field_name} 入力 終了")

            time.sleep(2)

            self.logger.debug(f"{field_name} Enterkey 入力")
            search_field.send_keys(Keys.ENTER)
            self.logger.debug(f"{field_name} Enterkey 終了")

        except InvalidSelectorException as e:
            self.logger.error(f"{field_name} 選択したロケーターと要素が違う: {e}")
            self.error_discord.process(
                f"{field_name}: 要素がみつからない",
                str(e)
            )

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
# 要素を探して取得して返す

    def get_element(self, by_pattern, xpath, field_name) -> None:
        try:
            # 要素を探す
            self.logger.debug(f"{field_name} 捜索 開始")
            self.logger.debug(f"by_pattern: {by_pattern} xpath: {xpath}")
            element = self.chrome.find_element(self._locator_select(by_pattern), xpath)
            self.logger.debug(f"{field_name} 発見")

        except InvalidSelectorException as e:
            self.logger.error(f"{field_name} 選択したロケーターと要素が違う: {e}")
            self.error_discord.process(
                f"{field_name}: 要素がみつからない",
                str(e)
            )
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

        return element


# ----------------------------------------------------------------------------------
# 要素を探してクリック
# 確認なしバージョン→URLが変わったなどのチェックなし

    def btn_click(self, by_pattern, xpath, field_name) -> None:
        try:
            current_url = self.chrome.current_url
            # btn要素を探してクリックできる状態になるまで待機
            self.logger.debug(f"{field_name} を捜索 開始")
            self.logger.debug(f"by_pattern: {by_pattern} xpath: {xpath}, current_url: {current_url}")
            btn = WebDriverWait(self.chrome, 10).until(
                EC.element_to_be_clickable((self._locator_select(by_pattern), xpath))
            )
            self.logger.debug(f"{field_name} 発見")

            # 要素に入力する
            self.logger.debug(f"{field_name} クリック 開始")
            btn.click()
            self.logger.debug(f"{field_name} クリック 終了")

        # 通常のクリックができないためJavaScriptにてクリック
        except ElementNotInteractableException:
            self.logger.debug(f"{field_name} JavaScriptを使用してクリック実行 開始")
            self.chrome.execute_script("arguments[0].click();", btn)
            self.logger.debug(f"{field_name} JavaScriptを使用してクリック実行 終了")


        except InvalidSelectorException as e:
            self.logger.error(f"{field_name} 選択したロケーターと要素が違う: {e}")
            self.error_discord.process(
                f"{field_name}: 要素がみつからない",
                str(e)
            )

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
# 要素を探してクリック

    def random_btn_click(self, by_pattern, xpath, field_name, timeout=10) -> None:
        try:
            current_url = self.chrome.current_url
            # btn要素を探してクリックできる状態になるまで待機
            self.logger.debug(f"{field_name} を捜索 開始")
            self.logger.debug(f"by_pattern: {by_pattern} xpath: {xpath}, current_url: {current_url}")

            # 重複してる要素を指定して一つの変数にまとめる
            elements = self.chrome.find_element(self._locator_select(by_pattern), xpath)

            if not elements:
                self.logger.debug(f"{field_name} 選定したpathの要素が存在しません（None）")
                self.none.any_checker
                return

            # 要素リストの中身を確認
            limited_elements = elements[:3]
            self.logger.debug(f"{field_name} elements_list {limited_elements}")

            self.logger.debug(f"{field_name} ランダムクリック 開始")

            # ランダムによるクリック
            random_choice_element = random.choice(elements)

            # クリックできる状態になっているか確認
            random_choice_element = self.driver_wait._no_locator_clickable(variable_name=random_choice_element, field_name=field_name, timeout=timeout)

            # 選定したものをクリック
            random_choice_element.click()

            self.logger.debug(f"{field_name} クリック 終了")

            # URLが切り替わるのを確認
            self.driver_wait._url_change(
                current_url=current_url,
                field_name=field_name,
                timeout=timeout
            )


        # 通常のクリックができないためJavaScriptにてクリック
        except ElementNotInteractableException:
            self.logger.debug(f"{field_name} JavaScriptを使用してクリック実行 開始")
            self.chrome.execute_script("arguments[0].click();", random_choice_element)
            self.logger.debug(f"{field_name} JavaScriptを使用してクリック実行 終了")


        except InvalidSelectorException as e:
            self.logger.error(f"{field_name} 選択したロケーターと要素が違う: {e}")
            self.error_discord.process(
                f"{field_name}: 要素がみつからない",
                str(e)
            )

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
# ロケーター選択→直接文字列で入れ込むことができない

    def _locator_select(self, locator) -> None:
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
# display:noneを解除

    def _display_none_unlock(self, field_name) -> None:
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

# ----------------------------------------------------------------------------------
# ページがちゃんと表示されるまで待機

    def _handle_wait_loadpage(self, field_name) -> None:
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

    def _handle_wait_next_page(self, xpath, field_name) -> None:
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


    def drop_down_select(self, by_pattern, xpath, select_word, field_name='drop_down_select'):
        try:
            self.logger.debug(f"********** {field_name} 処理 開始 **********")
            self.logger.debug(f"by_pattern: {by_pattern} xpath: {xpath}")

            self.logger.debug(f"{field_name} 捜索 開始")
            select_element = self.chrome.find_element(self._locator_select(by_pattern), xpath)
            self.logger.debug(f"{field_name} 発見")

            self.logger.debug(f"{field_name} 選択 開始")
            self.logger.debug(f"{field_name} select_word: {select_word}")

            # ドロップダウンメニューを選択できるように指定
            select_object = Select(select_element)

            time.sleep(1)

            # 選択肢をChoice
            select_object.select_by_visible_text(select_word)
            self.logger.debug(f"{field_name} 選択 終了")

            # ボタンを押した後のページ読み込みの完了確認
            self.driver_wait._js_page_checker(field_name=field_name)

        except NoSuchElementException as e:
            self.error_screenshot_discord(
                f"{self.account_id}: {field_name} 要素が見つからない",  # discordへの出力
                str(e)
            )

        except Exception as e:
            self.error_screenshot_discord(
                f"{self.account_id}: {field_name} 処理中にエラーが発生",  # discordへの出力
                str(e)
            )



# ----------------------------------------------------------------------------------
