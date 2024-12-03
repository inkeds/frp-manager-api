from typing import Any, Callable
import asyncio
from datetime import datetime
import logging
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    def __init__(self):
        self.tasks = {}
        self.running = False
        self.task_queue = asyncio.Queue()

    async def add_task(
        self,
        task_id: str,
        func: Callable,
        *args: Any,
        **kwargs: Any
    ):
        """添加后台任务"""
        await self.task_queue.put({
            'id': task_id,
            'func': func,
            'args': args,
            'kwargs': kwargs,
            'added_at': datetime.utcnow()
        })
        logger.info(f"Added task {task_id} to queue")

    async def start(self):
        """启动任务处理器"""
        self.running = True
        while self.running:
            try:
                task = await self.task_queue.get()
                task_id = task['id']
                self.tasks[task_id] = asyncio.create_task(
                    self._execute_task(task)
                )
                self.tasks[task_id].add_done_callback(
                    lambda t, tid=task_id: self._task_done(tid)
                )
            except Exception as e:
                logger.error(f"Error processing task: {str(e)}")
                continue

    async def stop(self):
        """停止任务处理器"""
        self.running = False
        # 等待所有任务完成
        remaining_tasks = list(self.tasks.values())
        if remaining_tasks:
            await asyncio.gather(*remaining_tasks, return_exceptions=True)
        self.tasks.clear()

    async def _execute_task(self, task: dict) -> Any:
        """执行任务"""
        try:
            func = task['func']
            args = task['args']
            kwargs = task['kwargs']
            result = await func(*args, **kwargs)
            logger.info(f"Task {task['id']} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Task {task['id']} failed: {str(e)}")
            raise

    def _task_done(self, task_id: str):
        """任务完成回调"""
        if task_id in self.tasks:
            del self.tasks[task_id]

    async def get_task_status(self, task_id: str) -> dict:
        """获取任务状态"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            if task.done():
                try:
                    result = task.result()
                    status = "completed"
                except Exception as e:
                    result = str(e)
                    status = "failed"
            else:
                result = None
                status = "running"
            return {
                "task_id": task_id,
                "status": status,
                "result": result
            }
        return {
            "task_id": task_id,
            "status": "not_found",
            "result": None
        }

task_manager = BackgroundTaskManager()
