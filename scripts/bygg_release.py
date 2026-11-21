#!/usr/bin/env python3
"""Bygger en zip-fil per skill för uppladdning under Customize > Skills.

Varje zip innehåller skillens mapp med samma namn som skillen (claude.ai
kräver det). Som i Anthropics package_skill.py packas inte evals/ i roten,
__pycache__, *.pyc eller .DS_Store. Filerna får fasta tidsstämplar så att
samma innehåll alltid ger samma zip; MANIFEST.txt listar SHA-256 per fil.

Varje skill valideras först. En ogiltig skill stoppar bygget.

Användning:
  python scripts/bygg_release.py              # alla skills till dist/
  python scripts/bygg_release.py --ut annan/  # annan katalog
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import sys
import zipfile
from pathlib import Path

from validera_skills import hitta_skills, validera_skill

ROT = Path(__file__).resolve().parent.parent
UTESLUT_MAPPAR = {"__pycache__", "node_modules"}
UTESLUT_FILER = {".DS_Store"}
UTESLUT_MONSTER = {"*.pyc"}
FAST_TID = (2026, 1, 1, 0, 0, 0)


def ska_uteslutas(rel: Path) -> bool:
    """rel är relativ till skillens förälder, så rel.parts[0] är skillens mapp."""
    if any(d in UTESLUT_MAPPAR for d in rel.parts):
        return True
    if len(rel.parts) > 1 and rel.parts[1] == "evals":
        return True
    if rel.name in UTESLUT_FILER:
        return True
    return any(fnmatch.fnmatch(rel.name, m) for m in UTESLUT_MONSTER)


def packa(mapp: Path, ut: Path) -> Path:
    ut.mkdir(parents=True, exist_ok=True)
    zipfil = ut / f"{mapp.name}.zip"
    filer = sorted(p for p in mapp.rglob("*") if p.is_file() and not ska_uteslutas(p.relative_to(mapp.parent)))
    with zipfile.ZipFile(zipfil, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in filer:
            info = zipfile.ZipInfo(str(p.relative_to(mapp.parent)), date_time=FAST_TID)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, p.read_bytes())
    return zipfil


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bygg zip per skill.")
    ap.add_argument("--ut", type=Path, default=ROT / "dist")
    a = ap.parse_args(argv)

    skills = hitta_skills(ROT)
    trasiga = []
    for mapp in skills:
        fel, _ = validera_skill(mapp)
        if fel:
            trasiga.append((mapp, fel))
    if trasiga:
        for mapp, fel in trasiga:
            print(f"FEL  {mapp.relative_to(ROT)}: " + "; ".join(fel))
        return 1

    rader = []
    for mapp in skills:
        z = packa(mapp, a.ut)
        sha = hashlib.sha256(z.read_bytes()).hexdigest()
        rader.append(f"{sha}  {z.name}")
        print(f"OK   {z.relative_to(ROT) if z.is_relative_to(ROT) else z}")
    a.ut.mkdir(parents=True, exist_ok=True)
    (a.ut / "MANIFEST.txt").write_text("\n".join(rader) + ("\n" if rader else ""), encoding="utf-8")
    if not skills:
        print("     (inga skills att packa)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
