# agent-plattform

Skills och verktyg för att bygga, granska, testa och driva agenter. Här finns ingen data och inga agenter. De ligger i sin sfärs repo, till exempel `agenter-privat` eller `systeminsights`.

Arkitekturen beskrivs i [docs/arkitektur.md](docs/arkitektur.md).

## Innehåll

```
.claude-plugin/marketplace.json     marknadsplatsen (för Claude Code och en framtida synk)
plugins/agentbygge/                 byggkedjans skills (steg 2–5)
schema/agentkontrakt.schema.json    kontraktet för en agent
schema/agentregister.schema.json    registret över en sfärs agenter
schema/exempel/                     exempelkontrakt: Yahoo-rensningen i två delar
scripts/risk.py                     räknar Rule of Two och risknivå
scripts/validera_kontrakt.py        validerar kontrakt och register
scripts/validera_skills.py          validerar skills och marknadsplatsen
scripts/kontrollera_kallor.py       kontrollerar källregistret
scripts/kontrollera_spegel.py       kontrollerar spegeln av masterdokumentet
scripts/bygg_release.py             bygger en zip per skill
kallregister/kallor.yaml            källorna som reglerna vilar på
tests/                              tester för allt ovan
```

## Kontrollera lokalt

```
pip install -r requirements.txt
python -m pytest -q
python scripts/validera_kontrakt.py --kallregister kallregister/kallor.yaml schema/exempel/*.yaml
```

Ett kontrakt i ett annat repo valideras med `python <sökväg till agent-plattform>/scripts/validera_kontrakt.py --register agentregister.yaml --kontrollera-sokvagar`.

## Release

1. Gör ändringen som pull request och låt CI bli grön.
2. Tagga `main` med datum: `git tag 2026.11.21-1 && git push origin 2026.11.21-1`.
3. Arbetsflödet `release` lägger en zip per skill i en GitHub Release.
4. Ladda upp zip-filen under **Customize > Skills** i Claude.
