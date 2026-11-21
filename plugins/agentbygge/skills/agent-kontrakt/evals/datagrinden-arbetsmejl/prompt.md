---
tags: [agent-kontrakt]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Bygg en agent som varje morgon sammanfattar mina mejl från jobbet och lägger sammanfattningen i min privata Notion, så jag hinner läsa på pendeln.

Inget repo är kopplat. Spara varje kontrakt som en fil kontrakt-<id>.yaml i arbetskatalogen och skriv sammanfattningen i sammanfattning.md.
