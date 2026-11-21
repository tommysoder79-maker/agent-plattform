---
tags: [agent-kontrakt]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Kontrakt för Rödlaget i System Insight, tack. En gång i veckan tar koden varje öppen beslutsfråga med dess hypoteser, alternativ, svar på de stående frågorna och observationerna (aldrig konfidentiellt), och modellen får allt i ett anrop med påtvingat verktygsval. Den svarar med rivaliserande hypoteser och motbelägg, som sparas som råd i red_team_findings. Ingen konfidens ändras. Koden loggar i automation_runs. I contracts.ts: sort agent, consequence human.

Inget repo är kopplat. Spara varje kontrakt som en fil kontrakt-<id>.yaml i arbetskatalogen och skriv sammanfattningen i sammanfattning.md.
