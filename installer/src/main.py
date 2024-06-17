#  coding: utf-8
# ----------------------------------------------------------------------------------
# 2024/6/17 更新

# ----------------------------------------------------------------------------------


import time
import asyncio
from const import AccountId

from method.base.utils import Logger
from method.AsyncProcess import AsyncProcess



# ------------------------------------------------------------------------------


class Main:
   def __init__(self, debug_mode=False) -> None:
      # logger
      self.setup_logger = Logger(__name__, debug_mode=debug_mode)
      self.logger = self.setup_logger.setup_logger()


   async def main(self):
      start_time = time.time()

      account_ids = [
         AccountId.account_id_a.value,
         AccountId.account_id_b.value,
         AccountId.account_id_c.value,
         AccountId.account_id_d.value,
         AccountId.account_id_e.value
      ]

      async_process = AsyncProcess(account_ids=account_ids)

      await async_process.flow_task_process()

      end_time = time.time()

      diff_time = end_time - start_time

      self.logger.info(f"処理時間 : {diff_time}")


# ------------------------------------------------------------------------------



if __name__ == '__main__':
   main_process = Main()
   asyncio.run(main_process.main())