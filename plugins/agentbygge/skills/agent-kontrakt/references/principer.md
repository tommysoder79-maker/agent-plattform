# Principerna bakom kontraktet

Läs den här filen när en princip behöver förklaras eller ett gränsfall avgöras.

1. **Modellen märker, koden verkar.** Kontraktet anger fakta, och koden räknar och kontrollerar. En regel som kod kan avgöra ska inte avgöras av omdöme, eftersom omdöme går att övertala.
2. **Lägsta sort först.** Motor före AI-steg, AI-steg före agent (`anthropic-building-effective-agents`, `openai-practical-guide`).
3. **Högst två av tre.** Inom en session får en agent ha högst två av A (opålitlig indata), B (känslig data) och C (ändrar tillstånd eller kommunicerar externt, så att modellen kan styra det, utan godkännande före varje handling) (`meta-rule-of-two`). Regeln förutsätter att prompt injection inte går att stoppa pålitligt. Därför begränsar den vad en lurad modell kan göra, i stället för att försöka hindra att den luras.
4. **Grind vid irreversibilitet.** Det som inte kan ångras kräver en människas godkännande före varje handling.
5. **Datagrinden.** Ingen information från användarens arbete och inget säkerhetsskyddsklassificerat, någonsin.
6. **En sfär per agent.** Privat, föreningen och Complexity Insight hålls isär.
7. **Egen identitet.** Egna, avgränsade nycklar per agent, så att den kan stängas av ensam. Befintliga standarder som OAuth används (`nccoe-agent-identity`).
8. **Djupet följer risken.** Nivå 1 klarar sig med automatiska kontroller. Nivå 2 kräver granskning, injektionsfall och skugga. Nivå 3 godtas inte.

Källorna står i `kallregister/kallor.yaml` i repot `agent-plattform`, med läsnivå och datum för senaste kontroll.

## Gränsfall

- **En människa har godkänt en text utifrån.** Texten är fortfarande opålitlig, eftersom godkännandet gällde innehållet och inte instruktioner som kan gömma sig i det.
- **Koden skickar data, modellen ser resultatet.** Anropet är inte C om koden ensam bestämmer mål och innehåll. Det modellen läser av svaret är däremot opålitligt (A).
- **Svar till den som frågar.** Ett svar till en person i den egna sfären är `rad`. Ett svar till en extern agent eller en person utanför sfären är extern kommunikation.
- **Planering utan körning.** En plan som loggas eller väntar på godkännande är ett förslag. När planens steg körs utan godkännande per steg ger de C.
