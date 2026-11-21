# Provkörning 1 av agent-sakerhetsgranskning (2026-11-21)

## Hur körningen gjordes

Samma session som skrev skillen följde SKILL.md, så körningen är **inte oberoende**. De tre fallen från System Insight återanvänder den riktiga granskningen i `systeminsights` (PR #240). De fyra påhittade fallen granskades i provkörningen. Utfallet bedömdes av kod (`jamfor_facit.py`), som också kontrollerar att utfallet är räknat ur fynden. Påståendena i `graders/` kräver en modells bedömning och är inte bedömda här.

En oberoende körning görs med `claude plugin eval . --allow-tools Write,Edit,Bash --scaffold` från skillens mapp, eller i månadsgranskningen.

## Resultat

| Fall | Utfall | Kodens kontroller |
|---|---|---|
| si-fraga-harvan-extern | underkänd (OAuth-klienter får organisationens material) | 5/5 |
| si-spanaren | godkänd med villkor | 6/6 |
| si-planeraren | godkänd med villkor (automatiskt läge blir nivå 3) | 5/5 |
| felmarkerad-hamtning | underkänd (kontraktet döljer C) | 5/5 |
| datagrind-dold | underkänd (jobbets kalender och mejl) | 4/4 |
| forening-svarsutkast | godkänd | 4/4 |
| motor-kpi | godkänd | 4/4 |

Två fall prövar det som bara en granskare kan se: felmarkerad-hamtning och datagrind-dold. Där klarar kontraktet valideringen, men flaggorna motsägs av resursernas beskrivning. Repots tester visar att jämföraren fäller en granskning som missar det dolda C, och att den upptäcker ett utfall som skrivits för hand.

## Begränsning

OWASP Top 10 for Agentic Applications är använd i andra hand. PDF:en gick att hämta i webbläsaren men saknar textlager, och att läsa den med pdf.js nekades. Titlarna är bekräftade i flera källor, men OWASP:s egna åtgärdstexter är inte lästa.
