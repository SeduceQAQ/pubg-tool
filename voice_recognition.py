"""Vosk 流式语音识别模块"""

import json
import os

import pyaudio
from vosk import KaldiRecognizer, Model, SetLogLevel

from config import CHUNK_SIZE, ITEM_ALIASES, ITEM_KEY_MAP, SAMPLE_RATE, VOSK_MODEL_NAME

# 抑制 Vosk 内部日志
SetLogLevel(-1)


def get_model_path() -> str:
    """获取本地 Vosk 模型路径，不存在则报错"""
    model_path = os.path.join(os.path.dirname(__file__), VOSK_MODEL_NAME)
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"未找到语音模型: {model_path}\n"
            f"请下载 {VOSK_MODEL_NAME} 并放置到项目根目录"
        )
    return model_path


def build_keyword_list() -> list[str]:
    """从配置中构建所有可识别的关键词列表"""
    keywords = list(ITEM_KEY_MAP.keys()) + list(ITEM_ALIASES.keys())
    return keywords


def match_item(text: str) -> str | None:
    """从识别文本中匹配道具名称，返回对应的按键。未匹配返回 None。"""
    # 优先匹配完整道具名
    for name, key in ITEM_KEY_MAP.items():
        if name in text:
            return key

    # 匹配别名
    for alias, standard_name in ITEM_ALIASES.items():
        if alias in text:
            return ITEM_KEY_MAP[standard_name]

    return None


def create_recognizer(model: Model) -> KaldiRecognizer:
    """创建 Vosk 识别器，限定识别词汇表以提升准确率"""
    keywords = build_keyword_list()
    # Vosk 词汇表格式: JSON 数组字符串，包含所有候选词 + "[unk]" 兜底
    grammar = json.dumps(keywords + ["[unk]"], ensure_ascii=False)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE, grammar)
    recognizer.SetWords(True)
    return recognizer


def open_microphone() -> pyaudio.Stream:
    """打开麦克风音频流"""
    pa = pyaudio.PyAudio()
    stream = pa.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
    )
    return stream


def listen_loop(stream: pyaudio.Stream, recognizer: KaldiRecognizer, on_match):
    """
    持续从麦克风读取音频并识别。
    匹配到道具关键词时调用 on_match(item_name, key) 回调。
    """
    print("开始监听语音... (Ctrl+C 退出)")
    while True:
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text and text != "[unk]":
                key = match_item(text)
                if key:
                    # 找到匹配的道具名
                    matched_name = text
                    for name in ITEM_KEY_MAP:
                        if name in text:
                            matched_name = name
                            break
                    else:
                        for alias, std in ITEM_ALIASES.items():
                            if alias in text:
                                matched_name = std
                                break
                    on_match(matched_name, key)
        else:
            # 部分识别结果（可选：用于实时反馈）
            partial = json.loads(recognizer.PartialResult())
            partial_text = partial.get("partial", "")
            if partial_text and partial_text != "[unk]":
                key = match_item(partial_text)
                if key:
                    matched_name = partial_text
                    for name in ITEM_KEY_MAP:
                        if name in partial_text:
                            matched_name = name
                            break
                    else:
                        for alias, std in ITEM_ALIASES.items():
                            if alias in partial_text:
                                matched_name = std
                                break
                    on_match(matched_name, key)
                    # 重置识别器，避免重复触发
                    recognizer.Reset()
