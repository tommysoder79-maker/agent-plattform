from conftest import ROT
from kontrollera_spegel import kontrollera

BAS = """# Dok (version 1, 2026-11-21)

## Ett

## Två

## Ändringslogg

- Version 1 (2026-11-21): första.
"""


def test_repots_dokument_ar_giltigt():
    assert kontrollera((ROT / "docs" / "arkitektur.md").read_text(encoding="utf-8"), None) == []


def test_oforandrat_godtas():
    assert kontrollera(BAS, BAS) == []


def test_andring_kraver_hogre_version():
    ny = BAS.replace("## Två", "## Två\n\nNy text.")
    assert any("höj versionen" in f for f in kontrollera(ny, BAS))


def test_tappat_avsnitt_maste_namnas():
    ny = (
        BAS.replace("version 1, 2026-11-21", "version 2, 2026-11-22")
        .replace("## Två\n\n", "")
        .replace("- Version 1", "- Version 2 (2026-11-22): kortare.\n- Version 1")
    )
    assert any("'Två' finns inte längre" in f for f in kontrollera(ny, BAS))
    ny_ok = ny.replace("kortare.", "tog bort avsnittet Två.")
    assert kontrollera(ny_ok, BAS) == []


def test_saknad_loggrad():
    ny = BAS.replace("version 1, 2026-11-21", "version 2, 2026-11-22")
    assert any("saknar en rad för version 2" in f for f in kontrollera(ny, BAS))
