---
tags: [agent-kontrakt]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Gör kontraktet för Spanaren i System Insight. Den körs varje tisdag. Koden söker i GDELT på organisationens bevakade ämnen, hämtar startsidor och flöden från de domäner som dyker upp och slår upp licensvillkoren. Sedan får modellen kandidaterna i ett enda anrop med påtvingat verktygsval och föreslår betyg och licensnivå. Förslagen hamnar i källregistret, där en admin godkänner eller avvisar. Koden loggar körningen i automation_runs. I contracts.ts står den i dag som sort agent med consequence informational.

Inget repo är kopplat. Spara varje kontrakt som en fil kontrakt-<id>.yaml i arbetskatalogen och skriv sammanfattningen i sammanfattning.md.
