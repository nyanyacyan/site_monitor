# coding: utf-8
# 2023/6/16  更新
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# import

import asyncio

from .base.utils import Logger
from .Flow import Flow


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# **********************************************************************************
# 非同期処理にて並列処理を実行していく

class AsyncProcess:
    def __init__(self, account_ids, debug_mode=False) -> None:
        # IDのリストを定義
        self.account_ids = account_ids
        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()


# ----------------------------------------------------------------------------------
# それぞれのaccount_idにて実行をしていく

    async def flow_task_process(self):
        tasks = []

        for account_id in self.account_ids:
            flow = Flow(account_id=account_id)
            tasks.append(flow.single_process_async())

        # すべてのタスクを非同期にて並列処理を実行する
        self.logger.info("これより並列処理を実行")
        await asyncio.gather(*tasks)


# ----------------------------------------------------------------------------------
# **********************************************************************************
# 非同期処理にて並列処理を実行していく

class AsyncGetPickle:
    def __init__(self, account_ids, debug_mode=False) -> None:
        # IDのリストを定義
        self.account_ids = account_ids
        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        #! 同時に行う処理の上限を設定
        self.semaphore = asyncio.Semaphore(2)

# ----------------------------------------------------------------------------------
# それぞれのaccount_idにて実行をしていく

    async def flow_task_process(self):
        tasks = []

        for account_id in self.account_ids:
            tasks.append(self._run_with_semaphore(account_id=account_id))
            await asyncio.sleep(10)


        # すべてのタスクを非同期にて並列処理を実行する
        self.logger.info("これより並列処理を実行")
        await asyncio.gather(*tasks)


# ----------------------------------------------------------------------------------
# 処理の設定をして上限を反映させる

    async def _run_with_semaphore(self, account_id):
        async with self.semaphore:
            flow = Flow(account_id=account_id)
            result = await flow.get_pickle_data_async()
            return result


# ----------------------------------------------------------------------------------
# **********************************************************************************