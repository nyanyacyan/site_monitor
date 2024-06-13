# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/4/22 更新

# ----------------------------------------------------------------------------------
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


# ----------------------------------------------------------------------------------
####################################################################################


class DFCreate:
    def __init__(self, chrome, debug_mode=False):
        self.chrome = chrome

        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()


        self.none_checker = NoneChecker(debug_mode=debug_mode)
        self.spread_input = SpreadsheetWrite(chrome=self.chrome, credentials_json_file=const.spread_json, spread_id=const.spread_id, debug_mode=False)




####################################################################################
# ----------------------------------------------------------------------------------
# ロケーター選択→直接文字列で入れ込むことができない

    def _locator_select(self, locator) -> None:
        mapping = {
            'ID' : By.ID,
            'XPATH' : By.XPATH,
            'CLASS' : By.CLASS_NAME,
            'CSS' : By.CSS_SELECTOR,
            'TAG' : By.TAG_NAME,
            'NAME' : By.NAME,
            'LINK_TEXT': By.LINK_TEXT,  # リンクテキスト全体に一致する要素を見つける
            'PARTIAL_LINK_TEXT': By.PARTIAL_LINK_TEXT  # リンクテキストの一部に一致する要素を見つける
        }

        # 入力された文字を大文字に直して選択
        return mapping.get(locator.upper())


# ----------------------------------------------------------------------------------
# 受け取ったデータをDataFrameに書き換える
#TODO: resultがNoneかどうかをチェックする

    def _to_df(self, data, index_column, field_name):

        self.logger.info(f"********** _to_df 開始 **********")

        try:
            # 辞書データをDataFrameに変換
            df = pd.DataFrame(data)

    # inplace=TrueはDFに直接変更をするため。
            if index_column in df.columns:
                df.set_index(index_column, inplace=True)

            else:
                raise ValueError(f"index_columnが見つからない")

            self.logger.debug(f"{field_name} DataFrameに変換\n {df}")

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生{e}")

        self.logger.info(f"********** _to_df 終了 **********")

        return df


# ----------------------------------------------------------------------------------
# 指定した要素の値を取得
#TODO: resultがNoneかどうかをチェックする

    def _get_element_value(self, by_pattern, xpath, search_name, field_name):
        try:
            # 特定の要素の値を取得する。
            element = self.chrome.find_element(self._locator_select(by_pattern), xpath)
            search_value = element.get_attribute(search_name)

            self.logger.debug(f"{field_name} search_value: {search_value}")

            return search_value

        except NoSuchElementException as e:
            self.logger.error(f"{field_name} 要素が見つかりません。")
            raise


# ----------------------------------------------------------------------------------
# リストを作成してcategory_nameをColumnにしてデータを整理
#TODO: resultがNoneかどうかをチェックする

    def _sort_data(self, by_pattern, xpath, category_info, field_name):
        '''
        category_info カテゴリーごとの情報→今回は「category_name, catch_by, catch_path」この３つ
        '''
        try:
            # 全体から対象のリストを取得
            item_boxs = self.chrome.find_elements(self._locator_select(by_pattern), xpath)

            # データ形式を指定して内包表記にて並び替える
            # category_name:[_, _] という形式にするように指定してる（初期化）
            data = {category_name: [] for category_name, _, _ in category_info}

            # 取得したリストを一つのものから中身を抽出する
            for item_box in item_boxs:
                # category_infoという得たデータから３つの情報を抜き取る
                for category_name, catch_by, catch_path in category_info:

                    # もしcatch_pathがattributeだった場合にはその値を記す
                    # .get_attribute は属性を取得するという意味
                    # 文字列で属性値を取得するのではなく、属性値を取得するため
                    if catch_path == "attribute":
                        element_value = item_box.get_attribute(catch_path)

                    else:
                    # 得た情報から処理を行って各それぞれの要素を取得する
                        element = item_box.find_element(catch_by, catch_path)
                        element_value = element.text
                    # 取得した各データを指定したデータの箱に入れていく
                    data[category_name].append(element_value)

            self.logger.debug(f"{field_name} data: {data}")

            return data

        except Exception as e:
            self.logger.error(f"{field_name} 商品データを整理中にエラーが発生{e}")
            raise


# ----------------------------------------------------------------------------------
# pickleデータを通常のデータへ変換
#TODO: resultがNoneかどうかをチェックする

    def _pkl_to_utf8(self, pkl_file, field_name):
        try:
            with open(pkl_file, 'rb') as f:
                binary_data = f.read()

                text_data = binary_data.decode('utf-8')

                self.logger.debug(f"{field_name} text_data: {text_data}")

                return text_data

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

    def _to_pkl(self, new_data, fullpath, field_name):
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
#TODO: resultがNoneかどうかをチェックする

    def diff_data_list_create(self, key_df, download_df, key_column, field_name):
        try:
            self.logger.debug(type(key_df))
            self.logger.debug(type(download_df))

# デバッグ用のCSV出力
            key_df.to_csv('key_df_result.csv')
            download_df.to_csv('download_df_result.csv')

            key_df_rows, key_df_columns = key_df.shape
            key_df_total_data_points = key_df_rows * key_df_columns

            self.logger.debug(f"key_df.columns: {key_df.columns}")
            self.logger.info(f"download_df.columns: {download_df.columns}")

            self.logger.debug(f"key_df_total_data_points: {key_df_total_data_points}")



# 実際のマージ処理前のデータ行数を確認
            self.logger.debug(f"Number of rows in key_df before merge: {len(key_df)}")
            self.logger.debug(f"Number of rows in download_df before merge: {len(download_df)}")
            # on=[key_column]が「Key」となるデータ
            # how='left'は左側（key_df）を基準する（old_dfにしかないデータはNaN）

# indexを初期状態にする
            key_df_reset = key_df.reset_index()
            download_df_reset = download_df.reset_index()

            print(key_df_reset['Date'].head())
            print(download_df_reset['Date'].head())

# ２つのdfを結合させる  右側に結合
# how=‘left’は左側（位置引数にあるdf）を軸とする
# on=[key_column] ここで選択したcolumnを基準にして結合させる→同じものは行で結合
# indicator=True これにより、dfに（‘left_only’、‘right_only’、‘both’）をステータスを追加
# suffixes=(’_site’, ‘_csv’)同じcolumn名があった場合に左側と右側で追記するものを指定できる
            result = pd.merge(key_df_reset, download_df_reset, on=[key_column], how='left', indicator=True, suffixes=('_after', '_before'))

            self.logger.debug(f"{field_name} result: {result}")
            self.logger.debug(f"{field_name} result.columns: {result.columns}")

# IndexをDateに変更
            result_df = result.set_index('Date')

# 大元データのColumnをリスト化
            key_columns = [col for col in key_df.columns if col != 'Date']

# 各行に対して関数を充てる
            result_df['Differences'] = result_df.apply(self._find_diff_value, axis=1, args=(key_columns,'diff_data_list_create'))

            self.logger.debug(f"{field_name} result_df: {result_df}")

            self.logger.debug(f"{field_name} result_df['Differences']: {result_df['Differences']}")

            clean_df = self._df_clean(df=result_df, column_name='Differences', field_name='diff_data_list_create')

            diff_df = self._cell_to_df(df=clean_df, column_name='Differences')

# 差異リストをCSV出力
            diff_df.to_csv('result.csv')

            return diff_df


        except KeyError as e:
            self.logger.error(f"{field_name} キーのエラー、データフレームに期待されるカラムが存在しない: {e}")
            raise

        except ValueError as e:
            self.logger.error(f"{field_name} データ型エラー: {e}")
            raise

        except Exception as e:
            self.logger.error(f"{field_name} 差分データを修正中にエラーが発生: {e}")
            raise




# ----------------------------------------------------------------------------------
# DFをNaNをなくすための関数

    def _df_clean(self, df, column_name, field_name):
        self.logger.info(f"********** _df_clean 開始 **********")

        try:
            self.logger.debug(f"{field_name} df: \n{df}")

# NaNなどの欠損値があったら消すメソッド
            clean_data = df.dropna(subset=[column_name])

            self.logger.debug(f"clean_data: \n{clean_data}")

            self.logger.info(f"********** _df_clean 終了 **********")

            return clean_data


        except Exception as e:
            self.logger.debug(f"{field_name} clean_data: 処理中にエラーが発生{e}")


# ----------------------------------------------------------------------------------
# dfのセルからdfを作成（辞書データ）

    def _cell_to_df(self, df, column_name):
        self.logger.info(f"********** _cell_to_df 開始 **********")

# ネストされたリスト（[['apple', 'banana'], ['grape', 'orange']]）このようなリストを一つ一つ取り出す
        diff_df = pd.DataFrame([item for sublist in df[column_name] for item in sublist])

        self.logger.info(f"diff_df: \n{diff_df}")

        self.logger.info(f"********** _cell_to_df 開始 **********")

        return diff_df


# ----------------------------------------------------------------------------------
# 通知に掲載するためのデフォルトのデータを整理するためのメソッド
#TODO: resultがNoneかどうかをチェックする

    def _find_diff_value(self, row, key_col, field_name):
        self.logger.info(f"********** find_diff_value 開始 **********")

# 差異があるものをリストに追加
        diff_value = []

        try:
            date = row.name
            for col in key_col:
                site_col = col + '_site'
                csv_col = col + '_csv'

# siteとCSVデータがNaNだったら場合にはスキップ
                if pd.isna(row[site_col]) and pd.isna(row[csv_col]):
                    continue

# siteとCSVデータが有っていた場合にはスキップ
                elif row[site_col] == row[csv_col]:
                    continue

# それ以外は差異になるためリストに追記
                else:
                    diff_dic = {
                        'Date' : date,
                        'diff_col' : col,
                        'site_value' : row[site_col] if pd.notna(row[site_col]) else 'NaN',
                        'diff_value' : row[csv_col] if pd.notna(row[csv_col]) else 'NaN',
                        'diff_explain' : f"{col}: Webサイト側の数値が「{row[site_col]}」に対してダウンロードファイルは「{row[csv_col]}」になっている"
                    }
                    append_content = diff_value.append(diff_dic)
                    # append_content = diff_value.append(f"{col}: Webサイト側の数値が「{row[site_col]}」に対してダウンロードファイルは「{row[csv_col]}」になっている")
                    self.logger.debug(f"{field_name} append_content: {append_content}")

            if not diff_value:
                return None

            self.logger.info(f"********** find_diff_value 終了 **********")

            return diff_value


        except NoSuchElementException as e:
            self.logger.error(f"{field_name} {row}か{key_col}が見つからない: {e}")
            raise

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")
            raise


# ----------------------------------------------------------------------------------
# ファイル名の一部からファイルのフルパスを入手
# file_name_partは一部になる場合には必ずアスタリスクで囲う

    def _get_file_path(self, file_name_part, field_name):
        self.logger.info(f"********** _get_file_path 開始 **********")

        try:
            self.logger.debug(f"{field_name} file_name_part: {file_name_part}")

            #! ルートディレクトリから始める場合（例えばLinuxやMacの場合は'/'、Windowsでは'C:\\'）__
            home_dir = Path(os.path.expanduser('~'))
            desktop_dir = home_dir / 'Desktop'

            matching_files = list(desktop_dir.rglob(file_name_part))


            # file_full_path = glob.glob(os.path.join(file_name_part))
            self.logger.debug(f"{field_name} file_full_path: {matching_files}")

# TODO 例外処理を追加
            if len(matching_files) > 1:
                self.logger.error(f"2つ以上のファイルが見つかった ダウンロードフォルダにあるデータの消去をしてください {matching_files}")
                raise ValueError

# TODO 例外処理を追加
            if len(matching_files) == 0:
                self.logger.error(f"指定のファイルが見つからなかった。 {matching_files}")
                raise FileNotFoundError

            self.logger.info(f"********** _get_file_path 終了 **********")

            return matching_files


        # except FileNotFoundError as e:
        #     self.logger.error(f"{field_name} fileがみつかりません{e}")
        #     raise

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生{e}")
            raise


# ----------------------------------------------------------------------------------
# ファイル名の一部からファイルのフルパスを入手
# file_name_partは一部になる場合には必ずアスタリスクで囲う

    def _get_all_file_path(self, file_name_part, field_name):
        self.logger.info(f"********** _get_all_file_path 開始 **********")

        try:
            self.logger.debug(f"{field_name} file_name_part: {file_name_part}")

            #! ルートディレクトリから始める場合（例えばLinuxやMacの場合は'/'、Windowsでは'C:\\'）__
            # デスクトップ以降のディレクトリ全てから探す
            home_dir = Path(os.path.expanduser('~'))
            desktop_dir = home_dir / 'Desktop'

            matching_files = list(desktop_dir.rglob(file_name_part))


            # file_full_path = glob.glob(os.path.join(file_name_part))
            self.logger.debug(f"{field_name} file_full_path: {matching_files}")


# 例外処理を追加
            if len(matching_files) == 0:
                self.logger.error(f"指定のファイルが見つからなかった。 {matching_files}")
                raise FileNotFoundError

            self.logger.info(f"********** _get_all_file_path 終了 **********")

            return matching_files


        except ValueError as e:
            self.logger.error(f"{field_name} 処理中にが発生{e}")

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生{e}")
            raise


# ----------------------------------------------------------------------------------
# ZIPファイルを解凍
# _get_file_pathにてzipファイルを探す
# new_file_pathは名前も含めて記載

    def _unzip_rename(self, zip_file_path, new_file_path, field_name):
        self.logger.info(f"********** _unzip_file 開始 **********")

        try:
            self.logger.debug(f"{field_name} zip_file_path:{zip_file_path}")

            new_full_path = os.path.abspath(new_file_path)
            self.logger.debug(f"{field_name} new_full_path:{new_full_path}")


            os.makedirs(new_file_path, exist_ok=True)

            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(new_full_path)

                self.logger.debug(f"{field_name} {zip_file_path}から{new_file_path}に変換")

        # except FileNotFoundError as e:
        #     self.logger.error(f"{field_name} {zip_file_path}が見つからない {e}")

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生 {e}")


        self.logger.info(f"********** _unzip_file 終了 **********")


# ----------------------------------------------------------------------------------
# ファイル名の一部からファイルのフルパスを入手
# file_name_partは一部になる場合には必ずアスタリスクで囲う

    def _get_files_choice(self, relative_path, file_name_part, field_name):
        self.logger.info(f"********** _get_files_choice 開始 **********")

        try:
            self.logger.debug(f"{field_name} file_name_part: {file_name_part}")

            full_path = os.path.abspath(relative_path)

            full_pattern = os.path.join(full_path, file_name_part)

            self.logger.debug(f"{field_name} full_pattern: {full_pattern}")

            matching_file = glob.glob(full_pattern)

            self.logger.debug(f"{field_name} matching_file: {matching_file}")


            if not matching_file:
                raise FileNotFoundError(f"指定されたパターンに一致するファイルが見つかりませんでした。")


            searching_file = matching_file[0]

            self.logger.debug(f"{field_name} searching_file: {searching_file}")

            self.logger.info(f"********** _get_files_choice 終了 **********")

            return searching_file


        except FileNotFoundError as e:
            self.logger.error(f"{field_name} fileがみつかりません{e}")
            raise

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生{e}")
            raise


# ----------------------------------------------------------------------------------
# CSVを読み込んでデータフレームにする

    def _csv_to_df(self, csv_path, field_name):
        self.logger.info(f"********** _csv_to_df 開始 **********")

        df = pd.read_csv(csv_path, encoding='utf-8')



# 'Date' 列を datetime 型に変換
        df['Date'] = pd.to_datetime(df['Date']).dt.date

# 'Date' 列をインデックスとして設定
        df.set_index('Date', inplace=True)

        df.fillna(value='NaN')

# 'Date' 列に基づいてデータフレームを昇順にソート
        df = df.sort_values(by='Date')

# Columnの型一覧
        self.logger.debug(f"{field_name} df.index: {df.index}")

        self.logger.debug(f"{field_name} df.columns: {df.columns}")

        self.logger.debug(f"{field_name} df: {df}")

        self.logger.info(f"********** _csv_to_df 終了 **********")

        return df


# ----------------------------------------------------------------------------------
# renameをする関数

    def _same_name_rename(self, df, rename_map, field_name):
        self.logger.info(f"********** _same_name_rename 開始 **********")

        df.rename(columns=rename_map, inplace=True )

        self.logger.info(f"{field_name} df.columns: {df.columns}")

        self.logger.info(f"********** _same_name_rename 終了 **********")

        return df


# ----------------------------------------------------------------------------------
# CSVを読み込んでデータフレームにする

    def _rename_csv_to_df(self, csv_path, rename_map, field_name):
        self.logger.info(f"********** _csv_to_df 開始 **********")

        df = pd.read_csv(csv_path, encoding='utf-8')

        rename_map = {old: new for old, new in rename_map.items() if old in df.columns}
        self._same_name_rename(df=df, rename_map=rename_map, field_name=field_name)

# 'Date' 列を datetime 型に変換
        df['Date'] = pd.to_datetime(df['Date']).dt.date

# 'Date' 列をインデックスとして設定
        df.set_index('Date', inplace=True)

        df.fillna(value='NaN')


# 'Date' 列に基づいてデータフレームを昇順にソート
        df = df.sort_values(by='Date')

# Columnの型一覧
        self.logger.debug(f"{field_name} df.index: {df.index}")

        self.logger.debug(f"{field_name} df.columns: {df.columns}")

        self.logger.debug(f"{field_name} df: {df}")

        self.logger.info(f"********** _csv_to_df 終了 **********")

        return df


# ----------------------------------------------------------------------------------


    def elements_totaling(self, attribute_map, field_name):
        self.logger.info(f"********** elements_totaling 開始 **********")

        try:
# きれいに属性値を付けたものを入れ込む箱
            all_list = []

            attribute_data = {}  # 入れ込む辞書を初期化
            for key, selector in attribute_map.items():
                attribute_value = self._get_element_value(by_pattern='xpath', xpath=selector)

                try:
                    # ここで持ってるkeyに指定したデータの値を追加する
                    # 辞書に追加する場合にはこういう書き方になる
                    attribute_dic = attribute_data[key] = attribute_value.int

                except TypeError as e:
                    self.logger.error(f"{field_name} 選定してるセレクターが間違えてる可能性: {e}")
                    raise

                self.logger.debug(f"attribute_dic: {attribute_dic}")

                all_list.append(attribute_dic)

            self.logger.debug(f"all_list: {all_list}")

            self.logger.info(f"********** elements_totaling 終了 **********")

            return all_list


        except NoSuchElementException as e:
            self.logger.error(f"{field_name} 'int型'になってない: {e}")
            raise

        except Exception as e:
            self.logger.error(f"{field_name} 処理中にエラーが発生: {e}")
            raise


# ----------------------------------------------------------------------------------
# サイトからのテーブルを取得してデータフレームを作成する。

    def _get_table_to_df(self, start_num, end_num, header_additions, select_headers):
        self.logger.info(f"********** _get_table 開始 **********")

# 全てのテーブルか、必要なテーブルを選択
        select_tables = self.chrome.find_elements(By.TAG_NAME, 'table')[start_num: end_num]
        table_count = len(select_tables)

        self.logger.debug(f"start_num: {start_num}, end_num: {end_num}")
        self.logger.debug(f"table_count: {table_count}, select_tables: {select_tables}")

        all_data_frames = []  # 一つ一つのテーブルのdfを格納

        for index, table in enumerate(select_tables):
            self.logger.debug(f"処理中の table 番号 {index}")

            table_data = []

            headers = [th.text for th in table.find_elements(By.TAG_NAME, 'tr')[0].find_elements(By.TAG_NAME, 'th')]
            self.logger.debug(f"Original headers: {headers}")

            if index in header_additions:
                self.logger.debug(f"Applying additions for index {index}")
                headers = [
                    f"{header_additions[index]} {header}" if header in select_headers else header
                    for header in headers
                ]

            # table_data.append(headers)
            self.logger.debug(f"headers: {headers}")

            # trを取得→テーブルの大枠
            rows = table.find_elements(By.TAG_NAME, 'tr')
            self.logger.debug(f"rows: {rows}")

            # テーブルの各行（td）を取得
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                col_data = [col.text for col in cols]

                self.logger.debug(f"col_data: {col_data}")

                if col_data:
                    table_data.append(col_data)

            if table_data:
                df = pd.DataFrame(table_data, columns=headers)
                all_data_frames.append(df)

            for column in df.columns:
                if column != 'Date':
                    df[column] = pd.to_numeric(df[column], errors='coerce')


        if all_data_frames:

            combined_df = reduce(
                lambda left, right: pd.merge(left, right, on='Date', how='outer', suffixes=('_1', '_2')),
                all_data_frames
            )
        else:
            self.logger.error(f"all_data_framesが存在しません: \n{all_data_frames}")

# 'Date' 列を datetime 型に変換
        combined_df['Date'] = pd.to_datetime(combined_df['Date']).dt.date

# 'Date' 列をインデックスとして設定
        # combined_df.set_index('Date', inplace=True)

# 'Date' 列に基づいてデータフレームを昇順にソート
        combined_df = combined_df.sort_values(by='Date')

        self.logger.debug(f"combined_df: {combined_df}")
        self.logger.debug(f"Combined DataFrame shape: {combined_df.shape}")

        # combined_df.to_csv('check_file.csv')
        self.logger.info(f"********** _get_table 終了 **********")

# サイトから得たテーブルをきれいに並び替えたDF
        return combined_df


# ----------------------------------------------------------------------------------


    def file_delete(self, dir, field_name):
        self.logger.info(f"********** file_delete 開始 **********")

        dir = os.path.abspath(dir)
        self.logger.debug(f"dir: {dir}")

        try:
            shutil.rmtree(dir)
            self.logger.debug(f"{field_name} ファイル {dir} 削除しました")

        except Exception as e:
                self.logger.debug(f"{field_name} 削除処理中にエラーが発生{e}")


        self.logger.debug(f"{field_name} 指定のフォルダはすべて削除しました")

        self.logger.info(f"********** file_delete 終了 **********")



# ----------------------------------------------------------------------------------


    def zip_delete(self, zip_file_paths, field_name):
        self.logger.info(f"********** zip_delete 開始 **********")

        try:
            self.logger.debug(f"zip_file_paths: {zip_file_paths} ")

            for zip_file in zip_file_paths:
                if zip_file.exists():
                    os.remove(zip_file)
                    self.logger.debug(f"{zip_file} 削除しました。")

        except FileNotFoundError:
            self.logger.error(f"{field_name}: 指定のZiPファイルはありませんでした。")

        except Exception as e:
            self.logger.error(f"{field_name} 削除処理中にエラーが発生{e}")
            raise


        self.logger.debug(f"{field_name} 指定のフォルダはすべて削除しました")

        self.logger.info(f"********** zip_delete 終了 **********")


# ----------------------------------------------------------------------------------

    def files_delete(self, file_paths, field_name):
        self.logger.info(f"********** zip_delete 開始 **********")

        try:
            self.logger.debug(f"file_paths: {file_paths} ")

            for file in file_paths:
                if file.exists():
                    os.remove(file)
                    self.logger.debug(f"{file} 削除しました。")

        except FileNotFoundError:
            self.logger.error(f"{field_name}: 指定のZiPファイルはありませんでした。")

        except Exception as e:
            self.logger.error(f"{field_name} 削除処理中にエラーが発生{e}")
            raise


        self.logger.debug(f"{field_name} 指定のフォルダはすべて削除しました")

        self.logger.info(f"********** zip_delete 終了 **********")


# ----------------------------------------------------------------------------------
# Dateスプシ書き込み

    def df_gss_date_input(self, worksheet, input_values):
        self.logger.info(f"********** df_gss_date_input 開始 **********")

        try:
            self.spread_input._gss_none_cell_update(
                worksheet = worksheet,
                col_left_num = 3,
                start_row = 1,
                input_values = input_values
            )

            self.logger.info(f"********** df_gss_date_input 終了 **********")

        except Exception as e:
                self.logger.debug(f"df_gss_date_input 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# col名 スプシ書き込み

    def df_gss_col_name_input(self, worksheet, input_values):
        self.logger.info(f"********** df_gss_col_name_input 開始 **********")

        try:
            self.spread_input._gss_none_cell_update(
                worksheet = worksheet,
                col_left_num = 2,
                start_row = 1,
                input_values = input_values
            )

            self.logger.info(f"********** df_gss_col_name_input 終了 **********")

        except Exception as e:
                self.logger.debug(f"df_gss_col_name_input 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# site_value スプシ書き込み

    def df_gss_site_value_input(self, worksheet, input_values):
        self.logger.info(f"********** df_gss_site_value_input 開始 **********")

        try:
            self.spread_input._gss_none_cell_update(
                worksheet = worksheet,
                col_left_num = 4,
                start_row = 1,
                input_values = input_values
            )

            self.logger.info(f"********** df_gss_site_value_input 終了 **********")

        except Exception as e:
                self.logger.debug(f"df_gss_site_value_input 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# diff_value スプシ書き込み

    def df_gss_diff_value_input(self, worksheet, input_values):
        self.logger.info(f"********** df_gss_diff_value_input 開始 **********")

        try:
            self.spread_input._gss_none_cell_update(
                worksheet = worksheet,
                col_left_num = 5,
                start_row = 1,
                input_values = input_values
            )

            self.logger.info(f"********** df_gss_diff_value_input 終了 **********")

        except Exception as e:
                self.logger.debug(f"df_gss_diff_value_input 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# explain スプシ書き込み

    def df_gss_explain_input(self, worksheet, input_values):
        self.logger.info(f"********** df_gss_explain_input 開始 **********")

        try:
            self.spread_input._gss_none_cell_update(
                worksheet = worksheet,
                col_left_num = 6,
                start_row = 1,
                input_values = input_values
            )

            self.logger.info(f"********** df_gss_explain_input 終了 **********")

        except Exception as e:
                self.logger.debug(f"df_gss_explain_input 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# 実施した日付の書き込み

    def df_gss_input_date(self, worksheet, input_values):
        self.logger.info(f"********** df_gss_input_date 開始 **********")

        try:
            self.spread_input._gss_none_cell_update(
                worksheet = worksheet,
                col_left_num = 1,
                start_row = 1,
                input_values = input_values
            )

            self.logger.info(f"********** df_gss_input_date 終了 **********")

        except Exception as e:
                self.logger.error(f"df_gss_input_date 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# スプシ書き込みFlow

    def gss_input_flow(self, worksheet, file_name):
        try:
            self.logger.info(f"********** gss_input_flow 開始 **********")

            diff_df = self.diff_data_list_create()
            self.logger.debug(f"diff_df: {diff_df}")


            if not diff_df.empty:
            # dateデータの文字列を変換
                diff_df['Date'] = diff_df['Date'].apply(lambda x: x.strftime('%Y-%m-%d'))

            # col_name 入力
                self.df_gss_col_name_input(
                    worksheet = worksheet,
                    input_values = diff_df['diff_col']
                )

            # date 入力
                self.df_gss_date_input(
                    worksheet = worksheet,
                    input_values = diff_df['Date']
                )

            # # col_name 入力
                self.df_gss_site_value_input(
                    worksheet = worksheet,
                    input_values = diff_df['site_value']
                )


            # # diff_value 入力
                self.df_gss_diff_value_input(
                    worksheet = worksheet,
                    input_values = diff_df['diff_value']
                )

            # # explain 入力
                self.df_gss_explain_input(
                    worksheet = worksheet,
                    input_values = diff_df['diff_explain']
                )

            else:
                self.logger.info(f"データ差異なし")

                self.df_gss_col_name_input(
                    worksheet = worksheet,
                    input_values = [f"{file_name}  差異なし"]
                )

            # date 入力
                self.df_gss_date_input(
                    worksheet = worksheet,
                    input_values = ['-']
                )

            # # col_name 入力
                self.df_gss_site_value_input(
                    worksheet = worksheet,
                    input_values = ['-']
                )


            # # diff_value 入力
                self.df_gss_diff_value_input(
                    worksheet = worksheet,
                    input_values = ['-']
                )

            # # explain 入力
                self.df_gss_explain_input(
                    worksheet = worksheet,
                    input_values = ['-']
                )

            self.logger.info(f"********** gss_input_flow 終了 **********")

        except Exception as e:
                self.logger.error(f"gss_input_flow  処理中にエラーが発生: {e}")
                raise


# ----------------------------------------------------------------------------------
#TODO: resultがNoneかどうかをチェックする

    def result_data_list_create(self, key_df, download_df, key_column, field_name):
        try:
            self.logger.debug(type(key_df))
            self.logger.debug(type(download_df))

            key_df.to_csv('key_df_result.csv')
            download_df.to_csv('download_df_result.csv')

            self.logger.debug(f"key_df.columns: {key_df.columns}")
            self.logger.info(f"download_df.columns: {download_df.columns}")

# データが入力できる箇所をカウント
            key_df_total_data_count = key_df.notna().sum().sum()

            self.logger.debug(f"key_df_total_data_points: {key_df_total_data_count}")


# 実際のマージ処理前のデータ行数を確認
            self.logger.debug(f"Number of rows in key_df before merge: {len(key_df)}")
            self.logger.debug(f"Number of rows in download_df before merge: {len(download_df)}")
            # on=[key_column]が「Key」となるデータ
            # how='left'は左側（key_df）を基準する（old_dfにしかないデータはNaN）

            key_df_reset = key_df.reset_index()
            download_df_reset = download_df.reset_index()

            print(key_df_reset['Date'].head())
            print(download_df_reset['Date'].head())

# ２つのdfを結合させる  右側に結合
# how=‘left’は左側（位置引数にあるdf）を軸とする
# on=[key_column] ここで選択したcolumnを基準にして結合させる→同じものは行で結合
# indicator=True これにより、dfに（‘left_only’、‘right_only’、‘both’）をステータスを追加
# suffixes=(’_site’, ‘_csv’)同じcolumn名があった場合に左側と右側で追記するものを指定できる
            result = pd.merge(key_df_reset, download_df_reset, on=[key_column], how='left', indicator=True, suffixes=('_site', '_csv'))

            self.logger.debug(f"{field_name} result: {result}")
            self.logger.debug(f"{field_name} result.columns: {result.columns}")

# IndexをDateに変更
            result_df = result.set_index('Date')

# CSVデバッグ
            result_df.to_csv('last_result.csv')

# 大元データのColumnをリスト化
            key_columns = [col for col in key_df.columns if col != 'Date']

# 各行に対して関数を充てる
            result_df['Differences'] = result_df.apply(self._find_diff_value, axis=1, args=(key_columns,'diff_data_list_create'))

            self.logger.debug(f"{field_name} result_df: {result_df}")

            self.logger.debug(f"{field_name} result_df['Differences']: {result_df['Differences']}")

            clean_df = self._df_clean(df=result_df, column_name='Differences', field_name='diff_data_list_create')

            diff_df = self._cell_to_df(df=clean_df, column_name='Differences')

# 間違えてるリストのIndexの数
            diff_count = len(diff_df.index)

            self.logger.debug(f"{field_name} diff_count: {diff_count}")

            result_list = [diff_count, key_df_total_data_count]

            self.logger.debug(f"{field_name} result_list: {result_list}")

            return result_list


        except KeyError as e:
            self.logger.error(f"{field_name} キーのエラー、データフレームに期待されるカラムが存在しない: {e}")
            raise

        except ValueError as e:
            self.logger.error(f"{field_name} データ型エラー: {e}")
            raise

        except Exception as e:
            self.logger.error(f"{field_name} 差分データを修正中にエラーが発生: {e}")
            raise


# ----------------------------------------------------------------------------------
# df_gss_write_result_category スプシ書き込み
# TODO カテゴリーの入力方法 '商品市況:CURRENCIES'

    def df_gss_write_result_category(self, worksheet, result_category):
        self.logger.info(f"********** df_gss_write_result_category 開始 **********")

        try:
            self.spread_input._gss_none_cell_update(
                worksheet = worksheet,
                col_left_num = 2,
                start_row = 1,
                input_values = result_category
            )

            self.logger.info(f"********** df_gss_write_result_unmatched_data 終了 **********")

        except Exception as e:
                self.logger.error(f"df_gss_write_result_unmatched_data 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------# result_unmatched_data スプシ書き込み

    def df_gss_write_result_unmatched_data(self, worksheet, input_values):
        self.logger.info(f"********** df_gss_write_result_unmatched_data 開始 **********")

        try:
            self.spread_input._gss_none_cell_update(
                worksheet = worksheet,
                col_left_num = 4,
                start_row = 1,
                input_values = input_values
            )

            self.logger.info(f"********** df_gss_write_result_unmatched_data 終了 **********")

        except Exception as e:
                self.logger.error(f"df_gss_write_result_unmatched_data 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# result_base_data スプシ書き込み

    def df_gss_write_result_base_data(self, worksheet, input_values):
        self.logger.info(f"********** df_gss_write_result_base_data 開始 **********")

        try:
            self.spread_input._gss_none_cell_update(
                worksheet = worksheet,
                col_left_num = 6,
                start_row = 1,
                input_values = input_values
            )

            self.logger.info(f"********** df_gss_write_result_base_data 終了 **********")

        except Exception as e:
                self.logger.error(f"df_gss_write_result_base_data 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------# result_error スプシ書き込み

    def df_gss_write_result_error(self, worksheet, input_values):
        self.logger.info(f"********** df_gss_write_result_base_data 開始 **********")

        try:
            self.spread_input._gss_none_cell_update(
                worksheet = worksheet,
                col_left_num = 7,
                start_row = 1,
                input_values = input_values
            )

            self.logger.info(f"********** df_gss_write_result_base_data 終了 **********")

        except Exception as e:
                self.logger.error(f"df_gss_write_result_base_data 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# スプシ書き込みFlow

    def gss_result_input_flow(self, worksheet, key_df, download_df, key_column, field_name, result_category):
        try:
            self.logger.info(f"********** gss_input_flow 開始 **********")

            result_data = self.result_data_list_create(key_df, download_df, key_column, field_name)
            self.logger.debug(f"result_data: {result_data}")

            if result_data:

            # カテゴリー 入力
                self.df_gss_write_result_category(
                    worksheet = worksheet,
                    result_category = [result_category]
                )

            # アンマッチ数 入力
                self.df_gss_write_result_unmatched_data(
                    worksheet = worksheet,
                    input_values = [int(result_data[0])]
                )

            # 分母 入力
                self.df_gss_write_result_base_data(
                    worksheet = worksheet,
                    input_values = [int(result_data[1])]
                )

            # error 入力
                self.df_gss_write_result_error(
                    worksheet = worksheet,
                    input_values = ['なし']
                )
            else:
                self.logger.error(f"result_data: リストがない")



            self.logger.info(f"********** gss_input_flow 終了 **********")

        except Exception as e:
                self.logger.error(f"gss_input_flow  処理中にエラーが発生: {e}")
                raise


# ----------------------------------------------------------------------------------