#!/usr/bin/env python3
"""Validerar agentkontrakt och agentregister.

Kontrollerna, i ordning:
  1. Schemat (schema/agentkontrakt.schema.json).
  2. Risknivån: den deklarerade måste vara lika med den som scripts/risk.py räknar.
     Nivå 3 godtas aldrig.
  3. Grind vid irreversibilitet: en oåterkallelig skrivning kräver godkännande
     före varje handling.
  4. Konsekvensklassen får inte vara lägre än vad skrivningarna kräver.
  5. Provsamlingen efter nivå: nivå 1 minst 5 fall, nivå 2 minst 10 fall och
     injektionsfall. Opålitlig indata (A) kräver alltid injektionsfall. Kravet
     gäller när läget är skugga eller automatiskt; i läget av blir en brist en varning.
  6. Säkerhetsgranskningen: underkänd får inte vara påslagen; nivå 2 kräver
     godkänd granskning innan läget är skugga eller automatiskt.
  7. Id och mapp: kontrakt.yaml ligger i en mapp med samma namn som id.
  8. Uppdelning: delarna finns bland de kontrakt som validerats i samma körning.
  9. Källor: id:n finns i källregistret (med --kallregister).
 10. Sökvägar: provsamlingens sökväg finns (med --kontrollera-sokvagar).

Med --register valideras ett agentregister, och alla kontrakt det pekar på.

Användning:
  python scripts/validera_kontrakt.py schema/exempel/*.yaml
  python scripts/validera_kontrakt.py --register agentregister.yaml --kontrollera-sokvagar
  python scripts/validera_kontrakt.py --kallregister kallregister/kallor.yaml agents/*/kontrakt.yaml
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from risk import KONSEKVENS_ORDNING, lagsta_konsekvens, rakna

HAR = Path(__file__).resolve().parent
ROT = HAR.parent


def _schemafil(namn: str) -> Path:
    """Repots schema/ i första hand; i en uppladdad skill ligger schemat bredvid skriptet."""
    for p in (ROT / "schema" / namn, HAR / namn):
        if p.is_file():
            return p
    return ROT / "schema" / namn


KONTRAKTSCHEMA = _schemafil("agentkontrakt.schema.json")
REGISTERSCHEMA = _schemafil("agentregister.schema.json")

MIN_FALL = {1: 5, 2: 10}


def _datum_till_text(v: Any) -> Any:
    """YAML läser 2026-11-21 som ett datum; schemat vill ha text."""
    if isinstance(v, (dt.date, dt.datetime)):
        return v.isoformat()
    if isinstance(v, dict):
        return {k: _datum_till_text(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_datum_till_text(x) for x in v]
    return v


def las_yaml(sokvag: Path) -> Any:
    with sokvag.open(encoding="utf-8") as f:
        return _datum_till_text(yaml.safe_load(f))


def _validerare(schemafil: Path) -> Draft202012Validator:
    schema = json.loads(schemafil.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, format_checker=FormatChecker())


def schemafel(validerare: Draft202012Validator, data: Any) -> list[str]:
    fel = []
    for e in sorted(validerare.iter_errors(data), key=lambda e: list(e.absolute_path)):
        plats = "/".join(str(p) for p in e.absolute_path) or "(roten)"
        fel.append(f"schema: {plats}: {e.message}")
    return fel


def regelfel(k: dict[str, Any], sokvag: Path, kontrollera_sokvagar: bool) -> tuple[list[str], list[str]]:
    """Kontrollerna efter schemat. Returnerar (fel, varningar)."""
    fel: list[str] = []
    varn: list[str] = []
    r = rakna(k)

    # 2. Risknivån
    if k.get("riskniva") != r.niva:
        fel.append(
            f"riskniva: kontraktet säger {k.get('riskniva')}, men räknat ur resurserna blir det {r.niva} ({r.kort()})"
        )
    if r.niva == 3:
        fel.append(
            "riskniva 3: agenten har A, B och C i samma session. Dela upp flödet i delar som var för sig har högst två "
            "egenskaper (se fältet uppdelning), eller kräv godkännande före varje handling."
        )

    # 3. Grind vid irreversibilitet
    for s in k.get("skriver") or []:
        if s.get("effekt") == "oaterkallelig" and s.get("godkannande") != "fore-varje-handling":
            fel.append(f"skriver/{s.get('resurs')}: oåterkallelig handling kräver godkannande: fore-varje-handling")

    # 4. Konsekvensklassen
    lagst = lagsta_konsekvens(k)
    dekl = k.get("konsekvens")
    if dekl in KONSEKVENS_ORDNING and KONSEKVENS_ORDNING[dekl] < KONSEKVENS_ORDNING[lagst]:
        fel.append(f"konsekvens: '{dekl}' är lägre än vad skrivningarna kräver ('{lagst}')")

    # 5. Provsamlingen. Kravet gäller när agenten är påslagen; i läget av är en brist en varning,
    #    så att ett kontrakt kan beskriva en agent som saknar facit utan att låtsas något annat.
    lage = k.get("lage")
    prov_brist = fel if lage != "av" else varn
    prov = k.get("provsamling") or {}
    min_fall = MIN_FALL.get(r.niva)
    if min_fall is not None and isinstance(prov.get("antal_fall"), int) and prov["antal_fall"] < min_fall:
        prov_brist.append(f"provsamling: nivå {r.niva} kräver minst {min_fall} fall, kontraktet har {prov['antal_fall']}")
    if (r.a or r.niva >= 2) and prov.get("injektionsfall") is not True:
        prov_brist.append("provsamling: opålitlig indata eller nivå 2 kräver injektionsfall")

    # 6. Säkerhetsgranskningen
    gr = (k.get("sakerhetsgranskning") or {}).get("utfall")
    if gr == "underkand" and lage != "av":
        fel.append("sakerhetsgranskning: underkänd granskning, men läget är inte av")
    if r.niva >= 2 and lage in ("skugga", "automatiskt") and gr != "godkand":
        fel.append(f"sakerhetsgranskning: nivå {r.niva} kräver godkänd granskning innan läget är {lage}")
    if r.niva == 1 and gr == "ej-gjord" and lage == "automatiskt":
        varn.append("sakerhetsgranskning: nivå 1 i automatiskt läge utan granskning; de automatiska kontrollerna har körts")

    # 7. Id och mapp
    if sokvag.name == "kontrakt.yaml" and sokvag.parent.name != k.get("id"):
        fel.append(f"id: '{k.get('id')}' stämmer inte med mappen '{sokvag.parent.name}'")

    # Sortens motivering för agent
    if k.get("sort") == "agent" and lage == "automatiskt" and r.niva >= 2:
        varn.append("sort agent på nivå 2 i automatiskt läge: kontrollera att befordran vilar på uppmätt samstämmighet")

    # 10. Sökvägar
    if kontrollera_sokvagar and prov.get("sokvag"):
        mal = (sokvag.parent / prov["sokvag"]).resolve()
        if not mal.exists():
            meddelande = f"provsamling: sökvägen '{prov['sokvag']}' finns inte"
            (varn if lage == "av" else fel).append(meddelande)
    gr_sokvag = (k.get("sakerhetsgranskning") or {}).get("sokvag")
    if kontrollera_sokvagar and gr_sokvag and not (sokvag.parent / gr_sokvag).exists():
        fel.append(f"sakerhetsgranskning: sökvägen '{gr_sokvag}' finns inte")

    return fel, varn


def validera_filer(
    sokvagar: list[Path], kallregister: Path | None, kontrollera_sokvagar: bool
) -> tuple[dict[Path, list[str]], dict[Path, list[str]], dict[str, dict[str, Any]]]:
    validerare = _validerare(KONTRAKTSCHEMA)
    kalla_ids: set[str] | None = None
    if kallregister is not None:
        reg = las_yaml(kallregister) or {}
        kalla_ids = {k.get("id") for k in reg.get("kallor") or []}

    alla_fel: dict[Path, list[str]] = {}
    alla_varn: dict[Path, list[str]] = {}
    laddade: dict[str, dict[str, Any]] = {}
    per_fil: dict[Path, dict[str, Any]] = {}

    for p in sokvagar:
        fel: list[str] = []
        varn: list[str] = []
        try:
            k = las_yaml(p)
        except (OSError, yaml.YAMLError) as e:
            alla_fel[p] = [f"kunde inte läsa: {e}"]
            continue
        if not isinstance(k, dict):
            alla_fel[p] = ["kontraktet måste vara ett YAML-objekt"]
            continue
        per_fil[p] = k
        fel += schemafel(validerare, k)
        if not fel:
            f2, v2 = regelfel(k, p, kontrollera_sokvagar)
            fel += f2
            varn += v2
        if kalla_ids is not None:
            for kid in k.get("kallor") or []:
                if kid not in kalla_ids:
                    fel.append(f"kallor: '{kid}' finns inte i källregistret")
        kid = k.get("id")
        if isinstance(kid, str):
            if kid in laddade:
                fel.append(f"id: '{kid}' finns redan i en annan fil")
            laddade[kid] = k
        alla_fel[p] = fel
        alla_varn[p] = varn

    # 8. Uppdelning
    for p, k in per_fil.items():
        if "uppdelning" not in k or not isinstance(k["uppdelning"], dict):
            continue
        delar = k["uppdelning"].get("delar") or []
        if k.get("id") not in delar:
            alla_fel[p].append("uppdelning: delar måste innehålla kontraktets eget id")
        for d in delar:
            if d not in laddade:
                alla_varn[p].append(f"uppdelning: delen '{d}' validerades inte i samma körning")

    return alla_fel, alla_varn, laddade


def validera_register(sokvag: Path, kallregister: Path | None, kontrollera_sokvagar: bool) -> int:
    reg = las_yaml(sokvag)
    fel = schemafel(_validerare(REGISTERSCHEMA), reg)
    if fel:
        _skriv(sokvag, fel, [])
        return 1
    kontrakt = [(sokvag.parent / a["kontrakt"]) for a in reg.get("agenter") or []]
    saknas = [p for p in kontrakt if not p.exists()]
    for p in saknas:
        fel.append(f"agenter: kontraktet '{p.relative_to(sokvag.parent)}' finns inte")
    finns = [p for p in kontrakt if p.exists()]
    k_fel, k_varn, laddade = validera_filer(finns, kallregister, kontrollera_sokvagar)
    for a in reg.get("agenter") or []:
        k = laddade.get(a["id"])
        if k is None:
            if (sokvag.parent / a["kontrakt"]).exists():
                fel.append(f"agenter/{a['id']}: kontraktet har ett annat id")
            continue
        if k.get("sfar") != reg.get("sfar"):
            fel.append(f"agenter/{a['id']}: kontraktets sfär '{k.get('sfar')}' är inte registrets '{reg.get('sfar')}'")
        if a["status"] in ("avvecklad", "pausad") and k.get("lage") != "av":
            fel.append(f"agenter/{a['id']}: status {a['status']} men kontraktets läge är {k.get('lage')}")
    rc = _skriv(sokvag, fel, [])
    for p in finns:
        rc |= _skriv(p, k_fel.get(p, []), k_varn.get(p, []), laddade)
    return rc


def _skriv(p: Path, fel: list[str], varn: list[str], laddade: dict[str, dict[str, Any]] | None = None) -> int:
    rubrik = str(p)
    if laddade is not None:
        try:
            k = las_yaml(p)
            if isinstance(k, dict) and not any(f.startswith("schema:") for f in fel):
                rubrik += f"  [{rakna(k).kort()}]"
        except (OSError, yaml.YAMLError):
            pass
    print(("FEL  " if fel else "OK   ") + rubrik)
    github = _i_github()
    for f in fel:
        print(f"     fel: {f}")
        if github:
            print(f"::error file={p}::{f}")
    for v in varn:
        print(f"     varning: {v}")
        if github:
            print(f"::warning file={p}::{v}")
    return 1 if fel else 0


def _i_github() -> bool:
    import os

    return os.environ.get("GITHUB_ACTIONS") == "true"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validera agentkontrakt och agentregister.")
    ap.add_argument("filer", nargs="*", type=Path, help="kontrakt att validera")
    ap.add_argument("--register", type=Path, help="agentregister att validera, med alla dess kontrakt")
    ap.add_argument("--kallregister", type=Path, help="källregister att kontrollera kallor mot")
    ap.add_argument("--kontrollera-sokvagar", action="store_true", help="kontrollera att provsamling och granskning finns")
    a = ap.parse_args(argv)

    if not a.filer and not a.register:
        ap.error("ange kontrakt eller --register")
    rc = 0
    if a.register:
        rc |= validera_register(a.register, a.kallregister, a.kontrollera_sokvagar)
    if a.filer:
        fel, varn, laddade = validera_filer(a.filer, a.kallregister, a.kontrollera_sokvagar)
        for p in a.filer:
            rc |= _skriv(p, fel.get(p, []), varn.get(p, []), laddade)
    return rc


if __name__ == "__main__":
    sys.exit(main())
