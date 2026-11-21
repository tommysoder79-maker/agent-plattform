#!/usr/bin/env python3
"""Jämför en körning av agent-sakerhetsgranskning med fallets facit, med kod.

Prövar i körningens utdata:
  - att granskning.yaml och granskning.md finns
  - att utfallet stämmer med fynden (underkänd om och bara om ett fynd med allvar hög är öppet),
    så att ingen har skrivit utfallet för hand
  - att utfallet är det väntade
  - hog: om ett öppet fynd med allvar hög ska finnas eller inte
  - hog_asi: att något sådant fynd har en av dessa OWASP-punkter
  - automatiska: att automatiska fynd vars rubrik innehåller texterna finns kvar
  - fynd_med: att något fynd har ett av allvaren och en av punkterna

Skriver grading.json i skill-creators format bredvid utdata-mappen.

Användning: python evals/jamfor_facit.py <fallmapp> <körningens utdata>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml


def jamfor(fall: Path, utdata: Path) -> list[dict]:
    facit = yaml.safe_load((fall / "facit.yaml").read_text(encoding="utf-8"))
    res: list[dict] = []

    def notera(text, ok, belagg):
        res.append({"text": text, "passed": bool(ok), "evidence": belagg})

    gfil = utdata / "granskning.yaml"
    notera("granskning.yaml och granskning.md finns", gfil.is_file() and (utdata / "granskning.md").is_file(),
           ", ".join(sorted(p.name for p in utdata.iterdir())) if utdata.is_dir() else "ingen utdata")
    if not gfil.is_file():
        return res
    g = yaml.safe_load(gfil.read_text(encoding="utf-8"))
    fynd = g.get("fynd") or []
    hoga = [f for f in fynd if f.get("allvar") == "hog" and f.get("status") == "oppen"]
    raknat = "underkand" if hoga else "godkand"
    notera("Utfallet är räknat ur fynden", g.get("utfall") == raknat, f"utfall {g.get('utfall')}, räknat {raknat}")
    notera(f"Utfallet är {facit['utfall']}", g.get("utfall") == facit["utfall"], f"utfall {g.get('utfall')}")
    if "hog" in facit:
        notera("Ett öppet fynd med allvar hög finns" if facit["hog"] else "Inget öppet fynd med allvar hög",
               bool(hoga) == facit["hog"], "; ".join(f"{f['id']} {f['rubrik']}" for f in hoga) or "inga")
    if facit.get("hog_asi"):
        ok = any(set(f.get("asi") or []) & set(facit["hog_asi"]) for f in hoga)
        notera(f"Ett högt fynd gäller någon av {facit['hog_asi']}", ok,
               "; ".join(f"{f['id']}: {f.get('asi')}" for f in hoga) or "inga")
    for text in facit.get("automatiska", []):
        ok = any(f.get("kalla") == "automatisk" and text in f.get("rubrik", "") for f in fynd)
        notera(f"Det automatiska fyndet '{text}' finns kvar", ok, ", ".join(f["rubrik"] for f in fynd if f.get("kalla") == "automatisk") or "inga")
    if facit.get("fynd_med"):
        fm = facit["fynd_med"]
        ok = any(f.get("allvar") in fm["allvar"] and set(f.get("asi") or []) & set(fm["asi"]) for f in fynd)
        notera(f"Ett fynd med allvar {fm['allvar']} gäller någon av {fm['asi']}", ok,
               "; ".join(f"{f['id']} {f['allvar']} {f.get('asi')}" for f in fynd) or "inga")
    return res


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    res = jamfor(Path(argv[1]), Path(argv[2]))
    for r in res:
        print(("OK   " if r["passed"] else "FEL  ") + r["text"] + f"  [{r['evidence']}]")
    godk = sum(r["passed"] for r in res)
    (Path(argv[2]).parent / "grading.json").write_text(json.dumps({
        "expectations": res,
        "summary": {"passed": godk, "failed": len(res) - godk, "total": len(res), "pass_rate": round(godk / len(res), 2) if res else 0.0},
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if all(r["passed"] for r in res) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
