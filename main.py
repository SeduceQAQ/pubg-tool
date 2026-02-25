"""PUBG 语音道具切换工具 — 主入口"""

from vosk import Model

from config import ITEM_KEY_MAP
from key_simulator import press_key
from voice_recognition import (
    create_recognizer,
    get_model_path,
    listen_loop,
    open_microphone,
)


def on_item_matched(item_name: str, key: str) -> None:
    """语音匹配到道具时的回调"""
    print(f"[识别] {item_name} → 按键 {key}")
    press_key(key)


def main():
    print("=== PUBG 语音道具切换工具 ===")
    print()

    # 显示当前道具映射
    print("当前道具映射:")
    for name, key in ITEM_KEY_MAP.items():
        print(f"  {name} → 按键 {key}")
    print()

    # 加载语音模型
    model_path = get_model_path()
    print(f"加载语音模型: {model_path}")
    model = Model(model_path)

    # 创建识别器
    recognizer = create_recognizer(model)

    # 打开麦克风
    stream = open_microphone()

    # 开始监听
    try:
        listen_loop(stream, recognizer, on_item_matched)
    except KeyboardInterrupt:
        print("\n已退出")
    finally:
        stream.stop_stream()
        stream.close()


if __name__ == "__main__":
    main()
