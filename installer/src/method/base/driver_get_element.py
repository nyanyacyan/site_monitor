# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/6/14更新


# ----------------------------------------------------------------------------------
import time

from selenium.common.exceptions import (NoSuchElementException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

# 自作モジュール
from .utils import Logger
from .driver_base import Wait



###############################################################


class GetElement:
    def __init__(self, chrome, debug_mode=False):
        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        self.chrome = chrome

        # 自作モジュール
        self.wait = Wait(chrome=self.chrome, debug_mode=False)


###############################################################
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
# 要素のリスト取得

    def _get_elements(self, by_pattern, xpath):
        try:
            self.logger.info(f"******** _get_element start ********")

            self.logger.debug(f"by_pattern: {by_pattern}")
            self.logger.debug(f"xpath: {xpath}")

            self.wait._handle_wait_loadpage(field_name='_get_elements')

            elements = self.chrome.find_elements(self._locator_select(by_pattern), xpath)
            self.logger.debug(f"element: {elements}")

            self.logger.info(f"******** _get_element end ********")

            return elements


        except NoSuchElementException as e:
            self.logger.error(f"_get_element 要素が見つからない: {e}")
            raise

        except Exception as e:
            self.logger.error(f"_get_element 処理中にエラーが発生: {e}")
            raise


# ----------------------------------------------------------------------------------
# 特定の要素にあるText（ｐタグ）を取得する

    def _get_element_text(self, element, text_pattern, text_xpath):
        try:
            self.logger.info(f"******** _get_element start ********")

            self.logger.debug(f"text_pattern: {text_pattern}")
            self.logger.debug(f"text_xpath: {text_xpath}")

            self._wait_element(by_pattern=text_pattern, xpath=text_xpath, field_name=__name__)

            # 要素にあるTextを取得
            # strip()はTextの前後にある空白を除去してくれる
            text_elements = element.find_element(self._locator_select(text_pattern), text_xpath).text.strip()

            self.logger.debug(f"text_element: {text_elements}")

            self.logger.info(f"******** _get_element end ********")

            return text_elements


        except NoSuchElementException as e:
            self.logger.error(f"_get_element 要素が見つからない: {e}")
            return None

        except Exception as e:
            self.logger.error(f"_get_element 処理中にエラーが発生: {e}")
            raise


# ----------------------------------------------------------------------------------


    def _wait_element(self, by_pattern, xpath, field_name):
        try:
            start_time = time.time()

            parent_xpath = xpath.rsplit("//", 1)[0]
            parent_element = self.chrome.find_element(By.XPATH, parent_xpath)

            parent_html = parent_element.get_attribute("outerHTML")

            self.logger.debug(f"Parent HTML: {parent_html}")
            with open("parent_element.html", "w", encoding="utf-8") as f:
                f.write(parent_html)

            element = WebDriverWait(self.chrome, 20).until(
                EC.presence_of_element_located((by_pattern, xpath))
            )
            end_time = time.time()
            diff_time = end_time - start_time

            self.logger.debug(f"DOMの更新はされています text: {element.text}")
            self.logger.debug(f"処理時間: {diff_time} 秒")

            return element

        except NoSuchElementException:
            self.logger.debug(f"NoSuchElementExceptionが発生: 要素が見つかりません")
            return None

        except Exception as e:
            self.logger.error(f"指定のPathの要素の確認をしている際にエラーが発生 \n{e}")
            raise


# ----------------------------------------------------------------------------------
# 特定の要素から指定するpathから要素を辞書にまとめる

    def elements_to_dict(self, items_xpath, data_xpaths,by_pattern=By.XPATH, text_pattern=By.XPATH):
        try:
            self.logger.info(f"******** elements_to_dict start ********")

            self.logger.debug(f"by_pattern: {by_pattern}")

            # ページがロード完了になるまで待機
            self.wait._handle_wait_loadpage(field_name='elements_to_dict')

            # 要素の集合体を取得（大枠）
            items = self._get_elements(by_pattern=by_pattern, xpath=items_xpath)

            self.logger.warning(f"items:\n{items}")

            data_list = []

            # 形式が「WebElement」の場合には単一担ってしまうため繰り返し処理ができないためリストへ変換
            if isinstance(items, WebElement):
                items = [items]

            # 要素の集合体から詳細データを取得
            for index, item in enumerate(items):
                item_count = len(items)

                self.logger.info(f"item_count:{index + 1} / {item_count} 実行中")
                self.logger.info(f"item: {item}")

                # 取得したいデータを辞書データとして取得
                # 辞書を初期化して入れ込んるようにする
                elements_dict = {}
                # items()は辞書のkeyとvalueを取得する際に使う
                for key, config in data_xpaths.items():
                    method = config['method']
                    detail_xpath = config['detail_xpath']

                    # 同列からの要素の取得は「attribute」にて取得
                    if method == 'attribute':

                        if key == 'item_link':
                            try:
                                # aタグを見つける
                                element = item.find_element(By.XPATH, detail_xpath)
                                attribute_value = element.get_attribute('href')
                                self.logger.debug(f"Attribute value: {attribute_value}")
                                elements_dict[key] = attribute_value
                            except Exception as e:
                                self.logger.error(f"Error finding element or attribute: {e}")
                                elements_dict[key] = None

                        else:
                            # 辞書のKeyを指定して値を代入
                            self.logger.debug(f"key: {key}")
                            elements_dict[key] = item.get_attribute(detail_xpath)

                    # htmlの子要素のTextを取得する
                    elif method == 'text':
                        self.logger.debug(f"key: {key}")

                        # 辞書のKeyを指定して値を代入
                        elements_dict[key] = self._get_element_text(element= item, text_pattern=text_pattern, text_xpath=detail_xpath)

                    else:
                        self.logger.error(f"意図してないmethodが指定されてる: {method}")
                        raise

                    self.logger.info(f"elements_dict:\n{elements_dict}")

                # 辞書データを追加
                data_list.append(elements_dict)

            self.logger.info(f"data_list: {data_list}")

            self.logger.info(f"******** _get_element end ********")

            return data_list


        except Exception as e:
            self.logger.error(f"elements_to_dict 処理中にエラーが発生: {e}")
            raise


# ----------------------------------------------------------------------------------
