#!/usr/bin/env python3
"""Kontrollerar källregistret.

Fel:
  - saknade fält, dubbla id:n, okända värden för niva, typ eller lasniva
  - en källa som bär beslut men är nivå 3, läst i andra hand eller inte läst
Varningar:
  - en källa som bär beslut och inte verifierats på --max-dagar dagar (90)
  - en källa som aldrig verifierats

Varningarna stoppar inte CI. Månadsgranskningen tar hand om dem.

Användning:
  python scripts/kontrollera_kallor.py kallregister/kallor.yaml
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

KRAVS = ("id", "titel", "utgivare", "niva", "typ", "lasniva", "verifierad", "bar_beslut", "galler")
TILLATNA = set(KRAVS) | {"url", "anmarkning"}
NIVAER = {1, 2, 3}
TYPER = {"specifikation", "standardorgan", "vagledning", "dokumentation", "sekundar"}
LASNIVAER = {"original", "extraktion", "andra-hand", "ej-last"}
ID_MONSTER = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def kontrollera(data: Any, idag: dt.date, max_dagar: int) -> tuple[list[str], list[str]]:
    fel: list[str] = []
    varn: list[str] = []
    if not isinstance(data, dict) or data.get("schema_version") != 1 or not isinstance(data.get("kallor"), list):
        return ["registret måste ha schema_version: 1 och en lista kallor"], []
    sedda: set[str] = set()
    for i, k in enumerate(data["kallor"]):
        if not isinstance(k, dict):
            fel.append(f"kallor[{i}]: måste vara ett objekt")
            continue
        kid = k.get("id", f"kallor[{i}]")
        for falt in KRAVS:
            if falt not in k:
                fel.append(f"{kid}: saknar {falt}")
        for falt in set(k) - TILLATNA:
            fel.append(f"{kid}: okänt fält {falt}")
        if not isinstance(k.get("id"), str) or not ID_MONSTER.match(k["id"]):
            fel.append(f"{kid}: id måste vara kebab-case")
        elif k["id"] in sedda:
            fel.append(f"{kid}: id finns redan")
        else:
            sedda.add(k["id"])
        if k.get("niva") not in NIVAER:
            fel.append(f"{kid}: niva måste vara 1, 2 eller 3")
        if k.get("typ") not in TYPER:
            fel.append(f"{kid}: typ måste vara en av {sorted(TYPER)}")
        if k.get("lasniva") not in LASNIVAER:
            fel.append(f"{kid}: lasniva måste vara en av {sorted(LASNIVAER)}")
        if not isinstance(k.get("bar_beslut"), bool):
            fel.append(f"{kid}: bar_beslut måste vara true eller false")

        verifierad = k.get("verifierad")
        if verifierad is not None and not isinstance(verifierad, dt.date):
            try:
                verifierad = dt.date.fromisoformat(str(verifierad))
            except ValueError:
                fel.append(f"{kid}: verifierad måste vara ett datum (ÅÅÅÅ-MM-DD) eller null")
                verifierad = None

        if k.get("bar_beslut") is True:
            if k.get("niva") == 3:
                fel.append(f"{kid}: en sekundärkälla (nivå 3) får inte bära beslut")
            if k.get("lasniva") in ("andra-hand", "ej-last"):
                fel.append(f"{kid}: en källa läst i andra hand eller inte läst får inte bära beslut")
            if verifierad is None:
                fel.append(f"{kid}: en källa som bär beslut måste ha ett verifieringsdatum")
            elif (idag - verifierad).days > max_dagar:
                varn.append(f"{kid}: bär beslut men verifierades senast {verifierad} ({(idag - verifierad).days} dagar sedan)")
        elif verifierad is None:
            varn.append(f"{kid}: aldrig verifierad")
    return fel, varn


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kontrollera källregistret.")
    ap.add_argument("register", type=Path)
    ap.add_argument("--max-dagar", type=int, default=90)
    ap.add_argument("--idag", type=dt.date.fromisoformat, default=dt.date.today())
    a = ap.parse_args(argv)

    with a.register.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    fel, varn = kontrollera(data, a.idag, a.max_dagar)
    github = os.environ.get("GITHUB_ACTIONS") == "true"
    antal = len(data.get("kallor") or []) if isinstance(data, dict) else 0
    print(("FEL  " if fel else "OK   ") + f"{a.register}  [{antal} källor]")
    for m in fel:
        print(f"     fel: {m}")
        if github:
            print(f"::error file={a.register}::{m}")
    for m in varn:
        print(f"     varning: {m}")
        if github:
            print(f"::warning file={a.register}::{m}")
    return 1 if fel else 0


if __name__ == "__main__":
    sys.exit(main())
