# Ändringslogg

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
