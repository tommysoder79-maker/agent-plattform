from pathlib import Path

import yaml

from conftest import EXEMPEL
from validera_kontrakt import (
    KONTRAKTSCHEMA,
    _validerare,
    main,
    regelfel,
    schemafel,
    validera_filer,
    validera_register,
)

P = Path("exempel.yaml")


def alla_fel(k, sokvag=P):
    fel = schemafel(_validerare(KONTRAKTSCHEMA), k)
    if fel:
        return fel
    f, _ = regelfel(k, sokvag, kontrollera_sokvagar=False)
    return f


def test_exemplen_ar_giltiga(capsys):
    filer = sorted(EXEMPEL.glob("*.yaml"))
    assert len(filer) >= 2
    assert main([str(f) for f in filer]) == 0
    ut = capsys.readouterr().out
    assert "AB- nivå 2" in ut and "-BC nivå 2" in ut


def test_en_session_med_lasning_och_radering_ar_niva_3(las):
    # Samma agent läser mejlen och flyttar dem: A + B + C.
    las["skriver"].append({"resurs": "inkorgen", "beskrivning": "flyttar", "effekt": "angringsbar", "godkannande": "ingen"})
    las["riskniva"] = 3
    fel = alla_fel(las)
    assert any("riskniva 3" in f for f in fel)


def test_deklarerad_niva_maste_stamma(las):
    las["riskniva"] = 1
    assert any("räknat ur resurserna blir det 2" in f for f in alla_fel(las))


def test_oaterkallelig_kraver_godkannande(utfor):
    utfor["skriver"][0]["effekt"] = "oaterkallelig"
    assert any("oåterkallelig handling kräver" in f for f in alla_fel(utfor))


def test_oaterkallelig_med_godkannande_godtas(utfor):
    utfor["skriver"][0]["effekt"] = "oaterkallelig"
    utfor["skriver"][0]["godkannande"] = "fore-varje-handling"
    utfor["riskniva"] = 1  # C försvinner med godkännande före varje handling
    utfor["provsamling"]["antal_fall"] = 5
    assert alla_fel(utfor) == []


def test_kodstyrd_skrivning_kraver_beskrivning(utfor):
    utfor["skriver"][0]["styrs_av_modellen"] = False
    assert any("kodstyrning" in f for f in alla_fel(utfor))
    utfor["skriver"][0]["kodstyrning"] = "Koden flyttar exakt de id som står på den godkända listan."
    utfor["riskniva"] = 1
    utfor["provsamling"]["antal_fall"] = 5
    assert alla_fel(utfor) == []


def test_datagrinden_kan_inte_stangas_av(las):
    las["datagrind"]["ingen_arbetsinformation"] = False
    assert any("datagrind" in f for f in alla_fel(las))


def test_automatiskt_kraver_befordran(las):
    las["lage"] = "automatiskt"
    las["sakerhetsgranskning"] = {"utfall": "godkand", "datum": "2026-11-21"}
    assert any("befordran" in f for f in alla_fel(las))


def _paslagen(k):
    k["lage"] = "skugga"
    k["sakerhetsgranskning"] = {"utfall": "godkand", "datum": "2026-11-21"}
    return k


def test_niva_2_kraver_tio_fall(las):
    las["provsamling"]["antal_fall"] = 9
    assert any("minst 10 fall" in f for f in alla_fel(_paslagen(las)))


def test_opalitlig_indata_kraver_injektionsfall(las):
    las["provsamling"]["injektionsfall"] = False
    assert any("injektionsfall" in f for f in alla_fel(_paslagen(las)))


def test_saknad_provsamling_ar_varning_i_laget_av(las):
    las["provsamling"]["antal_fall"] = 0
    las["provsamling"]["injektionsfall"] = False
    assert alla_fel(las) == []
    _, varn = regelfel(las, P, kontrollera_sokvagar=False)
    assert any("minst 10 fall" in v for v in varn) and any("injektionsfall" in v for v in varn)


def test_niva_2_i_skugga_kraver_godkand_granskning(las):
    las["lage"] = "skugga"
    assert any("kräver godkänd granskning" in f for f in alla_fel(las))
    las["sakerhetsgranskning"] = {"utfall": "godkand", "datum": "2026-11-21"}
    assert alla_fel(las) == []


def test_underkand_granskning_far_inte_vara_paslagen(las):
    las["sakerhetsgranskning"] = {"utfall": "underkand"}
    las["lage"] = "skugga"
    assert any("underkänd" in f for f in alla_fel(las))


def test_konsekvens_far_inte_vara_for_lag(las):
    las["konsekvens"] = "informativ"
    assert any("lägre än vad skrivningarna kräver" in f for f in alla_fel(las))


def test_agent_kraver_motivering_for_sorten(las):
    del las["sort_motivering"]
    assert any("sort_motivering" in f for f in alla_fel(las))


def test_personuppgifter_kraver_rattslig_grund(las):
    del las["gdpr"]["rattslig_grund"]
    assert any("rattslig_grund" in f for f in alla_fel(las))


def test_delad_nyckel_godtas_inte(las):
    las["identitet"]["nycklar"][0]["delad_med_annan_agent"] = True
    assert alla_fel(las) != []


def test_id_maste_stamma_med_mappen(las):
    assert any("stämmer inte med mappen" in f for f in alla_fel(las, Path("agents/annat-namn/kontrakt.yaml")))
    assert alla_fel(las, Path("agents/yahoo-rensning-las/kontrakt.yaml")) == []


def test_kallor_kontrolleras_mot_registret(tmp_path, las):
    las["kallor"] = ["finns-inte"]
    p = tmp_path / "k.yaml"
    p.write_text(yaml.safe_dump(las, allow_unicode=True), encoding="utf-8")
    fel, _, _ = validera_filer([p], EXEMPEL.parent.parent / "kallregister" / "kallor.yaml", False)
    assert any("finns-inte" in f for f in fel[p])


def _skriv_agent(rot: Path, k: dict) -> None:
    mapp = rot / "agents" / k["id"]
    (mapp / "evals").mkdir(parents=True)
    (mapp / "kontrakt.yaml").write_text(yaml.safe_dump(k, allow_unicode=True), encoding="utf-8")


def test_register_med_kontrakt(tmp_path, las, utfor, capsys):
    _skriv_agent(tmp_path, las)
    _skriv_agent(tmp_path, utfor)
    reg = {
        "schema_version": 1,
        "sfar": "privat",
        "agenter": [
            {"id": "yahoo-rensning-las", "kontrakt": "agents/yahoo-rensning-las/kontrakt.yaml", "status": "under-bygge"},
            {"id": "yahoo-rensning-utfor", "kontrakt": "agents/yahoo-rensning-utfor/kontrakt.yaml", "status": "under-bygge"},
        ],
    }
    (tmp_path / "agentregister.yaml").write_text(yaml.safe_dump(reg, allow_unicode=True), encoding="utf-8")
    assert validera_register(tmp_path / "agentregister.yaml", None, True) == 0
    assert "uppdelning" not in capsys.readouterr().out  # båda delarna validerades tillsammans


def test_register_fel_sfar_och_avveckling(tmp_path, las):
    _skriv_agent(tmp_path, las)
    reg = {
        "schema_version": 1,
        "sfar": "forening",
        "agenter": [{"id": "yahoo-rensning-las", "kontrakt": "agents/yahoo-rensning-las/kontrakt.yaml", "status": "under-bygge"}],
    }
    (tmp_path / "agentregister.yaml").write_text(yaml.safe_dump(reg), encoding="utf-8")
    assert validera_register(tmp_path / "agentregister.yaml", None, False) == 1

    reg["sfar"] = "privat"
    reg["agenter"][0].update({"status": "avvecklad", "avvecklad": "2026-11-21", "nycklar_aterkallade": False})
    (tmp_path / "agentregister.yaml").write_text(yaml.safe_dump(reg), encoding="utf-8")
    assert validera_register(tmp_path / "agentregister.yaml", None, False) == 1
