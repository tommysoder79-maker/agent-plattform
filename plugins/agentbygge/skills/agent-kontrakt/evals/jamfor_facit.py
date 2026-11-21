#!/usr/bin/env python3
"""Jämför en körning av agent-kontrakt med fallets facit, med kod.

Läser fallets facit.yaml och alla kontrakt-*.yaml i körningens utdata,
validerar kontrakten med skillens validerare, räknar Rule of Two och prövar:

  stoppar           true: inga kontrakt får finnas
  antal_kontrakt    tillåtna antal
  alla.*            gäller varje kontrakt: sfar, stack, validerar, riskniva_hogst,
                    personuppgifter, inte_lage
  sfarer            mängden sfärer bland kontrakten
  kontrakt[]        varje förväntat kontrakt ska matcha ett eget kontrakt:
                    abc (t.ex. "AB-"), riskniva, sort (tillåtna), konsekvens_minst

Skriver grading.json i skill-creators format (text, passed, evidence) i
körningens mapp och returnerar 0 om allt gick igenom.

Användning:
  python evals/jamfor_facit.py <fallmapp> <körningens utdata-mapp> [--grading <fil>]
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import yaml

SKILL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL / "scripts"))

from risk import KONSEKVENS_ORDNING, rakna  # noqa: E402
from validera_kontrakt import validera_filer  # noqa: E402


def matchar(forv: dict, k: dict) -> list[str]:
    """Tomt om kontraktet k uppfyller förväntningen, annars skälen."""
    r = rakna(k)
    skal = []
    abc = "".join(b if f else "-" for f, b in ((r.a, "A"), (r.b, "B"), (r.c, "C")))
    if "abc" in forv and forv["abc"] != abc:
        skal.append(f"abc {abc}, väntat {forv['abc']}")
    if "riskniva" in forv and forv["riskniva"] != r.niva:
        skal.append(f"nivå {r.niva}, väntat {forv['riskniva']}")
    if "sort" in forv and k.get("sort") not in forv["sort"]:
        skal.append(f"sort {k.get('sort')}, väntat en av {forv['sort']}")
    if "konsekvens_minst" in forv:
        kk = k.get("konsekvens")
        if kk not in KONSEKVENS_ORDNING or KONSEKVENS_ORDNING[kk] < KONSEKVENS_ORDNING[forv["konsekvens_minst"]]:
            skal.append(f"konsekvens {kk}, väntat minst {forv['konsekvens_minst']}")
    return skal


def jamfor(fall: Path, utdata: Path) -> list[dict]:
    facit = yaml.safe_load((fall / "facit.yaml").read_text(encoding="utf-8"))
    filer = sorted(utdata.glob("kontrakt-*.yaml"))
    resultat: list[dict] = []

    def notera(text: str, ok: bool, belagg: str) -> None:
        resultat.append({"text": text, "passed": bool(ok), "evidence": belagg})

    namn = ", ".join(f.name for f in filer) or "inga"
    if facit.get("stoppar"):
        notera("Datagrinden stoppar: inga kontrakt skrivs", not filer, f"kontrakt: {namn}")
        return resultat

    tillatna = facit.get("antal_kontrakt", [])
    notera(f"Antal kontrakt är ett av {tillatna}", len(filer) in tillatna, f"{len(filer)} kontrakt: {namn}")

    fel, _, laddade = validera_filer(filer, None, False)
    kontrakt = {f: laddade.get((yaml.safe_load(f.read_text(encoding="utf-8")) or {}).get("id")) for f in filer}
    alla = facit.get("alla", {})

    if alla.get("validerar"):
        trasiga = {f.name: e for f, e in fel.items() if e}
        notera("Alla kontrakt klarar validera_kontrakt.py", not trasiga, json.dumps(trasiga, ensure_ascii=False) or "inga fel")

    for f, k in kontrakt.items():
        if k is None:
            continue
        r = rakna(k)
        if "sfar" in alla:
            notera(f"{f.name}: sfären är {alla['sfar']}", k.get("sfar") == alla["sfar"], f"sfar: {k.get('sfar')}")
        if "stack" in alla:
            val = (k.get("stack") or {}).get("val")
            notera(f"{f.name}: stacken är {alla['stack']}", val == alla["stack"], f"stack: {val}")
        if "riskniva_hogst" in alla:
            notera(f"{f.name}: nivån är högst {alla['riskniva_hogst']}", r.niva <= alla["riskniva_hogst"], r.kort())
        if "personuppgifter" in alla:
            pu = (k.get("gdpr") or {}).get("personuppgifter")
            notera(f"{f.name}: personuppgifter är {alla['personuppgifter']}", pu == alla["personuppgifter"], f"gdpr.personuppgifter: {pu}")
        if "inte_lage" in alla:
            notera(f"{f.name}: läget är inte {alla['inte_lage']}", k.get("lage") not in alla["inte_lage"], f"lage: {k.get('lage')}")

    if "sfarer" in facit:
        sedda = sorted({(k or {}).get("sfar") for k in kontrakt.values() if k})
        notera(f"Sfärerna är {sorted(facit['sfarer'])}", sedda == sorted(facit["sfarer"]), f"sfärer: {sedda}")

    forvantade = facit.get("kontrakt") or []
    if forvantade:
        egna = [(f, k) for f, k in kontrakt.items() if k]
        bast: tuple[int, list[str]] | None = None
        for perm in itertools.permutations(egna, min(len(egna), len(forvantade))):
            skal = []
            for forv, (f, k) in zip(forvantade, perm):
                skal += [f"{f.name}: {s}" for s in matchar(forv, k)]
            skal += [f"saknas: {forv}" for forv in forvantade[len(perm):]]
            if bast is None or len(skal) < bast[0]:
                bast = (len(skal), skal)
        if bast is None:
            bast = (len(forvantade), [f"saknas: {forv}" for forv in forvantade])
        beskr = "; ".join(
            ", ".join(f"{n}={v}" for n, v in forv.items()) for forv in forvantade
        )
        notera(f"Kontrakten matchar facit ({beskr})", not bast[1], "; ".join(bast[1]) or "alla matchar")
    return resultat


def sammanfatta(res: list[dict]) -> dict:
    """Summeringen i grading.json, i det format skill-creators benchmark läser."""
    godkanda = sum(1 for r in res if r["passed"])
    return {"passed": godkanda, "failed": len(res) - godkanda, "total": len(res),
            "pass_rate": round(godkanda / len(res), 2) if res else 0.0}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Jämför en körning med facit.")
    ap.add_argument("fall", type=Path)
    ap.add_argument("utdata", type=Path)
    ap.add_argument("--grading", type=Path, help="var grading.json skrivs (standard: utdata/../grading.json)")
    a = ap.parse_args(argv)
    res = jamfor(a.fall, a.utdata)
    for r in res:
        print(("OK   " if r["passed"] else "FEL  ") + r["text"] + f"  [{r['evidence']}]")
    ut = a.grading or a.utdata.parent / "grading.json"
    ut.write_text(json.dumps({"expectations": res, "summary": sammanfatta(res)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if all(r["passed"] for r in res) else 1


if __name__ == "__main__":
    sys.exit(main())
