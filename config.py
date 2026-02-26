"""道具名称 → 游戏快捷键映射配置"""

from collections.abc import Callable

# 匹配回调类型: (道具名称, 按键) -> None
type MatchCallback = Callable[[str, str], None]

# Vosk 中文模型名称
VOSK_MODEL_NAME = "vosk-model-small-cn-0.22"

# 音频参数
SAMPLE_RATE = 16000  # Vosk 推荐采样率
CHUNK_SIZE = 4000  # 每次读取的音频帧数

# 防抖冷却时间（秒）— 同一道具在此时间内不会重复触发
COOLDOWN_SECONDS: float = 1.0

# 道具名称 → 游戏快捷键映射
# 键: 语音识别可能输出的中文文本（支持多个别名）
# 值: 对应的游戏快捷键（需与 PUBG 游戏设置中的绑定一致）
ITEM_KEY_MAP: dict[str, str] = {
    "手雷": "g",
    "蓝圈": "h",
    "闪光弹": "t",
    "燃烧瓶": "y",
    "烟雾弹": "u",
}

# 别名映射（口语化表达 → 标准名称）
ITEM_ALIASES: dict[str, str] = {
    "雷": "手雷",
    "手雷": "手雷",
    "蓝色": "蓝圈",
    "闪": "闪光弹",
    "闪光": "闪光弹",
    "烟": "烟雾弹",
    "烟雾": "烟雾弹",
    "烟雾弹": "烟雾弹",
    "火瓶": "燃烧瓶",
    "燃烧瓶": "燃烧瓶",
}
