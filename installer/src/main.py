#  coding: utf-8
# ----------------------------------------------------------------------------------
# 2024/6/17 更新

# ----------------------------------------------------------------------------------
from const import SiteUrl, AccountId
from method.Flow import Flow



# ------------------------------------------------------------------------------

class Main:
    def __init__(self,debug_mode=False) -> None:
       self.test_flow = Flow(sheet_url= SiteUrl.sheet.value, account_id= AccountId.account_id_a.value, debug_mode=debug_mode)




    def main(self):
       self.test_flow.single_process()

        account_ids = [AccountId.account_id_a.value, AccountId.account_id_b.value, AccountId.account_id_c.value, AccountId.account_id_d.value, AccountId.account_id_e.value]

# ------------------------------------------------------------------------------



if __name__ == '__main__':
    main_process = Main()
    main_process.main()