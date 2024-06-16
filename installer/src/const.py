#  coding: utf-8
# 文字列をすべてここに保管する
# ----------------------------------------------------------------------------------
# 2024/5/27 更新

# ----------------------------------------------------------------------------------
from enum import Enum


class AccountId(Enum):
    account_id_a = "BRAND_A"
    account_id_b = "BRAND_B"
    account_id_c = "BRAND_C"
    account_id_d = "BRAND_D"
    account_id_e = "BRAND_E"



class SiteUrl(Enum):
    #* スプシの最後をCSV出力に変更する→これによりDFにすることができる
    # https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/export?format=csv

    sheet = "https://docs.google.com/spreadsheets/d/1nNqyDuiU8_Llhh5HO9jTRS0IoI5NOTbqFZSeMmRH2Yc/export?format=csv"


class EndPoint(Enum):
    Line ="https://notify-api.line.me/api/notify"
    Chatwork = 'https://api.chatwork.com/v2'
    Slack = 'https://slack.com/api/chat.postMessage'
    Discord = ''
