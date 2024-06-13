# coding: utf-8
#* htmlの置換を行う基底クラス
# ----------------------------------------------------------------------------------
# 2023/5/30更新

# ----------------------------------------------------------------------------------
import re
import pandas as pd
from jinja2 import Environment, FileSystemLoader, exceptions
from tkinter import messagebox

# 自作モジュール
from .utils import Logger, NoneChecker

# ----------------------------------------------------------------------------------
###############################################################
# htmlを置換するクラス

class HtmlReplaceBase:
    def __init__(self, debug_mode=False):

        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        # noneチェック
        self.none = NoneChecker()


###############################################################
# ----------------------------------------------------------------------------------
# htmlファイルの読み込み

    def _html_file_read(self, input_html_file_path):
        try:
            self.logger.info(f"******** _html_file_read start ********")

            # htmlファイルを読み込む
            with open(input_html_file_path, 'r', encoding='utf-8') as file:
                html_code = file.read()

            self.logger.debug(f"html_code: \n{html_code[:30]}")

            self.logger.info(f"********  _html_file_read end ********")

            return html_code


        except FileNotFoundError as e:
            self.logger.error(f"{input_html_file_path} が見つかりません。pathを確認してください: {e}")
            messagebox.askretrycancel('エラー', f'{input_html_file_path}が見つかりません。pathを確認してください:{e}')

            raise

        except Exception as e:
            self.logger.error(f"{input_html_file_path}  読込中にエラーが発生: {e}")
            raise


# ----------------------------------------------------------------------------------
# 部分一致での置換

    def _partial_match_replace(self, mark_pattern, new_data, html_code, filed_name):
        try:
            self.logger.info(f"******** {filed_name} _replace_base start ********")

            self.logger.debug(f"{filed_name} mark_pattern: {mark_pattern}")
            self.logger.debug(f"{filed_name} new_data: {new_data}")
            self.logger.debug(f"{filed_name} html_code: {html_code[:30]}")

            # パターンを定義する（マークを定義）
            # re.compileは部分一致させることができる
            # →マークの間に「(.*?)」任意の文字列を最短一致でマッチさせる（非貪欲マッチ）
            pattern = re.compile(mark_pattern, re.DOTALL)

            # パターンを元に新しいデータに置換する
            # 第１の位置引数にパターン、第二引数に新しいデータ、第三引数に置換する全体のcode
            update_html_code = re.sub(pattern, new_data, html_code)

            self.logger.debug(f"{filed_name} update_html_code: \n{update_html_code[:100]}")

            self.logger.info(f"******** {filed_name}  _replace_base end ********")

            return update_html_code

        except Exception as e:
            self.logger.error(f"{filed_name} _replace_base 処理中にエラーが発生: {e}")
            messagebox.askretrycancel('エラー', f'処理中にエラーが発生:{e}')


# ----------------------------------------------------------------------------------
# htmlファイルを出力する

    def _html_file_write(self, update_file_path, all_update_html_code):
        try:
            self.logger.info(f"******** html_replace start ********")

            with open(update_file_path, 'w', encoding='utf-8') as file:
                new_html_file = file.write(all_update_html_code)


            self.logger.info(f"********  html_replace end ********")

            return new_html_file

        except FileNotFoundError as e:
            self.logger.error(f"{update_file_path} が見つかりません。pathを確認してください: {e}")
            raise

        except Exception as e:
            self.logger.error(f"{update_file_path} 書き込み中にエラーが発生: {e}")
            messagebox.askretrycancel('エラー', f'書き込み中にエラーが発生:{e}')

            raise


# ----------------------------------------------------------------------------------
# 行ごとのレビューデータの集約

    def review_html_generate(self, template_dir, file_name, row):
        try:
            self.logger.info(f"******** review_html_generate start ********")

            self.logger.debug(f"template_dir: {template_dir}")
            self.logger.debug(f"file_name: {file_name}")

            # jinja2を使って置換を行う際、ファイルまでのディレクトリを記載（ファイル名を除く）
            env = Environment(loader=FileSystemLoader(template_dir))

            # ファイル名を指定する
            template = env.get_template(file_name)

            review_html_list = []

            if not row.empty:
                # １から５までの数を繰り返し行う
                # iに代入することでその値を取得してレンダリングすることを繰り返し処理する
                for i in range(1, 6):
                    # 各行のColumnを定義（１〜５までのもの）
                    rating = row[f'review{i}_rating']
                    name = row[f'review{i}_name']
                    text = row[f'review{i}_text']

                    if pd.notna(rating) and pd.notna(name):
                        # 値のデータをDataFrameから抽出して辞書にまとめる
                        review = {
                            'rating' : rating,
                            'name' : name,
                            'text' : text if pd.notna(text) else ''
                        }

                        # templateを元に取得したデータを入れ込んでレンダリング実施
                        review_html = template.render(
                            rating=review['rating'],
                            name=review['name'],
                            text=review['text']
                        )

                        review_html_list.append(review_html)

                    else:
                        review_html_list.append('')

            # 行でのhtml生成したものを結合させる
            review_html = ''.join(review_html_list)

            self.logger.debug(f"review_html: {review_html}")
            self.logger.debug(type(review_html))

            # review_htmlが入っていたら
            if not review_html:
                return ''

            self.logger.info(f"******** review_html_generate end ********")

            return review_html


        except Exception as e:
            self.logger.error(f"review_html_generate 処理中にエラーが発生: {e}")
            messagebox.askretrycancel('review_html_generate エラー', f'処理中にエラーが発生:{e}')


# ----------------------------------------------------------------------------------
# 各行での処理を追加する

    def df_to_row_process(self, df, template_dir, file_name):
        try:
            self.logger.info(f"******** df_to_row_process start ********")

            self.logger.debug(f"template_dir: {template_dir}")

            # applyの中に「axis=1」を入れることで各行の処理にする
            #! 変数にDataFrameの新しいColumnを指定することで追記できる
            df['review_html'] = df.apply(
                lambda row: self.review_html_generate(template_dir, file_name, row), axis=1
            )

            self.logger.debug(df['review_html'].tail(5))

            # df.to_csv('installer/result_output/review_html.csv')

            self.logger.info(f"******** df_to_row_process end ********")

            return df

        except Exception as e:
            self.logger.error(f"df_to_row_process 処理中にエラーが発生: {e}")
            messagebox.askretrycancel('df_to_row_process エラー', f'処理中にエラーが発生:{e}')
            raise


# ----------------------------------------------------------------------------------
# すべての値を置換してhtml出力する

    def df_to_html(self, df, input_word, template_dir, file_name, update_file_path):
        try:
            self.logger.info(f"******** df_to_row_process start ********")

            self.logger.debug(df.head(3))

            # jinja2を使って置換を行う際、ファイルまでのディレクトリを記載（ファイル名を除く）
            env = Environment(loader=FileSystemLoader(template_dir))

            # ファイル名を指定する
            template = env.get_template(file_name)

            html_list = []

            if not df.empty:
                for index, row in df.iterrows():
                    name = row['name']
                    photo_link = row['photo_link']
                    prefectures = row['prefectures']
                    locality = row['locality']
                    input = input_word
                    center_lat = row['center_lat']
                    center_lng = row['center_lng']
                    japanese_address = row['japanese_address']
                    formatted_phone_number = row['formatted_phone_number']
                    business_hours = row['business_hours']
                    close_days = row['close_days']
                    website = row['website']
                    review_html = row['review_html']

                    # レンダリングの実施
                    html_code = template.render(
                        name=name,
                        photo_link=photo_link,
                        prefectures=prefectures,
                        locality=locality,
                        input=input,
                        center_lat=center_lat,
                        center_lng=center_lng,
                        japanese_address=japanese_address,
                        formatted_phone_number=formatted_phone_number,
                        business_hours=business_hours,
                        close_days=close_days,
                        website=website,
                        review_html=review_html
                    )

                    self.logger.debug(f"html_code.{index}: {html_code}")

                    html_list.append(html_code)

            html_list = ''.join(html_list)

            self.logger.debug(f"html_list: {html_list[:100]}")

            self.logger.info(f"******** df_to_row_process end ********")

            # htmlファイルに書き込み
            self._html_file_write(
                update_file_path=update_file_path,
                all_update_html_code=html_list
            )

        except exceptions.TemplateNotFound:
            self.logger.error(f"Templateに指定してる{file_name}がみつからない: {e}")
            messagebox.askretrycancel('エラー', f'{file_name}がみつからない: {e}')

            raise

        except Exception as e:
            self.logger.error(f"df_to_row_process 処理中にエラーが発生: {e}")
            messagebox.askretrycancel('df_to_row_process エラー', f'処理中にエラーが発生:{e}')
            raise


# ----------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------

#! 置換するものリスト

# 
#  店舗名
# TODO 写真
# TODO 電話番号
# TODO レビュー（ランク、名前、テキスト）
# TODO 営業時間
# TODO 定休日
# TODO サイトURL