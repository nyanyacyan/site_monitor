# coding: utf-8
# ----------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------
# 自作モジュール
from .driverLogin import AutoLogin
from .driverBase import Base
from .captcha_solve import TikTokCaptchaSolver


####################################################################################


class SiteLogin(AutoLogin):
    def __init__(self, chrome, debug_mode=False):
        super().__init__(chrome, debug_mode)


# ----------------------------------------------------------------------------------
# サイトを開くメソッド

    def open_site(self, url, by_pattern, userid_path, field_name):
        return super().open_site(url, by_pattern, userid_path, field_name)

####################################################################################


class SiteProgram(Base):
    def __init__(self, chrome, discord_url, debug_mode=False):
        super().__init__(chrome, discord_url, debug_mode)


# ----------------------------------------------------------------------------------
# 入力欄を探して入力

    def input_write(self, xpath, input_value, field_name):
        return super().input_write(xpath, input_value, field_name)

# ----------------------------------------------------------------------------------
# ボタンをクリック

    def btn_click(self, xpath, field_name):
        return super().btn_click(xpath, field_name)


# ----------------------------------------------------------------------------------
# ページがちゃんと表示されるまで待機

    def _handle_wait_loadpage(self, field_name):
        return super()._handle_wait_loadpage(field_name)


# ----------------------------------------------------------------------------------
# ページが切り替わった際に特定の要素が出るまで待機

    def _handle_wait_next_page(self, xpath, field_name):
        return super()._handle_wait_next_page(xpath, field_name)


####################################################################################


class Solve(TikTokCaptchaSolver):
    def __init__(self, api_key):
        super().__init__(api_key)


# ----------------------------------------------------------------------------------
# tiktoksolve

    def solve_captcha(self, cap_type, url1, url2):
        return super().solve_captcha(cap_type, url1, url2)


# ----------------------------------------------------------------------------------
