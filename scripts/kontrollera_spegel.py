#!/usr/bin/env python3
"""Kontrollerar spegeln av ett masterdokument mot förra versionen.

Ett masterdokument (som docs/arkitektur.md) har rubriken
  # Titel (version N, ÅÅÅÅ-MM-DD)
och en ändringslogg med en rad per version:
  - Version N (ÅÅÅÅ-MM-DD): ...

Regler:
  1. Rubriken har version och datum, och ändringsloggen har en rad för versionen.
  2. Har innehållet ändrats mot förra versionen (--bas) måste versionen vara högre.
  3. Ett avsnitt (## Rubrik) som fanns i förra versionen och saknas nu måste
     nämnas i ändringsloggens rad för den nya versionen.

Det skyddar mot det vanligaste felet: att en session skriver om hela
dokumentet och tappar avsnitt utan att någon märker det.

Användning:
  python scripts/kontrollera_spegel.py docs/arkitektur.md --bas /tmp/forra.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RUBRIK = re.compile(r"^# .*\(version (\d+), (\d{4}-\d{2}-\d{2})\)\s*$", re.MULTILINE)
AVSNITT = re.compile(r"^## (.+?)\s*$", re.MULTILINE)


def version(text: str) -> int | None:
    m = RUBRIK.search(text)
    return int(m.group(1)) if m else None


def loggrad(text: str, v: int) -> str | None:
    m = re.search(rf"^- Version {v} \(\d{{4}}-\d{{2}}-\d{{2}}\):(.*)$", text, re.MULTILINE)
    return m.group(1) if m else None


def kontrollera(ny: str, bas: str | None) -> list[str]:
    fel: list[str] = []
    v = version(ny)
    if v is None:
        return ["rubriken saknar '(version N, ÅÅÅÅ-MM-DD)'"]
    rad = loggrad(ny, v)
    if rad is None:
        fel.append(f"ändringsloggen saknar en rad för version {v}")
    if bas is None or bas == ny:
        return fel
    bv = version(bas)
    if bv is not None and v <= bv:
        fel.append(f"innehållet har ändrats men versionen är {v}, förra var {bv}; höj versionen")
    borta = [a for a in AVSNITT.findall(bas) if a not in set(AVSNITT.findall(ny))]
    for a in borta:
        if rad is None or a.lower() not in rad.lower():
            fel.append(f"avsnittet '{a}' finns inte längre och nämns inte i ändringsloggen för version {v}")
    return fel


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kontrollera spegeln av ett masterdokument.")
    ap.add_argument("dokument", type=Path)
    ap.add_argument("--bas", type=Path, help="förra versionen, till exempel från main")
    a = ap.parse_args(argv)
    ny = a.dokument.read_text(encoding="utf-8")
    bas = a.bas.read_text(encoding="utf-8") if a.bas and a.bas.is_file() and a.bas.stat().st_size else None
    fel = kontrollera(ny, bas)
    print(("FEL  " if fel else "OK   ") + f"{a.dokument}  [version {version(ny)}]")
    for f in fel:
        print(f"     fel: {f}")
    return 1 if fel else 0


if __name__ == "__main__":
    sys.exit(main())
