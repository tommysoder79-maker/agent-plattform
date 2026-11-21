# Sort och stack

## Sorten: välj den lägsta som räcker

Frågan är vem som bestämmer nästa steg.

| Sort | Nästa steg bestäms av | Prov |
|---|---|---|
| **motor** | Koden. Ingen modell. | Går reglerna att skriva ner? Då är det en motor: hämta, räkna, jämföra, skicka enligt regel. |
| **ai-steg** | Koden. Modellen gör ett avgränsat arbete i ett fast flöde, oftast ett anrop med strukturerat svar. | Kan flödet ritas i förväg, med modellen som en ruta? Då är det ett AI-steg, även om modellen väljer bland kandidater som koden hittat. |
| **agent** | Modellen, utifrån resultatet av föregående steg. | Måste modellen se vad ett steg gav innan den kan välja nästa, i en slinga med verktyg? Först då är det en agent. |

Kännetecken på ett AI-steg som ofta kallas agent:
- ett enda modellanrop med påtvingat verktygsval (`tool_choice` på en bestämd funktion), där svaret är data som koden verkställer
- koden hämtar och söker *före* modellen, och modellen bedömer det som hämtats
- modellen väljer bland kandidater som koden tagit fram, och koden kör valet utan att fråga modellen igen

Varför det spelar roll: ett AI-steg kan testas fall för fall med inspelade svar, och dess risk är lätt att avgränsa. En agent kan välja vägar ingen förutsett, och det kräver mer granskning, mer test och tätare tak. Anthropic skriver att de mest framgångsrika systemen bygger på enkla, sammansättbara mönster och lägger till komplexitet bara när det behövs (källa: `anthropic-building-effective-agents`).

Skriv i `sort_motivering` varför en lägre sort inte räcker. För ett AI-steg räcker en mening om varför regler inte duger. För en agent ska det framgå vilket beslut som kräver att modellen ser föregående resultat.

## Stacken

| `stack.val` | När | Körs ofta som |
|---|---|---|
| `claude-skill` | En session i taget i Claude, med verktyg och connectors som redan finns. Inget som måste överleva en omstart. | `claude-chatt`, `claude-schemalagd-uppgift`, `claude-code-lokalt` |
| `claude-agent-sdk` | Eget program med verktygsslinga, egna verktyg eller egen driftmiljö. | `github-actions`, `annan` |
| `langgraph` | Körningar som pågår länge och måste kunna fortsätta efter en omstart (durable execution), eller som ska vara oberoende av modelleverantör. | `annan` |
| `system-insight-modul` | Allt som körs i System Insight. Plattformens dörrar, register och grindar gäller. | `system-insight` |
| `annan` | Annat, till exempel ett vanligt skript för en motor. Motivera. | |

Utgå från `claude-skill` för privata behov och föreningens behov, och från `system-insight-modul` för allt i System Insight. Byt bara när ett krav i behovet inte går att uppfylla annars, och skriv kravet i `stack.motivering`.

Versioner och API:er för SDK:erna ändras ofta. Slå upp den aktuella dokumentationen när kontraktet skrivs, till exempel med Context7 eller på leverantörens webbplats, och skriv i `anteckningar` vad som kontrollerades och när. Skriv inte versionsnummer ur minnet.

För en motor sätts `modell.leverantor` till `ingen`.
