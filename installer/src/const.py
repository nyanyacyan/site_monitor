#  coding: utf-8
# 文字列をすべてここに保管する
# ----------------------------------------------------------------------------------
# 2024/5/27 更新

# ----------------------------------------------------------------------------------
from enum import Enum

class Debug(Enum):
    discord = ''


class AccountId(Enum):
    account_id_a = "BRAND_A"
    account_id_b = "BRAND_B"
    account_id_c = "BRAND_C"
    account_id_d = "BRAND_D"
    account_id_e = "BRAND_E"
    account_id_f = "BRAND_F"
    account_id_g = "BRAND_G"
    account_id_h = "BRAND_H"
    account_id_i = "BRAND_I"
    account_id_j = "BRAND_J"
    account_id_k = "BRAND_K"
    account_id_l = "BRAND_L"
    account_id_m = "BRAND_M"
    account_id_n = "BRAND_N"
    account_id_o = "BRAND_O"
    account_id_p = "BRAND_P"
    account_id_q = "BRAND_Q"
    account_id_r = "BRAND_R"
    account_id_s = "BRAND_S"
    account_id_t = "BRAND_T"



class SiteUrl(Enum):
    #* スプシの最後をCSV出力に変更する→これによりDFにすることができる
    # https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/export?format=csv

    sheet = "https://docs.google.com/spreadsheets/d/1nNqyDuiU8_Llhh5HO9jTRS0IoI5NOTbqFZSeMmRH2Yc/export?format=csv"


class EndPoint(Enum):
    Line ="https://notify-api.line.me/api/notify"
    Chatwork = 'https://api.chatwork.com/v2'
    Slack = 'https://slack.com/api/chat.postMessage'
    Discord = 'https://discord.com/api/webhooks/1341640718955053057/00MzVUHiUw__y-IjKGSRBg7D5VtgPbD24xyeSaPR5rML6uxZ3kkAw4mahWmJ3b04JsEm'

