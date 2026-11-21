# Arkitektur för agentbygget (version 4, 2026-11-21)

**Master.** Det här dokumentet är `claude/agent-arkitektur.md` i Claude-projektet "AI agenter". Spegeln ligger i repot som `docs/arkitektur.md`. Hur de hålls lika står i *Så hålls dokumentet aktuellt* längst ned.

## Kärnan i en mening

Skillsen beskriver inte hur agenter byggs. De kör en byggkedja: modellen skriver förslag, koden kontrollerar dem och du fattar besluten, på samma sätt som i System Insight.

## Principer

1. **Det som körs har git som master.** Kod, skills, scheman och kontrakt ändras genom pull requests i GitHub. Det du tänker i, som det här dokumentet, får ha Claude-projektet som master, så länge varje version också hamnar i git.
2. **Modellen märker, koden verkar.** Allt som kod kan avgöra avgör kod: schemat, risknivån, grinden vid oåterkalleliga handlingar och kraven på provsamlingen. En skill anropar skripten i stället för att bedöma själv.
3. **Lägsta sort först.** Motor före AI-steg, AI-steg före agent. En agent planerar egna steg och används bara där vägen inte kan bestämmas i förväg (Anthropic, *Building effective agents*). OWASP kallar samma sak minsta möjliga agentmakt (least agency): självständighet där den inte behövs ökar attackytan utan att tillföra något.
4. **Högst två av tre.** Inom en session får en agent ha högst två av egenskaperna A (opålitlig indata), B (känslig data) och C (ändrar tillstånd eller kommunicerar externt utan godkännande före varje handling) (Meta, *Agents Rule of Two*).
5. **Grind vid irreversibilitet.** En oåterkallelig handling kräver alltid en människas godkännande före varje handling.
6. **Djupet följer risken.** Risknivån bestämmer hur mycket granskning, test och skugga en agent behöver. En person ska orka förvalta det.
7. **Datagrinden.** Ingen information från arbetet, och inget säkerhetsskyddsklassificerat, får någonsin komma in i en agent eller i något av repona.
8. **En sfär per agent.** Privat, föreningen och Complexity Insight hålls isär. Ingen agent spänner över två sfärer.
9. **Egen identitet.** Varje agent har egna, avgränsade nycklar och kan stängas av utan att något annat påverkas. Befintliga standarder som OAuth används, ingen egen identitetsstack (NIST NCCoE).
10. **Utbytbar runtime, fasta kontrakt.** Bind hårt vid protokollen (MCP, A2A, Agent Skills, AGENTS.md) och kontrollerna. Ramverket under, som Claude Agent SDK eller LangGraph, ska gå att byta.

## Var allt ligger

| Plats | Innehåll |
|---|---|
| `tommysoder79-maker/agent-plattform` (privat) | Skillsens källa i `plugins/<plugin>/skills/`, `schema/`, `scripts/`, `kallregister/`, CI och release. Ingen data. |
| `tommysoder79-maker/agenter-privat` (privat) | `agentregister.yaml` och `agents/<namn>/` med kontrakt, granskning och evals för privata agenter. |
| `tommysoder79-maker/systeminsights` (privat) | System Insights agenter som i dag: kontrakten i `src/lib/modules/contracts.ts`, facit i `src/lib/eval/`. Skillsen skriver dit som pull requests. |
| Claude-kontot (Max), Customize > Skills | Skillsen som körs: personliga skills, uppladdade som zip. De syns i chatten och i Claude Code-sessioner. |
| Claude-projektet "AI agenter" | Det här dokumentet (master). |
| Claude-projektet "Complexity insight" | System Insights målarkitektur (master), oförändrat. |
| Schemalagda uppgifter i Claude | Månadsgranskningen, påminnelser och privata agenters körningar. |

Max har ingen automatisk synk från GitHub till Claude; den finns för Team och Enterprise. Därför finns ett releasesteg (se *Release*). `.claude-plugin/marketplace.json` finns ändå, så att repot kan synkas direkt vid ett byte till Team och kan installeras i Claude Code. Installera inte pluginet i Claude Code så länge skillsen också finns i kontot, eftersom det ger dubbletter.

## Byggkedjan

```
Behov ─► 1 agent-kontrakt ─► 2 agent-sakerhetsgranskning ─► 3 agent-evals ─► 4 agent-drift
          modellen skriver     skript först, sedan            facit, injektion,  skugga → automatiskt,
          skript validerar     OWASP efter risknivå           regression         budget, nödstopp, avveckling
          kontrakt.yaml        godkänd/underkänd + issues     evals/ + rapport   agentregister
          └─────────────────── du godkänner vid varje grind ───────────────────────────┘
```

Det finns ingen orkestrerande skill. Varje skill slutar med att peka på nästa steg. Säkerhetsgranskningen och evals kan också köras fristående, till exempel på System Insights agenter.

| Skill | Gör | Vilar på | Status |
|---|---|---|---|
| `agent-kontrakt` | Från behov till kontrakt: datagrinden, sfären, behovet (med `arkitektur-begreppsmodell`), sorten, resurserna, Rule of Two och risknivå med `scripts/risk.py`, uppdelning vid nivå 3, validering och leverans per sfär. För System Insight blir resultatet en post i `contracts.ts`, och avvikelser från posten redovisas som fynd. | `schema/agentkontrakt.schema.json`, `scripts/` | Byggd (steg 2) |
| `agent-sakerhetsgranskning` | `scripts/granska.py förbered` validerar, räknar Rule of Two, gör automatiska fynd och avgör vilka av ASI01–ASI10 som är relevanta. Granskaren prövar kontraktets flaggor mot koden och bedömer punkterna. `granska.py slutför` räknar utfallet: underkänd om ett fynd med allvar hög är öppet. Automatiska fynd kan inte tas bort, och bara en person kan acceptera en risk. | OWASP (original), Meta, NCCoE | Byggd (steg 3) |
| `agent-evals` | Facit ur verkliga fel, injektionsfall i varje fält som kommer utifrån, inspelade svar för regression och bedömning av utfall, inte väg. Mönstret kommer från System Insights `src/lib/eval`. | Anthropic, *Demystifying evals* | Steg 4 |
| `agent-drift` | Registrering, start i skugga, kriterier för befordran, budget, nödstopp, månadsgranskning och avveckling med återkallade nycklar. | System Insights register | Steg 5 |

## Agentkontraktet

Schemat finns i `schema/agentkontrakt.schema.json`, och exemplen i `schema/exempel/`. Fälten kommer från System Insights modulkontrakt: syfte, sort, utlösare, läser, skriver, modell, var den körs, identitet, konsekvens, läge, budget, avstängning och provsamling. Till det kommer sfär, behov, Rule of Two och risknivå, uppdelning, datagrind, GDPR, stack, säkerhetsgranskning och källor.

Kontraktet anger fakta per resurs, och koden räknar:

- **A** om någon läst resurs har `opalitlig: true`.
- **B** om någon läst resurs har `kanslig: true`.
- **C** om någon skrivning med effekt `angringsbar` eller `oaterkallelig`, eller någon extern kommunikation, saknar `godkannande: fore-varje-handling` och kan styras av modellen. Följande räknas inte som C:
  - ett förslag (`forslag`) som hamnar i en kö där en människa avgör
  - ett råd (`rad`) som bara läses av en människa
  - en skrivning eller ett anrop som koden ensam bestämmer (`styrs_av_modellen: false`, med `kodstyrning` beskriven)

  Rule of Two gäller det som en injicerad instruktion kan få modellen att göra.
- **Risknivå** är antalet egenskaper, men lägst 1. Den deklarerade nivån måste vara lika med den räknade.

`scripts/validera_kontrakt.py` kontrollerar också:
- att oåterkalleliga handlingar har en grind
- att konsekvensklassen inte är för låg
- att provsamlingen räcker för nivån när agenten är påslagen (i läget av är en brist en varning)
- att säkerhetsgranskningen är godkänd innan en agent på nivå 2 går i skugga
- att id och mapp stämmer
- att källorna finns i källregistret
- att delarna i en uppdelning finns

## Risknivåer

| Nivå | Rule of Two | Krav |
|---|---|---|
| 1 | Högst en egenskap | Kort kontrakt, minst 5 eval-fall (och injektionsfall vid A), automatiska kontroller. |
| 2 | Två egenskaper | Minst 10 eval-fall med injektionsfall, godkänd säkerhetsgranskning innan skugga, minst två veckor i skugga. |
| 3 | Alla tre | Godtas inte. Flödet delas upp i delar som var för sig har högst två egenskaper, eller får godkännande före varje handling. |

Exemplet är Yahoo-rensningen. I en enda session blir den nivå 3, eftersom mejlen är opålitlig indata, inkorgen är privat och radering ändrar tillstånd. Uppdelad blir den två delar på nivå 2: en läsdel som bara föreslår en lista, och en utförardel som bara läser den godkända listan och flyttar till papperskorgen. Det enda oåterkalleliga steget, att tömma papperskorgen, gör du själv.

## Säkerhetskärnan

- **Rule of Two** är första spärren och räknas av kod.
- **OWASP Top 10 for Agentic Applications 2026** är fördjupningen: ASI01 Agent Goal Hijack, ASI02 Tool Misuse and Exploitation, ASI03 Identity and Privilege Abuse, ASI04 Agentic Supply Chain Vulnerabilities, ASI05 Unexpected Code Execution (RCE), ASI06 Memory & Context Poisoning, ASI07 Insecure Inter-Agent Communication, ASI08 Cascading Failures, ASI09 Human-Agent Trust Exploitation och ASI10 Rogue Agents.
  - Listan är läst i original (version 2026, december 2025). `references/owasp-asi.md` sammanfattar varje punkt med OWASP:s rekommendationer och reglerna för hur ett fynd ska klassas.
  - Originalet är licensierat CC BY-SA 4.0, så bearbetningen lyder under samma licens.
- **Observerbarhet:** OWASP kallar den icke förhandlingsbar. Varje agent ska logga vad den gör, varför och med vilka verktyg, under sin egen identitet.
- **Identitet:** egna, avgränsade och helst kortlivade nycklar per agent. Nycklarnas namn och omfång står i kontraktet, aldrig deras värden.
- **Leverantörskedjan:** externa MCP-servrar och skills är kod som körs. Läs innan installation, lås versioner och använd bara källor på nivå 1–2. Det gäller också skills som Claude skriver.
- **Godkännandetrötthet:** godkännanden krävs bara för oåterkalleliga handlingar och visar rådata, inte agentens sammanfattning (ASI09).

## Kvalitet över tid

Tre loopar:

1. **Vid varje ändring (GitHub Actions):** tester, validering av skills och marknadsplats, att skillsens kopior av skript och scheman är lika med originalen (`scripts/synka_skillskript.py --kontrollera`), exempelkontrakt, källregistret, att spegeln av det här dokumentet har högre version och inte tappat avsnitt, och sökning efter hemligheter (gitleaks). `main` ska vara skyddad: pull request och gröna kontroller.
2. **Varje månad (schemalagd uppgift i Claude):**
   - Källregistret stäms av mot nivå 1-källorna.
   - Skillsens evals körs.
   - Kontots kopia av varje skill jämförs med `main`.
   - Resultatet blir issues eller pull requests, och du beslutar.
3. **Vid händelser:** ny Claude-modell ger omkörning av alla evals; en incident blir ett nytt testfall; en ny OWASP-version ger omgranskning av alla agenter på nivå 2.

Nyckeltal:
- andelen godkända evals per skill
- andelen källor som bär beslut och är verifierade de senaste 90 dagarna
- antalet agenter vars säkerhetsgranskning är äldre än deras senaste större ändring

Evals som körs i GitHub Actions kräver en API-nyckel och kostar pengar utöver Max. Därför gör CI de deterministiska kontrollerna, och evals körs i den schemalagda Claude-uppgiften.

## Release

1. Ändringen görs som pull request i `agent-plattform`. CI ska vara grön och du slår ihop.
2. En datumtagg (`ÅÅÅÅ.MM.DD-N`, som i System Insight) startar `release.yml`. Arbetsflödet bygger en zip per skill med `scripts/bygg_release.py` och lägger dem i en GitHub Release med `MANIFEST.txt`.
3. Zip-filen laddas upp under **Customize > Skills**.
4. Ändra aldrig en skill direkt i Claude. Månadsgranskningen fångar kopior som glidit isär.

## Källor

Källregistret finns i `kallregister/kallor.yaml` och följer en trappa:
- **Nivå 1:** specifikationer och standardorgan.
- **Nivå 2:** leverantörernas egna texter.
- **Nivå 3:** sekundärkällor, som bara är pekare.

Läsnivån följer skillen `registrera-kalla`. En källa som är nivå 3, är läst i andra hand eller inte är läst får aldrig bära ett beslut, och det kontrolleras i CI. Instabila uppgifter (versioner, API:er) slås upp när skillen körs och märks med ett verifieringsdatum.

## System Insight

System Insights agenter stannar i plattformen och styrs av dess eget kontrakt, som testas i CI. Skillsen matar den styrningen i stället för att bygga en egen vid sidan om. Den första körningen av `agent-sakerhetsgranskning` gäller System Insight, och luckorna från granskningen 2026-11-21 blir issues där:
- facit saknas för Rödlaget, Spanaren och Alternativbyggaren
- de öppna fynden M-8, L-2 och M-4
- MCP-dörren till externa klienter
- regeln för mastern
- uppgiften om A2A

**Granskningen 2026-11-21** gjordes med `agent-sakerhetsgranskning` och ligger i `systeminsights` som `docs/granskning-agenter-2026-11-21/` (PR #240).
- Alla moduler är godkända med villkor, utom Fråga härvans externa dörr, som är **underkänd**: `callerOf` begränsar bara registrerade maskinkunder till G, så OAuth-klienter får organisationens material.
- Fynden finns som issues #241–#248:
  - #241 OAuth-klienter (beslut)
  - #242 Planerarens automatiska läge (beslut)
  - #243 facit och injektionstester (kvar)
  - #244 sort och consequence (rättelse)
  - #245 ämnen till GDELT (kvar)
  - #246 M-8 (kvar)
  - #247 skydd för masterdokumentet (beslut)
  - #248 A2A-uppgiften (rättelse)
- #226 har fått en kommentar.
- L-2 följs i #211 och M-4 i #231.

Provkörningen av `agent-kontrakt` 2026-11-21 (`plugins/agentbygge/skills/agent-kontrakt/evals/provkorning-1.md`) gav ytterligare fynd till steg 3:
- **Alla sex moduler är AI-steg.** Varje modul gör ett anrop med påtvingat verktygsval, men alla står som `agent` i `contracts.ts`.
- **Fältet `consequence` används på två sätt.** Fyra moduler skriver förslag men står som `informational`, och Rödlaget skriver råd men står som `human`.
- **Planeraren blir nivå 3 i automatiskt läge.**
- **Spanaren skickar organisationens ämnen till GDELT.** Det är spridning av data, men inte C.

Lovables undantag från grenskyddet är en accepterad risk som omprövas före första betalande kund, dock senast 2027-02-21.

## Byggordning

| Steg | Innehåll | Status |
|---|---|---|
| 1 | Repona, schemat, validerarna, källregistret, CI och release | Klart 2026-11-21 |
| 2 | `agent-kontrakt`, med System Insights sex moduler och fyra påhittade fall som facit (nivå 3 som delas upp, motor, datagrinden, två sfärer) | Klart 2026-11-21 |
| 3 | `agent-sakerhetsgranskning`, första körningen på System Insight (PR #240 och issues #241–#248 i `systeminsights`) | Klart 2026-11-21 |
| 4 | `agent-evals`, först facit för Rödlaget, Spanaren och Alternativbyggaren (#243) | Nästa |
| 5 | `agent-drift`, med en pilot som väljs senare | |

## Öppna beslut

1. **Metodskillsen.** `registrera-kalla`, `prova-mot-motstandare`, `arkitektur-begreppsmodell` och `natoterm-referens` flyttas in i `plugins/metod/` först när du bekräftat att de inte innehåller något från arbetet. De två första är skrivna för projektet "portfölj och utvecklingsstyrning" och nämner Försvarsmaktens sammanhang.
2. **Läsnyckel för `agenter-privat`.** CI där behöver läsa `agent-plattform`. Det kräver en finkornig, skrivskyddad token som hemligheten `AGENT_PLATTFORM_LASA`. Utan den hoppar valideringen över med en varning.
3. **Grenskydd** på båda repona: pull request och gröna kontroller.
4. **Agent Skills-specen** ska läsas i original och stämmas av mot validatorn, som i dag följer Anthropics egen uppladdningskontroll.
5. **Pilot för `agent-drift`.** Yahoo-rensningen är struken från steg 2. Två saker är öppna: vilken pilot steg 5 ska ha, och om exemplen i `schema/exempel/` ska bytas ut.
6. **En oberoende körning av `agent-kontrakt` och `agent-sakerhetsgranskning`**, med `claude plugin eval` eller i månadsgranskningen, så att skillsen inte bara är prövade av den session som skrev dem.
7. **Besluten i System Insight:** #241 (OAuth-klienter), #242 (Planerarens automatiska läge) och #247 (skydd för masterdokumentet).

## Så hålls dokumentet aktuellt

1. Projektets kopia (`claude/agent-arkitektur.md`) är master; repots `docs/arkitektur.md` är spegeln.
2. **Högsta versionsnumret vinner.** Har två kopior samma version men olika innehåll, stanna och fråga.
3. Varje ändring höjer versionen i rubriken och får en rad i ändringsloggen. Ett avsnitt som tas bort nämns i den raden. `scripts/kontrollera_spegel.py` prövar båda delarna i CI.
4. Skriv till projektet genom att ladda upp repots fil, aldrig genom att skriva av dokumentet.
5. När ett steg i byggordningen är klart, eller ett öppet beslut avgörs, ändras tabellerna samma dag.

## Ändringslogg

- Version 4 (2026-11-21): OWASP Top 10 for Agentic Applications är läst i original, och skillens referens och källregistret är uppgraderade. Principen om minsta möjliga agentmakt och kravet på observerbarhet är införda. Det öppna beslutet om PDF:en är struket, och besluten i System Insight är nu nummer 7. Planerarens fynd i System Insight klassas under ASI08 i stället för ASI10.
- Version 3 (2026-11-21): steg 3 klart. `agent-sakerhetsgranskning` är byggd, med `scripts/granska.py`, ett schema för granskning, sju testfall och provkörning 1. Granskningen av System Insight är klar: PR #240 och issues #241–#248. OWASP-titlarna är rättade efter källorna, och det är skrivet att OWASP används i andra hand. De öppna besluten 7 och 8 är nya.
- Version 2 (2026-11-21): steg 2 klart. `agent-kontrakt` är byggd, med tio testfall, en jämförare och provkörning 1. Kontraktet har fått effekten `rad` och `styrs_av_modellen` med `kodstyrning`. Provsamlingens krav gäller när agenten är påslagen. Fynden om System Insight har lagts till, Yahoo-rensningen är struken som facit och pilot, och de öppna besluten 5 och 6 är nya.
- Version 1 (2026-11-21): första versionen. Principer, placering, byggkedjan, kontraktet, risknivåer, säkerhetskärnan, kvalitet över tid, release, källor, System Insight, byggordning och öppna beslut. Steg 1 klart.
