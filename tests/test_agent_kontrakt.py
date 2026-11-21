"""Tester för skillen agent-kontrakt: kopiorna, fallen och jämföraren."""
import copy
import sys
from pathlib import Path

import yaml

from conftest import ROT
from synka_skillskript import main as synka
from validera_kontrakt import las_yaml
from validera_skills import validera_skill

SKILL = ROT / "plugins" / "agentbygge" / "skills" / "agent-kontrakt"
sys.path.insert(0, str(SKILL / "evals"))
from jamfor_facit import jamfor  # noqa: E402


def test_skillen_ar_giltig():
    assert validera_skill(SKILL) == ([], [])


def test_skriptkopiorna_ar_lika_med_originalen():
    assert synka(["--kontrollera"]) == 0


def test_mallen_ar_ett_giltigt_kontrakt(tmp_path):
    from validera_kontrakt import validera_filer

    p = tmp_path / "mall.yaml"
    p.write_text((SKILL / "assets" / "kontrakt-mall.yaml").read_text(encoding="utf-8"), encoding="utf-8")
    fel, _, _ = validera_filer([p], None, False)
    assert fel[p] == []


def test_varje_fall_har_det_som_behovs():
    fall = [p for p in (SKILL / "evals").iterdir() if p.is_dir() and not p.name.startswith("__")]
    assert len(fall) >= 10
    for f in fall:
        assert (f / "prompt.md").read_text(encoding="utf-8").startswith("---\ntags: [agent-kontrakt]")
        case = yaml.safe_load((f / "case.yaml").read_text(encoding="utf-8"))
        assert case["schema_version"] == "1.1" and case["name"] == f.name
        assert list((f / "graders").glob("*.md")), f.name
        assert "antal_kontrakt" in yaml.safe_load((f / "facit.yaml").read_text(encoding="utf-8"))


def _spanaren(**over):
    k = las_yaml(SKILL / "assets" / "kontrakt-mall.yaml")
    k.update(
        id="scout-sources", sfar="complexity-insight", sort="ai-steg",
        stack={"val": "system-insight-modul"}, var_den_kors="system-insight", konsekvens="mansklig", riskniva=2,
        laser=[
            {"resurs": "webben", "beskrivning": "b", "opalitlig": True, "kanslig": False},
            {"resurs": "ämnen", "beskrivning": "b", "opalitlig": False, "kanslig": True},
        ],
        skriver=[{"resurs": "external_sources", "beskrivning": "b", "effekt": "forslag", "godkannande": "ingen"}],
    )
    k.update(over)
    return k


def _kor(tmp_path, *kontrakt):
    ut = tmp_path / "outputs"
    ut.mkdir()
    for k in kontrakt:
        (ut / f"kontrakt-{k['id']}.yaml").write_text(yaml.safe_dump(k, allow_unicode=True), encoding="utf-8")
    return jamfor(SKILL / "evals" / "si-spanaren", ut)


def test_jamforaren_godtar_ratt_kontrakt(tmp_path):
    assert all(r["passed"] for r in _kor(tmp_path, _spanaren()))


def test_jamforaren_faller_agent_med_for_lag_konsekvens(tmp_path):
    res = _kor(tmp_path, _spanaren(sort="agent", konsekvens="informativ"))
    fallna = [r["text"] for r in res if not r["passed"]]
    assert any("validera_kontrakt" in t for t in fallna)
    assert any("matchar facit" in t for t in fallna)


def test_jamforaren_faller_kontrakt_nar_datagrinden_ska_stoppa(tmp_path):
    ut = tmp_path / "outputs"
    ut.mkdir()
    (ut / "kontrakt-x.yaml").write_text(yaml.safe_dump(_spanaren(id="x")), encoding="utf-8")
    res = jamfor(SKILL / "evals" / "datagrinden-arbetsmejl", ut)
    assert not res[0]["passed"]


def test_jamforaren_faller_fel_antal(tmp_path):
    a = _spanaren()
    b = copy.deepcopy(a)
    b["id"] = "scout-sources-2"
    res = _kor(tmp_path, a, b)
    assert not res[0]["passed"]
