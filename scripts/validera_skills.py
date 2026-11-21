#!/usr/bin/env python3
"""Validerar skills och marknadsplatsen.

Skills (varje mapp plugins/<plugin>/skills/<namn>/):
  Reglerna följer Anthropics egen uppladdningskontroll i skill-creator
  (scripts/quick_validate.py), eftersom det är den claude.ai tillämpar:
  - exakt en SKILL.md, i skillens rot (evals/ i roten räknas inte)
  - YAML-frontmatter med bara fälten name, description, license,
    allowed-tools, metadata, compatibility
  - name: kebab-case, högst 64 tecken, inga dubbla eller yttre bindestreck,
    och samma som mappens namn (annars avvisar claude.ai uppladdningen)
  - description: högst 1024 tecken, inga vinkelparenteser
  - compatibility: högst 500 tecken
  Varning: SKILL.md längre än 500 rader (håll den kort; lägg resten i references/).

Marknadsplatsen (.claude-plugin/marketplace.json), enligt Claude Codes dokumentation:
  - name, owner.name och plugins krävs; varje post kräver name och source
  - en relativ source börjar med ./, innehåller inte .. och finns
  - postens name är samma som name i pluginens .claude-plugin/plugin.json
  - varje plugin-mapp i plugins/ finns i marknadsplatsen

Användning:
  python scripts/validera_skills.py            # hela repot
  python scripts/validera_skills.py plugins/agentbygge/skills/agent-kontrakt
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import yaml

ROT = Path(__file__).resolve().parent.parent
TILLATNA_FALT = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
NAMN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
UTESLUTNA_DELAR = {"__pycache__", "node_modules"}
MAX_RADER = 500


def _raknas(rel: Path) -> bool:
    delar = rel.parts[:-1]
    if any(d in UTESLUTNA_DELAR for d in delar):
        return False
    return not (delar and delar[0] == "evals")


def validera_skill(mapp: Path) -> tuple[list[str], list[str]]:
    fel: list[str] = []
    varn: list[str] = []
    skill_md = mapp / "SKILL.md"
    if not skill_md.is_file():
        return ["SKILL.md saknas"], []
    alla = [p for p in mapp.rglob("SKILL.md") if _raknas(p.relative_to(mapp))]
    if len(alla) > 1:
        extra = sorted(str(p.relative_to(mapp)) for p in alla if p != skill_md)
        fel.append("mer än en SKILL.md (claude.ai avvisar det): " + ", ".join(extra))

    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not m:
        return fel + ["frontmatter saknas eller är felformaterad (ska börja och sluta med ---)"], varn
    try:
        fm = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        return fel + [f"frontmatter är inte giltig YAML: {e}"], varn
    if not isinstance(fm, dict):
        return fel + ["frontmatter måste vara ett YAML-objekt"], varn

    okanda = set(fm) - TILLATNA_FALT
    if okanda:
        fel.append("okända fält i frontmatter (claude.ai avvisar dem): " + ", ".join(sorted(okanda)))

    namn = fm.get("name")
    if not isinstance(namn, str) or not namn.strip():
        fel.append("name saknas")
    else:
        namn = namn.strip()
        if not NAMN.match(namn):
            fel.append(f"name '{namn}' ska vara kebab-case: små bokstäver, siffror och enkla bindestreck")
        if len(namn) > 64:
            fel.append(f"name är {len(namn)} tecken, högst 64")
        if namn != mapp.name:
            fel.append(f"name '{namn}' är inte samma som mappen '{mapp.name}'")

    beskr = fm.get("description")
    if not isinstance(beskr, str) or not beskr.strip():
        fel.append("description saknas")
    else:
        if "<" in beskr or ">" in beskr:
            fel.append("description får inte innehålla vinkelparenteser")
        if len(beskr.strip()) > 1024:
            fel.append(f"description är {len(beskr.strip())} tecken, högst 1024")

    komp = fm.get("compatibility")
    if komp is not None and (not isinstance(komp, str) or len(komp) > 500):
        fel.append("compatibility måste vara text på högst 500 tecken")
    meta = fm.get("metadata")
    if meta is not None and not (isinstance(meta, dict) and all(isinstance(v, str) for v in meta.values())):
        fel.append("metadata måste vara ett objekt med textvärden")

    rader = text.count("\n") + 1
    if rader > MAX_RADER:
        varn.append(f"SKILL.md har {rader} rader; flytta detaljer till references/")
    return fel, varn


def hitta_skills(rot: Path) -> list[Path]:
    return sorted(p.parent for p in rot.glob("plugins/*/skills/*/SKILL.md"))


def validera_marknadsplats(rot: Path) -> list[str]:
    fel: list[str] = []
    mp_fil = rot / ".claude-plugin" / "marketplace.json"
    if not mp_fil.is_file():
        return [".claude-plugin/marketplace.json saknas"]
    try:
        mp = json.loads(mp_fil.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"marketplace.json är inte giltig JSON: {e}"]
    if not isinstance(mp.get("name"), str) or not NAMN.match(mp.get("name", "")):
        fel.append("marketplace.json: name saknas eller är inte kebab-case")
    if not isinstance(mp.get("owner"), dict) or not mp["owner"].get("name"):
        fel.append("marketplace.json: owner.name saknas")
    poster = mp.get("plugins")
    if not isinstance(poster, list):
        return fel + ["marketplace.json: plugins saknas"]
    listade: set[Path] = set()
    for i, post in enumerate(poster):
        namn = post.get("name")
        kalla = post.get("source")
        if not isinstance(namn, str) or not NAMN.match(namn):
            fel.append(f"plugins[{i}]: name saknas eller är inte kebab-case")
            continue
        if isinstance(kalla, str):
            if not kalla.startswith("./") or ".." in Path(kalla).parts:
                fel.append(f"plugins/{namn}: source ska vara en relativ sökväg från roten, utan '..'")
                continue
            mapp = (rot / kalla).resolve()
            listade.add(mapp)
            pj = mapp / ".claude-plugin" / "plugin.json"
            if not mapp.is_dir():
                fel.append(f"plugins/{namn}: mappen {kalla} finns inte")
            elif not pj.is_file():
                fel.append(f"plugins/{namn}: {kalla}/.claude-plugin/plugin.json saknas")
            else:
                try:
                    manifest = json.loads(pj.read_text(encoding="utf-8"))
                except json.JSONDecodeError as e:
                    fel.append(f"plugins/{namn}: plugin.json är inte giltig JSON: {e}")
                    continue
                if manifest.get("name") != namn:
                    fel.append(f"plugins/{namn}: namnet i plugin.json är '{manifest.get('name')}'")
        elif not isinstance(kalla, dict):
            fel.append(f"plugins/{namn}: source saknas")
    for mapp in sorted(p for p in (rot / "plugins").glob("*") if p.is_dir()):
        if mapp.resolve() not in listade:
            fel.append(f"plugins/{mapp.name}: finns som mapp men inte i marketplace.json")
    return fel


def _skriv(etikett: str, fel: list[str], varn: list[str]) -> int:
    github = os.environ.get("GITHUB_ACTIONS") == "true"
    print(("FEL  " if fel else "OK   ") + etikett)
    for m in fel:
        print(f"     fel: {m}")
        if github:
            print(f"::error file={etikett}::{m}")
    for m in varn:
        print(f"     varning: {m}")
        if github:
            print(f"::warning file={etikett}::{m}")
    return 1 if fel else 0


def main(argv: list[str]) -> int:
    rc = 0
    if len(argv) > 1:
        for arg in argv[1:]:
            f, v = validera_skill(Path(arg))
            rc |= _skriv(arg, f, v)
        return rc
    rc |= _skriv(".claude-plugin/marketplace.json", validera_marknadsplats(ROT), [])
    skills = hitta_skills(ROT)
    namn_sedda: dict[str, Path] = {}
    for mapp in skills:
        f, v = validera_skill(mapp)
        if mapp.name in namn_sedda:
            f.append(f"samma namn som {namn_sedda[mapp.name].relative_to(ROT)}; namnen måste vara unika i kontot")
        namn_sedda[mapp.name] = mapp
        rc |= _skriv(str(mapp.relative_to(ROT)), f, v)
    if not skills:
        print("     (inga skills ännu)")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
