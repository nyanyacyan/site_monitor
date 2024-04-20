# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/4/3更新

# ----------------------------------------------------------------------------------
import os

from installer.src.method.DebugScreenshot.utils import Logger
from installer.src.method.base.errorNotify import ErrorDiscord


####################################################################################


class APIErrorResponseException(Exception):
    def __init__(self, message, error_code, debug_mode=False):
        super().__init__(f"エラー {error_code}: {message}")
        self.logger = self.setup_logger(debug_mode=debug_mode)
        self.error_discord = ErrorDiscord(chrome=self.chrome, discord_url=self.discord_url)


####################################################################################
# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------


    def tiktok_solve_api(self, response_body):
        if response_body.get('success') == False:
            error_msg = response_body.get('errorMsg')
            error_code = response_body.get('errorCode')

            self.logger.error(f"レスポンス{error_code}: {error_msg}")

