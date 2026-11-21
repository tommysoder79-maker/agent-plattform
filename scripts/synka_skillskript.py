#!/usr/bin/env python3
"""Kopierar repots skript och scheman in i de skills som behöver dem.

En skill som laddas upp till Claude måste bära sina skript, eftersom repot
inte finns där den körs. Originalen ligger i scripts/ och schema/; kopiorna
i plugins/<plugin>/skills/<skill>/scripts/ ändras aldrig för hand.

Användning:
  python scripts/synka_skillskript.py               # kopiera
  python scripts/synka_skillskript.py --kontrollera # fel om någon kopia skiljer sig (körs i CI)
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent

# skill-mapp (relativ till roten) -> original som ska finnas i skillens scripts/
SYNK: dict[str, list[str]] = {
    "plugins/agentbygge/skills/agent-kontrakt": [
        "scripts/risk.py",
        "scripts/validera_kontrakt.py",
        "schema/agentkontrakt.schema.json",
        "schema/agentregister.schema.json",
    ],
}


def par() -> list[tuple[Path, Path]]:
    ut = []
    for skill, filer in SYNK.items():
        for f in filer:
            original = ROT / f
            ut.append((original, ROT / skill / "scripts" / original.name))
    return ut


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Synka skript och scheman till skills.")
    ap.add_argument("--kontrollera", action="store_true", help="ändra inget; fel om en kopia skiljer sig")
    a = ap.parse_args(argv)
    fel = 0
    for original, kopia in par():
        lika = kopia.is_file() and kopia.read_bytes() == original.read_bytes()
        if a.kontrollera:
            if not lika:
                print(f"FEL  {kopia.relative_to(ROT)} är inte lika med {original.relative_to(ROT)}; kör scripts/synka_skillskript.py")
                fel = 1
        elif not lika:
            kopia.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, kopia)
            print(f"kopierade {original.relative_to(ROT)} -> {kopia.relative_to(ROT)}")
    if a.kontrollera and not fel:
        print(f"OK   {len(par())} kopior är lika med originalen")
    return fel


if __name__ == "__main__":
    sys.exit(main())
