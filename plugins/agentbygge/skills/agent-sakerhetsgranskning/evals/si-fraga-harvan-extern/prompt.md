---
tags: [agent-sakerhetsgranskning]
max_turns: 40
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Granska kontraktet för Fråga härvans dörr för externa klienter i System Insight innan den släpps till fler kunder. Det du behöver veta om koden: i src/lib/mcp/agent.ts finns callerOf, som returnerar "machine_client" för en agent som en admin registrerat och "member" för alla andra anropare. Verktyget ask_tangle_v1 filtrerar på licens efter callerOf, så en maskinkund får bara licensnivå G. En person som loggar in med OAuth via till exempel Claude räknas som member och får sina egna rättigheter.

Spara granskning.yaml och granskning.md i arbetskatalogen, med kontraktet uppdaterat, och skriv sammanfattningen i sammanfattning.md.

Input files: kontrakt.yaml
