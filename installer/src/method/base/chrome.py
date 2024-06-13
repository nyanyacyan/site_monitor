# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/4/5更新

# ----------------------------------------------------------------------------------
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from .utils import Logger


####################################################################################


class ChromeManager:
    def __init__(self, debug_mode=False):
        self.logger = self.setup_logger(debug_mode=debug_mode)


####################################################################################
# ----------------------------------------------------------------------------------

# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# Chromeセットアップ（動かす箇所にしか配置しない）(要初期化)

    def setup_chrome(self) -> str:
        try:
            chrome_options = Options()
            # chrome_options.add_argument("--headless")  # ヘッドレスモードで実行
            chrome_options.add_argument(f"--window-position=0,0")
            chrome_options.add_argument("--window-size=1440,900")  # ウィンドウサイズの指定
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_extension(self._get_full_path('uBlock-Origin.crx'))  # iframe対策の広告ブロッカー
            # chrome_options.add_extension(self._get_full_path('hlifkpholllijblknnmbfagnkjneagid.crx'))  # CAPTCHA


            service = Service(ChromeDriverManager().install())
            chrome = webdriver.Chrome(service=service, options=chrome_options)

            return chrome

        except WebDriverException as e:
            self.logger.error(f"webdriverでのエラーが発生: {e}")
            raise

        except Exception as e:
            self.logger.error(f"インスタンス化に失敗: {e}")
            raise

# ----------------------------------------------------------------------------------
# chrome拡張機能のフルパス生成

    def _get_full_path(self, file_name) -> str:

        # 親要素のディレクトリに移動
        method_dir = os.path.dirname(os.path.abspath(__file__))

        src_dir = os.path.dirname(method_dir)

        # スクショ保管場所の絶対path
        input_data_dir = os.path.join(src_dir, 'input_data/')

        full_path = os.path.join(input_data_dir, file_name)
        self.logger.debug(f"full_path: {full_path}")

        return full_path


# ----------------------------------------------------------------------------------