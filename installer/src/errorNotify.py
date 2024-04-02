# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/3/29更新

# ----------------------------------------------------------------------------------
import os,requests
from datetime import datetime

# 自作モジュール
from logger.debug_logger import Logger


# ----------------------------------------------------------------------------------
class ErrorDiscord:
    def __init__(self, chrome, discord_url, screenshot_dir, debug_mode=False):
        self.chrome = chrome
        self.discord_url = discord_url
        self.screenshot_dir = screenshot_dir

        self.logger = self.setup_logger(debug_mode=debug_mode)


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()

# ----------------------------------------------------------------------------------
# スクショをタイムスタンプ付きで撮影

    def _get_screenshot(self, screenshot_title):
        # スクショ用のタイムスタンプ
        timestamp = datetime.now().strftime("%m-%d_%H-%M")

        # タイムスタンプ付きの名前
        filename = f"{screenshot_title}{timestamp}.png"

        # フルパスかどうかを確認
        if not os.path.isabs(self.screenshot_dir):
            base_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_dir, self.screenshot_dir, filename)

        # フルパスだったらファイル名を足すだけ
        else:
            full_path = os.path.join(self.screenshot_dir, filename)

        if self.chrome.save_screenshot(full_path):
            self.logger.debug(f"スクリーンショットを保存: {full_path}")

        else:
            self.logger.error(f"スクリーンショットを保存に失敗。。。")

        return full_path


# ----------------------------------------------------------------------------------
# discordでの通知

    def _discord(self, **kwargs):
        #* 引数
        comment = kwargs.get('comment')
        error_message = kwargs.get('error_message')
        discord_url = kwargs.get('discord_url')
        screenshot_path = kwargs.get('screenshot_path')


        content = f"【WARNING】{comment}: {error_message}"

        with open(screenshot_path, 'rb') as file:
            files = {"file": (screenshot_path, file, "image/png")}
            response = requests.post(discord_url, data={"content": content}, files=files)

            self.logger.debug(f"Discordへの通知結果: {response.status_code} : {error_message}")


# ----------------------------------------------------------------------------------
# errorのスクショをdiscordにて通知

    def error_screenshot_discord(self, screenshot_title, **kwargs):
        kwargs['screenshot_path'] = self._get_screenshot(screenshot_title)
        self._discord(**kwargs)

        # 最後にエラーで返す
        raise Exception(kwargs.get('error_message'))


#  ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------