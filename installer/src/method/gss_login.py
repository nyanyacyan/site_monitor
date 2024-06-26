# coding: utf-8
# ----------------------------------------------------------------------------------
#! ここで定義して「Flow」で扱う
#! 引数はここで基本渡す。


# ----------------------------------------------------------------------------------
import time

# 自作モジュール
from .base.spreadsheet_read import SpreadsheetRead
from .base.driverLogin import AutoLogin
from .base.driver_control import Operation
from .base.df_Create import DFCreate
from .base.utils import Logger


####################################################################################

# スプシから読み込み

class StartSpreadsheetRead(SpreadsheetRead):
    def __init__(self, sheet_url, account_id, debug_mode=False):
        super().__init__(sheet_url, account_id, debug_mode)


# スプシからブランド名を読み込む
    def _sort_brand_name(self):
        column_name = 'brand_name'
        return super()._sort_column_name(column_name)


# スプシからサイトURLを読み込む
    def _sort_site_url(self):
        column_name = 'url'
        return super()._sort_column_name(column_name)


####################################################################################


class OverAutoLogin(AutoLogin):
    def __init__(self, chrome, debug_mode=False):
        super().__init__(chrome, debug_mode)


    def sever_open_site(self, url, notify_func):
        by_pattern='id'
        check_path='searchOrder'
        field_name='open_site'
        return super().sever_open_site(url, by_pattern, check_path, notify_func, field_name)




####################################################################################


class Drop(Operation):
    def __init__(self, chrome, debug_mode=False):
        super().__init__(chrome, debug_mode)


    def drop_down_select(self, by_pattern, xpath, select_word, field_name='drop_down_select'):
        by_pattern='xpath'
        xpath="//ul[@id='searchOrderList']//a[contains(text(), '新着順')]"
        select_word='新着順'
        return super().drop_down_select(by_pattern, xpath, select_word, field_name)


####################################################################################


class GetData(DFCreate):
    def __init__(self, chrome, debug_mode=False):
        super().__init__(chrome, debug_mode)


    def _getSiteData(self, by_pattern, xpath, category_info, field_name):
        category_info = [
            ("商品ID", "attribute", "goodsid"),
            ("商品名", "xpath", "//p[@class='itemCard_name']"),
            ("状態", "xpath", "//p[@class='itemCard_status']"),
            ("価格", "xpath", "//p[contains(@class, 'itemCard_price')]")
        ]
        return super()._sort_data(by_pattern, xpath, category_info, field_name)


####################################################################################


class GssLogin:
    def __init__(self, sheet_url, account_id, chrome, debug_mode=False) -> None:
        self.chrome = chrome

        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        self.sheet_url = sheet_url
        self.account_id = account_id

        # インスタンス化
        self.gss_read = StartSpreadsheetRead(sheet_url=self.sheet_url, account_id=self.account_id, chrome=self.chrome, debug_mode=debug_mode)
        self.auto_login = OverAutoLogin(chrome=self.chrome, debug_mode=debug_mode)



    def process(self):
        try:
            self.logger.info(f"***** {self.account_id} process 開始 *****")

            # スプシから情報を取得
            brand_name = self.gss_read._sort_brand_name()
            site_url = self.gss_read._sort_site_url()

            self.logger.debug(f"brand_name: {brand_name}, site_url: {site_url} ")

            time.sleep(2)

            # サイトを開く
            self.auto_login.open_site(site_url)
            self.logger.debug(f"brand_name: {brand_name}, site_url: {site_url} ")


            self.logger.info(f"***** {self.account_id} process 終了 *****")


        except Exception as e:
            self.logger.error(f"{self.account_id} process: 処理中にエラーが発生{e}")


####################################################################################



####################################################################################



####################################################################################
