# OWASP Top 10 for Agentic Applications (2026)

**Läsnivå: original.** Bygger på *OWASP Top 10 for Agentic Applications 2026*, version 2026 (december 2025), OWASP GenAI Security Project, Agentic Security Initiative, 57 sidor. Läst i sin helhet den 2026-11-21. Källa: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/

**Licens.** Originalet är licensierat under Creative Commons CC BY-SA 4.0. Den här filen är en bearbetning: sammanfattad och översatt till svenska, med egna kontrollfrågor. Den lyder därför under samma licens, CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). Beskrivningar och rekommendationer är återgivna med egna ord. Kontrollfrågorna under *Pröva* är skrivna för den här skillen och är inte OWASP:s.

## Två principer som går genom hela listan

- **Minsta möjliga agentmakt (least agency).** OWASP utvidgar minsta behörighet till minsta självständighet. Agentbeteende där det inte behövs ökar attackytan utan att tillföra något. I kontraktet motsvaras det av lägsta sort först: motor före AI-steg, AI-steg före agent.
- **Observerbarhet är inte förhandlingsbar.** Utan insyn i vad agenten gör, varför och med vilka verktyg kan överflödig självständighet växa i det tysta och göra små fel till systemfel.

## Klassa rätt

OWASP drar gränserna så här. Använd dem när ett fynd ska få sin punkt:

- **ASI01, ASI06 och ASI10:**
  - ASI01 gäller när en angripare direkt ändrar agentens mål eller beslutsväg, också genom dokument eller data som placerats i förväg.
  - ASI06 gäller när lagrat sammanhang eller minne förgiftas och påverkar senare körningar.
  - ASI10 gäller när agenten glider från sitt uppdrag och fortsätter så, efter att avvikelsen väl har börjat.
- **ASI02, ASI03 och ASI05:**
  - ASI02 gäller när agenten använder sina egna rättigheter på ett osäkert sätt.
  - ASI03 gäller när rättigheter ärvs, eskaleras eller lånas, till exempel via delegering, en cachad nyckel eller en användares session.
  - ASI05 gäller när missbruket leder till att kod körs.
- **ASI02 och ASI04:** ett förvanskat verktygsgränssnitt under körning, till exempel en MCP-beskrivning, är ASI02. Ett verktyg som är skadligt redan vid källan är ASI04.
- **ASI08** gäller spridningen av ett fel, inte felets ursprung. Klassa ursprunget under ASI04, ASI06 eller ASI07. Använd ASI08 när felet sprids till andra agenter, sessioner eller flöden.
- **ASI09 och ASI10:** ASI09 gäller att människor övertolkar eller litar för mycket på agenten. ASI10 gäller att agenten själv avviker.

## ASI01 Agent Goal Hijack

**Vad det är.** Modeller kan inte pålitligt skilja instruktioner från innehåll. En angripare kan därför styra om agentens mål, val av uppgifter eller beslutsväg, genom text i webbsidor, dokument, mejl, kalenderinbjudningar, verktygssvar eller meddelanden från andra agenter. Skillnaden mot en vanlig prompt injection är att hela flerstegsbeteendet styrs om, inte bara ett svar.

**Typiska svagheter:**
- dolda instruktioner i hämtat innehåll som får agenten att föra ut data eller missbruka verktyg
- mejl eller inbjudningar utifrån som kapar agentens förmåga att skicka meddelanden under en betrodd identitet
- en manipulerad agent som flyttar pengar eller producerar vilseledande beslutsunderlag

**OWASP rekommenderar:**
- Behandla all naturlig text som opålitlig: användarens text, uppladdade dokument och hämtat innehåll.
- Begränsa skadan med minsta behörighet för verktygen och mänskligt godkännande av handlingar med stor verkan eller som ändrar målet.
- Lås systemprompterna, så att mål och tillåtna handlingar är uttryckliga och granskningsbara. Ändringar går via konfigurationshantering och godkännande.
- Pröva både användarens och agentens avsikt före handlingar med stor verkan. Stoppa vid oväntade målbyten och logga dem.
- Rensa och kontrollera varje datakälla innan den kan påverka mål eller handlingar.
- Logga och övervaka mot en baslinje för mål och verktygsanvändning, och larma vid avvikelser.
- Rödlagstesta återkommande med försök att skriva över målet.

**Pröva:**
- Når text utifrån modellen? Är den markerad som data i prompten?
- Finns det injektionsfall i facit för varje fält som kommer utifrån, och ett test som visar att prompten neutraliserar dem?
- Är systemprompten versionshanterad och granskad?
- Vad kan en lurad modell som mest åstadkomma med de verktyg den har? Det är Rule of Two i praktiken.

## ASI02 Tool Misuse and Exploitation

**Vad det är.** Agenten använder legitima verktyg på ett osäkert eller oavsett sätt, inom sina tilldelade rättigheter, till exempel genom att radera data, anropa dyra tjänster i en loop eller föra ut information. Det relaterar till Excessive Agency (LLM06:2025).

**Typiska svagheter:**
- verktyg med för många rättigheter, som en mejlsammanfattare som kan skicka och radera
- verktyg med för brett omfång
- opålitlig modellutdata som skickas vidare till ett skal eller en databas
- att agenten följer skadliga länkar
- loopar som driver upp kostnader
- kedjor av verktyg, som ett internt verktyg följt av ett externt utskick
- ett godkänt och till synes ofarligt verktyg som används för att föra ut data, till exempel ping via DNS

**OWASP rekommenderar:**
- En behörighetsprofil per verktyg: omfång, största takt och tillåtna nätmål. Gärna uttryckt som behörighetsregler.
- Autentisering per anrop och mänskligt godkännande för förstörande handlingar, med en förhandsvisning eller diff före godkännandet.
- Sandlådor och spärrar för utgående trafik.
- En spärr för avsikt (policy enforcement point) som behandlar modellens utdata som opålitlig och kontrollerar argument, scheman och takter innan något körs.
- Budgetar som stryper eller återkallar vid överskridande.
- Kortlivade nycklar som gäller just ett anrop eller en session.
- Fullt kvalificerade verktygsnamn och låsta versioner, och stopp vid tvetydighet.
- Oföränderliga loggar över alla verktygsanrop, och larm vid ovanliga kedjor.

**Pröva:**
- Är verktygen så smala som uppgiften kräver?
- Kontrollerar koden parametrarna, som mål, belopp, mottagare och adresser, innan de används?
- Finns det tak för antal anrop och kostnad?
- Kan modellen välja ett mål som koden inte prövat?
- Kan ett "ofarligt" verktyg som körs utan godkännande användas som kanal ut?

## ASI03 Identity and Privilege Abuse

**Vad det är.** Förtroende och delegering missbrukas för att få större åtkomst: ärvda rättigheter, delegeringskedjor, cachade nycklar, en användares session eller OAuth-token. Agentens identitet omfattar både dess roll och allt autentiseringsmaterial som representerar den. Utan en egen, styrd identitet uppstår ett tomrum där minsta behörighet inte går att genomdriva.

**Typiska svagheter:**
- en agent som delegerar hela sin behörighet till en smalare agent
- nycklar eller data som ligger kvar i minnet mellan uppgifter eller användare
- en betrodd intern agent som vidarebefordrar en förfalskad begäran (confused deputy)
- en behörighet som prövas i början men har ändrats när handlingen utförs
- falska agentidentiteter
- en agent som låter andra använda den identitet den fått å en användares vägnar

**OWASP rekommenderar:**
- Kortlivade, uppgiftsavgränsade behörigheter med egna identiteter per agent.
- Isolerade sessioner, där minne och tillstånd töms mellan uppgifter.
- Behörighetsprövning för varje privilegierat steg, i en central policymotor.
- Mänskligt godkännande vid eskalering eller oåterkalleliga handlingar.
- OAuth-token bundna till en signerad avsikt: subjekt, mottagare, syfte och session.
- Behörigheter bundna till subjekt, resurs, syfte och tid, med ny autentisering vid kontextbyte.
- Larm vid ärvda eller transitiva behörigheter.

**Pröva:**
- Har agenten en egen identitet, eller lånar den en persons?
- Vad ger en token faktiskt tillgång till, jämfört med vad verktyget använder?
- Prövas behörigheten där datan finns (till exempel RLS), och inte bara i agentens kod?
- När en extern klient anropar å en persons vägnar: får den personens hela behörighet, eller ett avgränsat syfte?

NIST NCCoE har samma linje: befintliga standarder som OAuth, avgränsade och kortlivade nycklar, ingen egen identitetsstack (`nccoe-agent-identity`).

## ASI04 Agentic Supply Chain Vulnerabilities

**Vad det är.** Delar som kommer från andra kan vara skadliga, komprometterade eller manipulerade på vägen: modeller, verktyg, insticksmoduler, dataset, andra agenter, MCP- och A2A-gränssnitt, register och uppdateringskanaler. Agenter sätter ofta ihop förmågor medan de körs, så leverantörskedjan är levande och kräver kontroll också vid körning.

**OWASP rekommenderar:**
- Signerade och attesterade manifest, prompter och verktygsdefinitioner, med SBOM eller AIBOM och en förteckning över AI-komponenterna.
- Tillåtna listor och låsta versioner, kontroll av typosquatting och verifierat ursprung före installation.
- Sandlådor och reproducerbara byggen.
- Prompter, orkestrering och minnesscheman under versionshantering med granskning.
- Ömsesidig autentisering mellan agenter, och ingen öppen registrering.
- Låsning av prompter, verktyg och konfiguration med hash, med stegvis utrullning och återställning vid avvikelse.
- En nödbrytare som kan stänga av ett verktyg, en prompt eller en koppling överallt.

**Pröva:**
- Vilka MCP-servrar, skills och paket används?
- Är de lästa före installation, och är versionerna låsta?
- Finns det beroendebevakning?
- Är prompterna versionshanterade?
- Vilken modelleverantör används, och var?
- Finns det en brytare per verktyg eller koppling?

## ASI05 Unexpected Code Execution (RCE)

**Vad det är.** Agenten genererar eller kör kod, och angripare kan via prompt injection, verktygsmissbruk eller osäker deserialisering få kod körd som komprometterar värden eller containern. Det omfattar skript, binärer, mallmotorer och utvärdering i minnet.

**OWASP rekommenderar:**
- Validera och koda utdata (LLM05:2025).
- Ingen direkt väg från agent till produktion.
- Ingen `eval` i produktion.
- Kör aldrig som root.
- Kör i sandlåda med begränsat nät och filsystem.
- Separera generering från körning med en kontrollpunkt emellan.
- Mänskligt godkännande för körning med förhöjda rättigheter, och en versionshanterad lista över det som får köras automatiskt.
- Statisk analys före körning.
- Logga alla körningar.

**Pröva:**
- Kan modellen få kod, kommandon, frågor mot databasen eller mallar körda? I vilken sandlåda, med vilket nät och vilka hemligheter i miljön?
- Kan opålitlig text hamna i något som tolkas?

## ASI06 Memory & Context Poisoning

**Vad det är.** Lagrad eller hämtbar kontext förgiftas: historik, minne, sammanfattningar, inbäddningar och RAG-lager. Det gör senare resonemang, planering och verktygsval vinklade eller osäkra. Engångsprompter hör inte hit. ASI06 leder ofta till ASI01.

**OWASP rekommenderar:**
- Kryptering och minsta behörighet.
- Kontroll av allt som skrivs till minnet.
- Segmentering per session och domän.
- Bara autentiserade, kuraterade källor.
- Kortast möjliga lagring.
- Ursprung för varje post.
- **Ingen automatisk återinläsning av agentens egna utdata i betrott minne**, för att undvika självförstärkande förgiftning.
- Ögonblicksbilder och återställning.
- Utgång och avtagande vikt för overifierat minne.
- Två oberoende stöd innan minne med stor verkan används.

**Pröva:**
- Sparas text som bygger på opålitlig indata?
- Var och av vem läses den igen?
- Läser agenten in sina egna tidigare utdata? I så fall: behandlas de som opålitliga?
- Kan sparat innehåll märkas, granskas och tas bort?

## ASI07 Insecure Inter-Agent Communication

**Vad det är.** Utbyten mellan agenter, via API:er, meddelandeköer eller delat minne, saknar autentisering, integritet eller semantisk kontroll. Meddelanden kan då avlyssnas, förfalskas, spelas upp igen eller ändras.

**OWASP rekommenderar:**
- Krypterade kanaler med ömsesidig autentisering per agent.
- Signerade meddelanden och kontroll av dolda eller ändrade instruktioner.
- Skydd mot uppspelning.
- Låsta protokollversioner (MCP, A2A).
- Autentiserad upptäckt och routning.
- Register med attesterade agentkort.
- Typade, versionerade meddelandescheman.

**Pröva:**
- Är klienten autentiserad, och prövas behörigheten för varje meddelande?
- Vet agenten vilken sorts klient den svarar? Begränsas svaret efter det?
- Vad lämnar ut till en klient vars egna verktyg du inte ser?

## ASI08 Cascading Failures

**Vad det är.** Ett enda fel sprids mellan agenter, verktyg och flöden och växer till systemövergripande skada. Felet kan vara en hallucination, skadlig indata, ett komprometterat verktyg eller förgiftat minne. Kännetecken är snabb spridning och felbeslut som upprepas.

**OWASP rekommenderar:**
- Utgå från att delar fallerar.
- Isolering och tydliga förtroendegränser.
- Kortlivad åtkomst per körning och kontroll av varje anrop med stor verkan mot regler i kod.
- **Planering och utförande separerade, med en oberoende policykontroll emellan.**
- Mänskliga kontrollpunkter innan utdata sprids vidare.
- Takt- och mängdspärrar.
- Brytare mellan den som planerar och den som utför.
- Uppföljning av avdrift.
- Repris i en isolerad miljö innan policyer vidgas.
- Spårbara loggar.

**Pröva:**
- Vilka andra delar läser agentens utdata?
- Finns det en grind innan ett förslag blir underlag för nästa del?
- Är planering och utförande skilda åt, och finns det en spärr emellan?
- Kan en del pausas utan att resten går sönder?
- Finns det tak som stoppar en loop?

## ASI09 Human-Agent Trust Exploitation

**Vad det är.** Människors förtroende för en flytande, säker och kunnig agent utnyttjas, så att någon godkänner, lämnar ut eller beslutar något utan egen prövning. Agenten blir en osynlig dålig påverkan: den sista, loggade handlingen är människans.

**OWASP rekommenderar:**
- Uttryckliga bekräftelser i flera steg före känslig åtkomst eller riskfyllda handlingar.
- Oföränderliga loggar.
- Övervakning av känslig data i konversationer.
- **En riskbeskrivning i klarspråk som inte är skriven av modellen**, och ett enkelt sätt att flagga misstänkt beteende.
- Graden av självständighet anpassad efter risk, med synliga markeringar som "osäkert" eller "okänd källa".
- Verifierbart ursprung för rekommendationer.
- Förhandsvisning skild från verkan.
- Gränssnitt som markerar högrisk och undviker övertalande språk i säkerhetskritiska flöden.
- Larm när agentens handlingar avviker från godkända flöden.

**Pröva:**
- Visar godkännandet rådata (mottagare, innehåll, mål) eller modellens motivering?
- Är godkännandena få nog att granskas på riktigt?
- Syns källorna? Är agentens utdata märkt som maskinens?
- Är utkast som ska övertyga, till exempel beslutsunderlag, tydligt märkta?

## ASI10 Rogue Agents

**Vad det är.** En agent avviker från sitt uppdrag eller sin behörighet och agerar skadligt, vilseledande eller parasitiskt. Varje enskild handling kan se legitim ut. Punkten gäller förlusten av beteendeintegritet efter att avvikelsen börjat, oavsett vad som startade den.

**OWASP rekommenderar:**
- Signerade, oföränderliga loggar över handlingar, verktygsanrop och kommunikation.
- Förtroendezoner och begränsade körmiljöer.
- Beteendeövervakning, gärna med en agent som vakar över andras utdata.
- Nödbrytare och återkallade nycklar.
- **Signerade beteendemanifest som anger förväntade förmågor, verktyg och mål och prövas före varje handling.**
- Återkommande attestering och nycklar som gäller en körning.
- Återinförande först efter ny attestering och mänskligt godkännande.

**Pröva:**
- Finns det ett nödstopp, och loggas allt under agentens egen identitet?
- Finns det tak för steg, kostnad och tid?
- Följs beteendet mot kontraktet, till exempel andelen godtagna förslag?
- Börjar agenten i skugga och befordras på uppmätt underlag?

Agentkontraktet är ett beteendemanifest i OWASP:s mening, men utan signering och utan prövning före varje handling.
