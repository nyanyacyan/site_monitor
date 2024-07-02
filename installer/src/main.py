#  coding: utf-8
# ----------------------------------------------------------------------------------
# 2024/6/17 更新

# ----------------------------------------------------------------------------------


import time, os
import asyncio
import jupyter_beeper
from const import AccountId

from method.base.utils import Logger
from method.Flow import Flow



# ------------------------------------------------------------------------------


class Main:
   def __init__(self, debug_mode=False):
      # logger
      self.setup_logger = Logger(__name__, debug_mode=debug_mode)
      self.logger = self.setup_logger.setup_logger()


   def main(self):
      start_time = time.time()
      b = jupyter_beeper.Beeper()
      # (重い処理)
      account_ids = [
         AccountId.account_id_a.value,
         AccountId.account_id_b.value,
         AccountId.account_id_c.value,
         AccountId.account_id_d.value,
         AccountId.account_id_e.value,
         AccountId.account_id_f.value,
         AccountId.account_id_g.value,
         AccountId.account_id_h.value,
         AccountId.account_id_i.value,
         AccountId.account_id_j.value
      ]

      for account_id in account_ids:
         flow = Flow(account_id=account_id)
         flow.single_process()

         time.sleep(3)

      end_time = time.time()

      diff_time = end_time - start_time

      self.logger.info(f"処理時間 : {diff_time}秒")

      b.beep(frequency=100, secs=1, blocking=True) # ここでブザー音が鳴る

# ------------------------------------------------------------------------------



if __name__ == '__main__':
   main_process = Main()
   main_process.main()
