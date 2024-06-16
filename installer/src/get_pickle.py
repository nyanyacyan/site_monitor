#  coding: utf-8
# ----------------------------------------------------------------------------------
# 2024/6/17 更新

# ----------------------------------------------------------------------------------
import asyncio
from const import SiteUrl, AccountId
from method.AsyncProcess import AsyncGetPickle



# ------------------------------------------------------------------------------

class Main:
    def __init__(self) -> None:
       pass


    async def main(self):
      account_ids = [
         AccountId.account_id_a.value,
         AccountId.account_id_b.value,
         AccountId.account_id_c.value,
         AccountId.account_id_d.value,
         AccountId.account_id_e.value
      ]

      async_process = AsyncGetPickle(account_ids=account_ids)

      await async_process.flow_task_process()

# ------------------------------------------------------------------------------



if __name__ == '__main__':
    main_process = Main()
    asyncio.run(main_process.main())