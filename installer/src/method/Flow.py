# coding: utf-8
#! ここにChromeを展開する
#! なるべくここでは引数を渡さない
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

# 2023/4/17 更新

#* 流れ  【非同期処理して並列処理】検索ワードを含んだURLにて検索→サイトを開く→解析→ブランド名、商品名、価格のリスト作成→バイナリデータへ保存→保存されてるバイナリデータ（保存した過去データ）を復元→現在のデータと突き合わせる→今までと違うものをリスト化→通知する
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


import os, time
import asyncio
import functools
import pandas as pd
from datetime import datetime
from const import SiteUrl

# 自作モジュール
from .base.chrome import ChromeManager
from .gss_login import StartSpreadsheetRead, OverAutoLogin, Drop
from .base.utils import Logger
from .base.driver_get_element import GetElement
from .base.pkl_change import PickleControl
from .diff_df_processing import DiffDfProcess
from .base.notify import LineNotify, DiscordNotify


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 一連の流れ

class Flow:
    def __init__(self, account_id, debug_mode=False):
        self.sheet_url = SiteUrl.sheet.value
        self.account_id = account_id

        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        # Chrome
        chrome_instance = ChromeManager()
        self.chrome = chrome_instance.setup_chrome()

        # インスタンス
        self.start_spreadsheet = StartSpreadsheetRead(sheet_url=self.sheet_url, account_id=account_id)
        self.auto_login = OverAutoLogin(chrome=self.chrome, debug_mode=debug_mode)
        self.drop_down = Drop(chrome=self.chrome, debug_mode=debug_mode)
        self.get_element = GetElement(chrome=self.chrome, debug_mode=debug_mode)
        self.pkl_control = PickleControl(chrome=self.chrome, debug_mode=debug_mode)
        self.diff_df_processing = DiffDfProcess(chrome=self.chrome, debug_mode=debug_mode)
        self.line = LineNotify(debug_mode=debug_mode)
        self.discord = DiscordNotify(debug_mode=debug_mode)

        # 現時刻を掲載
        self.current_date = datetime.now().strftime('%m-%d %H:%M')



###############################################################
# ----------------------------------------------------------------------------------


    def single_process(self):
        self.logger.debug(f"*****{self.account_id} process start*****")

        self.logger.info(f"self.sheet_url: {self.sheet_url}")
        self.logger.info(f"self.account_id: {self.account_id}")

        # 指定のスプシから情報を取得
        brand_name = self.start_spreadsheet.get_brand_name()
        url = self.start_spreadsheet.get_url()

        self.logger.info(f"brand_name: {brand_name}, url: {url}")

        # 指定のurlにアクセス
        self.auto_login.sever_open_site(
            url=url,
            notify_func=self.discord.discord_image_notify
        )


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

        # DataFrameとDataFrameを突合させて差分の真偽値別に処理をする
        self.diff_df_processing.diff_df_processing(
            data=dict_data,
            route='result_output/pickles',
            pkl_name=f' {self.account_id} ',
            head_num=30,
            select_column='goodsid',
            opening_message=f'{self.current_date}\n新しい商品が入荷を検知しました。\n下記の商品をご確認ください。\n',
            notify_func=self.line.line_notify,
            save_func=self.pkl_control.df_pickle,
            save_pickle_path=f'result_output/pickles/{self.account_id}.pkl',
            account_id=self.account_id
        )

        self.logger.debug(f"*****{self.account_id} process end*****")

        self.logger.warning(f"{self.account_id} 処理、完了しました。")


# ----------------------------------------------------------------------------------
# 非同期処理に変換

    async def single_process_async(self):
        # 現在、行ってるイベントループを取得
        loop = asyncio.get_running_loop()

        # ブロッキング、実行タイミング、並列処理などを適切に行えるように「functools」にてワンクッション置いて実行
        await loop.run_in_executor(None, functools.partial(self.single_process))


# ----------------------------------------------------------------------------------


    def get_pickle_data(self):
        self.logger.debug(f"*****{self.account_id} get_pickle_data start*****")

        self.logger.info(f"self.sheet_url: {self.sheet_url}")
        self.logger.info(f"self.account_id: {self.account_id}")

        # 指定のスプシから情報を取得
        brand_name = self.start_spreadsheet.get_brand_name()
        url = self.start_spreadsheet.get_url()

        self.logger.info(f"brand_name: {brand_name}, url: {url}")

        # 指定のurlにアクセス
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

        first_df = pd.DataFrame(dict_data)

        self.pkl_control.df_pickle(
            df=first_df,
            save_pickle_path=f'installer/result_output/pickles/{self.account_id}.pkl'
        )

        self.logger.debug(f"*****{self.account_id} get_pickle_data end*****")

        self.logger.info(f"{self.account_id}の最初に作成するpickleデータを作成完了")


# ----------------------------------------------------------------------------------
# 非同期処理に変換

    async def get_pickle_data_async(self):
        # 現在、行ってるイベントループを取得
        loop = asyncio.get_running_loop()

        # ブロッキング、実行タイミング、並列処理などを適切に行えるように「functools」にてワンクッション置いて実行
        await loop.run_in_executor(None, functools.partial(self.get_pickle_data))


# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# **********************************************************************************