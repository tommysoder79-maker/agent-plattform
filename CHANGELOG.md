# Ändringslogg

## 2026-11-21 · OWASP i original

- `agent-sakerhetsgranskning/references/owasp-asi.md` är omskriven från OWASP Top 10 for Agentic Applications 2026 (version 2026, december 2025). Den har:
  - beskrivning, typiska svagheter och OWASP:s rekommendationer per punkt
  - reglerna för hur ett fynd ska klassas
  - principerna om minsta möjliga agentmakt och observerbarhet
  - licens CC BY-SA 4.0 för bearbetningen
- Källregistret: `owasp-agentic-top10-2026` är läst i original och bär beslut.
- Testfallet för Planeraren väntar sig ASI02 eller ASI08.
- `docs/arkitektur.md` version 4.

## 2026-11-21 · steg 3

- Skillen `agent-sakerhetsgranskning`: arbetsgång i åtta steg, referenser om OWASP ASI01–ASI10 (andra hand), allvar och acceptans, och System Insight, med synkade kopior av skripten och schemana.
- `scripts/granska.py`:
  - `förbered` validerar, räknar Rule of Two, gör automatiska fynd och avgör relevanta OWASP-punkter
  - `slutför` kräver bedömning av varje relevant punkt, vägrar om ett automatiskt fynd tagits bort eller en modell accepterat en risk, räknar utfallet, skriver `granskning.md` och för in utfallet i kontraktet
- `schema/granskning.schema.json`.
- Sju testfall med indatafiler och jämföraren `jamfor_facit.py`; kontrakten som fallen bygger på ligger i `tests/fixtures/granskning/`.
- Provkörning 1 (självbedömd). Första körningen på System Insight: PR #240 och issues #241–#248 i `systeminsights`.
- Källregistret: anmärkningen om OWASP uppdaterad.
- Testerna laddar jämförarna via sökväg, eftersom båda skillsen har en modul som heter `jamfor_facit`.
- `docs/arkitektur.md` version 3.

## 2026-11-21 · steg 2

- Skillen `agent-kontrakt` i pluginet `agentbygge`: arbetsgång i elva steg, referenser om principer, sort och stack, fälten och System Insight, en mall och synkade kopior av `risk.py`, valideraren och schemat.
- Tio testfall i `evals/` i formatet för `claude plugin eval`: sex moduler ur System Insight och fyra påhittade (nivå 3 som delas upp, motor, datagrinden, två sfärer). Jämföraren `jamfor_facit.py` bedömer kontrakten med kod.
- Provkörning 1, självbedömd och därför inte oberoende, med fynd om System Insight.
- Schemat: effekten `rad` och `styrs_av_modellen` med `kodstyrning`. `risk.py` räknar inte C för det koden ensam bestämmer.
- Valideraren: provsamlingens krav gäller när agenten är påslagen, och i läget `av` är en brist en varning. Schemat hittas också bredvid skriptet, så att kopian i en skill fungerar.
- `scripts/synka_skillskript.py` och ett CI-steg som kontrollerar kopiorna.
- `docs/arkitektur.md` version 2.

## 2026-11-21 · steg 1

- Repots skelett: marknadsplats och pluginet `agentbygge` (ännu utan skills).
- Schema för agentkontrakt och agentregister, med exempelkontrakt för Yahoo-rensningen i två delar.
- `scripts/risk.py`: Rule of Two och risknivå räknas ur kontraktets resurser.
- `scripts/validera_kontrakt.py`: schema, risknivå, grind vid irreversibilitet, konsekvens, provsamling efter nivå, säkerhetsgranskning, id och mapp, uppdelning, källor och sökvägar.
- `scripts/validera_skills.py`: följer Anthropics uppladdningskontroll i skill-creator; validerar också marknadsplatsen.
- `scripts/kontrollera_kallor.py` och källregistret med 22 källor.
- `scripts/kontrollera_spegel.py`: versionen måste höjas och ett borttaget avsnitt nämnas i ändringsloggen.
- `scripts/bygg_release.py`: en zip per skill med fasta tidsstämplar och SHA-256.
- CI, release, gitleaks och Dependabot.
- `docs/arkitektur.md` version 1.
