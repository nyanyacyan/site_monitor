# coding: utf-8
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# 自作モジュール
from .driverLogin import AutoLogin
from .driver_control import Base
from .captcha_solve import TikTokSolver
from .spreadsheet_read import SpreadsheetRead


####################################################################################


class SiteLogin(AutoLogin):
    def __init__(self, chrome, discord_url, debug_mode=False):
        super().__init__(chrome, discord_url, debug_mode)


# サイトを開くメソッド
    def open_site(self, url, by_pattern, check_path, field_name):
        return super().open_site(url, by_pattern, check_path, field_name)

####################################################################################


class SiteProgram(Base):
    def __init__(self, chrome, discord_url, debug_mode=False):
        super().__init__(chrome, discord_url, debug_mode)


# 入力欄を探して入力
    def input_write(self, by_pattern, xpath, input_value, field_name):
        return super().input_write(by_pattern, xpath, input_value, field_name)


# 入力欄を探して要素を出力
    def get_element(self, by_pattern, xpath, field_name):
        return super().get_element(by_pattern, xpath, field_name)


# ボタンをクリック
    def btn_click(self, by_pattern, xpath, field_name):
        return super().btn_click(by_pattern, xpath, field_name)


# ページがちゃんと表示されるまで待機
    def _handle_wait_loadpage(self, field_name):
        return super()._handle_wait_loadpage(field_name)


# ページが切り替わった際に特定の要素が出るまで待機
    def _handle_wait_next_page(self, xpath, field_name):
        return super()._handle_wait_next_page(xpath, field_name)



    def random_btn_click(self, by_pattern, xpath, field_name, timeout=10) -> None:
        return super().random_btn_click(by_pattern, xpath, field_name, timeout)

####################################################################################


class Solve(TikTokSolver):
    def __init__(self, api_key, discord_url, debug_mode=False):
        super().__init__(api_key, discord_url, debug_mode)


# tiktoksolve
    def process(self, cw_by_pattern, cw_xpath, c3_by_pattern, c3_xpath, ss_by_pattern, ss_xpath, o_by_pattern, o_xpath, i_by_pattern, i_xpath, by_pattern, xpath):
        return super().process(cw_by_pattern, cw_xpath, c3_by_pattern, c3_xpath, ss_by_pattern, ss_xpath, o_by_pattern, o_xpath, i_by_pattern, i_xpath, by_pattern, xpath)


####################################################################################
# スプシ読み込んだデータから抽出

class OverSpreadsheetRead(SpreadsheetRead):
    def __init__(self, sheet_url, account_id, debug_mode=False):
        super().__init__(sheet_url, account_id, debug_mode)


    def get_input_text(self):
        return super().get_input_text()


####################################################################################
