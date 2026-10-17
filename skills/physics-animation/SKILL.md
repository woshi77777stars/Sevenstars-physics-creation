---
name: physics-animation
description: "为 A-Level 物理课堂制作演示动画的固定流程：读教学记忆 → 选管线 → 核对物理红线 → 出片 → 回写记忆。连续运动（轨迹、单摆、圆周运动、场变化）走 Manim 出视频；文字依次出现走 PPT 原生动画。触发场景：物理课件、演示动画、平抛、斜抛、自由落体、圆周运动、单摆、弹簧振子、Manim、演示视频、投影演示。不适用：与物理教学无关的普通汇报 PPT。"
agent_created: true
---

# 物理演示动画（A-Level / CIE 9702）

本技能为**项目内安装**：技能、命令、记忆、引擎全部位于项目根目录内，读写不超出项目目录。
若本套件以插件包形式安装（`CODEBUDDY_PLUGIN_ROOT` 已设置），命令中的相对路径一律相对插件根目录。

## 第 0 步：读教学记忆（必须先做）

读项目根目录的 `PHYSICS-MEMORY.md`。不存在就运行
`python plugins/alevel-physics-animations/scripts/anim.py memory init` 创建，并告知老师「记忆文件已建好」。
第 4 区（错误档案）必须逐条过一遍，同类错误不允许出现第二次。
读取优先级：老师当场交代 ＞ 记忆文件 ＞ 你的默认习惯。

## 第 1 步：对齐（最多 2 个问题，一轮问完）

记忆里已经写明的不要问。只问：这次课题要演示的现象与要突出的结论。

## 第 2 步：选管线

| 画面内容 | 管线 | 产物 |
| --- | --- | --- |
| 位置/角度/矢量连续变化（轨迹、单摆、圆周运动、场变化） | Manim | `outputs/videos/<topic>/<Scene>.mp4` |
| 文字依次出现 / 消失（定义、公式分步、要点逐条） | PPT 原生动画 | `outputs/pptx/<topic>.pptx` |
| 两者都有 | Manim 做运动主体，PPT 做文字 | PPT 内嵌 MP4 |

判定口径：画面里有运动就上 Manim。选定后用一行说明理由。

## 第 3 步：先给分镜再动手

用几行表格说清每一帧对应哪个物理时刻、标什么、停在哪一步。

## 第 4 步：生成时对照物理红线

全部数字从 `plugins/alevel-physics-animations/scripts/redlines.py` 的纯函数计算，禁止手画位置。
完整清单见仓库 `docs/redlines.md`。高频三条：抛体两方向独立；竖直等时位移比 1:3:5:7（仅竖直初速度为 0）；圆周加速度指向圆心、受力图不凭空加「向心力」。

## 第 5 步：实现

先跑 `python plugins/alevel-physics-animations/scripts/anim.py install-check`。

- 视频：`python plugins/alevel-physics-animations/scripts/anim.py render <topic> [--scene NAME] [--1080p30]`。
  **交付必须带 `--1080p30`**（不带是 480p15 快速预览）；不加旁白；渲染完自己看一遍成片。
- PPT：`python plugins/alevel-physics-animations/scripts/anim.py ppt <topic>`；每步点击出现，PowerPoint/WPS 可改。
- 交付前 `python plugins/alevel-physics-animations/scripts/anim.py scrub <输出目录>`。

## 第 6 步：交付前自检

- [ ] 管线选对；物理位置全部由 redlines.py 计算
- [ ] 矢量箭头方向/比例一致，坐标轴已标注，忽略空气阻力已注明
- [ ] 公式无乱码；视频 1920×1080 / 30 fps、无旁白
- [ ] PPT 动画逐条点击出现；单页动画数量合理
- [ ] scrub 无隐私告警

## 第 7 步：回写记忆（收工必做）

规则见 [references/memory-protocol.md](references/memory-protocol.md)。老师说「记住：……」立刻写；说「忘掉：……」删正文并在第 6 区留日期。被纠正时当场改掉对应条目，不要只道歉。收工用一行回报：`记忆已更新：<内容>（PHYSICS-MEMORY.md 第 N 区）`。

**硬性兜底**：Stop 钩子检测到「老师提了修改、但 PHYSICS-MEMORY.md 没更新」时会拒绝结束本轮（退出码 2）。钩子未启用时，本条仍然是必须执行的收尾步骤。

## 边界

- 不写账号、密码、密钥、学生信息、内网地址、本机绝对路径。
- 记忆文件约 400 行上限，超了压缩第 5 区。
- 渲染以分钟计，动手前先告知老师。
