---
name: agent-kontrakt
description: "Gör ett agentkontrakt: från ett behov till ett validerat kontrakt med sort, Rule of Two, risknivå, stack, budget och provsamling. Använd när en agent, ett AI-steg eller en automatisering ska byggas, ändras eller bedömas, när någon undrar om något borde vara en agent, och när en modul i System Insight ska få eller granska sitt kontrakt, även om ordet kontrakt inte nämns. Första steget i byggkedjan; följs av agent-sakerhetsgranskning."
---

# Agentkontrakt

Den här skillen gör ett behov till ett kontrakt som kod kan pröva. Du beskriver fakta: vad agenten läser, skriver och skickar. Skripten räknar risknivån och kontrollerar reglerna. Det är samma princip som i System Insight, att modellen märker och koden verkar. Den bärande tanken är att en risknivå som modellen själv bedömer går att resonera bort, medan en som räknas ur fakta inte går det.

Resultatet är ett eller flera kontrakt (`kontrakt.yaml`) som klarar `scripts/validera_kontrakt.py`, och en kort sammanfattning.

## Arbetsgång

Följ stegen i ordning. Läs referensfilerna när steget säger det, inte i förväg.

### 1. Datagrinden

Rör behovet information från användarens arbete, eller något säkerhetsskyddsklassificerat? Då byggs inget. Säg det i en mening, skriv inget kontrakt och erbjud ett alternativ som håller sig utanför, om det finns ett. Den här grinden går före allt annat, eftersom ett kontrakt i sig blir ett spår av informationen.

### 2. Sfären

Varje agent hör till exakt en sfär: `privat`, `forening` eller `complexity-insight`. Spänner behovet över två sfärer blir det två kontrakt. Sfärerna har olika data, olika ansvar och olika repon, och en agent som korsar dem flyttar data mellan dem utan att någon beslutat det.

### 3. Behovet

Formulera behovet i en eller två meningar, utan lösning. Finns skillen `arkitektur-begreppsmodell` och behovet hör till en arkitektur, ange var det fångas (nivå och vy) i `behov.sparning`.

### 4. Sorten

Välj den lägsta sort som räcker: motor, AI-steg eller agent. Läs `references/sort-och-stack.md`. Det vanligaste felet är att kalla ett fast flöde med ett modellanrop för agent. Det gör systemet dyrare att granska och svårare att testa, utan att något vinns.

### 5. Resurserna

Lista allt agenten läser (`laser`), skriver (`skriver`) och skickar utanför sfären (`kommunicerar_externt`), med flaggorna för varje resurs. Läs `references/falt.md` innan du sätter `opalitlig`, `kanslig`, `effekt`, `godkannande` och `styrs_av_modellen`. Det är där risknivån avgörs. Är du osäker på en flagga, välj det försiktigare värdet och skriv varför i `anteckningar`.

### 6. Räkna

Kör `python scripts/risk.py <kontrakt.yaml>` och skriv in nivån som skriptet ger i `riskniva`. Sätt aldrig nivån efter eget omdöme. Om nivån känns fel är det flaggorna som ska prövas igen, med fakta som skäl. Att vända en flagga för att få en lägre nivå är just det som kontraktet ska förhindra.

### 7. Nivå 3: dela upp

Ger skriptet nivå 3 (A, B och C i samma session) godtas inte kontraktet. Välj ett sätt att bryta kombinationen och beskriv valet i sammanfattningen:

- **Dela upp i delar** där var och en har högst två egenskaper. En del läser och föreslår, och en annan utför bara det som en människa godkänt. Sätt `uppdelning` i varje del.
- **Godkännande före varje handling** för det som ger C. Det passar när handlingarna är få och var och en är värd att titta på.
- **Ta bort åtkomsten** till det känsliga eller det opålitliga, om behovet klarar sig utan det.

Undvik godkännanden på allt. När allt kräver ett klick klickar man igenom, och då har grinden försvunnit (OWASP ASI09).

### 8. Resten av kontraktet

Utgå från `assets/kontrakt-mall.yaml`. Några regler att hålla:
- En ny agent börjar i läget `av`.
- Budget och största antal steg per körning är tak, inte uppskattningar.
- Provsamlingen ska ha minst 5 fall på nivå 1 och minst 10 med injektionsfall på nivå 2, och injektionsfall så fort agenten läser något opålitligt.
- Nycklar anges med namn och omfång, aldrig med värden.

### 9. Validera

Kör `python scripts/validera_kontrakt.py <filer>` med alla delar i samma körning, så att uppdelningen kan prövas. Rätta tills varje fil är OK. Felmeddelandena säger vilken regel som bröts. Saknas `jsonschema` eller `PyYAML`, installera dem med `pip install jsonschema pyyaml`.

### 10. Leverera

Det beror på sfären:

- **privat:** `agents/<id>/kontrakt.yaml` och en rad i `agentregister.yaml` i repot `agenter-privat`, som pull request om repot är kopplat. Annars lämnas filen till användaren.
- **forening:** det finns inget repo ännu. Lämna filen och säg det.
- **complexity-insight:** läs `references/system-insight.md`. Där är plattformens eget kontrakt i `src/lib/modules/contracts.ts` master, och kontraktet här är ett arbetsunderlag som översätts dit.

### 11. Sammanfatta

Avsluta med några rader, inte en genomgång av stegen:
- sort
- A, B och C med skälen, och risknivån
- vad som delades upp och varför
- för en befintlig modul: varje fält där kontraktet avviker från det som står i dag (sort, konsekvens, läge), som fynd att ta ställning till, inte som tysta ändringar
- nästa steg, som är `agent-sakerhetsgranskning`

## Skripten

`scripts/` innehåller kopior av repot `agent-plattform`: `risk.py`, `validera_kontrakt.py` och schemat. Kopiorna hålls lika med originalen av repots tester. Ändra dem inte här. En regel som behöver ändras ändras i repot, med ett test.
