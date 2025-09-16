# Home Assistant Add-on: ELTEK Smartpack SNMP to MQTT Bridge

\[!\[GitHub Release\]\[releases-shield\]\]\[releases\]
\[!\[License\]\[license-shield\]\]\[license\]

Integrálja az ELTEK Smartpack egyenirányítókat a Home Assistant rendszerbe, kifejezetten LiFePO4 akkumulátorok napelemes rendszerekben történő töltésének vezérlésére és monitorozására.

Ez az add-on egy "híd"-ként működik az ELTEK Smartpack eszközöd és a Home Assistant között. Rendszeres időközönként kiolvassa a szenzorok értékeit SNMP-n keresztül, és publikálja őket az MQTT brókerre. A Home Assistant MQTT Auto-Discovery funkciójának köszönhetően az eszköz és a hozzá tartozó összes entitás automatikusan megjelenik a felületen.

<!-- Helyettesítsd egy saját képernyőképpel -->

## Főbb Jellemzők

* **Automatikus Eszközfelismerés:** Az add-on az MQTT Auto-Discovery segítségével automatikusan létrehozza az ELTEK Smartpack eszközt és az összes entitást a Home Assistant rendszerben.

* **LiFePO4 Töltésvezérlés:** Lehetővé teszi a LiFePO4 akkumulátorokhoz szükséges töltési paraméterek (float/boost feszültség, áramkorlát) precíz beállítását.

* **Kritikus Értékek Monitorozása:** Kiolvassa a legfontosabb értékeket, mint például akkumulátor feszültség és áram.

* **Rugalmas Konfiguráció:** Támogatja a hivatalos Home Assistant MQTT brókert és külső (pl. EMQX) brókerek manuális beállítását is.

* **Könnyen Bővíthető:** Az új szenzorok hozzáadása egyszerűen, a Python szkriptben található `ENTITIES` szótár szerkesztésével lehetséges.

## Integrált Entitások

Az add-on a következő, LiFePO4 akkumulátorok napelemes rendszerekben történő töltéséhez elengedhetetlen entitásokat hozza létre:

#### Szenzorok

* **Akkumulátor Feszültség:** Az akkumulátor aktuális feszültsége (V).

* **Akkumulátor Áram:** A töltési (+) vagy kisütési (-) áram erőssége (A).

* **Töltési Státusz:** A töltési folyamat aktuális állapota (pl. Float, Boost).

* **Aktuális Töltési Limit:** A beállított töltési áramkorlát (A).

* **Aktuális Float Feszültség:** A beállított csepptöltési feszültség (V).

* **Aktuális Boost Feszültség:** A beállított emelt szintű töltési feszültség (V).

#### Vezérlők

* **Boost Töltés Kapcsoló:** Az emelt szintű töltés manuális be- és kikapcsolása.

* **Töltési Áram Limit Kapcsoló:** Az áramkorlát funkció aktiválása vagy deaktiválása.

* **Float Feszültség Beállítás:** A csepptöltési feszültség beállítása csúszkával.

* **Boost Feszültség Beállítás:** Az emelt szintű töltési feszültség beállítása csúszkával.

* **Áram Limit Beállítás:** A maximális töltési áram beállítása csúszkával.

## Előfeltételek

1. **Home Assistant:** Működő Home Assistant telepítés, ami képes add-onokat futtatni (pl. Home Assistant OS vagy Supervised).

2. **MQTT Bróker:** Egy működő MQTT bróker. Ez lehet a hivatalos **Mosquitto broker** add-on, vagy bármilyen más, a hálózaton elérhető bróker (pl. EMQX).

3. **SNMP Hozzáférés:** Az ELTEK Smartpack eszközön engedélyezett SNMP hozzáférés (általában v2c), valamint az olvasáshoz (`public`) és íráshoz (`private`) használt community stringek ismerete.

## Telepítés

1. **Repository Hozzáadása:**

    * Navigálj a Home Assistant felületén a **Beállítások > Bővítmények > Bővítménybolt** menüpontba.

    * Kattints a jobb felső sarokban lévő három pontra, és válaszd a **Tárolóhelyek** opciót.

    * Másold be a GitHub repository URL-jét (`https://github.com/a-te-felhasznaloneved/ha-eltek-smartpack-mqtt`) a mezőbe, és kattints a **Hozzáadás** gombra.

2. **Add-on Telepítése:**

    * A tárolóhely hozzáadása után a boltban meg fog jelenni egy új "ELTEK Smartpack SNMP" kártya.

    * Kattints rá, majd válaszd a **Telepítés** gombot.

## Konfiguráció

A telepítés után az **Információ** fülről navigálj a **Konfiguráció** fülre, és töltsd ki a szükséges mezőket.

| Beállítás | Leírás | Kötelező | 
 | ----- | ----- | ----- | 
| `snmp_host` | Az ELTEK Smartpack eszköz IP címe vagy hosztneve. | Igen | 
| `snmp_port` | Az eszközön futó SNMP szolgáltatás portja. (Alapértékelmezett: 161) | Nem | 
| `community_public` | Az SNMP olvasáshoz használt community string. (Alapértékelmezett: `public`) | Nem | 
| `community_private` | Az SNMP íráshoz használt community string. (Alapértékelmezett: `private`) | Nem | 
| `scan_interval` | A szenzorok frissítési gyakorisága másodpercben. (Alapértékelmezett: 15) | Nem | 
| `mqtt_host` | **Csak külső bróker esetén!** Az MQTT bróker IP címe. Ha üresen hagyod, az add-on a hivatalos Mosquitto add-ont keresi. | Nem | 
| `mqtt_port` | **Csak külső bróker esetén!** Az MQTT bróker portja. | Nem | 
| `mqtt_user` | **Csak külső bróker esetén!** Az MQTT felhasználónév. | Nem | 
| `mqtt_password` | **Csak külső bróker esetén!** Az MQTT jelszó. | Nem | 

A beállítások mentése után indítsd el az add-ont az **Információ** fülön.

## Használat

Az add-on sikeres elindulása és az MQTT brókerhez való csatlakozás után automatikusan létrehoz egy új eszközt a Home Assistant rendszerben.

* Navigálj a **Beállítások > Eszközök & Szolgáltatások > MQTT** menüpontba.

* Az eszközök listájában meg kell jelennie egy **ELTEK Smartpack** nevű eszköznek.

* Rákattintva láthatod az összes hozzá tartozó szenzort, kapcsolót és beállítót, amiket már szabadon használhatsz a dashboardjaidon és automatizációidban.

## Licenc

Ez a projekt az [MIT Licenc](https://www.google.com/search?q=./LICENSE) alatt érhető el.

Készítette: \[A Te Neved\]
```
