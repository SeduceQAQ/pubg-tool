# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

PUBG 游戏语音道具切换工具。运行在 Windows 上的 Python 程序，通过语音识别检测用户说出的道具名称（手雷、闪光弹、烟雾弹等），自动模拟键盘按键切换到对应道具。

**前提条件**: 用户需在 PUBG 游戏设置中为每种投掷物绑定独立快捷键。

**风险警告**: 本工具使用键盘模拟（类似 VoiceAttack），存在被 BattlEye 反作弊检测的风险，用户需自行承担。

## 技术栈

- Python 3.12+，使用 **uv** 管理项目和依赖
- 语音识别: **vosk**（离线、流式、低延迟）+ **pyaudio**（麦克风输入）
- 按键模拟: **pydirectinput**（SendInput + 扫描码，游戏可识别 DirectInput）
- Windows 平台专用

## 常用命令

```bash
# 依赖管理
uv add <package>          # 添加依赖
uv sync                   # 同步/安装依赖

# 运行
uv run main.py            # 运行主程序

# 测试
uv run pytest             # 运行全部测试
uv run pytest tests/test_foo.py::test_bar  # 运行单个测试
```

## 架构设计

核心流程：麦克风音频输入 → Vosk 流式识别 → 关键词匹配 → pydirectinput 模拟按键

关键模块：

- `main.py` — 入口，初始化 Vosk 模型，启动麦克风监听主循环
- `config.py` — 道具中文名称 → 游戏快捷键的映射配置
- `voice_recognition.py` — Vosk 流式语音识别，麦克风音频流读取，关键词匹配
- `key_simulator.py` — pydirectinput 按键模拟，向游戏发送 DirectInput 扫描码

## 开发约定

- 所有代码和注释使用中文
- 道具映射支持配置化（config.py 中修改映射表）
- Vosk 中文模型: `vosk-model-small-cn-0.22`（~50MB）
