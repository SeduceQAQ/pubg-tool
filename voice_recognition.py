"""Vosk 流式语音识别模块"""

import json
import logging
import os
import time

import pyaudio
from vosk import KaldiRecognizer, Model, SetLogLevel

from config import (
    CHUNK_SIZE,
    COOLDOWN_SECONDS,
    ITEM_ALIASES,
    ITEM_KEY_MAP,
    SAMPLE_RATE,
    VOSK_MODEL_NAME,
    MatchCallback,
)

logger = logging.getLogger(__name__)

# 抑制 Vosk 内部日志
SetLogLevel(-1)

# 上次触发时间记录（道具名 → 时间戳）
_last_trigger: dict[str, float] = {}


def get_model_path() -> str:
    """获取本地 Vosk 模型路径，不存在则报错"""
    model_path = os.path.join(os.path.dirname(__file__), VOSK_MODEL_NAME)
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"未找到语音模型: {model_path}\n请下载 {VOSK_MODEL_NAME} 并放置到项目根目录"
        )
    return model_path


def build_keyword_list() -> list[str]:
    """从配置中构建所有可识别的关键词列表"""
    keywords = list(ITEM_KEY_MAP.keys()) + list(ITEM_ALIASES.keys())
    return keywords


def match_item(text: str) -> tuple[str, str] | None:
    """
    从识别文本中匹配道具名称。
    返回 (道具名称, 按键) 元组，未匹配返回 None。
    """
    # 优先匹配完整道具名
    for name, key in ITEM_KEY_MAP.items():
        if name in text:
            return (name, key)

    # 匹配别名
    for alias, standard_name in ITEM_ALIASES.items():
        if alias in text:
            return (standard_name, ITEM_KEY_MAP[standard_name])

    return None


def _should_trigger(item_name: str, cooldown: float) -> bool:
    """检查该道具是否已过冷却期，可以再次触发"""
    now = time.monotonic()
    last = _last_trigger.get(item_name, 0.0)
    if now - last < cooldown:
        return False
    _last_trigger[item_name] = now
    return True


def _process_text(text: str, cooldown: float, on_match: MatchCallback) -> bool:
    """
    处理识别文本，匹配成功且通过冷却检查时调用回调。
    返回是否匹配成功（用于决定是否重置识别器）。
    """
    if not text or text == "[unk]":
        return False
    result = match_item(text)
    if result is None:
        return False
    item_name, key = result
    if not _should_trigger(item_name, cooldown):
        logger.debug("冷却中，跳过: %s", item_name)
        return False
    on_match(item_name, key)
    return True


def create_recognizer(model: Model) -> KaldiRecognizer:
    """创建 Vosk 识别器，限定识别词汇表以提升准确率"""
    keywords = build_keyword_list()
    # Vosk 词汇表格式: JSON 数组字符串，包含所有候选词 + "[unk]" 兜底
    grammar = json.dumps(keywords + ["[unk]"], ensure_ascii=False)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE, grammar)
    recognizer.SetWords(True)
    return recognizer


def open_microphone() -> tuple[pyaudio.PyAudio, pyaudio.Stream]:
    """打开麦克风音频流，返回 (PyAudio实例, 音频流) 元组"""
    pa = pyaudio.PyAudio()
    try:
        stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )
    except Exception:
        pa.terminate()
        raise
    return pa, stream


def listen_loop(
    stream: pyaudio.Stream,
    recognizer: KaldiRecognizer,
    on_match: MatchCallback,
) -> None:
    """
    持续从麦克风读取音频并识别。
    匹配到道具关键词时调用 on_match(item_name, key) 回调。
    """
    logger.info("开始监听语音... (Ctrl+C 退出)")
    while True:
        try:
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        except OSError:
            logger.exception("音频读取失败")
            break

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            _process_text(text, COOLDOWN_SECONDS, on_match)
        else:
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get("partial", "")
            if _process_text(partial_text, COOLDOWN_SECONDS, on_match):
                # 部分结果匹配成功后重置，避免与最终结果重复触发
                recognizer.Reset()
