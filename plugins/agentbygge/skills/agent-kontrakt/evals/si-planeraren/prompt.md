---
tags: [agent-kontrakt]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Bevakaren som planerare i System Insight ska få ett kontrakt. Varje dag, per öppen beslutsfråga, hittar koden möjliga steg (söka på frågans sökord, läsa en bevakad signals belägg, hämta sena flöden ur organisationens egna flöden, ställa de stående frågorna om en observation utan svar) med kostnad. Modellen får frågan, beläggen och kandidaterna i ett anrop och väljer nästa steg. I skuggläge loggas planen i agent_plans och jämförs med vad analytikern gjorde. I automatiskt läge kör koden läs- och hämtstegen direkt, medan AI-steg bara körs efter att en person godkänt dem. Den skriver aldrig beslut, konfidens eller källbetyg. I dag står den i skugga.

Inget repo är kopplat. Spara varje kontrakt som en fil kontrakt-<id>.yaml i arbetskatalogen och skriv sammanfattningen i sammanfattning.md.
