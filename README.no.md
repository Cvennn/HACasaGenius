**Språk:** [English](README.md) | [Suomi](README.fi.md) | [Svenska](README.sv.md) | [Norsk](README.no.md) | [Dansk](README.da.md)

# Swegon CASA Genius — Home Assistant-integrasjon

Home Assistant custom component for Swegon CASA Genius-ventilasjonsaggregatet.
Leser og styrer aggregatet via Modbus RTU (RS485). ~121 entiteter:
temperaturer, luftmengder, driftsmodus, alarmer, innstillinger.

Integrasjonen fungerer også med nyere Swegon CASA Smart-enheter, som bruker samme Genius-register.

> **Dette er en testversjon.** Installasjonen gjøres manuelt (ikke tilgjengelig via HACS ennå).

---

## Krav

Før du starter trenger du:

- Et **Swegon CASA Genius**-aggregat med styrekort **SCB 4.2** og programvare **SW 4.0 eller nyere**
  (testet på en W5 500W A-enhet, firmware 4.3.800)
- En **RS485-USB-adapter** koblet til aggregatets Modbus-buss og til Home Assistant-serveren
  (f.eks. en CH341-basert adapter, vises vanligvis som `/dev/ttyUSB0`)
- Home Assistant med tilgang til mappen `custom_components` (f.eks. via Studio Code Server,
  Samba eller File Editor)

Uten den fysiske enheten og en fungerende RS485-tilkobling kobler ikke integrasjonen til noe.

Alternative RS485-omformere:
- https://raspberrypi.dk/en/product/industrial-usb-to-rs485-bidirectional-converter/
- https://www.digikey.fi/en/products/detail/olimex-ltd/USB-RS485/21661988
- https://www.amazon.com/DSD-TECH-SH-U10-Converter-Compatible/dp/B078X5H8H7

---

## Tilkobling

CASA Genius-ventilasjonsaggregatet har et innebygd Modbus RTU-grensesnitt som hentes ut via en SEC- eller SEM-tilkoblingsmodul. Modulen kobles til kontakten "SEC/SEM" på aggregatets hovedkort med den medfølgende 2-meterskabelen.

To pinner på SEC/SEM-modulens koblingsplint brukes til Modbus-tilkoblingen: pinne 1 er Modbus A og pinne 2 er Modbus B. Disse kobles til en RS485-USB-omformer (f.eks. en Waveshare USB to RS485 (B)) slik at omformerens A+ kobles til Modbus A, og B- kobles til Modbus B. Bokstavmatchingen A↔A, B↔B er en vanlig konvensjon innen RS485, så dette er et trygt utgangspunkt — hvis tilkoblingen ikke fungerer med en gang, kan A- og B-lederne byttes om uten fare for skade.

| Fra | Til |
|---|---|
| Ventilasjonsaggregatet, **SEC/SEM**-porten på hovedkortet | SEC/SEM-modulens RJ-kontakt, med den medfølgende kabelen (2 m) |
| RS485-USB-omformerens **A+** | SEC/SEM-modulens plint 1 (Modbus A) |
| RS485-USB-omformerens **B-** | SEC/SEM-modulens plint 2 (Modbus B) |
| RS485-USB-omformerens GND (valgfritt) | SEC/SEM-modulens plint 8 (GND) |
| RS485-USB-omformerens USB-plugg | USB-porten på Home Assistant-enheten |

RS485-USB-omformeren kobles til USB-porten på enheten som kjører Home Assistant, der den vanligvis vises som `/dev/ttyUSB0`. Dette samsvarer også med integrasjonens standardinnstilling for seriell port.

1. Ventilasjonsaggregatets tilkoblingspanel
2. Swegon SEC-tilkoblingsmodul

![screenshot](SEC_cable.png)

*Merk: en GND-tilkobling brukes ikke i denne koblingen. Hvis busstrekket blir lengre eller du opplever forstyrrelser, kan en felles jording mellom SEC/SEM-modulens pinne 8 og omformerens GND-kontakt forbedre påliteligheten.*

### Manualer

Installasjonsveiledning for CASA SEM: https://www.swegon.com/globalassets/digizuite/10062-en-casasem_installation_en.pdf

Installasjonsveiledning for CASA SEC: https://www.swegon.com/globalassets/digizuite/10060-en-casasec_installation_en.pdf

## Tilkobling med SEMIO-modul

SEMIO er Swegons innkapslede Modbus-modul. Den inneholder samme SEM-kort som DIN-skinneversjonen, så den har samme formål som SEC/SEM-modulen ovenfor. Forskjellen er at tilkoblingene sitter på merkede skrueklemmer inne i boksen, ikke på den 8-polede pluggen med nummererte pinner. **Bruk A/B-merkingen som er trykt på kortet, ikke pinnenummer.**

**Før du starter:** slå av ventilasjonsaggregatet. Elektrisk installasjon må utføres i henhold til nasjonale bestemmelser. IO3-reléets klemmer kan føre opptil 250 V / 6 A, så hold Modbus-kablingen unna dem.

### Tilkoblinger

| Fra | Til |
|---|---|
| Ventilasjonsaggregatet, **SEC/SEM**-porten på hovedkortet | SEMIOs "CASA unit"-kontakt, med den medfølgende kabelen (2 m, maks 3 m) |
| RS485-USB-omformerens **A+** | SEMIO Modbus **A** ("in"-paret) |
| RS485-USB-omformerens **B-** | SEMIO Modbus **B** ("in"-paret) |
| RS485-USB-omformerens USB-plugg | USB-porten på Home Assistant-enheten |

Bruk **"in"**-klemmene. "Out"-paret brukes bare for å føre bussen videre til en annen SEM/SEMIO-modul.

![screenshot](SEMIO_wiring.png)

### Jumpere

- **JP1 (bussavslutning):** Swegons regel er å installere den i den siste enheten i Modbus-kjeden. Når én enkelt SEMIO er koblet direkte til omformeren, er den den siste enheten, så sett JP1 i posisjonen *Bus terminated*. Hvis tilkoblingen er ustabil på en lang kabel, kontroller avslutningen i begge ender.
- **JP2:** la stå i standardposisjon. Den må bare flyttes til IO3 hvis du bruker IO3-klemmen som digital eller analog inngang, noe denne integrasjonen ikke trenger.

### Kabelskjerm

Hvis du bruker skjermet kabel, jord skjermen i **bare ett punkt**, på omformerens/Home Assistants side ("masteren"). De to skjermklemmene på SEMIO-kortet er internt koblet til hverandre.

### Modbus-innstillinger på aggregatet

SEMIO bruker aggregatets Modbus-innstillinger. På et **Genius**-kontrollpanel åpner du menyen *Idriftsetting / (1234) / Modbus*. Fabrikkverdiene samsvarer med integrasjonens standardverdier:

| Innstilling | Verdi |
|---|---|
| Adresse | 1 |
| Baudrate | 38400 |
| Stoppbits | 1 |
| Paritet | ingen |

Hvis du har endret noen av disse, angi de samme verdiene når du legger til integrasjonen.

### Manual

Installasjonsveiledning for CASA SEMIO: https://www.swegon.com/globalassets/digizuite/10063-en-semio_installation_en.pdf

## Installasjon

1. Pakk ut pakken du fikk (`swegon_genius_jako.tar.gz`). Der finner du en mappe kalt `swegon_genius`.

2. Kopier hele mappen `swegon_genius` til Home Assistants mappe:

   ```
   /config/custom_components/swegon_genius/
   ```

   Hvis mappen `custom_components` ikke finnes, opprett den først.

   Hvis du pakker ut pakken direkte på serveren i en terminal:

   ```
   cd /config/custom_components
   tar -xzf /sti/swegon_genius_jako.tar.gz
   ```

3. Start Home Assistant på nytt:

   ```
   ha core restart
   ```

---

## Avinstallering

1. Fjern integrasjonen fra Home Assistant:
  - Åpne "Innstillinger → Enheter og tjenester"
  - Velg "Swegon CASA Genius"
  - Velg **Slett** (fra trepunktsmenyen)

2. Slett integrasjonens mappe:
   ```
   /config/custom_components/swegon_genius/
   ```

3. Start Home Assistant på nytt

Integrasjonen, dens entiteter og alle lagrede innstillinger fjernes.
> **Merk:** Dashbord, automatiseringer, skript, hjelpere og maler som refererer til integrasjonens entiteter **fjernes ikke automatisk**.
> Hvis de refererer til slettede entiteter, vil Home Assistant vise dem som *unavailable* til referansene fjernes eller oppdateres.

---

## Oppsett

1. **Innstillinger → Enheter og tjenester → Legg til integrasjon**
2. Søk etter **"Swegon CASA Genius"**
3. Angi tilkoblingsinnstillingene. Standardverdiene passer de fleste:

   | Innstilling | Standard | Merk |
   |--------|--------|------|
   | Seriell port | `/dev/ttyUSB0` | adapterens enhetssti |
   | Slaveadresse | `1` | aggregatets Modbus-adresse (1–247) |
   | Baudrate | `38400` | |
   | Stoppbits | `1` | |
   | Paritet | `N` | |

4. Lagre. Hvis tilkoblingen lykkes, vises entitetene under enheten.

---

## Hva pakken inneholder — og hva den IKKE inneholder

**Inkludert:**
- Selve integrasjonen (entiteter og styringer) samt oversettelser for fem språk (fi/en/sv/nb/da).
- Enkelt dashbord på engelsk.

**IKKE inkludert:**
- Virkningsgrad-mal (LTO %) — det er en egen definisjon i `configuration.yaml`
- PIN-beskyttelse for viftehastigheter — en dashbord-funksjon, ikke en del av integrasjonen

Du får altså hovedsakelig entitetene. Bortsett fra det enkle eksempeldashbordet er det ditt eget arbeid å gjøre dem synlige.

---

## Entitetsnavn, ID-er og språk

Entitetsnavn følger **systemspråket** (Innstillinger → System → Generelt → Språk), IKKE brukerprofilens språk. Slik fungerer Home Assistant.

Entitets-**ID-er** opprettes én gang, når en entitet legges til første gang. De bygges av enhetens navn og entitetens navn **på systemspråket i det øyeblikket**. For eksempel er driftsmodusvelgeren `select.swegon_casa_genius_dev_ttyusb0_operating_mode` på engelsk og `select.swegon_casa_genius_dev_ttyusb0_kayttotila` på finsk.

Dette betyr at:
- ID-er er forskjellige mellom systemer installert med ulike språk.
- Hvis du bytter språk i etterkant, endres bare de viste navnene. Eksisterende ID-er endres ikke.
- ID-en inneholder også enhetens navn, som inkluderer den serielle porten (f.eks. `dev_ttyusb0`). Hvis du bruker en annen port, er starten av ID-en annerledes.
- Et dashbord, en automatisering eller et skript fra en annen bruker kan ikke brukes som det er. Kontroller ID-ene og erstatt dem med dine egne.

**Finne dine egne ID-er:** Utviklerverktøy → Tilstander, søk etter "swegon". Eller Innstillinger → Enheter og tjenester → Swegon CASA Genius → velg en entitet → tannhjulikonet. Du kan også endre en ID derfra.

**Eksempeldashbord:** dashbordet i mappen `dashboards/` er laget for engelsk systemspråk og porten `/dev/ttyUSB0`. I andre tilfeller erstatter du ID-ene med dine egne. Hvis språket ditt er engelsk og bare porten er annerledes, er det nok å søke og erstatte det felles prefikset `swegon_casa_genius_dev_ttyusb0` med ditt eget. Med andre språk er også slutten av hver ID annerledes, så kontroller hver ID.

![screenshot](SwegonDashboard.png)

---

## Feilsøking

**"Tilkobling mislyktes — sjekk kabelen, slaveadressen og den serielle porten"**

- Sjekk adapteren? I en terminal: `ls -l /dev/ttyUSB*`
  Hvis ingenting vises, er adapteren ikke tilkoblet eller driveren ble ikke gjenkjent.
- Er den serielle porten riktig? På enkelte systemer er den `/dev/ttyUSB1` eller `/dev/ttyACM0`.
- Er slaveadressen riktig? Sjekk Modbus-innstillingene på aggregatets kontrollpanel.
- Er baudraten den samme som aggregatets? Standard er 38400, men den kan være 9600 eller 19200.
- Er bussens A/B riktig vei? Hvis du er usikker, prøv å bytte A↔B.

**Entiteter forblir "unavailable"**

- Sjekk at adapteren og kabelen forblir tilkoblet.
- Se på loggene: Innstillinger → System → Logger, søk etter "swegon".

---

## Tilbakemelding

Dette er en testversjon. Fortell meg hva som fungerer, hva som ikke gjør det, og hvilket
aggregat/firmware du testet med — det hjelper med ferdigstillelsen.
