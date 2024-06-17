# coding: utf-8
# ----------------------------------------------------------------------------------
#! ここで定義して「Flow」で扱う
#! 引数はここで基本渡す。


# ----------------------------------------------------------------------------------

# 自作モジュール
from .base.df_Create import DFCreate
from .base.utils import Logger


####################################################################################
####################################################################################


class GetData(DFCreate):
    def __init__(self, chrome, debug_mode=False):
        super().__init__(chrome, debug_mode)

    # サイトのデータを抽出して整理する
    def _getSiteData(self, by_pattern, xpath, category_info, field_name):
        category_info = [
            ("商品ID", "attribute", "goodsid"),
            ("商品名", "xpath", "//p[@class='itemCard_name']"),
            ("状態", "xpath", "//p[@class='itemCard_status']"),
            ("価格", "xpath", "//p[contains(@class, 'itemCard_price')]")
        ]
        return super()._sort_data(by_pattern, xpath, category_info, field_name)


    # 集めたデータをdfに置換する
    def _to_df(self, data):
        index_column='商品ID'
        field_name='_to_df'
        return super()._to_df(data, index_column, field_name)


    # TODO: フルパスになるようにする
    # 保存してあるデータを復元する→DataFrameにする
    def _pkl_to_utf8(self):
        pkl_file=''
        field_name='_pkl_to_utf8'
        return super()._pkl_to_utf8(pkl_file, field_name)


    # TODO: 比較する→DataFrameで左右にするようにして違う部分を抽出する
    # TODO: 一度整理する→クラスも明確になるようにする
    # TODO: 理解を深めて学習にもする


    # TODO: フルパスになるようにする
    # 現在データを今のファイルに保存する
    def _to_pkl(self, new_data):
        fullpath='installer/src/result_output/save'
        field_name='_to_pkl'
        return super()._to_pkl(new_data, fullpath, field_name)



####################################################################################
####################################################################################


class GetUlValue:
    def __init__(self, chrome, debug_mode=False) -> None:
        self.chrome = chrome

        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

####################################################################################
# 初回だけpickleデータを作成するための関数



####################################################################################
