**Sprog:** [English](README.md) | [Suomi](README.fi.md) | [Svenska](README.sv.md) | [Norsk](README.no.md) | [Dansk](README.da.md)

# Swegon CASA Genius — Home Assistant-integration

Home Assistant custom component til Swegon CASA Genius-ventilationsanlægget.
Læser og styrer anlægget via Modbus RTU (RS485). ~121 entiteter:
temperaturer, luftmængder, driftstilstand, alarmer, indstillinger.

> **Dette er en testversion.** Installationen foretages manuelt (endnu ikke tilgængelig via HACS).

---

## Krav

Før du går i gang, skal du bruge:

- Et **Swegon CASA Genius**-anlæg med styrekort **SCB 4.2** og software **SW 4.0 eller nyere**
  (testet på en W5 500W A-enhed, firmware 4.3.800)
- En **RS485-USB-adapter** tilsluttet anlæggets Modbus-bus og Home Assistant-serveren
  (f.eks. en CH341-baseret adapter, vises som regel som `/dev/ttyUSB0`)
- Home Assistant med adgang til mappen `custom_components` (f.eks. via Studio Code Server,
  Samba eller File Editor)

Uden den fysiske enhed og en fungerende RS485-forbindelse opretter integrationen ikke forbindelse til noget.

Alternative RS485-konvertere:
- https://raspberrypi.dk/en/product/industrial-usb-to-rs485-bidirectional-converter/
- https://www.digikey.fi/en/products/detail/olimex-ltd/USB-RS485/21661988
- https://www.amazon.com/DSD-TECH-SH-U10-Converter-Compatible/dp/B078X5H8H7

---

## Tilslutning

CASA Genius-ventilationsanlægget har en indbygget Modbus RTU-grænseflade, som føres ud via et SEC- eller SEM-tilslutningsmodul. Modulet tilsluttes "SEC/SEM"-stikket på anlæggets hovedkort med det medfølgende 2-meters kabel.

To ben på SEC/SEM-modulets klemrække bruges til Modbus-forbindelsen: ben 1 er Modbus A og ben 2 er Modbus B. Disse forbindes til en RS485-USB-konverter (f.eks. en Waveshare USB to RS485 (B)), så konverterens A+ forbindes til Modbus A og B- forbindes til Modbus B. Bogstavmatchningen A↔A, B↔B er en udbredt konvention inden for RS485, så det er et sikkert udgangspunkt — hvis forbindelsen ikke virker med det samme, kan A- og B-lederne byttes om uden risiko for skade.

RS485-USB-konverteren tilsluttes USB-porten på den enhed, der kører Home Assistant, hvor den som regel vises som `/dev/ttyUSB0`. Det svarer også til integrationens standardindstilling for seriel port.

1. Ventilationsanlæggets tilslutningspanel
2. Swegon SEC-tilslutningsmodul

![screenshot](SEC_cable.png)

![screenshot](SEC_SEM_wiring.png)

*Bemærk: der bruges ingen GND-forbindelse i denne tilslutning. Hvis buslængden øges, eller du oplever forstyrrelser, kan en fælles jordforbindelse mellem SEC/SEM-modulets ben 8 og konverterens GND-klemme forbedre pålideligheden.*

## Installation

1. Pak den modtagne pakke ud (`swegon_genius_jako.tar.gz`). Den indeholder en mappe med navnet `swegon_genius`.

2. Kopier hele mappen `swegon_genius` til Home Assistants mappe:

   ```
   /config/custom_components/swegon_genius/
   ```

   Hvis mappen `custom_components` ikke findes, så opret den først.

   Hvis du pakker pakken ud direkte på serveren i en terminal:

   ```
   cd /config/custom_components
   tar -xzf /sti/til/swegon_genius_jako.tar.gz
   ```

3. Genstart Home Assistant:

   ```
   ha core restart
   ```

---

## Fjernelse

1. Fjern integrationen fra Home Assistant:
  - Åbn "Indstillinger → Enheder og tjenester"
  - Vælg "Swegon CASA Genius"
  - Vælg **Slet** (fra menuen med tre prikker)

2. Slet integrationens mappe:
   ```
   /config/custom_components/swegon_genius/
   ```

3. Genstart Home Assistant

Integrationen, dens entiteter og alle gemte indstillinger fjernes.
> **Bemærk:** Dashboards, automatiseringer, scripts, hjælpere og skabeloner, der refererer til integrationens entiteter, **fjernes ikke automatisk**.
> Hvis de refererer til slettede entiteter, viser Home Assistant dem som *unavailable*, indtil referencerne fjernes eller opdateres.

---

## Opsætning

1. **Indstillinger → Enheder og tjenester → Tilføj integration**
2. Søg efter **"Swegon CASA Genius"**
3. Angiv forbindelsesindstillingerne. Standardværdierne passer til de fleste:

   | Indstilling | Standard | Bemærkning |
   |--------|--------|------|
   | Seriel port | `/dev/ttyUSB0` | adapterens enhedssti |
   | Slave-adresse | `1` | anlæggets Modbus-adresse (1–247) |
   | Baudrate | `38400` | |
   | Stopbit | `1` | |
   | Paritet | `N` | |

4. Gem. Hvis forbindelsen lykkes, vises entiteterne under enheden.

---

## Hvad pakken indeholder — og hvad den ikke indeholder

**Inkluderet:** selve integrationen (entiteter og styringer) samt oversættelser
til fem sprog (fi/en/sv/nb/da).

**Ikke inkluderet:**
- Dashboard / brugerfladekort — der følger kun et simpelt eksempel-dashboard (på engelsk) med i `dashboards/`; byg dit eget, hvis du vil have mere
- Virkningsgrad-skabelon (LTO %) — det er en separat definition i `configuration.yaml`
- PIN-beskyttelse af blæserhastigheder — en dashboard-funktion, ikke en del af integrationen

Du får altså hovedsageligt entiteterne. Bortset fra det simple eksempel-dashboard er det dit eget arbejde at gøre dem synlige.

---

## Entitetsnavne, ID'er og sprog

Entitetsnavne følger **systemsproget** (Indstillinger → System → Generelt → Sprog), IKKE brugerprofilens sprog. Sådan fungerer Home Assistant.

Entitets-**ID'er** oprettes én gang, når en entitet tilføjes første gang. De opbygges af enhedens navn og entitetens navn **på systemsproget i det øjeblik**. For eksempel er driftstilstandsvælgeren `select.swegon_casa_genius_dev_ttyusb0_operating_mode` på engelsk og `select.swegon_casa_genius_dev_ttyusb0_kayttotila` på finsk.

Det betyder, at:
- ID'er er forskellige mellem systemer, der er installeret med forskellige sprog.
- Hvis du skifter sprog senere, ændres kun de viste navne. Eksisterende ID'er ændres ikke.
- ID'et indeholder også enhedens navn, som inkluderer den serielle port (f.eks. `dev_ttyusb0`). Hvis du bruger en anden port, er starten af ID'et anderledes.
- Et dashboard, en automatisering eller et script fra en anden bruger kan ikke bruges, som det er. Kontrollér ID'erne, og erstat dem med dine egne.

**Find dine egne ID'er:** Udviklerværktøjer → Tilstande, søg efter "swegon". Eller Indstillinger → Enheder og tjenester → Swegon CASA Genius → vælg en entitet → tandhjulsikonet. Du kan også ændre et ID derfra.

**Eksempel-dashboard:** dashboardet i mappen `dashboards/` er lavet til engelsk systemsprog og porten `/dev/ttyUSB0`. I andre opsætninger skal du erstatte ID'erne med dine egne. Hvis dit sprog er engelsk, og kun porten er anderledes, er det nok at søge og erstatte det fælles præfiks `swegon_casa_genius_dev_ttyusb0` med dit eget. Med andre sprog er slutningen af hvert ID også anderledes, så kontrollér hvert ID.

---

## Fejlfinding

**"Forbindelsen mislykkedes — kontrollér kablet, slave-adressen og den serielle port"**

- Tjek adapteren? I en terminal: `ls -l /dev/ttyUSB*`
  Hvis intet vises, er adapteren ikke tilsluttet, eller driveren blev ikke genkendt.
- Er den serielle port korrekt? På nogle systemer er den `/dev/ttyUSB1` eller `/dev/ttyACM0`.
- Er slave-adressen korrekt? Tjek Modbus-indstillingerne på anlæggets betjeningspanel.
- Er baudraten den samme som anlæggets? Standard er 38400, men den kan være 9600 eller 19200.
- Vender busledningens A/B den rigtige vej? Hvis du er i tvivl, så prøv at bytte A↔B.

**Entiteter forbliver "unavailable"**

- Kontrollér, at adapteren og kablet forbliver tilsluttet.
- Tjek loggene: Indstillinger → System → Logs, søg efter "swegon".

---

## Feedback

Dette er en testversion. Fortæl, hvad der virker, hvad der ikke gør, og hvilket
anlæg/firmware du har testet med — det hjælper med at gøre den færdig.
