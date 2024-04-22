# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/4/22 更新

# ----------------------------------------------------------------------------------
import os
import time
import pickle
import pandas as pd
from selenium.webdriver.common.by import By
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


class DFCreate:
    def __init__(self, chrome, discord_url, debug_mode=False):
        self.chrome = chrome
        self.discord_url = discord_url
        self.none_checker = NoneChecker(debug_mode=debug_mode)
        self.logger = self.setup_logger(debug_mode=debug_mode)

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
# 受け取ったデータをDataFrameに書き換える
#TODO: resultがNoneかどうかをチェックする

    def _convert_to_dataframe(self, data):
        # 辞書データをDataFrameに変換
        df = pd.DataFrame(data)
        return df


# ----------------------------------------------------------------------------------
# 指定した要素の値を取得
#TODO: resultがNoneかどうかをチェックする

    def _get_element_value(self, by_pattern, xpath, search_name, field_name):
        try:
            # 特定の要素の値を取得する。
            element = self.chrome.find_element(self._locator_select(by_pattern), xpath)
            search_value = element.get_attribute(search_name)

            self.logger.debug(f"{field_name} search_value: {search_value}")

            return search_value

        except NoSuchElementException as e:
            self.logger.error(f"{field_name} 要素が見つかりません。")
            raise


# ----------------------------------------------------------------------------------
# リストを作成してcategory_nameをColumnにしてデータを整理
#TODO: resultがNoneかどうかをチェックする

    def _sort_data(self, by_pattern, xpath, category_info, field_name):

        # 全体から対象のリストを取得
        item_boxs = self.chrome.find_elements(self._locator_select(by_pattern), xpath)

        # データ形式を指定して内包表記にて並び替える
        # category_name:[_, _] という形式にするように指定してる（初期化）
        data = {category_name: [] for category_name, _, _ in category_info}

        # 取得したリストを一つのものから中身を抽出する
        for item_box in item_boxs:
            # category_infoという得たデータから３つの情報を抜き取る
            for category_name, catch_by, catch_path in category_info:
                # もしcatch_pathがattributeだった場合にはその値を記す
                if catch_path == "attribute":
                    element_value = item_box.get_attribute(catch_path)

                else:
                # 得た情報から処理を行って各それぞれの要素を取得する
                    element = item_box.find_element(catch_by, catch_path)
                    element_value = element.text
                # 取得した各データを指定したデータの箱に入れていく
                data[category_name].append(element_value)

        self.logger.debug(f"{field_name} data: {data}")

        return data


# ----------------------------------------------------------------------------------
#TODO: テスト期間中はDiscordに通知するようにする

    def diff_checker(self, new_df, old_df, diff_list_create, notify, field_name):
        current_time = time.time()
        if new_df.equals(old_df):
            self.logger.info(f"{field_name} {current_time} 前回のデータとの差異なし")


        else:
            self.logger.warning(f"{field_name} {current_time} 新商品が入荷")
            diff_list = diff_list_create()
            list_notify = notify()


# ----------------------------------------------------------------------------------
# pickleデータを通常のデータへ変換
#TODO: resultがNoneかどうかをチェックする

    def _pkl_to_utf8(self, pkl_file, field_name):
        try:
            with open(pkl_file, 'rb') as f:
                binary_data = f.read()

                text_data = binary_data.decode('utf-8')

                self.logger.debug(f"{field_name} text_data: {text_data}")

                return text_data

        except FileNotFoundError as e:
            self.logger.error(f"{field_name} {pkl_file}が見つまりません{e}")
            raise

        except UnicodeDecodeError as e:  # デコードエラーの処理
            self.logger.error(f"{field_name} {pkl_file}のデコード中にエラーが発生: {e}")
            raise

        except Exception as e:
            self.logger.error(f"{field_name} {pkl_file} pickleデータを変換中にエラーが発生{e}")
            raise


# ----------------------------------------------------------------------------------
# pickleデータへの変換

    def _to_pkl(self, new_data, fullpath, field_name):
        try:
            with open(f'{fullpath}.pkl', 'wb') as f:
                binary_data = pickle.dump(new_data, f)

                # Noneかどうかを確認
                self.none_checker.any_checker(result=binary_data)

                self.logger.debug(f"{field_name} {new_data}からバイナリデータへの書き込みが完了")

        except IOError as e:  # IOErrorを捕捉（ファイル関連のエラー）
            self.logger.error(f"{field_name} ファイル操作中にエラーが発生 {e}")
            raise

        except pickle.PickleError as e:  # pickleのエラーを捕捉
            self.logger.error(f"{field_name} データのpickle化中にエラーが発生 {e}")
            raise

        except Exception as e:
            self.logger.error(f"{field_name} {new_data} pickleデータを変換中にエラーが発生{e}")
            raise


# ----------------------------------------------------------------------------------
#TODO: resultがNoneかどうかをチェックする

    def diff_data_list_create(self, new_df, old_df, key_column, field_name):
        try:
            # on=[key_column]が「Key」となるデータ
            # how='left'は左側（new_df）を基準する（old_dfにしかないデータはNaN）
            result = pd.merge(new_df, old_df, on=[key_column], how='left', indicator=True)

            self.logger.debug(f"{field_name} result: {result}")

            # resultの中のresultの部分の_mergeのColumnをleft_onlyだけする
            diff_data = result[result['_merge'] == 'left_only']
            self.logger.debug(f"{field_name} diff_data: {diff_data}")

            # dfより「_merge」（被ってる部分）を削除
            diff_data = diff_data.drop(columns=['_merge'])

            return diff_data

        except Exception as e:
            self.logger.error(f"{field_name} 差分データを作成中にエラーが発生: {e}")




# ----------------------------------------------------------------------------------
# 通知に掲載するためのデフォルトのデータを整理するためのメソッド
#TODO: resultがNoneかどうかをチェックする

    def notify_sentence_create(self, diff_df, Key_title, value1_title, value2_title, value3_title, field_name):
        sentences = []
        self.logger.debug(f"{field_name} diff_df: {diff_df}")

        try:
            for _, row in diff_df.iterrows():
                sentence = f"{Key_title}: {row['Key']}, {value1_title}: {row['Value1']}, {value2_title}: {row['Value2']}, {value3_title}: {row['Value3']}"
                sentences.append(sentence)

            all_sentences = "\n".join(sentences)
            self.logger.debug(f"{field_name} sentences\n{all_sentences}")

            return all_sentences

        except KeyError as e:
            self.logger.error(f"{field_name} キーのエラー、データフレームに期待されるカラムが存在しない: {e}")

        except Exception as e:
            self.logger.error(f"{field_name} 差分データを修正中にエラーが発生: {e}")



# ----------------------------------------------------------------------------------
