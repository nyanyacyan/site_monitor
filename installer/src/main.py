#  coding: utf-8
# ----------------------------------------------------------------------------------
# 2024/5/27 更新

# ----------------------------------------------------------------------------------
from const import AccountId, SiteUrl
from method.Flow import Flow

# ------------------------------------------------------------------------------

class TestProcess:
    def __init__(self) -> None:
       sheet_url = SiteUrl.sheet
       account_id = AccountId.account_id_a

       self.test_flow = Flow(self, sheet_url, account_id)


    def test(self):
       self.test_flow.single_process()



# ------------------------------------------------------------------------------


if __name__ == '__main__':
    test_process = TestProcess()
    test_process.test()