# coding: utf-8
# ----------------------------------------------------------------------------------
#! ここで定義して「Flow」で扱う
#! 引数はここで基本渡す。


# ----------------------------------------------------------------------------------
import os

# 自作モジュール
from .base.chrome import ChromeManager
from .base.spreadsheet_read import SpreadsheetRead
from .base.driverLogin import AutoLogin
from .base.driver_control import Base
from .base.DataFlameCreate import DataFlameCreate


from dotenv import load_dotenv

####################################################################################
# Chrome

class OverChrome(ChromeManager):
    def __init__(self, debug_mode=False):
        super().__init__(debug_mode)


    def setup_chrome(self) -> str:
        return super().setup_chrome()


####################################################################################
# スプシから読み込み

class StartSpreadsheetRead(SpreadsheetRead):
    def __init__(self, brand_id, debug_mode=False):
        sheet_url = os.getenv('SHEET_URL')
        index = 'ID'
        super().__init__(sheet_url, brand_id, index, debug_mode)


# スプシからブランド名を読み込む
    def get_name(self):
        name = 'ブランド名'
        field_name = 'get_name'
        return super().get_name(name, field_name)


# スプシからURLを読み込む
    def get_url(self):
        url = 'サイトURL'
        field_name= 'get_url'
        return super().get_url(url, field_name)


####################################################################################


class OverAutoLogin(AutoLogin):
    def __init__(self, chrome, discord_url, debug_mode=False):
        super().__init__(chrome, discord_url, debug_mode)


    def open_site(self, url):

        by_pattern='id'
        check_path='searchOrder'
        field_name='open_site'
        return super().open_site(url, by_pattern, check_path, field_name)


####################################################################################


class Drop(Base):
    def __init__(self, chrome, discord_url, debug_mode=False):
        super().__init__(chrome, discord_url, debug_mode)



    def drop_down_select(self, by_pattern, xpath, select_word, field_name='drop_down_select'):

        by_pattern='xpath'
        xpath="//ul[@id='searchOrderList']//a[contains(text(), '新着順')]"
        select_word='新着順'
        return super().drop_down_select(by_pattern, xpath, select_word, field_name)



####################################################################################


class GetData(DataFlameCreate):
    def __init__(self, chrome, discord_url, debug_mode=False):
        super().__init__(chrome, discord_url, debug_mode)


    def _sort_data(self, by_pattern, xpath, category_info, field_name):
        category_info = [
            ("商品ID", "attribute", "goodsid"),
            ("商品名", "xpath", "//p[@class='itemCard_name']"),
            ("状態", "xpath", "//p[@class='itemCard_status']"),
            ("価格", "xpath", "//p[contains(@class, 'itemCard_price')]")
        ]
        return super()._sort_data(by_pattern, xpath, category_info, field_name)

####################################################################################

####################################################################################

####################################################################################

####################################################################################
