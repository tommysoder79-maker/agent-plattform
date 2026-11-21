#!/usr/bin/env python3
"""Säkerhetsgranskning av ett agentkontrakt: förbered och slutför.

Modellen märker, koden verkar. Koden gör det som kan avgöras utan omdöme,
och granskaren gör resten:

  förbered  validerar kontraktet, räknar Rule of Two, gör automatiska fynd och
            avgör vilka OWASP-punkter (ASI01–ASI10) som är relevanta och varför.
            Skriver ett skelett till granskning.yaml.
  granskaren läser kod och konfiguration, prövar kontraktets flaggor mot hur
            agenten faktiskt fungerar, skriver en bedömning per relevant punkt
            och lägger till egna fynd (F1, F2, ...).
  slutför   kontrollerar att alla relevanta punkter är bedömda och att inget
            automatiskt fynd har tagits bort, räknar utfallet och skriver
            granskning.md. Med --uppdatera-kontrakt förs utfallet in i kontraktet.

Utfallet räknas, det skrivs aldrig för hand:
  underkänd  om något fynd med allvar hög är öppet
  godkänd    annars; öppna fynd med allvar medel och låg blir villkor

Ett accepterat fynd räknas inte som öppet. Det kräver vem som accepterade det
(en person, inte en modell), datum och när det prövas igen.

Användning:
  python scripts/granska.py forbered agents/x/kontrakt.yaml --ut agents/x/granskning.yaml
  python scripts/granska.py slutfor agents/x/granskning.yaml --uppdatera-kontrakt
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from risk import rakna
from validera_kontrakt import KONTRAKTSCHEMA, _schemafil, _validerare, las_yaml, regelfel, schemafel

GRANSKNINGSSCHEMA = _schemafil("granskning.schema.json")

ASI_TITLAR = {
    "ASI01": "Agent Goal Hijack",
    "ASI02": "Tool Misuse and Exploitation",
    "ASI03": "Identity and Privilege Abuse",
    "ASI04": "Agentic Supply Chain Vulnerabilities",
    "ASI05": "Unexpected Code Execution (RCE)",
    "ASI06": "Memory & Context Poisoning",
    "ASI07": "Insecure Inter-Agent Communication",
    "ASI08": "Cascading Failures",
    "ASI09": "Human-Agent Trust Exploitation",
    "ASI10": "Rogue Agents",
}

HOGA_REGLER = ("riskniva 3", "datagrind", "oåterkallelig", "underkänd")
AGENTORD = re.compile(r"\b(agent|agenter|mcp|a2a|klient)\b", re.IGNORECASE)


def _nyckel(text: str) -> str:
    return re.sub(r"[^a-z0-9åäö]+", "-", text.lower()).strip("-")[:80]


def automatiska_fynd(k: dict[str, Any], sokvag: Path) -> list[dict[str, Any]]:
    """Fynd som koden kan göra ur kontraktet själv."""
    fynd: list[dict[str, Any]] = []
    r = rakna(k)

    def lagg(rubrik, allvar, beskrivning, atgard, asi, nyckel):
        fynd.append({
            "id": f"A{len(fynd) + 1}", "nyckel": nyckel, "rubrik": rubrik, "asi": asi, "allvar": allvar,
            "beskrivning": beskrivning, "atgard": atgard, "kalla": "automatisk", "status": "oppen",
        })

    s_fel = schemafel(_validerare(KONTRAKTSCHEMA), k)
    if s_fel:
        for f in s_fel:
            hog = any(h in f for h in HOGA_REGLER)
            lagg("Kontraktet följer inte schemat", "hog" if hog else "medel", f,
                 "Rätta kontraktet med agent-kontrakt och granska igen.", [], "schema-" + _nyckel(f))
        return fynd

    fel, varn = regelfel(k, sokvag, kontrollera_sokvagar=False)
    for f in fel:
        hog = any(h in f for h in HOGA_REGLER)
        lagg("Kontraktet bryter en regel", "hog" if hog else "medel", f,
             "Rätta kontraktet med agent-kontrakt och granska igen.",
             ["ASI01", "ASI02"] if "riskniva 3" in f else [], "regel-" + _nyckel(f))
    for v in varn:
        if v.startswith("provsamling"):
            lagg("Facit räcker inte för att slå på agenten", "medel", v,
                 "Bygg facit med agent-evals innan läget blir skugga.",
                 ["ASI01"] if r.a else [], "provsamling-" + _nyckel(v))

    kanslig = r.b
    for kom in k.get("kommunicerar_externt") or []:
        if kom.get("styrs_av_modellen") is False and kanslig:
            lagg(f"Koden skickar data utanför sfären: {kom.get('mottagare')}", "lag",
                 f"{kom.get('beskrivning')} Det är inte C, eftersom koden bestämmer mål och innehåll, men agenten har känslig "
                 f"data och det som skickas kan avslöja den.",
                 "Beskriv spridningen där dataplatsen och biträdena beskrivs, och avgör om den är godtagen.",
                 [], "spridning-" + _nyckel(str(kom.get("mottagare"))))

    nycklar = (k.get("identitet") or {}).get("nycklar") or []
    if r.c and r.niva >= 2:
        for n in nycklar:
            if not n.get("kortlivad"):
                lagg(f"Nyckeln {n.get('namn')} är inte kortlivad", "lag",
                     "Agenten ändrar tillstånd eller kommunicerar externt utan godkännande per handling, och nyckeln gäller tills den återkallas.",
                     "Gör nyckeln kortlivad eller skriv varför det inte går.", ["ASI03"], "nyckel-kortlivad-" + _nyckel(str(n.get("namn"))))
    if not nycklar and (k.get("stack") or {}).get("val") != "system-insight-modul" and k.get("sort") != "motor":
        lagg("Ingen egen nyckel angiven", "lag",
             "Kontraktet anger ingen nyckel. Då går det inte att se vilken identitet agenten använder, eller att den kan stängas av ensam.",
             "Ange agentens egna nycklar med namn och omfång.", ["ASI03"], "nyckel-saknas")
    return fynd


def relevanta_asi(k: dict[str, Any]) -> list[dict[str, Any]]:
    """Vilka OWASP-punkter som är relevanta för kontraktet, och varför."""
    r = rakna(k)
    skriver = k.get("skriver") or []
    komm = k.get("kommunicerar_externt") or []
    effekter = {s.get("effekt") for s in skriver}
    sort = k.get("sort")
    stack = (k.get("stack") or {}).get("val")
    lage = k.get("lage")
    text_komm = " ".join(f"{x.get('mottagare', '')} {x.get('beskrivning', '')}" for x in komm)
    text_las = " ".join(f"{x.get('resurs', '')} {x.get('beskrivning', '')}" for x in k.get("laser") or [])
    godk = any(s.get("godkannande") == "fore-varje-handling" for s in skriver) or any(
        x.get("godkannande") == "fore-varje-handling" for x in komm)

    def punkt(asi: str, relevant: bool, ja: str, nej: str) -> dict[str, Any]:
        return {"id": asi, "titel": ASI_TITLAR[asi], "relevant": relevant, "skal": ja if relevant else nej,
                "bedomning": "", "kontroller_som_finns": [], "fynd": []}

    return [
        punkt("ASI01", r.a, "Agenten läser opålitlig indata (A).", "Ingen opålitlig indata."),
        punkt("ASI02", bool(effekter & {"angringsbar", "oaterkallelig"}) or bool(komm) or sort == "agent",
              "Agenten har verktyg som ändrar något eller skickar något, eller planerar egna steg.",
              "Agenten skriver bara råd och förslag och skickar inget."),
        punkt("ASI03", True, "Varje agent har en identitet och behörigheter.", ""),
        punkt("ASI04", True, "Varje agent vilar på modell, verktyg, paket eller skills från andra.", ""),
        punkt("ASI05", sort == "agent" or stack in ("claude-skill", "claude-agent-sdk", "langgraph"),
              "Agenten planerar egna steg eller körs i en miljö där modellen kan köra kod.",
              "Agenten är en motor eller ett AI-steg i ett fast flöde, utan kodkörning som modellen styr."),
        punkt("ASI06", r.a and bool(skriver),
              "Agenten läser opålitlig indata och sparar text som läses igen senare.",
              "Ingen opålitlig text sparas och läses igen."),
        punkt("ASI07", bool(AGENTORD.search(text_komm) or AGENTORD.search(text_las)),
              "Agenten utbyter meddelanden med andra agenter eller klienter.",
              "Inget utbyte med andra agenter."),
        punkt("ASI08", bool(k.get("uppdelning")) or stack == "system-insight-modul" or sort == "agent",
              "Agenten ingår i en kedja där ett fel kan föras vidare till andra delar.",
              "Agenten står ensam."),
        punkt("ASI09", bool(effekter & {"rad", "forslag"}) or godk,
              "Människor läser agentens råd eller förslag, eller godkänner dess handlingar.",
              "Ingen människa förlitar sig på agentens utdata."),
        punkt("ASI10", sort == "agent" or lage == "automatiskt",
              "Agenten planerar egna steg eller körs automatiskt.",
              "Agenten är ett AI-steg eller en motor som inte körs automatiskt."),
    ]


def forbered(kontrakt: Path, ut: Path, granskare: str, idag: dt.date) -> dict[str, Any]:
    k = las_yaml(kontrakt)
    r = rakna(k)
    g = {
        "schema_version": 1,
        "kontrakt": str(Path(_relativ(kontrakt, ut.parent))),
        "kontrakt_id": k.get("id", "okant"),
        "kontrakt_version": k.get("version", 1),
        "datum": idag.isoformat(),
        "granskare": granskare,
        "underlag": [],
        "rule_of_two": {"abc": "".join(b if f else "-" for f, b in ((r.a, "A"), (r.b, "B"), (r.c, "C"))),
                        "niva": r.niva, "skal": list(r.skal)},
        "asi": relevanta_asi(k),
        "fynd": automatiska_fynd(k, kontrakt),
    }
    ut.parent.mkdir(parents=True, exist_ok=True)
    ut.write_text(
        "# Skelett från granska.py förbered. Fyll i underlag, bedömning för varje relevant punkt och egna fynd (F1, F2, ...).\n"
        "# Ta inte bort automatiska fynd (A1, ...): rätta kontraktet i stället, eller acceptera fyndet med namn, datum och omprövning.\n"
        + yaml.safe_dump(g, allow_unicode=True, sort_keys=False, width=110),
        encoding="utf-8",
    )
    return g


def _relativ(mal: Path, fran: Path) -> str:
    import os

    return os.path.relpath(mal.resolve(), fran.resolve())


def slutfor(granskning: Path, uppdatera_kontrakt: bool) -> tuple[list[str], dict[str, Any]]:
    g = las_yaml(granskning)
    fel: list[str] = []
    schema = json.loads(GRANSKNINGSSCHEMA.read_text(encoding="utf-8"))
    for e in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(g):
        plats = "/".join(str(p) for p in e.absolute_path) or "(roten)"
        fel.append(f"schema: {plats}: {e.message}")
    if fel:
        return fel, g

    kontrakt = (granskning.parent / g["kontrakt"]).resolve()
    if not kontrakt.is_file():
        return [f"kontraktet {g['kontrakt']} finns inte"], g
    k = las_yaml(kontrakt)
    if k.get("id") != g["kontrakt_id"] or k.get("version") != g["kontrakt_version"]:
        fel.append("granskningen gäller inte kontraktets nuvarande id och version; kör förbered igen")

    if not g["underlag"]:
        fel.append("underlag: ange vad som lästes utöver kontraktet (kod, konfiguration, dokument)")

    ids = {f["id"] for f in g["fynd"]}
    if len(ids) != len(g["fynd"]):
        fel.append("fynd: två fynd har samma id")
    for p in g["asi"]:
        if p["relevant"] and not p["bedomning"].strip():
            fel.append(f"asi/{p['id']}: relevant punkt utan bedömning")
        for fid in p.get("fynd") or []:
            if fid not in ids:
                fel.append(f"asi/{p['id']}: fyndet {fid} finns inte")
    for f in g["fynd"]:
        if f["status"] == "accepterad" and re.search(r"claude|modell|agent", f.get("accepterad_av", ""), re.IGNORECASE):
            fel.append(f"fynd/{f['id']}: en risk accepteras av en person, inte av en modell")

    # Inget automatiskt fynd får försvinna så länge kontraktet ger det.
    kvar = {f.get("nyckel") for f in g["fynd"] if f["kalla"] == "automatisk"}
    for a in automatiska_fynd(k, kontrakt):
        if a["nyckel"] not in kvar:
            fel.append(f"fynd: det automatiska fyndet '{a['rubrik']}' saknas; rätta kontraktet eller acceptera fyndet")
    if fel:
        return fel, g

    oppna = [f for f in g["fynd"] if f["status"] == "oppen"]
    hoga = [f for f in oppna if f["allvar"] == "hog"]
    g["utfall"] = "underkand" if hoga else "godkand"
    if hoga:
        g["utfall_skal"] = "Öppna fynd med allvar hög: " + ", ".join(f"{f['id']} {f['rubrik']}" for f in hoga) + "."
    elif oppna:
        g["utfall_skal"] = "Inga öppna fynd med allvar hög. Villkor: " + ", ".join(f"{f['id']} {f['rubrik']}" for f in oppna) + "."
    else:
        g["utfall_skal"] = "Inga öppna fynd."

    granskning.write_text(
        "# Slutförd med granska.py slutför. Utfallet är räknat; ändra fynden och kör slutför igen.\n"
        + yaml.safe_dump(g, allow_unicode=True, sort_keys=False, width=110),
        encoding="utf-8",
    )
    granskning.with_suffix(".md").write_text(rendera(g, k), encoding="utf-8")
    if uppdatera_kontrakt:
        _uppdatera_kontrakt(kontrakt, g["utfall"], g["datum"], _relativ(granskning.with_suffix(".md"), kontrakt.parent))
    return [], g


ALLVAR = {"hog": "Hög", "medel": "Medel", "lag": "Låg"}
STATUS = {"oppen": "öppen", "accepterad": "accepterad", "atgardad": "åtgärdad"}


def rendera(g: dict[str, Any], k: dict[str, Any]) -> str:
    rader = [
        f"# Säkerhetsgranskning: {k.get('namn', g['kontrakt_id'])}",
        "",
        f"- **Kontrakt:** `{g['kontrakt_id']}` version {g['kontrakt_version']} (`{g['kontrakt']}`)",
        f"- **Datum:** {g['datum']}",
        f"- **Granskare:** {g['granskare']}",
        f"- **Rule of Two:** {g['rule_of_two']['abc']} nivå {g['rule_of_two']['niva']}",
        f"- **Utfall:** {'godkänd' if g['utfall'] == 'godkand' else 'underkänd'}. {g['utfall_skal']}",
        "",
        "Utfallet är räknat av `granska.py`: underkänd om ett fynd med allvar hög är öppet, annars godkänd med de öppna fynden som villkor.",
        "",
        "## Underlag",
        "",
    ]
    rader += [f"- {u}" for u in g["underlag"]]
    rader += ["", "## Fynd", ""]
    if not g["fynd"]:
        rader.append("Inga fynd.")
    for f in sorted(g["fynd"], key=lambda f: ({"hog": 0, "medel": 1, "lag": 2}[f["allvar"]], f["id"])):
        asi = ", ".join(f["asi"]) or "inget"
        rader += [
            f"### {f['id']} ({ALLVAR[f['allvar']]}, {STATUS[f['status']]}): {f['rubrik']}",
            "",
            f["beskrivning"],
            "",
            f"**Åtgärd:** {f['atgard']}",
            "",
            f"OWASP: {asi}. Källa: {'automatisk kontroll' if f['kalla'] == 'automatisk' else 'granskarens bedömning'}."
            + (f" Accepterad av {f['accepterad_av']} {f['accepterad_datum']}, omprövas {f['omprovas']}." if f["status"] == "accepterad" else "")
            + (f" Issue: {f['issue']}." if f.get("issue") else ""),
            "",
        ]
    rader += ["## OWASP Top 10 for Agentic Applications", "", "| Punkt | Relevant | Bedömning | Fynd |", "|---|---|---|---|"]
    for p in g["asi"]:
        bed = p["bedomning"].replace("\n", " ").strip() if p["relevant"] else p["skal"]
        rader.append(f"| {p['id']} {p['titel']} | {'ja' if p['relevant'] else 'nej'} | {bed} | {', '.join(p.get('fynd') or []) or '–'} |")
    rader += ["", "## Rule of Two", ""] + [f"- {s}" for s in g["rule_of_two"]["skal"]] + [""]
    return "\n".join(rader)


def _uppdatera_kontrakt(kontrakt: Path, utfall: str, datum: str, sokvag: str) -> None:
    """Byter blocket sakerhetsgranskning i kontraktet utan att röra resten av filen."""
    text = kontrakt.read_text(encoding="utf-8")
    nytt = f"sakerhetsgranskning:\n  utfall: {utfall}\n  datum: {datum}\n  sokvag: {sokvag}\n"
    monster = re.compile(r"^sakerhetsgranskning:\n(?:[ \t]+.*\n?)*", re.MULTILINE)
    if monster.search(text):
        text = monster.sub(nytt, text, count=1)
    else:
        text = text.rstrip("\n") + "\n\n" + nytt
    kontrakt.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Förbered och slutför en säkerhetsgranskning.")
    under = ap.add_subparsers(dest="kommando", required=True)
    f = under.add_parser("forbered")
    f.add_argument("kontrakt", type=Path)
    f.add_argument("--ut", type=Path)
    f.add_argument("--granskare", default="Claude (agent-sakerhetsgranskning)")
    f.add_argument("--idag", type=dt.date.fromisoformat, default=dt.date.today())
    s = under.add_parser("slutfor")
    s.add_argument("granskning", type=Path)
    s.add_argument("--uppdatera-kontrakt", action="store_true")
    a = ap.parse_args(argv)

    if a.kommando == "forbered":
        ut = a.ut or a.kontrakt.parent / "granskning.yaml"
        g = forbered(a.kontrakt, ut, a.granskare, a.idag)
        relevanta = [p["id"] for p in g["asi"] if p["relevant"]]
        print(f"OK   skelett skrivet: {ut}")
        print(f"     Rule of Two: {g['rule_of_two']['abc']} nivå {g['rule_of_two']['niva']}")
        print(f"     automatiska fynd: {len(g['fynd'])} ({', '.join(f'{x['id']} {x['allvar']}' for x in g['fynd']) or 'inga'})")
        print(f"     relevanta OWASP-punkter: {', '.join(relevanta)}")
        return 0

    fel, g = slutfor(a.granskning, a.uppdatera_kontrakt)
    if fel:
        print(f"FEL  {a.granskning}")
        for m in fel:
            print(f"     fel: {m}")
        return 1
    print(f"OK   {a.granskning}: {g['utfall']}. {g['utfall_skal']}")
    print(f"     {a.granskning.with_suffix('.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
