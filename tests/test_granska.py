import datetime as dt
from pathlib import Path

import yaml

from conftest import ROT
from granska import automatiska_fynd, forbered, relevanta_asi, slutfor
from validera_kontrakt import las_yaml

MALL = ROT / "plugins" / "agentbygge" / "skills" / "agent-kontrakt" / "assets" / "kontrakt-mall.yaml"
IDAG = dt.date(2026, 11, 21)


def kontrakt(**over):
    k = las_yaml(MALL)
    k.update(
        id="spanaren", sfar="complexity-insight", sort="ai-steg", stack={"val": "system-insight-modul"},
        var_den_kors="system-insight", konsekvens="mansklig", riskniva=2,
        laser=[
            {"resurs": "webben", "beskrivning": "b", "opalitlig": True, "kanslig": False},
            {"resurs": "ämnen", "beskrivning": "b", "opalitlig": False, "kanslig": True},
        ],
        skriver=[{"resurs": "external_sources", "beskrivning": "b", "effekt": "forslag", "godkannande": "ingen"}],
        kommunicerar_externt=[{"mottagare": "GDELT", "beskrivning": "Sökfråga ur ämnena.", "godkannande": "ingen",
                               "styrs_av_modellen": False, "kodstyrning": "Koden bygger frågan."}],
        provsamling={"sokvag": "evals/", "antal_fall": 0, "injektionsfall": False},
    )
    k.update(over)
    return k


def skriv(tmp: Path, k: dict) -> Path:
    p = tmp / "kontrakt.yaml"
    p.write_text(yaml.safe_dump(k, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return p


def fyll(g: dict, underlag=("src/x.ts",)) -> dict:
    g["underlag"] = list(underlag)
    for p in g["asi"]:
        if p["relevant"]:
            p["bedomning"] = "Bedömd."
    return g


def spara(p: Path, g: dict) -> None:
    p.write_text(yaml.safe_dump(g, allow_unicode=True, sort_keys=False), encoding="utf-8")


def test_automatiska_fynd_for_spanaren(tmp_path):
    p = skriv(tmp_path, kontrakt())
    fynd = automatiska_fynd(las_yaml(p), p)
    rubriker = [f["rubrik"] for f in fynd]
    assert any("Facit räcker inte" in r for r in rubriker)
    assert any("GDELT" in r and f["allvar"] == "lag" for r, f in zip(rubriker, fynd))
    assert all(f["allvar"] != "hog" for f in fynd)


def test_niva_3_ger_hogt_fynd(tmp_path):
    k = kontrakt(riskniva=3, skriver=[{"resurs": "x", "beskrivning": "b", "effekt": "angringsbar", "godkannande": "ingen"}])
    p = skriv(tmp_path, k)
    assert any(f["allvar"] == "hog" for f in automatiska_fynd(las_yaml(p), p))


def test_relevanta_punkter():
    asi = {p["id"]: p["relevant"] for p in relevanta_asi(kontrakt())}
    assert asi["ASI01"] and asi["ASI03"] and asi["ASI08"] and asi["ASI09"]
    assert not asi["ASI05"] and not asi["ASI10"]
    asi_agent = {p["id"]: p["relevant"] for p in relevanta_asi(kontrakt(sort="agent", lage="av"))}
    assert asi_agent["ASI05"] and asi_agent["ASI10"]


def test_slutfor_godkand_med_villkor_och_uppdaterat_kontrakt(tmp_path):
    p = skriv(tmp_path, kontrakt())
    g_fil = tmp_path / "granskning.yaml"
    g = fyll(forbered(p, g_fil, "test", IDAG))
    spara(g_fil, g)
    fel, ut = slutfor(g_fil, uppdatera_kontrakt=True)
    assert fel == []
    assert ut["utfall"] == "godkand" and "Villkor" in ut["utfall_skal"]
    assert (tmp_path / "granskning.md").read_text(encoding="utf-8").startswith("# Säkerhetsgranskning")
    k = las_yaml(p)
    assert k["sakerhetsgranskning"] == {"utfall": "godkand", "datum": "2026-11-21", "sokvag": "granskning.md"}


def test_hogt_eget_fynd_ger_underkand(tmp_path):
    p = skriv(tmp_path, kontrakt())
    g_fil = tmp_path / "granskning.yaml"
    g = fyll(forbered(p, g_fil, "test", IDAG))
    g["fynd"].append({"id": "F1", "rubrik": "Kontraktet döljer C", "asi": ["ASI02"], "allvar": "hog",
                      "beskrivning": "Modellen väljer adresser.", "atgard": "Rätta.", "kalla": "bedomning", "status": "oppen"})
    spara(g_fil, g)
    fel, ut = slutfor(g_fil, uppdatera_kontrakt=False)
    assert fel == [] and ut["utfall"] == "underkand"


def test_accepterat_hogt_fynd_kraver_person(tmp_path):
    p = skriv(tmp_path, kontrakt())
    g_fil = tmp_path / "granskning.yaml"
    g = fyll(forbered(p, g_fil, "test", IDAG))
    g["fynd"].append({"id": "F1", "rubrik": "r", "asi": [], "allvar": "hog", "beskrivning": "b", "atgard": "a",
                      "kalla": "bedomning", "status": "accepterad", "accepterad_av": "Claude",
                      "accepterad_datum": "2026-11-21", "omprovas": "2027-02-21"})
    spara(g_fil, g)
    fel, _ = slutfor(g_fil, uppdatera_kontrakt=False)
    assert any("person" in f for f in fel)
    g["fynd"][-1]["accepterad_av"] = "Tommy"
    spara(g_fil, g)
    fel, ut = slutfor(g_fil, uppdatera_kontrakt=False)
    assert fel == [] and ut["utfall"] == "godkand"


def test_automatiskt_fynd_far_inte_tas_bort(tmp_path):
    p = skriv(tmp_path, kontrakt())
    g_fil = tmp_path / "granskning.yaml"
    g = fyll(forbered(p, g_fil, "test", IDAG))
    g["fynd"] = [f for f in g["fynd"] if "Facit" not in f["rubrik"]]
    spara(g_fil, g)
    fel, _ = slutfor(g_fil, uppdatera_kontrakt=False)
    assert any("saknas" in f for f in fel)


def test_relevant_punkt_maste_bedomas_och_underlag_kravs(tmp_path):
    p = skriv(tmp_path, kontrakt())
    g_fil = tmp_path / "granskning.yaml"
    forbered(p, g_fil, "test", IDAG)
    fel, _ = slutfor(g_fil, uppdatera_kontrakt=False)
    assert any("utan bedömning" in f for f in fel)
    assert any("underlag" in f for f in fel)


def test_gammal_granskning_godtas_inte_efter_ny_version(tmp_path):
    p = skriv(tmp_path, kontrakt())
    g_fil = tmp_path / "granskning.yaml"
    g = fyll(forbered(p, g_fil, "test", IDAG))
    spara(g_fil, g)
    skriv(tmp_path, kontrakt(version=2))
    fel, _ = slutfor(g_fil, uppdatera_kontrakt=False)
    assert any("version" in f for f in fel)
