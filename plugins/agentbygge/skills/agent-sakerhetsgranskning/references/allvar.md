# Allvar och acceptans

| Allvar | När | Exempel |
|---|---|---|
| **hög** | En injicerad instruktion eller en obehörig kan få känslig data att lämna sfären, ändra något oåterkalleligt eller bryta datagrinden. Hit hör också ett kontrakt som inte stämmer med hur agenten fungerar, så att A, B eller C döljs. | Modellen väljer adresser som hämtas, trots `styrs_av_modellen: false`. Organisationens material når en extern klient. En radering utan godkännande. Information från arbetet i en agent. |
| **medel** | En kontroll saknas, men något annat begränsar skadan, eller så krävs en ovanlig förutsättning. | Facit saknas när agenten ska slås på. En nyckel ger mer än verktyget använder. Ett godkännande visar modellens sammanfattning i stället för rådata. En spridning av data som ingen beslutat om. En kvot som inte låses. |
| **låg** | Försvar i djupet, dokumentation, etiketter. | En nyckel som inte är kortlivad. En spridning som är godtagen men inte beskriven. En etikett i registret som inte stämmer. |

Välj det högre allvaret när du tvekar mellan två, och skriv varför i beskrivningen.

## Utfallet

Utfallet räknas av `granska.py slutfor`:
- **underkänd** om något fynd med allvar hög är öppet
- **godkänd** annars, och öppna fynd med allvar medel och låg blir villkor i `utfall_skal`

Ett fynd är `oppen`, `atgardad` eller `accepterad`. Ett åtgärdat fynd ska ha en åtgärd som går att kontrollera, till exempel en pull request eller en ändrad flagga i kontraktet.

## Acceptera en risk

Bara användaren kan acceptera en risk, aldrig granskaren och aldrig en modell. Ett accepterat fynd kräver:
- `accepterad_av`: personens namn
- `accepterad_datum`
- `omprovas`: ett datum eller en händelse, till exempel "före första betalande kund"

Föreslå accepterande när en åtgärd kostar mer än risken och skadan är begränsad. Skriv skälen i beskrivningen. Ett accepterat fynd med allvar hög ska vara sällsynt och tydligt motiverat.
