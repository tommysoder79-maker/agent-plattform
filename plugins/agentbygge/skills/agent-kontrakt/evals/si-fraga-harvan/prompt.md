---
tags: [agent-kontrakt]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Kontrakt för Fråga härvan i System Insight. En person ställer en fråga i appen; koden söker i härvan (ord, betydelse och grafen) med personens egna rättigheter och hämtar beläggen, och modellen skriver i ett anrop ett svar där varje påstående pekar på sina källor. Frågan och svaret loggas i tangle_questions. Samma funktion finns som verktyget ask_tangle_v1 i MCP-dörren: registrerade maskinkunder får bara svar ur material med licensnivå G, medan en person som loggat in med OAuth via till exempel Claude får svar med sina egna rättigheter. Konfidentiellt material når aldrig modellen.

Inget repo är kopplat. Spara varje kontrakt som en fil kontrakt-<id>.yaml i arbetskatalogen och skriv sammanfattningen i sammanfattning.md.
