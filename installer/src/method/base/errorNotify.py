# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/3/29更新

# ----------------------------------------------------------------------------------
import os,requests
from datetime import datetime

# 自作モジュール
from installer.src.method.DebugScreenshot.utils import Logger


# ----------------------------------------------------------------------------------
class ErrorDiscord:
    def __init__(self, chrome, discord_url, debug_mode=False):
        self.chrome = chrome
        self.discord_url = discord_url  # メインまで渡す
        self.logger = self.setup_logger(debug_mode=debug_mode)


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()

# ----------------------------------------------------------------------------------
# スクショ用のフルパス生成

    def _get_full_path(self, file_name) -> str:
        # 1つ前の親要素のディレクトリに移動
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # # さらにもう一つ前の親要素へディレクトリを移動
        # parent_dir = os.path.dirname(base_dir)

        # スクショ保管場所の絶対path
        screenshot_dir = os.path.join(base_dir, 'DebugScreenshot/')

        full_path = os.path.join(screenshot_dir, file_name)
        # self.logger.debug(f"full_path: {full_path}")

        return full_path


# ----------------------------------------------------------------------------------
# スクショをタイムスタンプ付きで撮影

    def _get_screenshot(self) -> str:
        # スクショ用のタイムスタンプ
        timestamp = datetime.now().strftime("%m-%d_%H-%M")

        # タイムスタンプ付きの名前
        filename = f"error_image_{timestamp}.png"

        # ファイル名を組み合わせてフルパスに
        full_path = self._get_full_path(filename)

        if self.chrome.save_screenshot(full_path):
            self.logger.debug(f"スクリーンショットを保存: {full_path}")

        else:
            self.logger.error(f"スクリーンショットを保存に失敗。。。")

        return full_path


# ----------------------------------------------------------------------------------
# discordでの通知

    def process(self, comment, e) -> None:

        screenshot_path = self._get_screenshot()

        content = f"【WARNING】{comment}: {e}"

        with open(screenshot_path, 'rb') as file:
            files = {"file": (screenshot_path, file, "image/png")}
            response = requests.post(self.discord_url, data={"content": content}, files=files)

        # 最後にエラーで返す
        raise Exception(f"【WARNING】{comment}: {e}")


# ----------------------------------------------------------------------------------
# エラーではない箇所でのdiscordでの通知

    def no_error_process(self, comment) -> None:

        screenshot_path = self._get_screenshot()

        content = f"【WARNING】{comment}"

        with open(screenshot_path, 'rb') as file:
            files = {"file": (screenshot_path, file, "image/png")}
            response = requests.post(self.discord_url, data={"content": content}, files=files)

        # 最後にエラーで返す
        raise Exception(f"【WARNING】{comment}")


# ----------------------------------------------------------------------------------