# coding: utf-8
# 2023/6/15  更新
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import pandas as pd

from .base.utils import Logger
from .base.df_Create import DFCreate
from .base.pkl_change import PickleControl



# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class DiffDfProcess:
    def __init__(self, chrome, debug_mode=False):
        # chrome
        self.chrome = chrome

        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        # instance
        self.df_create = DFCreate(chrome=self.chrome, debug_mode=debug_mode)
        self.pickle_control = PickleControl(chrome=self.chrome, debug_mode=debug_mode)


# ----------------------------------------------------------------------------------
# DataFrameとDataFrameを突合させて差分の真偽値別に処理をする

    def diff_df_processing(self, data, pkl_name, pkl_path, head_num, select_column, opening_message, notify_func, save_func, save_pickle_path, account_id):
        try:
            self.logger.info(f"********** {account_id} diff_df_processing start **********")

            if data:
                self.logger.debug(f"data:\n{data}")

                # dataからDataFrameに変換
                current_df = pd.DataFrame(data)

                # 過去のpickleデータをDataFrameに変換
                old_df = self.pickle_control._pickle_df(pkl_name=pkl_name, pkl_path=pkl_path)

                # old_dfがなかったらエラーを出す
                if old_df is None or old_df.empty:
                     raise ValueError('pkl_data is None ')

                # ２つのDataFrameの行単位での差分を出す
                diff_row_df = self.df_create.df_row_diff_value(current_df=current_df, old_df=old_df, head_num=head_num, select_column=select_column, account_id=account_id)

                # 返ってくる値によって実行処理を変更する
                self.df_create.is_result_branch(diff_row_df=diff_row_df, opening_message=opening_message, notify_func=notify_func, save_func=save_func, key_df=current_df, save_pickle_path=save_pickle_path)

                self.logger.info(f"********** {account_id} diff_df_processing end **********")

            else:
                raise ValueError('pkl_data が None ')


        except ValueError as ve:
            self.logger.error(f"pkl_data None {ve}")
            raise

        except Exception as e:
                self.logger.error(f"diff_df_processing  処理中にエラーが発生: {e}")
                raise


# ----------------------------------------------------------------------------------
# **********************************************************************************
