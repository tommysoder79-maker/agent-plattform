---
tags: [agent-sakerhetsgranskning]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Granska kontraktet för svarsutkasten till föreningens info-adress. Utkastet visas i sin helhet med mottagare innan någon i styrelsen godkänner det, och inget skickas utan godkännande.

Spara granskning.yaml och granskning.md i arbetskatalogen, med kontraktet uppdaterat, och skriv sammanfattningen i sammanfattning.md.

Input files: kontrakt.yaml
