# Fälten som avgör risknivån

Risknivån räknas ur fem flaggor. Sätt dem efter fakta och skriv skälet när det inte är uppenbart.

## laser: opalitlig

Sätt `opalitlig: true` när någon annan än ägaren kan ha format texten som modellen får se:
- webbsidor, flöden, sökträffar
- mejl och meddelanden från andra
- dokument utifrån
- svar från andras agenter
- kalenderinbjudningar från andra

**Smittan följer texten.** Text som kommer utifrån förblir opålitlig när den sammanfattats, bearbetats av en modell, lagrats eller godkänts av en människa, så länge en utomstående kan ha format den. En sammanfattning av ett mejl kan bära mejlets instruktion vidare. System Insight följer samma princip: det som vilar på konfidentiellt är konfidentiellt, och drivkrafters namn neutraliseras i prompterna eftersom de bygger på text utifrån.

`opalitlig: false` gäller:
- text som bara ägaren eller koden skrivit
- tal och fält som koden läser ur ett känt format utan att någon modell ser fritext, till exempel ett pris ur ett API eller ett id ur en lista

## laser: kanslig

Sätt `kanslig: true` för:
- privata data: egen inkorg, kalender, ekonomi, anteckningar
- personuppgifter om andra
- organisationens eget material: beslutsfrågor, hypoteser, alternativ, bevakade ämnen, egna underlag
- allt med licensnivå A eller R i System Insight

`kanslig: false` gäller öppet material som fritt får lämna sfären, till exempel öppna data och G-licensierat material.

## skriver: effekt

| Effekt | Betyder | Exempel |
|---|---|---|
| `rad` | Text som bara läses av en människa och inte ändrar något annat | förklaring, råd, svar på en fråga, körlogg |
| `forslag` | Hamnar i en kö där en människa avgör | förslag till källregistret, utkast som väntar på godkännande |
| `angringsbar` | Ändrar tillstånd men kan ångras | flytta till papperskorgen, lägga till en rad, sätta en etikett |
| `oaterkallelig` | Kan inte ångras | radera för gott, skicka pengar, publicera, skicka ett mejl |

Ett skickat mejl eller meddelande kan inte tas tillbaka. Det skrivs under `kommunicerar_externt` när det går utanför sfären.

## skriver och kommunicerar_externt: godkannande

`fore-varje-handling` betyder att en människa godkänner varje enskild handling med rådata framför sig: mottagare, innehåll och mål, inte modellens sammanfattning. Att godkänna en hel lista i förväg räknas inte. Listan är då ett förslag, och utförandet sker utan godkännande per handling. En oåterkallelig handling kräver alltid `fore-varje-handling`.

## skriver och kommunicerar_externt: styrs_av_modellen

Standard är `true`. Sätt `false` bara när koden ensam bestämmer mål och innehåll, så att modellens svar inte kan ändra vart något går eller vad det innehåller. Beskriv hur i `kodstyrning`. Exempel:
- Koden bygger en sökfråga ur organisationens ämnen och skickar den *innan* modellen anropas.
- Koden skriver en körlogg med fasta fält.

Det räknas inte som C, eftersom en injicerad instruktion inte kan påverka det. Det är ändå en spridning av data:
- Skickar koden känslig data till en tredje part, till exempel ämnen till en sökmotor, skriv det under `kommunicerar_externt` med `styrs_av_modellen: false`.
- Nämn det i `gdpr` eller `anteckningar`, så att säkerhetsgranskningen tar ställning till det.

Ett svar som modellen skriver och som går till någon utanför sfären är extern kommunikation som modellen styr. Det gäller till exempel en extern agent som ställer en fråga. Är svaret dessutom byggt på känslig data har agenten B och C, och med opålitlig indata blir det nivå 3.

## konsekvens

Den lägsta tillåtna klassen följer av skrivningarna:
- `mansklig` om något är ett förslag eller oåterkalleligt
- `angringsbar` om något är ångringsbart
- annars `informativ`

En strängare klass är tillåten. Översättningen till System Insight: `informativ` = `informational`, `angringsbar` = `reversible`, `mansklig` = `human`.

## Övrigt

- `lage`: `av` för ett nytt kontrakt. `skugga` kräver godkänd säkerhetsgranskning från nivå 2, och `automatiskt` kräver `befordran` med datum och underlag. För en befintlig modul som redan körs: sätt `av` tills granskningen är gjord, och skriv dagens läge i `anteckningar`.
- `budget`: tak i kronor per månad och steg per körning. Körs agenten inom ett abonnemang kan kronbeloppet vara 0, men stegtaket ska alltid finnas.
- `provsamling`: antal fall och om det finns injektionsfall, efter nivån.
- `identitet.nycklar`: en egen nyckel per agent, med namn och omfång. Ange om nyckeln ger mer åtkomst än verktyget använder, och var begränsningen i så fall ligger.
- `gdpr`: behandlas personuppgifter krävs rättslig grund och vilka som är registrerade. För privat bruk av egna data gäller i regel hushållsundantaget. Skriv att det inte är juridiskt prövat.
