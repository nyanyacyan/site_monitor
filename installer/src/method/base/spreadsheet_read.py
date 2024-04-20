# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/3/29更新

# ----------------------------------------------------------------------------------
import os
import requests
import pandas as pd
import io

from dotenv import load_dotenv

from .utils import Logger, NoneChecker

load_dotenv()

####################################################################################

class SpreadsheetRead:
    def __init__(self, sheet_url, brand_id, index, debug_mode=False):
        self.sheet_url = sheet_url
        self.brand_id = brand_id
        self.index = index
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.none = NoneChecker()

        self.df = self.load_spreadsheet()


####################################################################################
# ----------------------------------------------------------------------------------

# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# スプシ読み込みからpandasでの解析→文字列データを仮想的なファイルを作成

    def load_spreadsheet(self):
        # スプシデータにアクセス
        spreadsheet = requests.get(self.sheet_url)

        # バイナリデータをutf-8に変換する
        # on_bad_lines='skip'→パラメータに'skip'を指定することで、不正な形式スキップして表示できる（絵文字、特殊文字）
        # StringIOは、文字列データをファイルのように扱えるようにするもの。メモリ上に仮想的なテキストファイルを作成する
        # .set_index('account')これによってIndexを'account'に設定できる。
        string_data = spreadsheet.content.decode('utf-8')
        data_io = io.StringIO(string_data)

        df = pd.read_csv(data_io, on_bad_lines='skip')

        self.logger.debug(f"columns: {df.columns}")

        # Indexを「brand_id」にしたデータフレームを返してる
        return df.set_index(self.index)


# ----------------------------------------------------------------------------------
# Columnまでの公式を入れ込んだ関数

    def _sort_column_name(self, column_name):
        sort_value = self.df.loc[self.brand_id, column_name]
        return sort_value


# ----------------------------------------------------------------------------------
# アカウントIDの抽出

    def get_id(self, id, field_name):

        self.logger.debug(f"***** {field_name} 開始*****")


        get_id = self._sort_column_name(id)
        self.logger.debug(f"{field_name} get_id: {get_id}")


        self.logger.debug(f"***** {field_name} 終了*****")

        return get_id


# ----------------------------------------------------------------------------------
# パスの抽出

    def get_pass(self, password, field_name):

        self.logger.debug(f"***** {field_name} 開始*****")


        get_password = self._sort_column_name(password)
        self.logger.debug(f"{field_name} get_password: {get_password}")


        self.logger.debug(f"***** {field_name} 終了*****")

        return get_password

# ----------------------------------------------------------------------------------
# 検索ワードの抽出

    def get_search_word(self, search_word, field_name):

        self.logger.debug(f"***** {field_name} 開始*****")


        get_search_word = self._sort_column_name(search_word)
        self.logger.debug(f"{field_name} get_search_word: {get_search_word}")


        self.logger.debug(f"***** {field_name} 終了*****")

        return get_search_word


# ----------------------------------------------------------------------------------
# 検索時、前から何番目のものを選択するのかを抽出

    def get_select_number(self, select_number, field_name):

        self.logger.debug(f"***** {field_name} 開始*****")


        get_select_number = self._sort_column_name(select_number)
        self.logger.debug(f"{field_name} get_select_number: {get_select_number}")


        self.logger.debug(f"***** {field_name} 終了*****")

        return get_select_number

# ----------------------------------------------------------------------------------
# DMテキスト部分の抽出

    def get_text(self, text, field_name):

        self.logger.debug(f"***** {field_name} 開始*****")


        get_text = self._sort_column_name(text)
        self.logger.debug(f"{field_name} get_text: {get_text}")


        self.logger.debug(f"***** {field_name} 終了*****")

        return get_text

# ----------------------------------------------------------------------------------
# URL部分の抽出

    def get_url(self, url, field_name):

        self.logger.debug(f"***** {field_name} 開始*****")


        get_url = self._sort_column_name(url)
        self.logger.debug(f"{field_name} get_url: {get_url}")


        self.logger.debug(f"***** {field_name} 終了*****")

        return get_url

# ----------------------------------------------------------------------------------
# 名前の抽出

    def get_name(self, name, field_name):

        self.logger.debug(f"***** {field_name} 開始*****")


        get_name = self._sort_column_name(name)
        self.logger.debug(f"{field_name} get_name: {get_name}")


        self.logger.debug(f"***** {field_name} 終了*****")

        return get_name

# ----------------------------------------------------------------------------------