# coding: utf-8
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# 2023/6/14 更新

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


import os
import pickle
import pandas as pd

# 自作モジュール
# import const
from .utils import Logger


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************


class PickleControl:
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
# pickleデータからDataFrameに変換

    def _pickle_df(self, pkl_name, pkl_path):
        try:
            self.logger.info(f"******** _pickle_df start ********")

            self.logger.debug(f"pkl_name: {pkl_name}")

            pkl_to_df = None

            # 前後についてしまってる余計な空白を除去
            pkl_file_name = pkl_name.strip()

            pkl_full_path = os.path.join(pkl_path, f'{pkl_file_name}.pkl')

            self.logger.warning(f"pkl_full_path: {pkl_full_path}")

            if os.path.exists(pkl_full_path):
                # pickleデータ読み込んでDataFrameにする
                pkl_to_df = pd.read_pickle(pkl_full_path)
                self.logger.debug(f"pkl_to_df: \n{pkl_to_df.head()}")


            self.logger.info(f"******** _pickle_df end ********")

            return pkl_to_df


        except FileNotFoundError as fe:
            self.logger.error(f"{pkl_name}.pkl が見つかりません {fe}")
            raise

        except ValueError as ve:
            self.logger.error(f"pkl_data None {ve}")
            raise

        except Exception as e:
            self.logger.error(f"_pickle_df pickleデータを変換中にエラーが発生{e}")
            raise


# ----------------------------------------------------------------------------------
# DataFrameからpickleデータへ変換

    def df_pickle(self, df, route, pickle_name):
        try:
            self.logger.info(f"******** df_pickle start ********")

            self.logger.debug(f"df:\n{df.head(3)}")
            self.logger.debug(f"route:{route}")
            self.logger.debug(f"save_pickle_path:{pickle_name}")

            route_path = self._get_route_path(route)

            self.logger.warning(f"route_path: {route_path}")

            pickle_full_path= os.path.join(route_path, pickle_name)

            if not df.empty:
                df.to_pickle(pickle_full_path)
                self.logger.info("pickleに保存完了")

            else:
                raise ValueError('pkl_data is None ')


            self.logger.info(f"******** df_pickle end ********")


        except ValueError as ve:
            self.logger.error(f"pkl_data None {ve}")
            raise

        except Exception as e:
            self.logger.error(f"df_pickle pickleデータを変換中にエラーが発生{e}")
            raise


# ----------------------------------------------------------------------------------
# pickleディレクトリまでのフルパスの生成

    def _get_route_path(self, route) -> str:

        # base ディレクトリに移動
        base_dir = os.path.dirname(os.path.abspath(__file__))

        self.logger.debug(f"base_dir: {base_dir}")

        # method ディレクトリに移動
        method_dir = os.path.dirname(base_dir)

        self.logger.debug(f"method_dir: {method_dir}")

        # src ディレクトリに移動
        src_dir = os.path.dirname(method_dir)

        self.logger.debug(f"src_dir: {src_dir}")

        # installer ディレクトリに移動
        installer_dir = os.path.dirname(src_dir)

        self.logger.debug(f"installer_dir: {installer_dir}")


        full_path = os.path.join(installer_dir, route)
        self.logger.debug(f"full_path: {full_path}")

        return full_path


# ----------------------------------------------------------------------------------
# **********************************************************************************

