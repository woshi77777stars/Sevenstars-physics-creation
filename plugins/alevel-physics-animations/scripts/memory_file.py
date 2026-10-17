"""Project memory: a single structured Markdown file, PHYSICS-MEMORY.md.

WorkBuddy-native: the memory lives inside the project and travels with it.
The model edits the Markdown directly (per the skill's memory protocol);
this module only locates, reads, seeds and timestamps it.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import _runtime


MEMORY_TEMPLATE = """# 教学记忆 · 物理演示动画

- 协议版本：v1.0
- 位置：项目根目录（随项目分发，不读写项目外位置）
- 维护者：AI 维护，老师可随时改
- 读取优先级：老师当场交代 ＞ 本文件 ＞ AI 默认习惯

> **怎么用**：开工前读全文；收工前只在本轮出现「他纠正了你 / 新要求 / 决定被推翻 / 新踩的坑」时才更新。
> **怎么改**：老师说「记住：……」就写进对应区；说「忘掉：……」就删正文，并在第 6 区留一行日期。
> **别写什么**：账号、密码、密钥、学校内部资料、学生个人信息、内网地址、本机绝对路径。
> **上限**：约 400 行；超了就压缩第 5 区。

---

## 1. 课堂呈现习惯

格式：`- <习惯> ｜ 证据：<他哪次说过>`

## 2. 物理正确性红线

完整清单见技能与 `plugins/alevel-physics-animations/scripts/redlines.py`，必须逐条核对。

## 3. 动画实现规范

| 画面内容 | 管线 | 产物 |
| --- | --- | --- |
| 连续运动（轨迹、单摆、圆周运动、场变化） | Manim 视频 | `.mp4` |
| 文字依次出现 / 消失 | PPT 原生动画 | `.pptx` |

## 4. 错误档案

格式：`- YYYY-MM-DD ｜ <错误> ｜ <正确做法> ｜ 复发次数：n`

## 5. 修改与制作记录

格式：`- YYYY-MM-DD ｜ 老师要求：<内容> ｜ 已改为：<内容>`

## 6. 已废弃 / 删除留痕

格式：`- YYYY-MM-DD ｜ 删除/废弃：<内容> ｜ 原因：<一句>`

## 7. 未确认项

格式：`- <问题> ｜ 待老师确认`
"""


def memory_path() -> Path:
    override = os.environ.get("PHYSICS_ANIM_MEMORY_FILE")
    if override:
        return Path(override)
    return _runtime.project_root() / "PHYSICS-MEMORY.md"


def exists() -> bool:
    return memory_path().exists()


def read() -> str:
    path = memory_path()
    return path.read_text(encoding="utf-8") if path.exists() else ""


def mtime() -> float:
    path = memory_path()
    return path.stat().st_mtime if path.exists() else 0.0


def ensure_exists() -> Path:
    path = memory_path()
    if not path.exists():
        path.write_text(MEMORY_TEMPLATE, encoding="utf-8")
    return path


def sections() -> dict[int, str]:
    """Split the memory file into its numbered sections."""
    result: dict[int, str] = {}
    current = 0
    buffer: list[str] = []
    for line in read().splitlines():
        match = re.match(r"^##\s+(\d+)\.", line)
        if match:
            if current:
                result[current] = "\n".join(buffer)
            current = int(match.group(1))
            buffer = []
        elif current:
            buffer.append(line)
    if current:
        result[current] = "\n".join(buffer)
    return result
