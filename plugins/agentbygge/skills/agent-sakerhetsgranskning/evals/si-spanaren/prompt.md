---
tags: [agent-sakerhetsgranskning]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Säkerhetsgranska Spanaren i System Insight. Om koden: allt hämtas av koden före modellanropet (GDELT-sökning byggd av organisationens ämnen, startsidor och flöden, med skydd mot interna adresser), modellen anropas en gång med påtvingat verktygsval och texten neutraliseras i prompten. Förslagen kräver en admin. Det finns inget facit för modulen, och dess promptbyggare finns inte i injection.test.ts.

Spara granskning.yaml och granskning.md i arbetskatalogen, med kontraktet uppdaterat, och skriv sammanfattningen i sammanfattning.md.

Input files: kontrakt.yaml
