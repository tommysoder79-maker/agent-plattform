---
tags: [agent-kontrakt]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Gör kontraktet för Alternativbyggaren i System Insight. På onsdagar räknar koden landskapet per scenario för varje öppen beslutsfråga. Modellen får beslutsfrågan, alternativen, deras drivkrafter och beroenden och scenarierna i ett anrop och föreslår nya eller kombinerade alternativ, beroenden med konfidens och utkast till beslutsunderlag, handlingsplan och bevakningsplan. Allt hamnar i case_proposals och väntar på granskning. Drivkrafternas namn och beskrivningar har en gång föreslagits ur observationer och godkänts av en person. I contracts.ts: sort agent, consequence informational.

Inget repo är kopplat. Spara varje kontrakt som en fil kontrakt-<id>.yaml i arbetskatalogen och skriv sammanfattningen i sammanfattning.md.
