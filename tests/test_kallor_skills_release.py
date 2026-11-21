import datetime as dt
import hashlib
import json
import zipfile
from pathlib import Path

import yaml

import validera_skills
from bygg_release import packa
from conftest import ROT
from kontrollera_kallor import kontrollera
from validera_skills import validera_marknadsplats, validera_skill

IDAG = dt.date(2026, 11, 21)


# Källregistret

def test_kallregistret_har_inga_fel():
    data = yaml.safe_load((ROT / "kallregister" / "kallor.yaml").read_text(encoding="utf-8"))
    fel, _ = kontrollera(data, IDAG, 90)
    assert fel == []


def _kalla(**over):
    k = {
        "id": "x", "titel": "t", "utgivare": "u", "niva": 2, "typ": "vagledning",
        "lasniva": "extraktion", "verifierad": IDAG, "bar_beslut": True, "galler": "g",
    }
    k.update(over)
    return {"schema_version": 1, "kallor": [k]}


def test_andra_hand_far_inte_bara_beslut():
    fel, _ = kontrollera(_kalla(lasniva="andra-hand"), IDAG, 90)
    assert any("andra hand" in f for f in fel)


def test_sekundarkalla_far_inte_bara_beslut():
    fel, _ = kontrollera(_kalla(niva=3, typ="sekundar"), IDAG, 90)
    assert any("nivå 3" in f for f in fel)


def test_gammal_verifiering_ger_varning():
    fel, varn = kontrollera(_kalla(verifierad=IDAG - dt.timedelta(days=91)), IDAG, 90)
    assert fel == [] and any("91 dagar" in v for v in varn)


# Skills

def _skill(rot: Path, namn: str, frontmatter: str, kropp: str = "# Rubrik\n") -> Path:
    mapp = rot / namn
    mapp.mkdir(parents=True)
    (mapp / "SKILL.md").write_text(f"---\n{frontmatter}\n---\n\n{kropp}", encoding="utf-8")
    return mapp


def test_giltig_skill(tmp_path):
    m = _skill(tmp_path, "min-skill", 'name: min-skill\ndescription: "Använd när något ska göras."')
    assert validera_skill(m) == ([], [])


def test_citerade_varden_godtas(tmp_path):
    # Dina befintliga skills har name och description inom citattecken.
    m = _skill(tmp_path, "registrera-kalla", 'name: "registrera-kalla"\ndescription: "Läs in en källa."')
    assert validera_skill(m)[0] == []


def test_namn_och_mapp_maste_stamma(tmp_path):
    m = _skill(tmp_path, "mappen", "name: annat\ndescription: d")
    assert any("inte samma som mappen" in f for f in validera_skill(m)[0])


def test_namnregler(tmp_path):
    for namn in ("Stora", "dubbla--streck", "-borjar", "slutar-", "a" * 65):
        m = _skill(tmp_path / namn.replace("-", "x")[:20], namn, f"name: {namn}\ndescription: d")
        assert validera_skill(m)[0], namn


def test_vinkelparenteser_och_okanda_falt(tmp_path):
    m = _skill(tmp_path, "s", "name: s\ndescription: 'Använd för <x>'\nversion: 2")
    fel = validera_skill(m)[0]
    assert any("vinkelparenteser" in f for f in fel)
    assert any("okända fält" in f for f in fel)


def test_bara_en_skill_md_men_evals_raknas_inte(tmp_path):
    m = _skill(tmp_path, "s", "name: s\ndescription: d")
    (m / "evals").mkdir()
    (m / "evals" / "SKILL.md").write_text("x", encoding="utf-8")
    assert validera_skill(m)[0] == []
    (m / "references").mkdir()
    (m / "references" / "SKILL.md").write_text("x", encoding="utf-8")
    assert any("mer än en SKILL.md" in f for f in validera_skill(m)[0])


def test_repots_marknadsplats_ar_giltig():
    assert validera_marknadsplats(ROT) == []


def test_marknadsplats_fel(tmp_path):
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / "plugins" / "p" / ".claude-plugin").mkdir(parents=True)
    (tmp_path / "plugins" / "p" / ".claude-plugin" / "plugin.json").write_text('{"name": "q"}', encoding="utf-8")
    (tmp_path / "plugins" / "ej-listad").mkdir()
    mp = {"name": "m", "owner": {"name": "o"}, "plugins": [
        {"name": "p", "source": "./plugins/p"},
        {"name": "r", "source": "./../utanfor"},
    ]}
    (tmp_path / ".claude-plugin" / "marketplace.json").write_text(json.dumps(mp), encoding="utf-8")
    fel = validera_marknadsplats(tmp_path)
    assert any("namnet i plugin.json" in f for f in fel)
    assert any("utan '..'" in f for f in fel)
    assert any("ej-listad" in f for f in fel)


# Release

def test_zip_har_skillens_mapp_i_roten_och_utan_evals(tmp_path):
    m = _skill(tmp_path / "src", "min-skill", "name: min-skill\ndescription: d")
    (m / "scripts").mkdir()
    (m / "scripts" / "a.py").write_text("print(1)\n", encoding="utf-8")
    (m / "evals").mkdir()
    (m / "evals" / "fall.json").write_text("[]", encoding="utf-8")
    (m / "scripts" / "__pycache__").mkdir()
    (m / "scripts" / "__pycache__" / "a.cpython.pyc").write_bytes(b"x")

    z1 = packa(m, tmp_path / "ut1")
    z2 = packa(m, tmp_path / "ut2")
    namn = zipfile.ZipFile(z1).namelist()
    assert namn == ["min-skill/SKILL.md", "min-skill/scripts/a.py"]
    assert hashlib.sha256(z1.read_bytes()).digest() == hashlib.sha256(z2.read_bytes()).digest()


def test_hitta_skills_ser_bara_plugin_skills(tmp_path, monkeypatch):
    _skill(tmp_path / "plugins" / "p" / "skills", "a", "name: a\ndescription: d")
    _skill(tmp_path / "annat", "b", "name: b\ndescription: d")
    assert [p.name for p in validera_skills.hitta_skills(tmp_path)] == ["a"]
