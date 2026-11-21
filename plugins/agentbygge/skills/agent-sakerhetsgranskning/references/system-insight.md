# Granska en modul i System Insight

## Läs först

Läs repots `AGENTS.md`, `ARCHITECTURE.md` och `docs/sakerhet.md` (hotmodell, kontroller och tidigare fynd). Ett fynd som redan står i `docs/sakerhet.md` eller i ett öppet issue är inte nytt. Hänvisa till det i stället för att skriva det igen.

## Var kontrollerna finns

| Fråga | Var |
|---|---|
| Når text utifrån modellen, och hur märks den? | Modulens `buildPrompt`; `src/lib/ai-untrusted.ts` (`neutralise`, datablock) |
| Når spärrat material modellen? | `src/lib/ai/scope.ts` (`ai_visible_scope`), `src/lib/ai-sensitivity.ts`; `src/lib/ai/scope.test.ts` stoppar CI om en anropare saknar omfånget |
| Ett eller flera modellanrop, och styr modellen nästa steg? | Modulens `*/run.server.ts`: `aiFetch(` och `tool_choice` |
| Vad skrivs, och genom vilken grind? | `agent_propose_*`, granskningskön, registret (`automation_rules`) och dess lägen |
| Vem anropar, och med vilka rättigheter? | `src/lib/mcp/agent.ts` (`agentTool`, `decide`, `callerOf`), `src/lib/mcp/reads.ts` |
| Budget, kvot och nödstopp | `src/lib/modules/contracts.ts` (`budgetSek`), registret, `aiFetch` (budget per månad), plattformens brytare |
| Hämtningar och skydd mot interna adresser | `src/lib/extract/text.server.ts`, modulens egna hämtningar |
| Facit och injektionstester | `src/lib/eval/sets/`, `src/lib/eval/injection.test.ts`, `docs/eval.md` |

## Var granskningen läggs

Granskningarna läggs i `docs/granskning-agenter-<datum>/<modul>/` i `systeminsights` (kontrakt, granskning.yaml och granskning.md), i en gren och som pull request. CI kontrollerar YAML-filer med Prettier, så kör `npx prettier --write "docs/granskning-agenter-<datum>/**/*.yaml"` innan push; Markdown kontrolleras inte. Ändra inte `docs/malarkitektur.md` i samma pull request: den är en spegel av projektets master, och mastern uppdateras i Claude-projektet "Complexity insight" när användaren beslutat om fynden.

## Fynd blir issues

Plattformens issues har två etiketter:
- **typ:** `typ: rättelse` för fel, `typ: beslut` för det som kräver användarens ställningstagande, `typ: kvar` för det som återstår
- **spår:** säkerhet och agentdörren hör till `spår: B`

Gör så här:
- Skriv ett issue per fynd med allvar hög eller medel, eller per grupp av låga fynd som hör ihop.
- Rubriken säger vad som är fel, och texten säger modul, allvar, vad som kan hända, underlag med sökväg och föreslagen åtgärd.
- Länka till granskningen.
- Finns ett öppet issue som täcker fyndet, skriv en kommentar där i stället.
- Skapa issues först när användaren bett om det. Ett issue syns i repot och kan inte tas bort, bara stängas.
