# Banc seize LED — prototype D, USB et 3,3 V

Ce banc permet de vérifier les huit voies logiques avec deux registres
et des LED d'indication. Aucun fil pilote, radiateur, photorelais, module
secteur ou alimentation secteur ouverte ne doit y être raccordé.

Le firmware V0.2 installé reste inchangé. Le firmware de banc est préparé,
validé et compilé, mais **pas flashé ni testé physiquement**.

## Documents et composants

- [Schéma électrique SVG](heating_controller_logic_bench.svg).
- [Projet KiCad](heating_controller_logic_bench.kicad_pro).
- [Point d'entrée ESPHome](../heating_controller_logic_bench.yaml).
- [Générateur du schéma](generate_heating_bench.py).

![Banc USB à seize LED](heating_controller_logic_bench.svg)

| Quantité | Composant proposé | Repères |
| --- | --- | --- |
| 1 | ESP32-H2-DevKitM-1 existante, alimentation USB uniquement | Carte de commande |
| 2 | TI SN74AHC595N, boîtier traversant PDIP-16, sous 3,3 V | U1, U2 |
| 16 | LED d'indication adaptées à une faible intensité ; stock multicolore utilisable | D1 à D16 |
| 16 | Résistance 2,2 kΩ, 1 %, 0,125 W ou plus | R1 à R16 |
| 1 | Résistance 1 kΩ, 1 %, 0,125 W ou plus | R17 |
| 4 | Résistance 10 kΩ, 1 %, 0,125 W ou plus | R18 à R21 |
| 2 | Condensateur céramique 100 nF, tension nominale ≥6,3 V | C1, C2 |
| 1 | Condensateur électrolytique radial 10 µF, stock 35 V ou 50 V utilisable | C3 |
| 1 | Interrupteur SPST, fermé pour inhiber | S1 |
| Selon montage | Plaque d'essai, fils et supports DIP-16 | Connexions courtes |

C3 est polarisé : borne + au 3V3, borne − au GND. Choisir le 35 V si son
encombrement convient ; le 50 V convient également. Les 100 nF restent
des céramiques non polarisées. Le schéma indique la polarité de C3.

### Stock déclaré et adaptation possible

- Dix-sept LED après complément du stock : 4 rouges 5 mm, 4 vertes 5 mm,
  6 jaunes 5 mm et 3 jaunes 3 mm.
- Toutes les résistances nécessaires, deux céramiques 100 nF, électrolytiques
  10 µF 35/50 V, interrupteur, breadboard et fils disponibles.
- SN74LVC244AN disponibles, mais aucun registre 595.

Les [SN74LVC244A](https://www.ti.com/lit/ds/symlink/sn74lvc244a.pdf) sont
des buffers parallèles, sans registre à décalage ni verrou de mémorisation.
Ils ne remplacent pas les deux 595 du schéma ou du firmware préparé.
Leur utilisation demanderait un autre montage et une autre interface GPIO.

Le stock permet maintenant de monter **les huit paires (16 LED)**,
avec une LED jaune 5 mm de rechange. Aucune sortie n'a besoin d'être omise.

Répartition possible : rouge/vert sur FP1, FP2, FP3 et FP5 ; jaune 5 mm /
jaune 3 mm sur FP6, FP7 et FP8 ; deux jaunes 5 mm sur FP4/réserve.
Garder le repérage +/− par étiquette.
Conserver 2,2 kΩ pour commencer ; la luminosité peut varier avec la couleur.
Les références exactes des LED ne sont pas connues et les courants n'ont
pas été mesurés.

Le montage série prévu reste en attente de deux registres compatibles,
de préférence les SN74AHC595N indiqués ci-dessous. Aucun remplacement
du 595 par le 244 n'est validé.

Référence des registres : [TI SN74AHC595](https://www.ti.com/lit/ds/symlink/sn74ahc595.pdf).
Ne pas substituer un 74HCT595 alimenté en 5 V sur la base du seul numéro
595. Les niveaux logiques et l'alimentation de ce schéma sont 3,3 V.

Les LED sont directement alimentées par les sorties via leurs résistances.
Même en supposant une chute LED nulle, 3,6 V et une résistance à −1 %,
le courant reste inférieur à 1,66 mA par sortie, soit 13,3 mA pour huit
sorties. Ces calculs sont des budgets conservateurs de banc ; les valeurs
réelles dépendent des LED et seront relevées à la mise en service.

Le banc utilise des LED d'indication à faible courant : il ne reproduit
pas la charge des LED de photorelais 5 V de l'étude B.

## Interface de la DevKit

Le connecteur JH1 est celui du banc. Les repères J1/J3 dans la dernière
colonne désignent les connecteurs de la DevKit, selon le
[guide Espressif](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32h2/esp32-h2-devkitm-1/user_guide.html).

| JH1 du banc | Signal | Broche DevKit proposée |
| --- | --- | --- |
| 1 | +3V3 | J1-1, 3V3 |
| 2 | GND_TBT | Une broche GND, par exemple J1-13 |
| 3 | DATA | GPIO0, J1-3 |
| 4 | CLOCK | GPIO1, J1-4 |
| 5 | LATCH | GPIO22, J3-9 |
| 6 | BENCH_OE_N | GPIO10, J3-4 |

Vérifier le repérage de la carte et l'orientation des DIP avant raccordement.
Registres : broche 16 à 3V3, broche 8 à GND, broche 10 à 3V3 ; broches
11 et 12 communes pour CLOCK/LATCH. La broche 9 de U1 va à la broche 14
de U2 ; la broche 9 de U2 reste libre. Les détails du schéma font foi.
Placer chaque 100 nF près de son registre, entre VCC et GND.

R17 sépare GPIO10 du nœud OE_N. R18 tire OE_N à 3V3 au repos. Lorsque
S1 est fermé, OE_N est forcé haut et toutes les sorties sont inhibées,
même si GPIO10 demande leur activation ; R17 limite alors le courant.
L'état de S1 n'est pas lu par le firmware.

**GPIO10 n'est pas ARM sur ce banc.** Il commande directement OE_N avec
la polarité opposée à l'ARM de l'étude C. Ce câblage et ce firmware ne
doivent donc pas être branchés sur la future carte d'inhibition C.

## Comportement du firmware de banc

Le fichier racine `heating_controller_logic_bench.yaml` réutilise les
packages de la V0.2. Son nom réseau est `heating-controller-bench` et
son nom convivial « Banc LED chauffage ». Il conserve les secrets locaux
API et Thread, sans en créer de nouveaux.

- Les six modes initiaux sont Arrêt, sans restauration.
- Le banc démarre désactivé : le mot `0x5555` est envoyé, mais OE_N reste haut.
- L'interrupteur Home Assistant « Activer le banc LED » autorise ensuite
  les sorties, si S1 est ouvert. Il revient désactivé après redémarrage.
- Chaque mot est envoyé bit 15 en premier, avec une seule impulsion LATCH
  après les seize bits ; aucun état intermédiaire n'est présenté aux LED.
- Les enveloppes sont échantillonnées toutes les 50 ms. Les trois appareils
  Séjour cuisine partagent la même phase de cycle.
- « Mot envoyé aux registres » affiche une commande, pas une mesure.
- Le début de l'OTA désactive le banc ; un échec OTA ne le réactive pas.
- Le shutdown logiciel désactive aussi les sorties. Une panne logicielle
  peut toutefois laisser un ancien mot actif : S1 est alors l'inhibition locale.

Cette variante emploie un transfert GPIO simple et testé plutôt que seize
écritures successives via des sorties individuelles du composant ESPHome :
elle permet de conserver une seule impulsion LATCH par mot. Elle ne
comporte pas encore le watchdog ni les superviseurs matériels de l'étude C.

## Montage et mise en service du banc

1. Garder la carte débranchée pendant le montage. Assembler le schéma
    basse tension et vérifier les rails, le sens des circuits et des LED.
2. Fermer S1 pour inhiber les sorties. Vérifier l'absence de liaison entre
    les rails d'alimentation avant de brancher le câble USB.
3. Avec les sorties inhibées, contrôler l'alimentation 3,3 V des registres.
    Ne pas ajouter une alimentation externe simultanée à l'USB de la DevKit.
4. Valider et compiler la configuration, puis identifier le port USB réel :

```sh
esphome config heating_controller_logic_bench.yaml
esphome compile heating_controller_logic_bench.yaml
ls -l /dev/serial/by-id/
```

Après montage et vérifications, remplacer `PORT_USB_REEL` par le port de
la carte et installer ce firmware de banc par USB :

```sh
esphome upload heating_controller_logic_bench.yaml --device PORT_USB_REEL
esphome logs heating_controller_logic_bench.yaml --device PORT_USB_REEL
```

L'identité annoncée change temporairement ; Home Assistant doit joindre
`heating-controller-bench.local` pour cette session de banc. La configuration
V0.2 reste disponible dans `heating_controller.yaml` pour le retour USB.

## Essais à réaliser une fois le montage prêt

| Essai | Résultat attendu |
| --- | --- |
| Démarrage avec S1 fermé | Aucune LED allumée, activation HA désactivée |
| Ouvrir S1, activation HA toujours désactivée | Aucune LED allumée |
| Activer le banc, modes initiaux Arrêt | Une LED positive sur chaque paire, mot `0x5555` |
| Tous les modes Confort | Toutes les LED éteintes, mot `0x0000` |
| Tous les modes Éco | Seize LED allumées, mot `0xFFFF` |
| Tous les modes Hors-gel | LED négatives seules, mot `0xAAAA` |
| Changer une zone | Seules ses paires changent ; Séjour cuisine agit sur FP1/FP2/FP3 |
| Confort −1 °C, puis −2 °C | Les deux LED de la paire s'allument 3 s ou 7 s par cycle de 300 s, à la résolution du banc |
| Fermer S1 pendant un mode actif | Toutes les LED s'éteignent ; la commande HA peut rester activée |
| Désactiver l'activation HA, puis ouvrir S1 | Les LED restent éteintes |
| Redémarrer la carte | Modes Arrêt, activation HA désactivée ; aucun rallumage automatique |
| Début d'une mise à jour OTA | Banc désactivé ; réactivation explicite requise |

Ces résultats restent à observer physiquement. La lecture de l'état HA ne
prouve pas le niveau réel des sorties. Le banc ne qualifie pas les charges
fil pilote, les photorelais, les surtensions ou l'isolation secteur.

## Vérifications déjà effectuées

- Configuration et compilation : ESPHome 2026.10.1, ESP-IDF 5.5.6, réussite.
- RAM : 38,7 % ; partition applicative : 42,1 %.
- Tests C++ : mapping des huit paires, mots extrêmes, ordre des seize bits
  et impulsion unique de verrouillage, réussite.
- ERC KiCad : zéro erreur et zéro avertissement. Contrôle des quarante nets
  utiles : alimentation, cascade, polarités LED et inhibition, réussite.
- SVG exporté et inspecté visuellement. Aucun flash ni essai physique du banc.

Reproduire les contrôles locaux :

```sh
g++ -std=c++17 -Wall -Wextra -Werror tests/heating_bench_test.cpp -o /tmp/heating-bench-test
/tmp/heating-bench-test
python -B schematics/generate_heating_bench.py
kicad-cli sch erc --exit-code-violations --output /tmp/heating-bench-erc.rpt schematics/heating_controller_logic_bench.kicad_sch
kicad-cli sch export netlist --output /tmp/heating-bench.net schematics/heating_controller_logic_bench.kicad_sch
python -B tests/check_heating_bench_netlist.py /tmp/heating-bench.net
```
