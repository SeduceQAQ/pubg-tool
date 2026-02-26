"""PUBG 语音道具切换工具 — 主入口"""

import logging
import sys

from vosk import Model

from config import ITEM_KEY_MAP
from key_simulator import press_key
from voice_recognition import (
    create_recognizer,
    get_model_path,
    listen_loop,
    open_microphone,
)

logger = logging.getLogger(__name__)


def on_item_matched(item_name: str, key: str) -> None:
    """语音匹配到道具时的回调"""
    logger.info("[识别] %s → 按键 %s", item_name, key)
    press_key(key)


def main() -> None:
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )

    logger.info("=== PUBG 语音道具切换工具 ===")

    # 显示当前道具映射
    logger.info("当前道具映射:")
    for name, key in ITEM_KEY_MAP.items():
        logger.info("  %s → 按键 %s", name, key)

    # 加载语音模型
    try:
        model_path = get_model_path()
        logger.info("加载语音模型: %s", model_path)
        model = Model(model_path)
    except FileNotFoundError:
        logger.exception("语音模型加载失败")
        sys.exit(1)
    except Exception:
        logger.exception("语音模型初始化失败")
        sys.exit(1)

    # 创建识别器
    recognizer = create_recognizer(model)

    # 打开麦克风
    pa = None
    stream = None
    try:
        pa, stream = open_microphone()
    except Exception:
        logger.exception("麦克风打开失败，请检查音频设备")
        sys.exit(1)

    # 开始监听
    try:
        listen_loop(stream, recognizer, on_item_matched)
    except KeyboardInterrupt:
        logger.info("用户中断，正在退出...")
    finally:
        if stream is not None:
            stream.stop_stream()
            stream.close()
        if pa is not None:
            pa.terminate()
        logger.info("已退出")


if __name__ == "__main__":
    main()
