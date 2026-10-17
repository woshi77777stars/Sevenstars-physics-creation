# Two-machine acceptance checklist

Before distributing, run this on at least two real machines (one must be
Windows):

1. Install: copy the repository (or the offline zip) into a fresh project
   folder. Open it in WorkBuddy. Confirm the `physics-animation` skill and
   the `new-topic` command are visible.
2. Build a PPT: ask for a text-only topic (e.g. capacitance definitions).
   Confirm `outputs/pptx/<topic>.pptx` appears and each step reveals on
   click in PowerPoint/WPS without a repair prompt.
3. Propose a modification: after delivery say "把标题字号调大" and confirm
   the assistant updates `PHYSICS-MEMORY.md` section 5 and reports
   "记忆已更新：…".
4. Negative test: if the Stop hook is active, make a modification request,
   then interrupt/prevent the memory write. Confirm the session cannot
   finish and the gate message appears.
5. Video (Linux/Windows, or macOS with Homebrew cairo): render
   `kinematics` with `--1080p30`; confirm all three scenes render and the
   projectile video shows equal horizontal spacing and 1:3:5 vertical gaps.
6. Privacy: ask the assistant to remember "密码=abc123"; confirm it refuses
   and the value never appears in memory, PPT or chat.

Record OS, WorkBuddy version, Python used and pass/fail per row. Any row
failing means the package is not ready to distribute.
