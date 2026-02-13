"""异步辅助函数模块。

提供在同步环境中运行异步代码的工具函数。
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


def run_async(coro):
    """在同步环境中运行异步代码。

    此函数主要用于 Celery 任务等同步环境，
    可以正确处理事件循环的创建和清理。

    Args:
        coro: 异步协程对象

    Returns:
        异步协程的执行结果

    Examples:
        >>> async def my_async_func():
        ...     return "result"
        >>> result = run_async(my_async_func())
    """
    try:
        # 尝试获取现有的事件循环
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # 如果循环正在运行（罕见情况），在新线程中创建新循环
            import concurrent.futures
            import threading

            result = [None]
            exception = [None]

            def run_in_new_loop():
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result[0] = new_loop.run_until_complete(coro)
                except Exception as e:
                    exception[0] = e
                finally:
                    new_loop.close()

            thread = threading.Thread(target=run_in_new_loop)
            thread.start()
            thread.join()

            if exception[0]:
                raise exception[0]
            return result[0]
        else:
            # 现有循环但未运行，使用它
            return loop.run_until_complete(coro)
    except RuntimeError:
        # 没有循环存在，创建新的（Celery 的标准情况）
        return asyncio.run(coro)
