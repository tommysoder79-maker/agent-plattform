# OWASP Top 10 for Agentic Applications (2026)

**Läsnivå: andra hand.** OWASP publicerade listan 2025-12-09 (OWASP GenAI Security Project, Agentic Security Initiative). Titlarna nedan är bekräftade i flera oberoende källor. OWASP:s egna beskrivningar och åtgärder är inte lästa i original, eftersom PDF:en inte gick att läsa i den session som skrev filen. Kontrollfrågorna är skrivna för den här skillen och följer de åtgärder som källorna återger. Läs PDF:en i original innan filen räknas som original, och uppdatera källregistret (`owasp-agentic-top10-2026`).

Den genomgående principen är **minsta möjliga agentmakt** (least agency): ge en agent den minsta självständighet, de minsta verktygen och de minsta behörigheterna som uppgiften kräver.

## ASI01 Agent Goal Hijack

En angripare ändrar vad agenten försöker uppnå, oftast genom instruktioner i ett dokument, ett mejl eller en webbsida som agenten läser.

Pröva:
- Når text utifrån modellen? Ligger den i markerade datablock, och står det utanför blocken att de är data?
- Finns det injektionsfall i facit för varje fält som kommer utifrån?
- Vad kan en lurad modell som mest åstadkomma, givet verktygen? Det är Rule of Two i praktiken.

## ASI02 Tool Misuse and Exploitation

Legitima verktyg används på ett osäkert eller oavsiktligt sätt, med parametrar som modellen styr.

Pröva:
- Är verktygen så smala som uppgiften kräver?
- Kontrolleras parametrarna av koden, med mål, belopp, mottagare och adresser mot en tillåten lista?
- Finns det tak för antal anrop och kostnad?
- Kan modellen välja ett mål som koden inte har prövat?

## ASI03 Identity and Privilege Abuse

Agenten använder en identitet eller behörighet som är bredare än uppgiften, eller ärver en persons rättigheter där den inte borde.

Pröva:
- Har agenten en egen identitet, eller lånar den en persons?
- Är nycklarna avgränsade och helst kortlivade?
- Vad ger en token faktiskt tillgång till, jämfört med vad verktyget använder?
- Prövas behörigheten igen där datan finns (till exempel RLS), inte bara i agentens kod?

NIST NCCoE:s linje är att befintliga identitetsstandarder ska användas, som OAuth och avgränsade, kortlivade nycklar, och ingen egen identitetsstack (`nccoe-agent-identity`).

## ASI04 Agentic Supply Chain Vulnerabilities

Något agenten vilar på kan vara komprometterat: modelleverantör, MCP-servrar, skills, paket eller andra agenter.

Pröva:
- Vilka MCP-servrar och skills används? Är de lästa före installation, och är versionerna låsta?
- Varifrån kommer paketen? Finns det beroendebevakning?
- Vilken modelleverantör används, och i vilken region?

## ASI05 Unexpected Code Execution (RCE)

Modellen får kod körd, genom ett verktyg som kör skript, en tolk eller indata som tolkas som kommandon.

Pröva:
- Kan modellen köra kod eller kommandon? I vilken sandlåda, och med vilken nätåtkomst och vilka hemligheter i miljön?
- Kan opålitlig text hamna i ett kommando, en fråga mot databasen eller en mall som tolkas?

## ASI06 Memory & Context Poisoning

Opålitlig text sparas i minne, historik eller kunskapsbas och påverkar senare körningar eller andra agenter.

Pröva:
- Sparas text som bygger på opålitlig indata? Var läses den igen, och av vem?
- Behandlas den som opålitlig även då, så att smittan följer texten?
- Kan sparat innehåll granskas, märkas och tas bort?

## ASI07 Insecure Inter-Agent Communication

Meddelanden mellan agenter, eller mellan agent och klient, saknar autentisering, integritet eller avgränsning.

Pröva:
- Är meddelanden autentiserade, till exempel med OAuth eller signerade agentkort i A2A?
- Prövas avsändarens behörighet för varje meddelande?
- Vad lämnar ut till en extern klient, och vet agenten vilken sorts klient det är?

## ASI08 Cascading Failures

Ett fel, en lurad modell eller ett felaktigt förslag i en del förs vidare till andra delar.

Pröva:
- Vilka andra delar läser agentens utdata?
- Finns det en grind mellan delarna, så att ett förslag väntar på en människa innan det blir underlag för nästa?
- Kan en del pausas utan att resten går sönder?
- Finns det tak som stoppar en loop?

## ASI09 Human-Agent Trust Exploitation

Människors förtroende för agenten utnyttjas. En övertygande sammanfattning får någon att godkänna något, eller så klickar man igenom godkännanden av vana.

Pröva:
- Visar godkännandet rådata (mottagare, innehåll, mål) eller modellens sammanfattning?
- Är godkännandena få nog att granskas på riktigt?
- Syns källorna, så att ett råd går att pröva?
- Är agentens utdata märkt som maskinens?

## ASI10 Rogue Agents

En agent agerar utanför sitt uppdrag, efter en kompromettering eller på egen hand, och ser ändå legitim ut.

Pröva:
- Finns det ett nödstopp, och loggas allt agenten gör under sin egen identitet?
- Finns det tak för steg, kostnad och tid?
- Övervakas beteendet mot kontraktet, till exempel andelen godtagna förslag?
- Börjar agenten i skugga och befordras på uppmätt underlag?
