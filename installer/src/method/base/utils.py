# coding: utf-8
# ----------------------------------------------------------------------------------

#* 文字列処理
# ユーザー入力のサニタイズ
# 文字列の正規化やフォーマット変更
# ランダムな文字列の生成

#* 数値処理
# 数値のフォーマット（通貨、パーセンテージなど）
# 範囲内でのランダムな数値の生成
# 単位変換（例：温度、距離）

#* データ変換と検証
# JSON、XMLといったフォーマットへの変換およびそれらからの変換
# 入力データの検証ルール（例：メールアドレスの形式確認）

#* デートとタイム
# 日付や時刻のフォーマット変更
# 特定の日付・時刻までの残り時間計算
# タイムゾーンの変換

#* ファイル操作
# ファイル読み込み・書き込みのラッパー関数
# 一時ファイルの生成と管理
# ディレクトリの操作（作成、削除、探索）

#* ネットワーク通信
# HTTPリクエストの送受信
# URLの組み立てや解析
# データエンコーディングやデコーディング


# ----------------------------------------------------------------------------------
import logging
import os
import re
import sys

from typing import Any

####################################################################################


class LoggerBasicColor(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[90m",  # グレー
        "INFO": "\033[94m",   # 青色
        "WARNING": "\033[93m", # 黄色
        "ERROR": "\033[91m",  # 赤色
        "CRITICAL": "\033[95m", # マゼンダ
    }

    RESET = "\033[0m"

    def format(self, record):
        message = super().format(record)
        color = self.COLORS.get(record.levelname, "")
        return f"{color}{message}{self.RESET}"


####################################################################################


class Logger:
    def __init__(self, module_name, debug_mode=False):
        try:
            self.logger = logging.getLogger(module_name)

            # 同じログは表示しないように設定
            if not self.logger.handlers:
                self.logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

                # コンソールにログを出力するハンドラを追加
                console_handler = logging.StreamHandler()
                self.logger.addHandler(console_handler)

                # ログのフォーマットを設定
                log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                console_handler.setFormatter(log_format)

                log_format = LoggerBasicColor('%(asctime)s - %(levelname)s - %(message)s')
                console_handler.setFormatter(log_format)

                # ログファイルの保存先ディレクトリを設定
                log_directory = "installer/src/method/logs"

                # 各モジュールの名前でログファイルを分ける
                log_filename = f"{log_directory}/{module_name}_debug.log"

                # ディレクトリが存在しない場合は作成
                if not os.path.exists(log_directory):
                    os.makedirs(log_directory)

                # ファイル出力用のハンドラー
                file_handler = logging.FileHandler(log_filename)  # ファイル名を指定
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)

        except Exception as e:
            self.logger.error(f"ロガー設定中にエラーが発生しました: {e}")


    def get_logger(self):
        return self.logger

print(sys.path)


####################################################################################
# Noneをチェックする

class NoneChecker:
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
# 数値でのNoneをチェックする
# self.none_checker = NoneChecker(debug_mode=False)
# self.none_checker._none_value_checker(result=)

    def value_checker(self, result) -> int:  # 文字列＋整数値
        if result is None:
            raise ValueError("resultが「None」です")
        else:
            self.logger.debug(f"resultは None ではない")
        return result.value


# ----------------------------------------------------------------------------------
# 文字列含むすべての値のNoneをチェックする
# self.none_checker = NoneChecker(debug_mode=False)
# self.none_checker._none_any_checker(result=)

    def any_checker(self, result) -> Any:
        if result is None:
            raise ValueError("resultが「None」です")
        else:
            self.logger.debug(f"resultは None ではない")
        return result


# ----------------------------------------------------------------------------------
####################################################################################
# 数値の方の確認

class NumberChecker:
    def __init__(self, debug_mode=False):
        self.logger = self.setup_logger(debug_mode=debug_mode)


# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# 整数値になってるかをチェック→違う場合には変換
# self.number_checker = NumberChecker(debug_mode=False)
# self.number_checker._int_checker(value=)

    def _int_checker(self, value) -> int:
        if value is None:
            raise ValueError("valueが「None」です")

        # isinstanceだとサブクラスなど深い階層のデータでも型を確認できる
        if not isinstance(value, int):
            try:
                value = int(value)
                self.logger.debug(f"value {value}")

            except ValueError as e:
                self.logger.error(f"_int_check 処理中にエラー {e}")
                raise

        return value


# ----------------------------------------------------------------------------------
# 小数点ありの整数値になってるかをチェック→違う場合には変換
# self.number_checker = NumberChecker(debug_mode=False)
# self.number_checker._float_checker(value=)

    def _float_checker(self, value) -> int:
        if value is None:
            raise ValueError("valueが「None」です")

        # isinstanceだとサブクラスなど深い階層のデータでも型を確認できる
        if not isinstance(value, float):
            try:
                value = float(value)
                self.logger.debug(f"value {value}")

            except ValueError as e:
                self.logger.error(f"_float_check 処理中にエラー {e}")
                raise

        return value


# ----------------------------------------------------------------------------------

####################################################################################


class clean_value:
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
# 整数値をきれいにする→int型

    def clean_int(self, value, filed_name):
        if value is None:
            self.logger.error(f"{filed_name} 値が「None」です")
            raise

        # カンマとピリオドを除去
        value = value.replace(',', '')
        value = value.replace('.', '')

        # 数値以外の文字を除去
        clean_value = re.sub(r'[^\d-]', '', value)

        try:
            clean_int = int(clean_value)
            self.logger.debug(f"{filed_name} {clean_value} クリーニング成功")

            return clean_int

        except ValueError as e:
            self.logger.error(f"数値クリーニングしようとしていた値が文字列歯科なくなってしまった可能性が高い: {clean_value}")


# ----------------------------------------------------------------------------------
# 整数値をきれいにする→float型

    def clean_float(self, value, filed_name):
        if value is None:
            self.logger.error(f"{filed_name} 値が「None」です")
            raise

        # カンマとピリオドを除去
        value = value.replace(',', '')
        value = value.replace('.', '')

        # 数値以外の文字を除去
        clean_value = re.sub(r'[^\d-]', '', value)

        try:
            clean_float = float(clean_value)
            self.logger.debug(f"{filed_name} {clean_value} クリーニング成功")

            return clean_float

        except ValueError as e:
            self.logger.error(f"数値クリーニングしようとしていた値が文字列歯科なくなってしまった可能性が高い: {clean_value}")


# ----------------------------------------------------------------------------------
####################################################################################
# Path操作系

class Path:
    def __init__(self, debug_mode=False):
        self.logger = self.setup_logger(debug_mode=debug_mode)


####################################################################################
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# relative_path（相対Path）からfull_pathへ
# self.path = Path(debug_mode=False)
# self.path._get_full_path(relative_path=, file_name=)

    def _get_full_path(self, relative_path, file_name):
        try:
            if relative_path is None:
                raise ValueError("relative_path「None」です")

            # 相対Pathだと指定してるけど、フルパスの可能性だったらそのまま返す
            if os.path.isabs(relative_path):
                full_path = relative_path
                self.logger.debug(f"{file_name} すでに full_path")

            # 親のディレクトリ
            parents_dir = os.path.dirname(__file__)

            # 親の親ディレクトリ
            grandparents_dir = os.path.dirname(parents_dir)

            if relative_path:
                # 親までのディレクトリ＋相対Pathでfull_path
                full_path = os.path.join(grandparents_dir, relative_path)

            self.logger.debug(f"{file_name} full_path: {full_path}")

            return full_path

        except Exception as e:
            self.logger.error(f"{file_name} full_path変換でエラー: {e}")


# ----------------------------------------------------------------------------------
# full_path生成 ファイル名 + path
# self.path = Path(debug_mode=False)
# self.path._generate_fullpath(file_name=)

    def _generate_fullpath(self, file_name):
        try:
            # 親のディレクトリ
            parents_dir = os.path.dirname(__file__)

            # 親までのディレクトリ＋相対Pathでfull_path
            full_path = os.path.join(parents_dir, file_name)
            self.logger.debug(f"{file_name} full_path: {full_path}")

            return full_path

        except Exception as e:
            self.logger.error(f"{file_name} full_path生成でエラー: {e}")


# ----------------------------------------------------------------------------------
