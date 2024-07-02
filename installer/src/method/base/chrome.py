# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/4/5更新

# ----------------------------------------------------------------------------------
import os
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

from .utils import Logger


###############################################################



class ChromeManager:
    def __init__(self, debug_mode=False):
        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()


###############################################################
# ----------------------------------------------------------------------------------
    def get_chrome_driver_version(self):
    # ChromeDriverManagerでインストールされたChromeDriverのパスを取得
        chrome_driver_path = ChromeDriverManager().install()

        # ChromeDriverのバージョンはsubprocessを使って取得が必要
        result = subprocess.run([chrome_driver_path, '--version'], stdout=subprocess.PIPE)
        version = result.stdout.decode('utf-8').strip()
        return chrome_driver_path, version

# ----------------------------------------------------------------------------------
# Chromeセットアップ（動かす箇所にしか配置しない）(要初期化)

    def setup_chrome(self):
        try:
            chrome_driver_path, chrome_driver_version = self.get_chrome_driver_version()
            self.logger.warning(f"Installed ChromeDriver version: {chrome_driver_version}")

            chrome_options = Options()
            chrome_options.add_argument("--headless=new")  # ヘッドレスモードで実行
            chrome_options.add_argument(f"--window-position=0,0")
            # chrome_options.add_argument("--window-size=1440,900")  # ウィンドウサイズの指定
            chrome_options.add_argument("start-maximized")
            chrome_options.add_argument("--no-sandbox")
            # chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument('--lang=ja-JP')

            # ヘッドレスでの場合に「user-agent」を設定することでエラーを返すものを通すことができる
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.63 Safari/537.36')
            # chrome_options.add_extension(self._get_full_path('uBlock-Origin.crx'))  # iframe対策の広告ブロッカー
            # chrome_options.add_extension(self._get_full_path('hlifkpholllijblknnmbfagnkjneagid.crx'))  # CAPTCHA

            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_argument("--disable-translate")

            # chrome_options.add_argument("--disable-blink-features")
            # chrome_options.add_argument("--remote-debugging-port=9222")

            # ヘッドレス仕様のオプション
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option('prefs', {
                'credentials_enable_service': False,
                'profile': {
                    'password_manager_enabled': False
                }
            })

            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")

            chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # ブラウザが自動化されていることを示す機能を無効化
            chrome_options.add_argument("--disable-infobars")  #"Chrome is being controlled by automated test software" の情報バーを無効化



            service = Service(chrome_driver_path)
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