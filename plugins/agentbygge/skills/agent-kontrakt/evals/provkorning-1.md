# Provkörning 1 av agent-kontrakt (2026-11-21)

## Hur körningen gjordes

Samma session som skrev skillen följde SKILL.md för vart och ett av de tio fallen och sparade kontrakt och sammanfattning. Körningen är alltså **inte oberoende**, och det finns ingen baslinje utan skill.

Kontrakten bedömdes av kod (`jamfor_facit.py`): validering, Rule of Two, nivå, sort, sfär, stack, konsekvens och antal. Påståendena i `graders/`, som kräver en modells bedömning, bedömdes av samma session och är märkta som självbedömda.

En oberoende körning görs med `claude plugin eval . --allow-tools Write,Edit,Bash` från skillens mapp (Claude Code), eller i månadsgranskningen.

## Resultat

| Fall | Kontrakt | Rule of Two | Kodens kontroller | Självbedömda påståenden |
|---|---|---|---|---|
| si-spanaren | scout-sources | AB- nivå 2 | 5/5 | 3/3 |
| si-rodlaget | red-team | AB- nivå 2 | 5/5 | 2/2 |
| si-scenarioberattaren | explain-scenarios | AB- nivå 2 | 5/5 | 2/2 |
| si-alternativbyggaren | build-options | AB- nivå 2 | 5/5 | 2/2 |
| si-fraga-harvan | ask-tangle-app, ask-tangle-extern | AB- nivå 2, A-C nivå 2 | 9/9 | 2/2 |
| si-planeraren | plan-watch | AB- nivå 2 (skugga) | 6/6 | 2/2 |
| forening-autosvar | forening-svarsutkast | AB- nivå 2 | 5/5 | 3/3 |
| motor-kpi | kpi-till-budget | -B- nivå 1, motor | 4/4 | 1/1 |
| datagrinden-arbetsmejl | inget (stoppat) | – | 1/1 | 2/2 |
| tva-sfarer | forening-avgiftspaminnelse, rakningsbevakning | -B- nivå 1, AB- nivå 2 | 5/5 | 1/1 |

Testerna i repot visar att jämföraren fäller ett felaktigt kontrakt: en agent med för låg konsekvens, ett kontrakt där datagrinden skulle ha stoppat och fel antal kontrakt.

## Fynd om System Insight

Fynden kommer ur kontrakten och från koden i `systeminsights`. De förs till steg 3 (`agent-sakerhetsgranskning`) och avgörs där.

1. **Alla sex moduler är AI-steg, inte agenter.** Varje modul gör ett modellanrop med påtvingat verktygsval i ett flöde som koden styr. I `contracts.ts` står alla som `agent`, vilket strider mot plattformens egen definition (agent = planerar egna steg). Planeraren är ett gränsfall: den väljer steg, men i ett enda anrop.
2. **Fältet `consequence` används på två sätt.** Spanaren, Scenarioberättaren, Alternativbyggaren och Planeraren skriver förslag som väntar på en människa men står som `informational`. Rödlaget skriver råd men står som `human`.
3. **Facit saknas** för Spanaren, Rödlaget och Alternativbyggaren. Det bekräftar lucka 1 från granskningen. Valideraren varnar för alla tre.
4. **Fråga härvan blir nivå 3** genom MCP-dörren, eftersom en person som loggat in med OAuth får svar med sina egna rättigheter i en extern klient. Uppdelad i appens svar och en extern dörr som bara ger licensnivå G blir båda delarna nivå 2. Det bekräftar lucka 4.
5. **Planeraren blir nivå 3 i automatiskt läge**, eftersom läs- och hämtstegen som modellen valt då körs utan godkännande. Skuggläget är nivå 2.
6. **Spanaren skickar organisationens ämnen till GDELT.** Det är inte C, eftersom koden bygger frågan, men det är data som lämnar plattformen och bör stå i dataplatsens beskrivning.

## Vad som ändrades i repot under körningen

- Effekten `rad` för text som bara läses, och `styrs_av_modellen` med `kodstyrning` för det som koden ensam bestämmer. Utan dem gick System Insights mönster inte att beskriva rätt.
- Provsamlingens krav gäller när agenten är påslagen; i läget `av` är en brist en varning. Annars gick det inte att skriva ett sant kontrakt för en modul som saknar facit.
