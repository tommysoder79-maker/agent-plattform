# Arbeta i agent-plattform

- Läs `docs/arkitektur.md` först. Där står principerna, var allt ligger, byggkedjan, kontraktet, risknivåerna och byggordningen. Bygg det som står först i *Byggordning* om inte Tommy säger annat.
- **Datagrinden:** ingen information från Tommys arbete och inget säkerhetsskyddsklassificerat förs in i repot, i en skill eller i ett exempel. Är du osäker, stanna och fråga.
- **Modellen märker, koden verkar.** Det som kan avgöras av kod finns i `scripts/` (schema, risknivå, grindar, provsamlingens krav). En skill anropar skripten och ändrar dem inte för att få ett visst utfall. Ändras en regel, ändras den i skriptet med ett test.
- **Skills** ligger i `plugins/<plugin>/skills/<namn>/` och följer Anthropics uppladdningskontroll, som `scripts/validera_skills.py` tillämpar:
  - frontmatter med bara `name`, `description`, `license`, `allowed-tools`, `metadata` och `compatibility`
  - `name` i kebab-case, samma som mappen
  - en SKILL.md
  - SKILL.md hålls kort, med stabil kunskap i `references/`, skript i `scripts/`, mallar i `assets/` och skillens egna testfall i `evals/`
  - instabila uppgifter (versioner, API:er) slås upp när skillen körs och märks med ett verifieringsdatum
- **Källor:** ett val som vilar på en källa står i `kallregister/kallor.yaml`. En källa på nivå 3, läst i andra hand eller inte läst får inte bära ett beslut.
- **Ändringar** görs i en gren och som pull request. CI ska vara grön, och Tommy slår ihop. Inga hemligheter i repot; nycklars namn och omfång står i kontrakt, aldrig deras värden.
- **Masterdokumentet:** `docs/arkitektur.md` speglar `claude/agent-arkitektur.md` i Claude-projektet "AI agenter":
  - Högsta versionsnumret vinner; vid samma version med olika innehåll, stanna och fråga.
  - Höj versionen och skriv en rad i ändringsloggen vid varje ändring.
  - Skriv till projektet genom att ladda upp repots fil, aldrig genom att skriva av den.
- **Release:** en datumtagg `ÅÅÅÅ.MM.DD-N` bygger en zip per skill. Zip-filen laddas upp under Customize > Skills. Ändra aldrig en skill direkt i Claude.
- Skriv dokument och meddelanden på enkel svenska. Identifierare i kod och scheman skrivs utan å, ä och ö.

Kör allt som CI kör:

```
pip install -r requirements.txt
python -m pytest -q
python scripts/validera_skills.py
python scripts/validera_kontrakt.py --kallregister kallregister/kallor.yaml schema/exempel/*.yaml
python scripts/kontrollera_kallor.py kallregister/kallor.yaml
python scripts/kontrollera_spegel.py docs/arkitektur.md
```
