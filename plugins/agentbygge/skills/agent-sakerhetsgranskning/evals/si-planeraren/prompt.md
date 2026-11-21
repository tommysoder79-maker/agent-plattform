---
tags: [agent-sakerhetsgranskning]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Granska Planeraren i System Insight. Den står i skugga i dag. I automatiskt läge kör koden de läs- och hämtsteg som modellen valt direkt, och AI-steg först efter en persons godkännande. En admin kan byta läge i registret i Bakom scenerna. Verktygen är fasta, målen prövas igen och planen har en budget.

Spara granskning.yaml och granskning.md i arbetskatalogen, med kontraktet uppdaterat, och skriv sammanfattningen i sammanfattning.md.

Input files: kontrakt.yaml
