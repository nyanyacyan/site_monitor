# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/3/29更新

# ----------------------------------------------------------------------------------
import os
import requests
import pandas as pd
import io

from dotenv import load_dotenv

from method.utils import Logger, NoneChecker

load_dotenv()

####################################################################################

class SpreadsheetRead:
    def __init__(self, sheet_url, account_id, debug_mode=False):
        self.sheet_url = sheet_url
        self.account_id = account_id
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

        # Indexを「account_id」にしたデータフレームを返してる
        return df.set_index('アカウントNo.')


# ----------------------------------------------------------------------------------
# Columnまでの公式を入れ込んだ関数

    def _sort_column_name(self, column_name):
        sort_value = self.df.loc[self.account_id, column_name]
        return sort_value


# ----------------------------------------------------------------------------------
# アカウントIDの抽出

    def get_id(self):
        return self._sort_column_name('ユーザーネーム')


# ----------------------------------------------------------------------------------
# パスの抽出

    def get_pass(self):
        return self._sort_column_name('ユーザーパスワード')


# ----------------------------------------------------------------------------------
# 検索ワードの抽出

    def get_search_word(self):
        return self._sort_column_name('検索ワード')


# ----------------------------------------------------------------------------------
# 検索時、前から何番目のものを選択するのかを抽出

    def get_select_number(self):
        return self._sort_column_name('選択No.')


# ----------------------------------------------------------------------------------
# DMテキスト部分の抽出

    def get_dm_text(self):
        return self._sort_column_name('DM送付コメント')


# ----------------------------------------------------------------------------------