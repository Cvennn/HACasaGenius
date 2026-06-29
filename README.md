# Swegon CASA Genius — Home Assistant -integraatio

Home Assistant custom component Swegon CASA Genius -ilmanvaihtokoneelle.
Lukee ja ohjaa konetta Modbus RTU:n (RS485) yli. ~121 entiteettiä:
lämpötilat, ilmavirrat, käyttötila, hälytykset, asetukset.

> **Tämä on testiversio.** Asennus tehdään käsin (ei vielä HACS-kaupasta).

---

## Vaatimukset

Ennen kuin aloitat, tarvitset:

- **Swegon CASA Genius** -kone, ohjainkortti **SCB 4.2**, ohjelmisto **SW 4.0 tai uudempi**
  (testattu mallilla W5 500W A, firmware 4.3.800)
- **RS485-USB-adapteri** kytkettynä koneen Modbus-väylään ja Home Assistant -palvelimeen
  (esim. CH341-pohjainen adapteri näkyy yleensä nimellä `/dev/ttyUSB0`)
- Home Assistant, jossa pääsy custom_components-kansioon (esim. Studio Code Server,
  Samba tai File Editor)

Ilman fyysistä laitetta ja toimivaa RS485-kytkentää integraatio ei yhdistä mihinkään.

---

## Asennus

1. Pura saamasi paketti (`swegon_genius_jako.tar.gz`). Sieltä löytyy kansio `swegon_genius`.

2. Kopioi koko `swegon_genius`-kansio Home Assistantin kansioon:

   ```
   /config/custom_components/swegon_genius/
   ```

   Jos `custom_components`-kansiota ei ole, luo se ensin.

   Jos purat paketin suoraan palvelimella terminaalissa:

   ```
   cd /config/custom_components
   tar -xzf /polku/swegon_genius_jako.tar.gz
   ```

3. Käynnistä Home Assistant uudelleen:

   ```
   ha core restart
   ```

---

## Käyttöönotto

1. **Asetukset → Laitteet ja palvelut → Lisää integraatio**
2. Hae **"Swegon CASA Genius"**
3. Syötä yhteysasetukset. Oletukset sopivat useimmille:

   | Asetus | Oletus | Huom |
   |--------|--------|------|
   | Sarjaportti | `/dev/ttyUSB0` | adapterin laitepolku |
   | Slave-osoite | `1` | koneen Modbus-osoite (1–247) |
   | Baud rate | `38400` | |
   | Stop bits | `1` | |
   | Pariteetti | `N` | |

4. Tallenna. Jos yhteys onnistuu, entiteetit ilmestyvät laitteen alle.

---

## Mitä paketti sisältää — ja mitä EI

**Mukana:** itse integraatio (entiteetit ja ohjaukset) sekä käännökset
viidelle kielelle (fi/en/sv/nb/da).

**EI mukana:**
- Dashboard / käyttöliittymäkortit — rakennat omasi tai et
- Hyötysuhde-template (LTO-%) — se on erillinen `configuration.yaml`-määrittely
- Puhallinnopeuksien PIN-suojaus — dashboard-ominaisuus, ei integraation osa

Saat siis pelkät entiteetit. Niiden saaminen näkyväksi dashboardille on oma työnsä.

---

## Entiteettien nimet ja kielet

Entiteettien nimet kääntyvät **järjestelmän kielen** mukaan
(Asetukset → Kodin tiedot → Kieli), EI käyttäjäprofiilin kielen. Tämä on
Home Assistantin toimintatapa. Entity ID:t pysyvät kielestä riippumatta samoina.

Huom: entity ID:t generoituvat sinun laitteesi nimestä, joten ne ovat eri kuin
muilla. Valmista dashboardia ei voi suoraan kopioida toiselta käyttäjältä.

---

## Vianetsintä

**"Yhteys epäonnistui — tarkista kaapeli, slave-osoite ja sarjaportti"**

- Tarkista adapteri? Terminaalissa: `ls -l /dev/ttyUSB*`
  Jos mitään ei näy, adapteri ei ole kytketty tai ajuria ei tunnistettu.
- Onko sarjaportti oikea? Joillakin se on `/dev/ttyUSB1` tai `/dev/ttyACM0`.
- Onko slave-osoite oikea? Tarkista koneen ohjauspaneelista Modbus-asetukset.
- Onko baudrate sama kuin koneessa? Oletus 38400, mutta voi olla 9600 tai 19200.
- Onko väyläkaapeli A/B oikein päin? Jos epävarma, kokeile vaihtaa A↔B.

**Entiteetit jäävät "unavailable"**

- Tarkista että adapteri ja kaapeli pysyvät kytkettyinä.
- Katso lokit: Asetukset → Järjestelmä → Lokit, hae "swegon".

---

## Palaute

Tämä on testiversio. Kerro mikä toimii, mikä ei, ja millä koneella/firmwarella
testasit — se auttaa viimeistelyssä.
