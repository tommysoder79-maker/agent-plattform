# Kontrakt för System Insight

I System Insight är modulkontraktet i `src/lib/modules/contracts.ts` master, och det testas mot registret i CI. Kontraktet som den här skillen gör är ett arbetsunderlag: det används för att räkna Rule of Two och pröva reglerna och översätts sedan till plattformens format. Det checkas inte in i System Insight.

## Innan du ändrar något

Läs repots `AGENTS.md` och masterdokumentet för målarkitekturen (`docs/malarkitektur.md`, där projektets kopia är master). Bygg det som står först i *Aktuell byggplan* om inte användaren säger annat. Ändringar görs som pull request i en gren, och plattformens egna regler för master, ändringslogg och tester gäller.

## Översättning

| Kontraktet här | `ModuleContract` |
|---|---|
| `id` (kebab-case) | `key` (snake_case: `scout-sources` blir `scout_sources`) |
| `sort`: motor / ai-steg / agent | `sort`: `engine` / `ai_step` / `agent` |
| `syfte` | `purpose: T(sv, en)` |
| `utlosare.typ`: schema / handelse / pa-begaran | `trigger`: `schedule` / `event` / `request` |
| `laser[].resurs` | `reads` |
| `skriver[].resurs` med effekt | `writes`, med "(förslag)" eller "(råd)" efter förslag och råd |
| `modell` | `route` (uppgiften i `aiFetch`), eller `null` för en motor |
| `var_den_kors: system-insight` | `where`: `app` / `database` / `worker` |
| (tempoklassen) | `tempo`: `pulse` / `flow` / `series` / `structure` / `request` |
| `konsekvens`: informativ / angringsbar / mansklig | `consequence`: `informational` / `reversible` / `human` |
| `lage` | registrets läge (`register` är regelns nyckel) |
| `budget.max_kostnad_kr_per_manad` | `budgetSek`, inom organisationens AI-budget |
| `provsamling` | `testSet: T(sv, en)` och `evalSet` (sökväg i `src/lib/eval/sets/`) |

Rule of Two och risknivån har inget eget fält i `ModuleContract`. Skriv dem i pull requestens beskrivning och som en kommentar ovanför posten, till exempel `// Rule of Two: AB- (nivå 2), räknat med agent-kontrakt 2026-11-21`.

## Särdrag att ta hänsyn till

- **Ett modellanrop med påtvingat verktygsval** är plattformens vanliga mönster: koden hämtar och väljer kandidater, modellen svarar med strukturerad data, och koden skriver förslag genom grinden. Det är ett AI-steg (`ai_step`), även när modulen i dag står som `agent`.
- **Agenter föreslår, tillämpar aldrig.** Det mesta som moduler skriver är förslag i granskningskön (`forslag`) eller råd (`rad`), och körloggen `automation_runs` skrivs av koden (`styrs_av_modellen: false`).
- **Konfidentiellt till AI aldrig.** Spärrat material (`ai_blocked`, `confidential`, `restricted`) når aldrig modellen. Det tar inte bort B: organisationens öppna material är ändå organisationens.
- **Dörren för externa agenter (MCP).** Ett svar till en extern klient är extern kommunikation som modellen formar. Registrerade maskinkunder får bara licensnivå G. En person som loggat in med OAuth får sina egna rättigheter.

## Avvikelser är fynd

Skiljer sig det räknade kontraktet från posten i `contracts.ts`, till exempel i sort, konsekvens eller läge, skriv avvikelsen som ett fynd i sammanfattningen och i pull requestens beskrivning. Låt användaren avgöra. Ändra inte posten i samma pull request utan att avvikelsen är godkänd, eftersom fältet kan ha en innebörd i plattformen som kontraktet här inte ser.

## Facit

En modul på nivå 2 behöver minst 10 fall med injektionsfall. Plattformens eval-ramverk (`src/lib/eval/`, `docs/eval.md`) har en adapter per modul som bygger exakt den förfrågan som produktionen skickar. Ett nytt facit följer det mönstret: ett set i `src/lib/eval/sets/`, en adapter i `src/lib/eval/modules/` och inspelade svar. Saknas facit för en befintlig modul, skriv det som ett fynd.
