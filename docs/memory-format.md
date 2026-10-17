# Memory format: PHYSICS-MEMORY.md

One structured Markdown file at the project root, edited directly by the
model and travelling with the project. Full protocol:
`skills/physics-animation/references/memory-protocol.md`.

| Section | Content | Write rule |
|---|---|---|
| 1 | Classroom presentation habits | Only on explicit "remember", with evidence |
| 2 | Physics red lines | Read-only unless the teacher corrects physics |
| 3 | Pipeline rules | Defaults |
| 4 | Error archive | Automatic, dated; repeat -> recurrence +1 |
| 5 | Modification records | Automatic, dated, per applied teacher request |
| 6 | Deleted / superseded entries | "Forget" leaves a dated line here |
| 7 | Open questions | Ask once, then record the answer |

Enforcement: the WorkBuddy Stop hook scans new user messages each turn; a
detected modification request with an unchanged file blocks the turn
(exit 2). Privacy: credentials, student data, intranet addresses and
absolute paths never enter this file.
