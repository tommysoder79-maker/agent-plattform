import pytest

from risk import lagsta_konsekvens, rakna


def kontrakt(laser=(), skriver=(), kommunicerar=()):
    return {"laser": list(laser), "skriver": list(skriver), "kommunicerar_externt": list(kommunicerar)}


def las(opalitlig=False, kanslig=False, resurs="r"):
    return {"resurs": resurs, "opalitlig": opalitlig, "kanslig": kanslig}


def skriv(effekt, godkannande="ingen", resurs="w"):
    return {"resurs": resurs, "effekt": effekt, "godkannande": godkannande}


@pytest.mark.parametrize(
    "k, abc, niva",
    [
        (kontrakt([las()]), (False, False, False), 1),
        (kontrakt([las(opalitlig=True)]), (True, False, False), 1),
        (kontrakt([las(kanslig=True)], [skriv("forslag")]), (False, True, False), 1),
        (kontrakt([las(opalitlig=True, kanslig=True)]), (True, True, False), 2),
        (kontrakt([las(kanslig=True)], [skriv("angringsbar")]), (False, True, True), 2),
        (kontrakt([las(opalitlig=True, kanslig=True)], [skriv("angringsbar")]), (True, True, True), 3),
        # Godkännande före varje handling tar bort C.
        (kontrakt([las(True, True)], [skriv("oaterkallelig", "fore-varje-handling")]), (True, True, False), 2),
        # Extern kommunikation utan godkännande ger C.
        (kontrakt([las(True, True)], [], [{"mottagare": "x", "godkannande": "ingen"}]), (True, True, True), 3),
        (kontrakt([las(True, True)], [], [{"mottagare": "x", "godkannande": "fore-varje-handling"}]), (True, True, False), 2),
    ],
)
def test_rule_of_two(k, abc, niva):
    r = rakna(k)
    assert (r.a, r.b, r.c) == abc
    assert r.niva == niva


def test_skalen_namnger_resurserna():
    r = rakna(kontrakt([las(True, False, "webben")], [skriv("angringsbar", resurs="kalendern")]))
    assert any("webben" in s for s in r.skal)
    assert any("kalendern" in s for s in r.skal)


@pytest.mark.parametrize(
    "k, lagst",
    [
        (kontrakt([las()]), "informativ"),
        (kontrakt([las()], [skriv("angringsbar")]), "angringsbar"),
        (kontrakt([las()], [skriv("forslag")]), "mansklig"),
        (kontrakt([las()], [skriv("oaterkallelig", "fore-varje-handling")]), "mansklig"),
        (kontrakt([las()], [], [{"mottagare": "x", "godkannande": "ingen"}]), "angringsbar"),
    ],
)
def test_lagsta_konsekvens(k, lagst):
    assert lagsta_konsekvens(k) == lagst
