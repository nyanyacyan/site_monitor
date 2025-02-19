#  coding: utf-8
# ----------------------------------------------------------------------------------
# 2024/6/17 更新

# ----------------------------------------------------------------------------------


import time, os
import asyncio
from const import AccountId
from functools import partial
from method.base.utils import Logger
from method.Flow import Flow
from method.base.thread_pool_executor import ParallelThreadPool



# ------------------------------------------------------------------------------


class Main:
    def __init__(self, debug_mode=False):
        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()



    def main(self):
        start_time = time.time()
        #! pickle生成がされてない場合には別メソッドの実行（get_pickle.py）
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
            AccountId.account_id_j.value,
            AccountId.account_id_k.value,
            AccountId.account_id_l.value,
            AccountId.account_id_m.value,
            AccountId.account_id_n.value,
            AccountId.account_id_o.value,
            AccountId.account_id_p.value,
            AccountId.account_id_q.value,
            AccountId.account_id_r.value,
            AccountId.account_id_s.value,
            AccountId.account_id_t.value
        ]

        for account_id in account_ids:
            flow = Flow(account_id=account_id)
            flow.single_process()

            time.sleep(3)

        end_time = time.time()

        diff_time = end_time - start_time

        self.logger.info(f"処理時間 : {diff_time}秒")


# ------------------------------------------------------------------------------


class MainParallel:
    def __init__(self, debug_mode=False):
        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        self.parallel = ParallelThreadPool(debug_mode=debug_mode)


    def main(self):
        #! pickle生成がされてない場合には別メソッドの実行（get_pickle.py）
        start_time = time.time()

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
            AccountId.account_id_j.value,
            AccountId.account_id_k.value,
            AccountId.account_id_l.value,
            AccountId.account_id_m.value,
            AccountId.account_id_n.value,
            AccountId.account_id_o.value,
            AccountId.account_id_p.value,
            AccountId.account_id_q.value,
            AccountId.account_id_r.value,
            AccountId.account_id_s.value,
            AccountId.account_id_t.value
        ]

        print(account_ids)

        results = self.parallel.process_single_arg(
            task_func=partial(self.process_flow),
            task_args_list=account_ids
        )
        end_time = time.time()
        diff_time = end_time - start_time

        # 結果を示す
        self.parallel.result_write(results_list=results)

        self.logger.warning(f"--全体-- 処理完了 処理時間 : {diff_time}秒")


# ------------------------------------------------------------------------------


    def process_flow(self, account_id):
        start_time = time.time()

        flow = Flow(account_id=account_id)
        flow.single_process()
        time.sleep(3)

        end_time = time.time()
        diff_time = end_time - start_time

        self.logger.info(f"--{account_id}-- 処理完了 処理時間 : {diff_time}秒")


# ------------------------------------------------------------------------------


if __name__ == '__main__':

    main_process = Main()
    main_process.main()
