#  coding: utf-8
# ----------------------------------------------------------------------------------
# 2024/5/27 更新

# ----------------------------------------------------------------------------------
from const import SiteUrl, AccountId
from method.Flow import Flow



# ------------------------------------------------------------------------------

class TestProcess:
    def __init__(self,debug_mode=False) -> None:
       self.test_flow = Flow(sheet_url= SiteUrl.sheet.value, account_id= AccountId.account_id_a.value, debug_mode=debug_mode)




    def test(self):
       self.test_flow.single_process()



# ------------------------------------------------------------------------------



if __name__ == '__main__':
    test_process = TestProcess()
    test_process.test()