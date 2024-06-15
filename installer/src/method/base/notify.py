# coding: utf-8
# 2023/6/16  更新
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import time

import os
import requests
import const
from PIL import Image
from dotenv import load_dotenv

from .utils import Logger

load_dotenv()


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# LINE通知

class LineNotify:
    def __init__(self, debug_mode=False):
        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        self.line_token = os.getenv('LINE_TOKEN')


# ----------------------------------------------------------------------------------
# LINE本文のみ送信

    def line_notify(self, message):
        try:
            self.logger.info(f"********** line_notify start **********")

            self.logger.debug(f"message: {message}")

            line_end_point = const.EndPoint.Line.value
            headers = {'Authorization': f'Bearer {self.line_token}'}
            data = {'message': message}

            response = requests.post(line_end_point, headers = headers, data=data)

            if response.status_code == 200:
                self.logger.info("送信成功")
            else:
                self.logger.error(f"送信に失敗しました: ステータスコード {response.status_code},{response.text}")

            self.logger.info(f"********** line_notify end **********")


        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"line_image_notify 処理中にエラーが発生:{e}")
            raise


# ----------------------------------------------------------------------------------
# LINE 本文＋画像を送信

    def line_image_notify(self, message, image_path):
        try:
            self.logger.info(f"********** line_image_notify start **********")

            self.logger.debug(f"message: {message}")

            line_end_point = const.EndPoint.Line.value
            headers = {'Authorization': f'Bearer {self.line_notify_token}'}
            data = {'message': message}

            image_file = image_path
            with open(image_file, mode= 'rb') as jpeg_bin:
                files = {'imageFile': (image_file, jpeg_bin, 'image/jpeg')}
                response = requests.post(line_end_point, headers = headers, data=data, files=files)

                if response.status_code == 200:
                    self.logger.debug("送信成功")
                else:
                    self.logger.error(f"送信に失敗しました: ステータスコード {response.status_code},{response.text}")

            self.logger.info(f"********** line_image_notify end **********")


        except FileNotFoundError as e:
            self.logger.error(f"{image_path} が見つかりません:{e}")
            raise

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"line_image_notify 処理中にエラーが発生:{e}")
            raise


# ----------------------------------------------------------------------------------
# **********************************************************************************
# Chatwork通知

class ChatworkNotify:
    def __init__(self, debug_mode=False):
        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        # chatwork Token
        self.chatwork_notify_token = os.getenv('CHATWORK_NOTIFY_TOKEN')
        self.chatwork_roomid = os.getenv('CHATWORK_ROOMID')


# ----------------------------------------------------------------------------------
# 本文のみ送信

    def chatwork_notify(self, message):
        try:
            self.logger.info(f"********** chatwork_notify start **********")

            end_point = const.EndPoint.Chatwork.value

            url = end_point + '/rooms/' + str(self.chatwork_roomid) + '/messages'


            headers = { 'X-ChatWorkToken': self.chatwork_notify_token}
            params = {'body': {message}}

            response = requests.post(url, headers = headers, params=params)

            if response.status_code == 200:
                self.logger.info("送信成功")
            else:
                self.logger.error(f"送信に失敗しました: ステータスコード {response.status_code},{response.text}")

            self.logger.info(f"********** chatwork_notify end **********")


        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"line_image_notify 処理中にエラーが発生:{e}")
            raise


# ----------------------------------------------------------------------------------
# 本文＋画像

    def chatwork_image_notify(self, message, img_path, resize_image_path):
        try:
            self.logger.info(f"********** chatwork_image_notify start **********")
            end_point = const.EndPoint.Chatwork.value

            self.logger.debug(f"message: {message}")
            self.logger.debug(f"img_path: {img_path}")

            img = self._isChecked_image_size(img_path, resize_image_path=resize_image_path)


            url = end_point + '/rooms/' + str(self.chatwork_roomid) + '/files'
            headers = { 'X-ChatWorkToken': self.chatwork_notify_token}

            # ファイルの形式の選定
            # Content-Typeでの指定が必要=> "image/png"

            with open(img, 'rb') as png_bin:
                files = {'file': (img, png_bin, "image/png")}

                data = {'message': message}

                # chatworkに画像とメッセージを送る
                response = requests.post(url, headers = headers, data=data, files=files)

                if response.status_code == 200:
                    self.logger.debug("送信成功")
                    time.sleep(5)

                    self._img_remove(img_path=img_path)
                    self.logger.info(f"********** chatwork_image_notify end **********")
                    return self.logger.info('送信処理に成功（画像削除完了）')

                else:
                    self.logger.error(f"送信に失敗しました: ステータスコード {response.status_code},{response.text}")
                    self._img_remove(img_path=img_path)
                    self.logger.info(f"********** chatwork_image_notify end **********")
                    return self.logger.warning('送信処理に失敗（画像削除完了）')


        except FileNotFoundError as e:
            self.logger.error(f"{img_path} が見つかりません:{e}")
            raise

        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection error: {e}")
            raise

        except requests.exceptions.Timeout as e:
            self.logger.error(f"Timeout error: {e}")
            raise

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error: {e}")
            raise

        except Exception as e:
            self.logger.error(f"line_image_notify 処理中にエラーが発生:{e}")
            raise

# ----------------------------------------------------------------------------------
# 画像のサイズによって送信できるようにリサイズ

    def _isChecked_image_size(self, img_path, max_mb_size=5):
        try:
            self.logger.info(f"********** _image_resize start **********")

            self.logger.debug(f"img_path: {img_path}")

            if img_path and os.path.exists(img_path):  #os.path.existsは有効なpathなのかを確認する
                # バイト単位で表示。バイト（B）: コンピュータのデータの最小単位。
                img_size = os.path.getsize(img_path)

                # キロバイト（KB）: 1 KB = 1024 バイト、メガバイト（MB）: 1 MB = 1024 キロバイト = 1024 * 1024 バイト。
                img_MB_size = img_size / (1024 * 1024)

                # 指定したMAXのサイズよりも大きかったら処理する
                if img_MB_size > max_mb_size:

                    # resizeする画像の名称を定義
                    path, ext = os.path.splitext(img_path)
                    resize_image_path = f'{path}_resize{ext}'

                    # 指定の画像を開く
                    with Image.open(img_path) as png:

                        # MAXのサイズよりも小さかったら繰り返し処理する
                        while img_MB_size > max_mb_size:
                            png = png.resize((png.width // 2, png.height // 2))
                            png.save(resize_image_path, "PNG")

                            img_size = os.path.getsize(resize_image_path)
                            img_MB_size = img_size / (1024 * 1024)

                    return resize_image_path

            else:
                return img_path

            self.logger.info(f"********** _image_resize end **********")


        except Exception as e:
            self.logger.error(f"_image_resize 処理中にエラーが発生:{e}")
            raise


# ----------------------------------------------------------------------------------
# resize_img削除

    def _img_remove(self, img_path):
        try:
            self.logger.info(f"********** _img_remove start **********")

            self.logger.debug(f"remove_img: {img_path}")

            if img_path and os.path.exists(img_path):  #os.path.existsは有効なpathなのかを確認する
                # resizeする画像の名称を定義
                path, ext = os.path.splitext(img_path)
                resize_image_path = f'{path}_resize{ext}'

                if os.path.exists(resize_image_path):
                    os.remove(resize_image_path)
                    self.logger.info(f"********** _img_remove end **********")
                    return self.logger.debug(f"{resize_image_path}を削除しました")

                else:
                    return self.logger.debug(f'{resize_image_path}なし')

            else:
                self.logger.info(f"********** _img_remove end **********")
                return self.logger.debug(f'{resize_image_path}なし')


        except Exception as e:
            self.logger.error(f"_img_remove 処理中にエラーが発生:{e}")
            raise


# ----------------------------------------------------------------------------------
# **********************************************************************************