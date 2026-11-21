---
tags: [agent-kontrakt]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Scenarioberättaren i System Insight behöver ett kontrakt. Varje natt, för varje scenario som skrivits om eller fallit, bygger koden underlaget (scenarierna, drivkrafterna, beläggen och observationerna, aldrig konfidentiell text) och modellen skriver i ett anrop en förklaring med trådar till beläggen. Den kan också föreslå drivkrafter som saknas. Förklaringen sparas i scenario_explanations och visas för användarna; drivkraftsförslagen går till granskning i driver_proposals. Den rör aldrig scenarierna. I contracts.ts: sort agent, consequence informational.

Inget repo är kopplat. Spara varje kontrakt som en fil kontrakt-<id>.yaml i arbetskatalogen och skriv sammanfattningen i sammanfattning.md.
