# Banc LED avec MCP23017 — préparation

Variante sur `heating/v0.3-mcp23017-bench`, USB et 3,3 V uniquement.
Le montage avec deux 595 reste la référence physiquement testée. Cette
variante n'a pas été câblée ni flashée. L'étude d'inhibition externe reste
une étude distincte, sans composants supplémentaires imposés à ce banc.

Le plan ci-dessous concerne le **MCP23017 en boîtier DIP 28 broches**.
« Nu » ne précise pas le boîtier : vérifier le marquage et les deux rangées
de pattes au pas de 2,54 mm avant de suivre ces numéros. Un boîtier CMS
nécessite un adaptateur. Repérer l'encoche ; compter les broches en vue
de dessus, dans le sens antihoraire à partir de la broche 1.

## Connexions à préparer hors tension

Les deux 595 doivent être déconnectés des GPIO avant de réutiliser ceux-ci.
Tous les GND sont communs ; aucune connexion aux fils pilotes.

| Signal MCP23017 | Broche DIP | Connexion |
| --- | --- | --- |
| VDD | 9 | 3,3 V |
| VSS | 10 | GND |
| SCL | 12 | GPIO1, avec 4,7 kΩ vers 3,3 V |
| SDA | 13 | GPIO0, avec 4,7 kΩ vers 3,3 V |
| A0, A1, A2 | 15, 16, 17 | GND : adresse 0x20 |
| RESET_N | 18 | GPIO10 à travers 1 kΩ ; 10 kΩ de RESET_N vers GND |
| INTA, INTB, NC | 20, 19, 11, 14 | Non connectés |

Placer 100 nF au plus près de VDD/VSS et conserver le 10 µF sur le rail
3,3 V, avec sa borne négative vers GND. Les condensateurs existants
peuvent être réutilisés après déconnexion des 595.

S1 est un poussoir normalement ouvert **entre RESET_N et GND**.
Son ancien raccordement à 3,3 V pour OE_N ne convient pas ici.
La résistance série de 1 kΩ limite le courant quand S1 est enfoncé et
que GPIO10 commande un niveau haut.

## Quatre paires de LED

Conserver les vertes à gauche et les rouges à droite, chacune avec sa
résistance série de 2,2 kΩ. Sortie → résistance → anode ; cathode → GND.
Le tableau donne rouge/positive puis verte/négative, indépendamment de
leur disposition physique.

| Paire | Port A : broches rouge / verte | Port B : broches rouge / verte |
| --- | --- | --- |
| 1 | GPA0/1 : 21 / 22 | GPB0/1 : 1 / 2 |
| 2 | GPA2/3 : 23 / 24 | GPB2/3 : 3 / 4 |
| 3 | GPA4/5 : 25 / 26 | GPB4/5 : 5 / 6 |
| 4 | GPA6/7 : 27 / 28 | GPB6/7 : 7 / 8 |

Utiliser un seul port à la fois avec les quatre paires disponibles.
A reprend les canaux U1 : trois sorties Séjour cuisine, puis Couloir réserve.
B reprend U2 : Sèche-serviettes, Chambre 1, Chambre 2, Chambre 3.

## Firmware et limites

Point d'entrée : `heating_controller_mcp23017_bench.yaml` ; nom réseau
`heating-controller-mcp-bench`. Il conserve les six zones simulées.
Le transport ESPHome `i2c_device` permet de gérer explicitement le reset,
le préchargement des registres et les erreurs de communication.

Chaque activation remet le MCP à zéro, précharge les niveaux, puis configure
les sorties. Banc désactivé, RESET_N est maintenu bas. Une erreur I²C ou une
incohérence des registres contrôlés désactive le banc et impose une nouvelle
activation explicite. Le diagnostic conserve le défaut jusqu'à une activation
réussie. Le mot demandé reste une consigne, même lorsque le banc est désactivé.

Les lectures vérifient la configuration et les registres de sortie, pas la
tension des LED. Les ports A et B sont écrits successivement ; il n'y a pas
de verrouillage simultané des seize sorties comme avec les deux 595.

S1 réinitialise le MCP : le relâcher ne reconfigure pas ses sorties. Le contrôle
périodique doit constater la perte de configuration, puis le banc doit être
réactivé explicitement. Ces comportements restent à vérifier sur breadboard.

Le rappel de RESET_N à GND vise l'inhibition lorsque GPIO10 est relâché.
Mesurer RESET_N avant les essais : bas au démarrage et banc désactivé,
haut avec une marge suffisante au-dessus de 0,8 × VDD lorsque le banc est
activé. Avec 3,3 V idéal et le diviseur 1 kΩ/10 kΩ, la valeur attendue est
environ 3,0 V ; la mesure réelle doit confirmer le niveau fourni par l'ESP32.

Le watchdog interne ne coupe pas immédiatement un état figé : les dernières
sorties peuvent persister jusqu'au reset de l'ESP32. Le retour à l'inhibition
lors d'un reset watchdog n'a pas encore été testé physiquement. Ce montage
LED ne qualifie aucun dispositif de sécurité pour un étage secteur.

## Vérifications avant et après installation

```sh
esphome config heating_controller_mcp23017_bench.yaml
esphome compile heating_controller_mcp23017_bench.yaml
g++ -std=c++17 -Wall -Wextra -Werror tests/heating_mcp23017_bench_test.cpp -o /tmp/heating-mcp-bench-test
/tmp/heating-mcp-bench-test
```

Les tests hôtes injectent des erreurs de transport, une écriture partielle,
une configuration incorrecte et un reset du MCP entre deux cycles.
Ils ne remplacent pas les essais électriques.

Après confirmation du boîtier, câblage hors tension et contrôle des tensions,
prévoir un flash USB explicitement demandé. Vérifier ensuite : démarrage
éteint, activation volontaire, modes sur A puis B, S1, désactivation,
redémarrage, OTA et déconnexion I²C. Le banc doit rester désactivé après défaut.
Le test de blocage du programme et du watchdog doit faire l'objet d'un essai
séparé avant toute conclusion sur ce repli.

Références : [fiche technique Microchip, brochage et registres](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-MCP23S17-16-Bit-IO-Expander-with-Serial-Interface-DS20001952.pdf),
[transport I²C ESPHome](https://esphome.io/components/i2c_device/).
