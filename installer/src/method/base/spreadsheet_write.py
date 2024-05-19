# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/5/8更新

#? APIを使って書き込みする
# ----------------------------------------------------------------------------------
import os
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import errors


from dotenv import load_dotenv

from .utils import Logger, NoneChecker


load_dotenv()

# ----------------------------------------------------------------------------------
####################################################################################


class SpreadsheetWrite:
    def __init__(self, chrome, credentials_json_file, spread_id, debug_mode=False):

        self.chrome = chrome
        self.none_checker = NoneChecker(debug_mode=debug_mode)
        self.logger = self.setup_logger(debug_mode=debug_mode)

        self.logger.debug(f"credentials_json_file: {credentials_json_file}")
        self.logger.debug(f"spread_id: {spread_id}")


# jsonファイル
        self.credentials_json_file = self._get_full_path(file_name=credentials_json_file)


# スプシのID → https://docs.google.com/spreadsheets/d/スプレッドシートID/edit#gid=シート番号
        self.spread_id = spread_id


# 認証情報の読み込み 認証情報＝jsonファイル + スコープ
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_json_file)
        self.client = gspread.authorize(self.creds)

        self.logger.debug(f"self.creds: {self.creds}")
        self.logger.debug(f"self.client: {self.client}")





####################################################################################
# ----------------------------------------------------------------------------------
# Loggerセットアップ

    def setup_logger(self, debug_mode=False):
        debug_mode = os.getenv('DEBUG_MODE', 'False') == 'True'
        logger_instance = Logger(__name__, debug_mode=debug_mode)
        return logger_instance.get_logger()


# ----------------------------------------------------------------------------------
# フルパス生成

    def _get_full_path(self, file_name):

        # 事前にファイル名が反映してるのか確認
        self.logger.debug(f"file_name: {file_name}")

        # 親要素までのPathを取得（ファイル名をあと入力できるように）
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # 更に親要素に戻る
        parent_dir = os.path.dirname(base_dir)

        full_path = os.path.join(parent_dir, 'input_data', file_name)  # フルパス生成
        self.logger.debug(f"full_path: {full_path}")  # フルパス確認

        return full_path


# ----------------------------------------------------------------------------------


    def _gss_direct_write(self, worksheet, cell, data):
        try:
            self.logger.info(f"********** _gss_direct_write 開始 **********")

            self.logger.debug(f"self.spread_id: {self.spread_id}")
            self.logger.debug(f"worksheet: {worksheet}")

    # スプシへのアクセスを定義（API）
            #* Scopeはこの場所で特定が必要
            scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            c = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_json_file, scope)
            gs = gspread.authorize(c)

        # ワークシートのデータを取得
            select_sheet = gs.open_by_key(self.spread_id).worksheet(worksheet)

            self.logger.debug(f"select_sheet: {select_sheet}")

            select_sheet.update(cell, data)

            self.logger.info(f"********** _gss_direct_write 終了 **********")


        except Exception as e:
            self.logger.error(f"スプシ: 処理中にエラーが発生{e}")



# ----------------------------------------------------------------------------------

# cellの値がない行を特定

    def _gss_none_cell_update(self, worksheet, col_left_num, start_row, input_values):
        self.logger.info(f"********** _column_none_cell 開始 **********")

        try:
            self.logger.debug(f"self.spread_id: {self.spread_id}, start_row: {start_row}")

            self.logger.debug(f"worksheet: {worksheet}, col_left_num: {col_left_num}, start_row: {start_row}")


    # スプシへのアクセスを定義（API）
            #* Scopeはこの場所で特定が必要
            scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            c = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_json_file, scope)
            gs = gspread.authorize(c)

            select_sheet = gs.open_by_key(self.spread_id).worksheet(worksheet)

            self.logger.debug(f"select_sheet: {select_sheet}")


    # 指定のスプシへアクセス
            col_row = select_sheet.col_values(col_left_num)

            for i, cell in enumerate(col_row, start=start_row):
                if cell == '':
                    write_last_row = i
            else:
                write_last_row = len(col_row) + start_row

            self.logger.debug(f"write_last_row: {write_last_row}")

            # Aが１になるように変更
            column = chr(64 + col_left_num)

            cell_range = f"{column}{write_last_row}"

            input_list = [[value] for value in input_values]

            self.logger.debug(f"cell_range: {cell_range}")
            self.logger.debug(f"input_list: {input_list}")

            select_sheet.update(cell_range, input_list)

            self.logger.info(f"********** _column_none_cell 終了 **********")

        except errors.HttpError as e:
            self.logger.error(f"スプシ: 認証失敗{e}")
            raise

        except gs.exceptions.APIError as e:
            self.logger.error(f"スプシ: サーバーエラーのため実施不可{e}")
            raise

        except Exception as e:
            self.logger.error(f"スプシ: 処理中にエラーが発生{e}")
            raise


# ----------------------------------------------------------------------------------
# cellの値がない場所を指定

    def update_timestamps(self, worksheet):
        self.logger.info(f"********** update_timestamps 開始 **********")

        try:
            self.logger.debug(f"worksheet: {worksheet}")


    # スプシへのアクセスを定義（API）
            scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
            c = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_json_file, scope)
            gs = gspread.authorize(c)

            select_sheet = gs.open_by_key(self.spread_id).worksheet(worksheet)

            self.logger.debug(f"select_sheet: {select_sheet}")

            get_a_values = select_sheet.col_values(1)
            get_b_values = select_sheet.col_values(2)

            # filtered_a_values = get_a_values[2:]
            # filtered_b_values = get_b_values[2:]


            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for index, b_val in enumerate(get_b_values[2:], start=3):
                try:
                    a_val = get_a_values[index -1] if index - 1 < len(get_a_values) else ""

                except IndexError:
                    a_val = ""

                if b_val and not a_val:

                    date_cell = f"A{index}"
                    select_sheet.update(date_cell, [[current_date]])
                    self.logger.debug(f"a_val: {a_val}, b_val: {b_val}")


            self.logger.info(f"********** update_timestamps 終了 **********")


        except errors.HttpError as error:
            self.logger.error(f"スプシ: 認証失敗: {error}")
            raise

        except gs.exceptions.APIError as e:
            self.logger.error(f"スプシ: サーバーエラーのため実施不可{e}")
            raise

        except Exception as e:
            self.logger.error(f"スプシ: 処理中にエラーが発生: {e}")
            raise


# ----------------------------------------------------------------------------------
# データフレームから下記のデータを書き込む


#TODO: 日付→リストにあるものをすべて表示
#TODO: 4つ目以降のテーブルを実施
#TODO: 

