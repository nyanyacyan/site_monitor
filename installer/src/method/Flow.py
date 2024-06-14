# coding: utf-8
#! ここにChromeを展開する
#! なるべくここでは引数を渡さない
# ----------------------------------------------------------------------------------
# 2023/4/17 更新

#* 流れ  【非同期処理して並列処理】検索ワードを含んだURLにて検索→サイトを開く→解析→ブランド名、商品名、価格のリスト作成→バイナリデータへ保存→保存されてるバイナリデータ（保存した過去データ）を復元→現在のデータと突き合わせる→今までと違うものをリスト化→通知する
# ----------------------------------------------------------------------------------


import os, time
import pandas as pd
from datetime import datetime

# 自作モジュール
from .base.chrome import ChromeManager
from .gss_login import StartSpreadsheetRead, OverAutoLogin, Drop
from .base.utils import Logger
from .base.driver_get_element import GetElement
from .base.df_Create import DFCreate


# ----------------------------------------------------------------------------------
###############################################################

# 一連の流れ

class Flow:
    def __init__(self, sheet_url, account_id, debug_mode=False):
        self.sheet_url = sheet_url
        self.account_id = account_id

        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        # Chrome
        chrome_instance = ChromeManager()
        self.chrome = chrome_instance.setup_chrome()

        # インスタンス
        self.start_spreadsheet = StartSpreadsheetRead(sheet_url=sheet_url, account_id=account_id)
        self.auto_login = OverAutoLogin(chrome=self.chrome, debug_mode=debug_mode)
        self.drop_down = Drop(chrome=self.chrome, debug_mode=debug_mode)
        self.get_element = GetElement(chrome=self.chrome, debug_mode=debug_mode)
        DFCreate(chrome=self.chrome, debug_mode=debug_mode)

        # 現時刻を掲載
        self.current_date = datetime.now().strftime('%m-%d %H:%M')



###############################################################


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



    def single_process(self, field_name='monitor_flow'):
        self.logger.debug(f"***** {field_name} {self.account_id} 開始*****")

#TODO ここからの流れをgss_loginにて定義してリトライができるようにする
        self.logger.info(f"self.sheet_url: {self.sheet_url}")
        self.logger.info(f"self.account_id: {self.account_id}")

        brand_name = self.start_spreadsheet.get_brand_name()
        url = self.start_spreadsheet.get_url()

        self.logger.info(f"brand_name: {brand_name}, url: {url}")
        self.auto_login.open_site(url=url)


        # 商品のリスト読み込む
        dict_data =self.get_element.elements_to_dict(
            items_xpath="//div[@id='searchResultListWrapper']//li[@class='js-favorite itemCard']",
            data_xpaths={
                'goodsid':  {'method': 'attribute', 'detail_xpath': 'goodsid'},
                'brand': {'method': 'text', 'detail_xpath': ".//p[@class='itemCard_brand']"},
                'name': {'method': 'text', 'detail_xpath': ".//p[@class='itemCard_name']"},
                'status': {'method': 'text', 'detail_xpath': ".//p[@class='itemCard_status']"},
                'price': {'method': 'text', 'detail_xpath': ".//p[contains (@class, 'itemCard_price')]"}
            },
        )
        time.sleep(2)

        # DataFrameにして比較できるようにする
        df = pd.DataFrame(dict_data)
        self.logger.info(f"df: \n{df.head(5)}")

        df.to_csv(f'installer/result_output/{self.account_id}_{self.current_date}.csv')



        #todo 過去のバイナリデータを読み込む
        # バイナリデータを読み込むクラスを作成
        # バイナリデータをdfにして比較できるようにする





        #todo 比較して「過去のデータにない商品」を真偽値で示す
        # 真偽値にてFalseだった場合には処理を終了

        #todo 比較して「過去のデータにない商品」をピックアップする

        #todo 最新のデータをバイナリデータで保存

        #todo 新着商品がある場合に通知

        self.logger.debug(f"***** {field_name}  {self.account_id} 終了*****")





# ----------------------------------------------------------------------------------
#todo 各メソッドをまとめる

    def process(self, ):
        self.logger.debug(f"***** Flow.process 開始 *****")

        self.get_name()
        self.get_url()



        self.logger.debug(f"***** Flow.process 終了 *****")



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# テスト実施


