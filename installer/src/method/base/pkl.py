# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2023/6/14 更新

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

import os
import glob
import pickle
import zipfile
import const
import pandas as pd
from pathlib import Path
import shutil
from functools import reduce
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (NoSuchElementException)

# 自作モジュール
# import const
from .utils import Logger, NoneChecker
from .spreadsheet_write import SpreadsheetWrite


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class Pickle:
    def __init__(self, chrome, debug_mode=False):
        self.chrome = chrome

        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()



# ----------------------------------------------------------------------------------
# pickleデータを通常のデータへ変換

    def _pkl_to_utf8(self, pkl_file, field_name):
        try:
            if pkl_file:
                with open(pkl_file, 'rb') as f:
                    binary_data = f.read()

                    text_data = binary_data.decode('utf-8')

                    self.logger.debug(f"{field_name} text_data: {text_data}")

                    return text_data

            else:
                self.logger.warning(f"pickle が存在しない: {pkl_file}")
                raise FileNotFoundError(f"{field_name} {pkl_file}が見つまりません{e}")

        except FileNotFoundError as e:
            self.logger.error(f"{field_name} {pkl_file}が見つまりません{e}")
            raise

        except UnicodeDecodeError as e:  # デコードエラーの処理
            self.logger.error(f"{field_name} {pkl_file}のデコード中にエラーが発生: {e}")
            raise

        except Exception as e:
            self.logger.error(f"{field_name} {pkl_file} pickleデータを変換中にエラーが発生{e}")
            raise


# ----------------------------------------------------------------------------------
# pickleデータへの変換

    def _to_pkl(self, new_data, fullpath, field_name='_to_pkl'):
        try:
            with open(f'{fullpath}.pkl', 'wb') as f:
                binary_data = pickle.dump(new_data, f)

                # Noneかどうかを確認
                self.none_checker.any_checker(result=binary_data)

                self.logger.debug(f"{field_name} {new_data}からバイナリデータへの書き込みが完了")

        except IOError as e:  # IOErrorを捕捉（ファイル関連のエラー）
            self.logger.error(f"{field_name} ファイル操作中にエラーが発生 {e}")
            raise

        except pickle.PickleError as e:  # pickleのエラーを捕捉
            self.logger.error(f"{field_name} データのpickle化中にエラーが発生 {e}")
            raise

        except Exception as e:
            self.logger.error(f"{field_name} {new_data} pickleデータを変換中にエラーが発生{e}")
            raise


# ----------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------
# **********************************************************************************
