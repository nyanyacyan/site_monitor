# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/3/27更新

#! webdriverをどこが開いているのかを確認しながら実装が必要。
# ----------------------------------------------------------------------------------


import os


from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException,
                                        InvalidSelectorException,
                                        TimeoutException)

# 自作モジュール
from .utils import Logger
# from .errorNotify import ErrorDiscord

####################################################################################
# from driver_utils import Wait
# self.driver_wait = Wait(chrome=chrome, debug_mode=debug_mode)

class Wait:
    def __init__(self, chrome, debug_mode=False):
        self.chrome = chrome
        self.logger = self.setup_logger(debug_mode=debug_mode)

        # self.error_discord = ErrorDiscord(chrome=self.chrome, discord_url=discord_url)

####################################################################################
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


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


# ----------------------------------------------------------------------------------# URLが変わるまで待機 デフォルト10秒
# self.driver_wait._url_change(current_url=, timeout=)

    def _url_change(self, current_url, field_name, timeout: int=10):
        try:
            WebDriverWait(self.chrome, timeout).until(EC.url_changes(current_url))
            self.logger.debug(f"{field_name} URLの切り替え成功")

        except TimeoutException as e:
            self.logger.error(f"{field_name} URLの切り替えされるまで、{timeout}秒以上経過したためタイムアウト: {e}")
            self.error_discord.process(
                f"{field_name} URLの切り替えされるまで、{timeout}秒以上経過したためタイムアウト: {e}",
                str(e)
            )

        except Exception as e:
            self.logger.error(f"{field_name} URLの切り替えの待機中になんらかのエラーが発生 {e}")
            self.error_discord.process(
                f"{field_name}: URLの切り替えの待機中になんらかのエラーが発生",
                str(e)
            )


# ----------------------------------------------------------------------------------
# クリックができるようになるまで待機 デフォルト10秒
# self.driver_wait._element_clickable(by_pattern=, xpath=, timeout=)

    def _element_clickable(self, by_pattern, element_path, field_name, timeout=10):
        try:
            WebDriverWait(self.chrome, timeout).until(EC.element_to_be_clickable((self._locator_select(by_pattern), element_path)))
            self.logger.debug(f"{field_name} クリックできる状態")

        except TimeoutException as e:
            self.logger.error(f"{field_name} クリックが可能になるまで、{timeout}秒以上経過したためタイムアウト: {e}")
            self.error_discord.process(
                f"{field_name} クリックが可能になるまで、{timeout}秒以上経過したためタイムアウト: {e}",
                str(e)
            )

        except Exception as e:
            self.logger.error(f"{field_name} クリックが可能になるまでの待機中になんらかのエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name} クリックが可能になるまでの待機中になんらかのエラーが発生: {e}",
                str(e)
            )


# ----------------------------------------------------------------------------------
#* locatorなし→変数による代入（事前に要素を選択して変数代入してあるものを選択）
# self.driver_wait._no_locator_clickable(variable_name=, field_name=, timeout=)

    def _no_locator_clickable(self, variable_name, field_name, timeout=10):
        try:
            WebDriverWait(self.chrome, timeout).until(EC.element_to_be_clickable(variable_name))
            self.logger.debug(f"{field_name} クリックできる状態")

        except TimeoutException as e:
            self.logger.error(f"{field_name} クリックが可能になるまで、{timeout}秒以上経過したためタイムアウト: {e}")
            self.error_discord.process(
                f"{field_name} クリックが可能になるまで、{timeout}秒以上経過したためタイムアウト: {e}",
                str(e)
            )

        except Exception as e:
            self.logger.error(f"{field_name} クリックが可能になるまでの待機中になんらかのエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name} クリックが可能になるまでの待機中になんらかのエラーが発生: {e}",
                str(e)
            )


# ----------------------------------------------------------------------------------# 指定の要素がDOM上に存在するまで待機

# self.driver_wait._dom_checker(by_pattern=, xpath=, field_name, timeout=timeout)

    def _dom_checker(self, by_pattern, xpath, field_name, timeout=10):
        try:
            WebDriverWait(self.chrome, timeout).until(EC.presence_of_element_located((self._locator_select(by_pattern), xpath)))
            self.logger.debug(f"{field_name} ページが更新されてます。")

        except TimeoutException as e:
            self.logger.error(f"{field_name} ページが更新されるまで、{timeout}秒以上経過したためタイムアウト: {e}")
            self.error_discord.process(
                f"{field_name} ページが更新されるまで、{timeout}秒以上経過したためタイムアウト: {e}",
                str(e)
            )

        except Exception as e:
            self.logger.error(f"{field_name} ページが更新されるまでの待機中になんらかのエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name}: Uページが更新されるまでの待機中になんらかのエラーが発生: {e}",
                str(e)
            )

# ----------------------------------------------------------------------------------
# 次のページに移動後にページがちゃんと開いてる状態か全体を確認してチェックする
#? JavaScriptCommand
# self.driver_wait._js_page_update_checker(field_name=, timeout=10)

    def _js_page_checker(self, field_name, timeout=10):
        try:
            WebDriverWait(self.chrome, timeout).until(lambda driver: driver.execute_script('return document.readyState')=='complete')
            self.logger.debug(f"{field_name} ページが更新されてます。")

        except TimeoutException as e:
            self.logger.error(f"{field_name} ページが更新されるまで、{timeout}秒以上経過したためタイムアウト: {e}")
            self.error_discord.process(
                f"{field_name} ページが更新されるまで、{timeout}秒以上経過したためタイムアウト: {e}",
                str(e)
            )

        except Exception as e:
            self.logger.error(f"{field_name} ページが更新されるまでの待機中になんらかのエラーが発生: {e}")
            self.error_discord.process(
                f"{field_name}: Uページが更新されるまでの待機中になんらかのエラーが発生: {e}",
                str(e)
            )


# ----------------------------------------------------------------------------------
# 指定の要素がDOM上に存在するまで待機
