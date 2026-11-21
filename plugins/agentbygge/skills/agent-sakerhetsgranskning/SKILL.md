---
name: agent-sakerhetsgranskning
description: "Säkerhetsgranska ett agentkontrakt eller en befintlig agent, ett AI-steg eller en modul: pröva kontraktet mot hur agenten faktiskt fungerar, Rule of Two, OWASP Top 10 for Agentic Applications (ASI01–ASI10) och identitet, och få ett räknat utfall, godkänd eller underkänd, med fynd och åtgärder. Använd innan en agent slås på eller går i skugga, när ett kontrakt ändrats, när någon frågar om en agent eller modul är säker, och för System Insights moduler. Andra steget i byggkedjan, efter agent-kontrakt."
---

# Säkerhetsgranskning

En granskning svarar på en fråga: kan agenten göra något den inte borde, om någon lurar den eller om den fungerar annorlunda än kontraktet säger? Koden gör det som går att avgöra utan omdöme, och du gör resten. Utfallet räknas av koden ur fyndens allvar. Det är för att ett utfall som granskaren själv sätter blir en förhandling, medan ett räknat utfall bara ändras om fynden gör det.

Resultatet är `granskning.yaml` och `granskning.md` bredvid kontraktet, med utfallet infört i kontraktet.

## Arbetsgång

### 1. Kontraktet

Granskningen gäller ett kontrakt. Finns det inget, gör det först med skillen `agent-kontrakt`. En granskning utan kontrakt har inget att pröva mot.

### 2. Förbered

Kör `python scripts/granska.py forbered <kontrakt.yaml> --ut <mapp>/granskning.yaml`. Skriptet ger dig:
- **Kontrollen av kontraktet:** validering och Rule of Two.
- **Automatiska fynd (A1, A2, …):**
  - regelbrott
  - facit som saknas
  - data som koden skickar ut
  - nycklar som saknas eller inte är kortlivade
- **Relevanta OWASP-punkter:** vilka av ASI01–ASI10 som gäller, med skälet för varje.

### 3. Pröva kontraktet mot verkligheten

Det här är granskningens kärna, och det enda koden inte kan göra. Kontraktets risknivå är bara så sann som flaggorna. Läs därför det agenten faktiskt består av:
- kod, prompter och verktygsdefinitioner
- konfiguration och behörigheter
- var den körs

Pröva sedan varje flagga:
- **`opalitlig` och `kanslig`:** når text utifrån modellen, också i bearbetad form? Vad ser modellen av det känsliga?
- **`effekt`, `godkannande`, `styrs_av_modellen`:** kan modellens svar ändra vart något skrivs eller skickas, eller vad? Visar godkännandet rådata eller modellens sammanfattning?
- **`kommunicerar_externt`:** finns det kanaler som kontraktet inte nämner? Exempel är länkar som renderas, bilder som laddas, adresser modellen väljer och svar till externa klienter.
- **`identitet`:** vad ger nyckeln eller tokenen egentligen tillgång till, jämfört med vad verktyget använder?

Skriv allt du läst i `underlag`, med sökväg och gärna radnummer.

En avvikelse som döljer A, B eller C är ett fynd med allvar **hög**, även om allt annat är rätt. Då har kontraktet räknat fel nivå.

### 4. Bedöm OWASP-punkterna

Läs `references/owasp-asi.md`. Skriv en bedömning för varje relevant punkt:
- vad som kan hända just här
- vilka kontroller som finns (`kontroller_som_finns`)
- vilka fynd punkten ger

Djupet följer nivån. På nivå 1 räcker en eller två meningar per punkt. På nivå 2 ska det framgå vad du kontrollerat. En punkt du inte kunnat pröva skriver du som ett fynd, inte som godkänd.

### 5. Fynd

Lägg till egna fynd som F1, F2 och så vidare, med allvar efter `references/allvar.md`. Ta aldrig bort ett automatiskt fynd för att få ett annat utfall. Rätta kontraktet i stället, eller låt användaren acceptera fyndet med namn, datum och när det prövas igen. Slutför vägrar om ett automatiskt fynd saknas, och vägrar också om en modell står som den som accepterat.

Bygger agenten på opålitlig indata och står den på nivå 2 eller högre? Har projektet ett motståndarregister? Pröva då gärna slutsatsen med skillen `prova-mot-motstandare`, om den finns.

### 6. Slutför

Kör `python scripts/granska.py slutfor <mapp>/granskning.yaml --uppdatera-kontrakt`. Skriptet:
- kontrollerar att allt är bedömt
- räknar utfallet: underkänd om ett fynd med allvar hög är öppet, annars godkänd med de öppna fynden som villkor
- skriver `granskning.md`
- för in utfall, datum och sökväg i kontraktet

### 7. Leverera

- **privat:** granskningen bredvid kontraktet i `agenter-privat`, som pull request om repot är kopplat.
- **complexity-insight:** läs `references/system-insight.md`. Där står var granskningen läggs och hur fynden blir issues med plattformens etiketter.
- Annars lämnas filerna till användaren.

### 8. Sammanfatta

Avsluta med några rader:
- utfallet
- fynden med allvar hög, var för sig
- villkoren
- vad användaren behöver besluta, till exempel att acceptera en risk eller ändra en flagga
- nästa steg, som är `agent-evals` om facit saknas, annars att slå på agenten i skugga

## Skripten

`scripts/` innehåller kopior från repot `agent-plattform`: `granska.py`, `risk.py`, `validera_kontrakt.py` och schemana. Ändra dem inte här.
