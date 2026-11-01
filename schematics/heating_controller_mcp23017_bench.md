# Banc LED avec MCP23017 — essais en cours

Variante sur `heating/v0.3-mcp23017-bench`, USB et 3,3 V uniquement.
Cette variante est câblée et flashée par USB ; les premiers essais physiques
sont confirmés ci-dessous. L'étude d'inhibition externe reste
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

Ajouter également **100 nF céramique entre RESET_N (18) et GND (10)**,
au plus près du MCP, pour le filtrage testé ci-dessous. Ce second condensateur
ne remplace pas le découplage entre VDD et VSS.

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
réactivé explicitement. Ces comportements sont confirmés sur breadboard.

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

## Résultats physiques confirmés par l'utilisateur

- Flash USB réussi avec ESPHome 2026.10.1 ; démarrage et relâchement de S1
  avec les huit LED éteintes, banc désactivé.
- RESET_N mesuré à 0 V banc désactivé. Banc activé, mesure au Metrix MX2B
  sur calibre continu 5 V : un peu moins de 3 V, sans valeur plus précise.
  La marge au seuil haut n'est donc pas quantifiée.
- Le contact de la pointe sur RESET_N déclenche une désactivation avec défaut,
  y compris sur un point déporté. Pointes placées avant activation, le banc
  s'active et reste actif pendant la mesure. La cause de cette sensibilité
  reste à établir ; aucun diagnostic précis du transitoire n'a été enregistré.
- S1 : extinction à l'appui, maintien éteint après relâchement avec défaut actif,
  puis réactivation volontaire possible.
- Port A : quatre rouges seules en Arrêt ; trois premières paires éteintes
  en Confort, deux couleurs en Éco, vertes seules en Hors-gel pour Séjour
  cuisine. Couloir réserve sur Confort éteint uniquement la quatrième rouge
  lorsque les trois premières paires sont en Hors-gel. Retour des deux zones
  sur Arrêt : quatre rouges seules. Désactivation : toutes éteintes.
- Après déplacement des LED hors tension vers B et remise sous tension :
  toutes éteintes. Activation avec six zones sur Arrêt : quatre rouges seules.
  Sèche-serviettes Confort, Chambre 1 Éco, Chambre 2 Hors-gel, Chambre 3 Arrêt :
  paires respectivement éteinte, deux couleurs, verte seule et rouge seule.

- Redémarrage demandé depuis Home Assistant, banc activé avec des modes
  différents sur B : après reconnexion, toutes les LED restent éteintes,
  le banc est désactivé, les six sélecteurs sont sur Arrêt et le défaut est inactif.
- Sur B, Sèche-serviettes en Confort −1 : les deux LED de la première paire
  s'allument environ 3 secondes puis s'éteignent. En Confort −2 : environ
  7 secondes puis extinction. Les trois autres paires gardent leur rouge seule.
  Durées observées par l'utilisateur, sans mesure instrumentée ni observation
  de la répétition après 300 secondes.

- OTA chiffrée du même firmware réussie : transfert 125,96 secondes, mise à
  jour 126,54 secondes au total. Départ avec Sèche-serviettes en Éco sur B,
  banc activé et S1 relâché. L'utilisateur confirme l'extinction au début du
  transfert, le maintien éteint, la reconnexion Home Assistant, le banc
  désactivé, les six modes sur Arrêt et le défaut inactif après redémarrage.

- Sur B, Sèche-serviettes en Confort −1 : une deuxième impulsion d'environ
  3 secondes est observée vers 5 minutes après le changement de mode,
  sans nouvelle commande. Les trois autres rouges restent allumées.

- Sur B, Sèche-serviettes en Confort −2 : l'utilisateur confirme deux
  impulsions d'environ 7 secondes espacées de 5 minutes. Cette observation
  complète le test de répétition, sans mesure instrumentée de précision.

- Perte I²C provoquée, banc activé et Sèche-serviettes en Éco : retrait du
  seul fil SDA entre GPIO0 et la broche 13. L'utilisateur confirme l'extinction
  de toutes les LED, la désactivation du banc et le défaut actif. Après
  reconnexion de SDA, les LED restent éteintes, le banc désactivé et le défaut
  actif. Une activation volontaire efface le défaut et rétablit les deux
  couleurs sur la première paire et les rouges seules sur les trois autres.

- Test de blocage volontaire : capture USB à 18:37:05,180 du message de
  blocage de la boucle, puis déclenchement `task_wdt` à 18:37:09,529 avec
  `loopTask (CPU 0)` non alimentée, abandon et `Rebooting...` à 18:37:10,052.
  Ces horodatages de réception USB donnent environ 4,35 secondes jusqu'au
  diagnostic watchdog ; ce n'est pas une mesure instrumentée du délai matériel.
  La ligne ROM suivante indique `rst:0xc (SW_CPU)` : le log watchdog et
  l'abandon précédents établissent ici la cause, pas ce code ROM seul.
  L'utilisateur confirme l'extinction des LED, leur maintien éteint et la
  reconnexion Home Assistant. Les états détaillés après reset et la valeur
  du diagnostic de cause du reset n'ont pas été relevés séparément.
- Après le test watchdog : firmware normal revalidé, recompilé et réinstallé
  par USB avec succès, pour retirer le bouton d'injection de faute. L'utilisateur
  confirme après restauration : banc désactivé, six modes sur Arrêt, défaut
  inactif et toutes les LED éteintes.

Les essais fonctionnels listés ci-dessus sont confirmés pour ce banc LED.
La sensibilité au contact de la pointe sur RESET_N n'est plus reproduite
sur une dizaine d'essais avec le filtre 100 nF. L'origine du transitoire et la
marge électrique statique restent à établir. Les validations du banc 595 ne sont pas
transférées automatiquement à ce montage.

## Diagnostic de la sensibilité de RESET_N — en cours

Le firmware normal expose **Détail du défaut MCP23017** et journalise le
premier échec avant de maintenir RESET_N bas. Le diagnostic est conservé
jusqu'à une activation réussie ou un redémarrage :

- `NONE` : aucun défaut mémorisé.
- `I2C READ/WRITE reg=...` : transaction échouée, sans valeur de registre
  exploitable. Cela ne distingue pas à lui seul un reset d'une perturbation du bus.
- `REGISTER reg=... expected=... actual=...` : lectures réussies, mais
  configuration ou registres de sortie incohérents. Pour 0x00, le mot regroupe
  IODIRA en octet bas et IODIRB en octet haut ; 0x14 regroupe OLATA et OLATB.
  Une direction lue à 0xFFFF au lieu de 0x0000 est compatible avec un retour
  aux valeurs de reset, sans prouver à elle seule la cause électrique.

Les lectures I²C et leur ordre, les délais, les seuils matériels et le câblage
ne sont pas modifiés pour cette instrumentation. Les tests hôtes vérifient
le détail pour chaque transaction échouée, le contenu lu avant inhibition,
la conservation du diagnostic et son effacement après activation réussie.

Pour reproduire : banc activé avec un état statique, S1 relâché, garder le
cordon noir au GND puis appliquer uniquement la pointe rouge au point RESET_N
déporté, multimètre inchangé en continu 5 V. Relever le détail du défaut avant
toute réactivation, ainsi que le maintien ou non de la connexion Home Assistant.
Comparer ensuite avec le branchement des pointes avant activation déjà réussi.
Ne pas ajouter de filtrage avant d'avoir relevé ces observations.

Premiers résultats avec le diagnostic détaillé : au contact de la pointe
sur RESET_N, `REGISTER reg=0x00 expected=0x0000 actual=0xFFFF` est relevé
dans Home Assistant et dans les logs USB. Aucun redémarrage de l'ESP32
n'est enregistré à cet instant. Après réactivation, la mesure sur le rail
3,3 V donne 3,3 V et ne désactive pas le banc. Cela oriente vers une
perturbation locale de RESET ; la forme et l'origine du transitoire ne sont
pas établies par ces seules observations.

Filtre installé hors tension : 100 nF céramique entre RESET_N et GND, au plus
près des broches 18 et 10, en conservant le découplage de VDD.
Avec 1 kΩ série et 10 kΩ vers GND, la constante de temps
approximative lorsque GPIO10 commande le niveau est de 91 µs. Les pauses
de 1 ms de la séquence d'activation sont conservées. En cas de GPIO relâché,
la décharge par 10 kΩ possède une constante de temps de 1 ms : le filtrage
ajoute donc aussi un délai à l'inhibition. Le condensateur ne relève pas la
tension haute statique.

Résultats confirmés avec le filtre :

- Une dizaine de contacts de la pointe sur RESET_N, sans désactivation du banc.
- S1 : extinction à l'appui, maintien éteint après relâchement, banc désactivé
  et défaut actif.
- Redémarrage demandé depuis Home Assistant après réactivation : toutes les
  LED restent éteintes après reconnexion, banc désactivé, six modes sur Arrêt
  et défaut inactif.

- Test watchdog répété avec le filtre : message de blocage à 19:03:32,150,
  déclenchement `task_wdt` pour `loopTask` à 19:03:37,073, puis redémarrage
  à 19:03:37,565 dans la capture USB. L'utilisateur confirme l'extinction
  des LED, leur maintien éteint et la reconnexion Home Assistant. Intervalle
  observé dans les logs d'environ 4,92 secondes avant le diagnostic watchdog,
  sans mesure instrumentée de la transition physique de RESET_N.

Ces résultats renforcent l'hypothèse d'un transitoire sur RESET_N, sans en
identifier l'origine ni mesurer sa forme. Le filtre passe les essais de
contact de pointe, de S1, de redémarrage commandé et de reset watchdog.
Après ce second test watchdog, le firmware normal avec diagnostic détaillé
est revalidé, recompilé et réinstallé par USB avec succès. L'utilisateur
confirme après cette dernière restauration : toutes les LED éteintes,
banc désactivé, six modes sur Arrêt et défaut inactif.

## Essai du watchdog interne — procédure et firmware temporaire

Le point d'entrée temporaire `heating_controller_mcp23017_watchdog_test.yaml`
inclut le banc normal et conserve son identité réseau et ses clés. Il ajoute
un bouton diagnostic **TEST Bloquer la boucle principale** et un diagnostic
**TEST Cause du dernier reset**. Le firmware normal ne possède pas ces entités.

Le bouton exige un banc activé. Il attend deux secondes, puis vérifie encore
que le banc est activé et que la tâche courante est abonnée au watchdog.
Le test suspend ensuite indéfiniment la boucle ESPHome avec `vTaskDelay`,
sans nourrir le watchdog, sans modifier les sorties et sans demander un
redémarrage logiciel. Les interruptions et l'ordonnanceur FreeRTOS restent
actifs. Ce test couvre ce blocage de boucle, pas toutes les pannes possibles.

La compilation exige le watchdog de tâche actif, initialisé, fatal et réglé
sur cinq secondes. La configuration de référence possède déjà ces réglages ;
le firmware de test ne les modifie pas. Aucun déclenchement automatique au boot.
Après redémarrage, le banc reste désactivé selon les mêmes actions de démarrage.

Procédure pour les LED USB uniquement :

1. Valider et compiler le point d'entrée de test, puis installer ce firmware
    sur le contrôleur identifié. Ne pas lancer le test pendant une OTA.
2. Vérifier le banc désactivé après installation, S1 relâché. Sur le port B,
    régler Sèche-serviettes sur Éco et laisser les autres zones sur Arrêt.
    Activer le banc : première paire avec deux couleurs, autres rouges seules.
3. Ouvrir une capture des logs USB pour conserver le message de blocage,
    le diagnostic du watchdog et le démarrage suivant. Aucun débogueur OpenOCD.
4. Appuyer une seule fois sur le bouton TEST. Les LED peuvent conserver leur
    état pendant le blocage ; attendre le déclenchement après environ cinq
    secondes à partir du message de blocage, hors délai initial de deux secondes
    et temps de redémarrage. Observer leur extinction au reset et leur maintien
    éteint ensuite. Ne pas appuyer sur S1, couper l'USB ni demander un redémarrage
    pendant cette observation : cela ne vérifierait pas le chemin watchdog.
5. Après reconnexion, relever la cause du reset (TASK_WDT attendue, à recouper
    avec les logs), vérifier les six modes sur Arrêt, banc désactivé et défaut
    MCP inactif. Noter les durées observées et toute anomalie. Si le redémarrage
    automatique n'arrive pas, le test est en échec ; couper l'USB pour récupérer.
6. Recompiler puis réinstaller `heating_controller_mcp23017_bench.yaml` après
    l'essai pour retirer l'injection de faute et vérifier le retour désactivé.
    Les deux variantes partagent le répertoire de build : toujours recompiler
    la variante voulue avant son téléversement.

Commandes de préparation :

```sh
esphome config heating_controller_mcp23017_watchdog_test.yaml
esphome compile heating_controller_mcp23017_watchdog_test.yaml
```

Source : [watchdogs ESP-IDF pour ESP32-H2](https://docs.espressif.com/projects/esp-idf/en/v5.5/esp32h2/api-reference/system/wdts.html).

Références : [fiche technique Microchip, brochage et registres](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP23017-MCP23S17-16-Bit-IO-Expander-with-Serial-Interface-DS20001952.pdf),
[transport I²C ESPHome](https://esphome.io/components/i2c_device/).
