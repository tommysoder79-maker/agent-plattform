"""Tester för skillen agent-sakerhetsgranskning: skillen, fallen och jämföraren."""
import datetime as dt
import shutil

import yaml

from conftest import ROT
from granska import forbered, slutfor
from validera_skills import validera_skill

SKILL = ROT / "plugins" / "agentbygge" / "skills" / "agent-sakerhetsgranskning"


def _ladda(namn, fil):
    """Laddar en jämförare via sökväg: båda skillsen har en modul som heter jamfor_facit."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(namn, fil)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


jamfor_facit = _ladda("jamfor_facit_granskning", SKILL / "evals" / "jamfor_facit.py")


def test_skillen_ar_giltig():
    assert validera_skill(SKILL) == ([], [])


def test_varje_fall_har_kontrakt_och_facit():
    fall = [p for p in (SKILL / "evals").iterdir() if p.is_dir() and not p.name.startswith("__")]
    assert len(fall) >= 7
    for f in fall:
        assert (f / "files" / "kontrakt.yaml").is_file(), f.name
        assert (f / "place-files.sh").is_file()
        case = yaml.safe_load((f / "case.yaml").read_text(encoding="utf-8"))
        assert case["context"]["scaffold_script"] == "place-files.sh"
        assert "utfall" in yaml.safe_load((f / "facit.yaml").read_text(encoding="utf-8"))


def _granska(tmp_path, fall, egna=()):
    ut = tmp_path / "outputs"
    ut.mkdir()
    shutil.copy(SKILL / "evals" / fall / "files" / "kontrakt.yaml", ut / "kontrakt.yaml")
    g = forbered(ut / "kontrakt.yaml", ut / "granskning.yaml", "test", dt.date(2026, 11, 21))
    g["underlag"] = ["kontrakt.yaml"]
    for p in g["asi"]:
        if p["relevant"]:
            p["bedomning"] = "Bedömd."
    g["fynd"] += list(egna)
    (ut / "granskning.yaml").write_text(yaml.safe_dump(g, allow_unicode=True, sort_keys=False), encoding="utf-8")
    fel, _ = slutfor(ut / "granskning.yaml", uppdatera_kontrakt=True)
    assert fel == []
    return ut


HOG = {"id": "F1", "rubrik": "r", "asi": ["ASI02"], "allvar": "hog", "beskrivning": "b", "atgard": "a",
       "kalla": "bedomning", "status": "oppen"}


def test_jamforaren_faller_en_granskning_som_missar_det_dolda_c(tmp_path):
    # Kontraktet ser giltigt ut; bara en granskare som läser kodstyrningen ser felet.
    ut = _granska(tmp_path, "felmarkerad-hamtning")
    res = jamfor_facit.jamfor(SKILL / "evals" / "felmarkerad-hamtning", ut)
    assert not all(r["passed"] for r in res)


def test_jamforaren_godtar_ratt_granskning(tmp_path):
    ut = _granska(tmp_path, "felmarkerad-hamtning", [HOG])
    res = jamfor_facit.jamfor(SKILL / "evals" / "felmarkerad-hamtning", ut)
    assert all(r["passed"] for r in res)


def test_jamforaren_upptacker_utfall_skrivet_for_hand(tmp_path):
    ut = _granska(tmp_path, "motor-kpi")
    g = yaml.safe_load((ut / "granskning.yaml").read_text(encoding="utf-8"))
    g["fynd"].append(dict(HOG))
    (ut / "granskning.yaml").write_text(yaml.safe_dump(g, allow_unicode=True), encoding="utf-8")
    res = jamfor_facit.jamfor(SKILL / "evals" / "motor-kpi", ut)
    assert not next(r for r in res if r["text"] == "Utfallet är räknat ur fynden")["passed"]
