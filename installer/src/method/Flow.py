# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/4/17 更新

#* 流れ  【非同期処理して並列処理】検索ワードを含んだURLにて検索→サイトを開く→解析→ブランド名、商品名、価格のリスト作成→バイナリデータへ保存→保存されてるバイナリデータ（保存した過去データ）を復元→現在のデータと突き合わせる→今までと違うものをリスト化→通知する
# ----------------------------------------------------------------------------------
import os, time


# 自作モジュール
from .OverRide import OverChrome, StartSpreadsheetRead, OverAutoLogin
from .base.utils import Logger
# ----------------------------------------------------------------------------------
####################################################################################
# 一連の流れ

class Flow:
    def __init__(self, brand_id, debug_mode=False):
        self.brand_id = brand_id

        # インスタンス
        self.chrome.inst = OverChrome(debug_mode=debug_mode)
        self.chrome = self.chrome.inst
        self.discord_url = os.getenv('DISCORD_BOT_URL')

        self.start_spreadsheet = StartSpreadsheetRead(brand_id=self.brand_id)
        self.auto_login = OverAutoLogin(chrome=self.chrome, discord_url=self.discord_url, debug_mode=debug_mode)
        self.logger = self.setup_logger(debug_mode=debug_mode)

####################################################################################
# ----------------------------------------------------------------------------------

# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# スプシから「ブランド名」を読み込む
#todo サイトを開く
# 専用のURLを使う
# 画面領域は広く取る
# 新着順に並び替える

#todo 商品のリスト読み込む
# ブランド名（各メソッドに埋め込めるようにする）
# ジャンル
# 商品状態
# DataFrameにして比較できるようにする

#todo 過去のバイナリデータを読み込む
# バイナリデータを読み込むクラスを作成
# バイナリデータをdfにして比較できるようにする

#todo 比較して「過去のデータにない商品」を真偽値で示す
# 真偽値にてFalseだった場合には処理を終了

#todo 比較して「過去のデータにない商品」をピックアップする

#todo 最新のデータをバイナリデータで保存

#todo 新着商品がある場合に通知


    def single_process(self, field_name='monitor_flow'):
        self.logger.debug(f"***** {field_name} 開始*****")

        brand_name = self.start_spreadsheet.get_name()
        url = self.start_spreadsheet.get_url()

        self.auto_login.open_site(url=url)





        self.logger.debug(f"***** {field_name} 開始*****")





# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    def process(self, ):
        self.logger.debug(f"***** Flow.process 開始 *****")

        self.get_name()
        self.get_url()



        self.logger.debug(f"***** Flow.process 終了 *****")



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施


