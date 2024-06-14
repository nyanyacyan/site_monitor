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
    def __init__(self, sheet_url, account_id, debug_mode=False):
        self.sheet_url = sheet_url
        self.account_id = account_id

        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        self.none = NoneChecker()

        self.df = self.load_spreadsheet()


####################################################################################
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

        # Indexを「account_id」にしたデータフレームを返してる
        return df.set_index('ID')


# ----------------------------------------------------------------------------------
# Columnまでの公式を入れ込んだ関数

    def _sort_column_name(self, column_name):
        sort_value = self.df.loc[self.account_id, column_name]
        return sort_value


# ----------------------------------------------------------------------------------
# アカウントIDの抽出

    def get_id(self):
        get_id = self._sort_column_name('ユーザーネーム')
        self.logger.debug(f"get_id: {get_id}")

        return get_id


# ----------------------------------------------------------------------------------
# パスの抽出

    def get_pass(self):
        get_pass = self._sort_column_name('ユーザーパスワード')
        self.logger.debug(f"get_pass: {get_pass}")

        return get_pass


# ----------------------------------------------------------------------------------
# 検索ワードの抽出

    def get_search_word(self):
        get_search_word = self._sort_column_name('検索ワード')
        self.logger.debug(f"get_search_word: {get_search_word}")

        return get_search_word


# ----------------------------------------------------------------------------------
# 検索時、前から何番目のものを選択するのかを抽出

    def get_select_number(self):
        get_select_number = self._sort_column_name('選択No.')
        self.logger.debug(f"get_select_number: {get_select_number}")

        return get_select_number


# ----------------------------------------------------------------------------------
# DMテキスト部分の抽出

    def get_dm_text(self):
        get_dm_text = self._sort_column_name('DM送付コメント')
        self.logger.debug(f"get_dm_text: {get_dm_text}")

        return get_dm_text


# ----------------------------------------------------------------------------------
# ブランド名 抽出

    def get_brand_name(self):
        get_brand_name = self._sort_column_name('brand_name')
        self.logger.debug(f"get_brand_name: {get_brand_name}")

        return get_brand_name


# ----------------------------------------------------------------------------------
# URL 抽出

    def get_url(self):
        get_url = self._sort_column_name('url')
        self.logger.debug(f"get_url: {get_url}")

        return get_url


# ----------------------------------------------------------------------------------