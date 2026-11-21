# Ändringslogg

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
