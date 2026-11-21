#!/usr/bin/env python3
"""Räknar Rule of Two och risknivå ur ett agentkontrakt.

Modellen märker, koden verkar: kontraktet beskriver fakta per resurs
(vad agenten läser, skriver och skickar), och den här koden räknar ut
egenskaperna A, B och C och risknivån. En deklarerad nivå i kontraktet
måste stämma med det som räknas här.

  A  bearbetar opålitlig indata      någon läst resurs har opalitlig: true
  B  har åtkomst till känslig data   någon läst resurs har kanslig: true
  C  ändrar tillstånd eller          någon skrivning med effekt angringsbar eller
     kommunicerar externt            oaterkallelig, eller någon extern kommunikation,
                                     som modellen kan styra och som inte kräver
                                     godkännande före varje handling

Ett förslag som hamnar i en kö där en människa avgör, och ett råd som bara
läses av en människa, räknas inte som C. En skrivning eller ett anrop som
koden ensam bestämmer (styrs_av_modellen: false, med kodstyrning beskriven)
räknas inte heller: Rule of Two gäller det en injicerad instruktion kan få
modellen att göra.

Nivå = antalet egenskaper, men lägst 1. Nivå 3 godtas aldrig: flödet ska
delas upp eller få mänskligt godkännande före varje handling.

Källa: Meta, "Agents Rule of Two: A Practical Approach to AI Agent Security"
(2025-10-31), se kallregister/kallor.yaml (meta-rule-of-two).

Användning:
  python scripts/risk.py agents/<namn>/kontrakt.yaml
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Any, Mapping

GODKANNANDE_FORE = "fore-varje-handling"
TILLSTANDSANDRING = {"angringsbar", "oaterkallelig"}

KONSEKVENS_ORDNING = {"informativ": 0, "angringsbar": 1, "mansklig": 2}


@dataclass(frozen=True)
class RuleOfTwo:
    a: bool
    b: bool
    c: bool
    skal: tuple[str, ...]

    @property
    def antal(self) -> int:
        return int(self.a) + int(self.b) + int(self.c)

    @property
    def niva(self) -> int:
        return max(1, self.antal)

    def kort(self) -> str:
        def m(flag: bool, bokstav: str) -> str:
            return bokstav if flag else "-"
        return f"{m(self.a, 'A')}{m(self.b, 'B')}{m(self.c, 'C')} nivå {self.niva}"


def rakna(kontrakt: Mapping[str, Any]) -> RuleOfTwo:
    """Räkna A, B, C och skälen till varje ur kontraktets resurser."""
    skal: list[str] = []
    laser = kontrakt.get("laser") or []
    skriver = kontrakt.get("skriver") or []
    kommunicerar = kontrakt.get("kommunicerar_externt") or []

    a_resurser = [r.get("resurs", "?") for r in laser if r.get("opalitlig") is True]
    b_resurser = [r.get("resurs", "?") for r in laser if r.get("kanslig") is True]
    c_skriv = [
        s.get("resurs", "?")
        for s in skriver
        if s.get("effekt") in TILLSTANDSANDRING
        and s.get("godkannande") != GODKANNANDE_FORE
        and s.get("styrs_av_modellen", True) is not False
    ]
    c_komm = [
        k.get("mottagare", "?")
        for k in kommunicerar
        if k.get("godkannande") != GODKANNANDE_FORE and k.get("styrs_av_modellen", True) is not False
    ]

    if a_resurser:
        skal.append("A: opålitlig indata från " + ", ".join(a_resurser))
    if b_resurser:
        skal.append("B: känslig data i " + ", ".join(b_resurser))
    if c_skriv:
        skal.append("C: ändrar utan godkännande i " + ", ".join(c_skriv))
    if c_komm:
        skal.append("C: kommunicerar utan godkännande med " + ", ".join(c_komm))

    return RuleOfTwo(a=bool(a_resurser), b=bool(b_resurser), c=bool(c_skriv or c_komm), skal=tuple(skal))


def lagsta_konsekvens(kontrakt: Mapping[str, Any]) -> str:
    """Den lägsta konsekvensklass kontraktet får deklarera.

    Ett förslag eller en oåterkallelig handling väntar alltid på en människa
    (System Insights princip: grind efter konsekvens). En ångringsbar ändring
    är ångringsbar. Råd och svar som bara läses är informativa.
    """
    skriver = kontrakt.get("skriver") or []
    kommunicerar = kontrakt.get("kommunicerar_externt") or []
    effekter = {s.get("effekt") for s in skriver}
    if "forslag" in effekter or "oaterkallelig" in effekter:
        return "mansklig"
    if any(k.get("godkannande") == GODKANNANDE_FORE for k in kommunicerar):
        return "mansklig"
    if "angringsbar" in effekter or kommunicerar:
        return "angringsbar"
    return "informativ"


def main(argv: list[str]) -> int:
    import yaml  # importeras här så att modulen kan användas utan PyYAML i tester av rakna()

    if len(argv) < 2:
        print(__doc__)
        return 2
    rc = 0
    for sokvag in argv[1:]:
        with open(sokvag, encoding="utf-8") as f:
            kontrakt = yaml.safe_load(f)
        r = rakna(kontrakt)
        print(f"{sokvag}: {r.kort()}")
        for s in r.skal:
            print(f"  {s}")
        if r.niva == 3:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
