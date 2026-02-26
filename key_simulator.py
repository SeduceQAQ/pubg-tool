"""按键模拟模块 — 使用 pydirectinput 发送 DirectInput 扫描码"""

import logging

import pydirectinput

logger = logging.getLogger(__name__)

# 禁用 pydirectinput 的安全暂停（默认每次操作前暂停 0.1 秒）
pydirectinput.PAUSE = 0.0


def press_key(key: str) -> None:
    """模拟按下并释放指定按键"""
    try:
        pydirectinput.press(key)
        logger.debug("按键已发送: %s", key)
    except Exception:
        logger.exception("按键发送失败: %s", key)
