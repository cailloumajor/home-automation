# Contrôleur de chauffage — V0.2

Prototype de connectivité pour ESP32-H2-DevKitM-1 : ESP-IDF, OpenThread
FTD, API native ESPHome chiffrée, OTA chiffrée, uptime et redémarrage.
Alimentation USB uniquement ; aucune sortie fil pilote ni connexion secteur.

## Six zones simulées

Les six sélecteurs sont : Séjour cuisine, Sèche-serviettes, Chambre 1,
Chambre 2, Chambre 3 et Couloir réserve. Ces noms restent provisoires jusqu'à
vérification du regroupement réel des radiateurs. Le package réutilisable
`inc/heating_zone.yaml` définit chaque zone ; `inc/fil_pilote_simulation.h`
calcule les enveloppes logiques indépendantes.

Deux capteurs binaires de diagnostic par zone exposent les alternances
positive et négative simulées. Ils représentent une autorisation logique,
pas une sinusoïde 50 Hz, une tension mesurée ou une commande matérielle.

| Mode | Positive simulée | Négative simulée |
| --- | --- | --- |
| Confort | Non | Non |
| Confort -1 °C | Oui pendant 3 s par cycle de 300 s | Identique |
| Confort -2 °C | Oui pendant 7 s par cycle de 300 s | Identique |
| Éco | Oui | Oui |
| Hors-gel | Non | Oui |
| Arrêt | Oui | Non |

Chaque changement de mode redémarre le cycle de la zone concernée.
Au démarrage, toutes les zones prennent le mode **Arrêt**, sans restauration
depuis la mémoire flash. C'est une politique de simulation, à réexaminer
avant toute réalisation matérielle ; le mode fil pilote Arrêt n'est pas
une coupure électrique.

En cas de perte de Home Assistant ou du réseau Thread, le dernier mode
reste en RAM et les cycles continuent localement. `api.reboot_timeout: 0s`
désactive le redémarrage automatique lié à l'absence de client API.
Une coupure d'alimentation ou un redémarrage ramène toutes les zones à Arrêt.

Tests de la logique temporelle :

```sh
g++ -std=c++17 -Wall -Wextra -Werror tests/fil_pilote_simulation_test.cpp -o /tmp/fil-pilote-simulation-test
/tmp/fil-pilote-simulation-test
```

Ils couvrent les six modes, les limites à 3 s et 7 s, la répétition des
cycles, des phases indépendantes, le débordement du compteur `millis()`
pendant une impulsion et le repli d'un indice invalide sur Arrêt.

Références : [sélecteur template ESPHome](https://esphome.io/components/select/template/)
et [commandes fil pilote Thermor](https://www.thermor.fr/faq/radiateur/utiliser/qu-est-ce-que-le-fil-pilote-d-un-radiateur-electrique).

### Vérification V0.2 sur carte — 31 octobre 2026

- Validation `esphome config heating_controller.yaml` et compilation ESP-IDF
  5.5.6 réussies avec ESPHome 2026.10.1.
- Tests C++ de la logique réussis ; RAM utilisée 38,4 %, partition applicative
  utilisée 41,3 % à la compilation.
- Installation OTA chiffrée réussie en 119,26 s, puis reconnexion API réussie.
- `tests/check_heating_controller_api.py` a vérifié sur la carte : six
  sélecteurs avec les six options attendues, douze états binaires simulés,
  six modes de chaque zone, indépendance des zones, fin des impulsions
  de 3 et 7 s, redémarrage depuis six zones en Éco puis retour de toutes
  les zones à Arrêt avec les états simulés correspondants.
- Le test laisse toutes les zones à Arrêt. La déconnexion API observée
  pendant le redémarrage est attendue.
- Les limites exactes des impulsions et la répétition à 300 s sont vérifiées
  par les tests C++. Le test sur carte contrôle les fins d'impulsion avec
  une marge de 0,5 s ; il ne constitue pas une mesure temporelle électrique.
- Redémarrage de Home Assistant testé par l'utilisateur : tous les états
  de l'appareil correspondent à l'attendu après reconnexion. Le maintien
  des modes pendant cette interruption de Home Assistant est confirmé.
- Interruption puis relance du Border Router : test déclaré concluant par
  l'utilisateur selon la procédure proposée (interruption de deux minutes,
  retour du contrôleur, modes conservés et uptime sans remise à zéro).
  Le Border Router est hébergé dans Home Assistant sur Raspberry Pi 4,
  avec un Sonoff Zigbee 3.0 USB Dongle Plus V2 connecté au Raspberry Pi.
  Les états simulés n'ont pas été observés directement pendant la coupure ;
  ce test valide leur état après reconnexion et l'absence de redémarrage.
- Les vérifications V0.2 prévues sont terminées pour le prototype sans
  sorties matérielles. La conception de l'étage fil pilote relève de la V0.3.

Le script API se lance avec le Python de l'environnement ESPHome depuis
la racine du dépôt. Il lit `secrets.yaml` sans afficher la clé, change les
modes simulés et redémarre la carte ; l'utiliser sur ce prototype sans
sorties matérielles uniquement.

## Migration Thread — 31 octobre 2026

Le dataset publié anciennement dans l'historique Git a été remplacé par
un nouveau réseau créé depuis Home Assistant : `ha-thread-98ba` remplace
`ha-thread-780b`. La clé réseau, le PSKc et l'Extended PAN ID ont changé.
Les valeurs privées restent uniquement dans `secrets.yaml`, ignoré par Git.
L'ancien réseau a été supprimé de Home Assistant par l'utilisateur.

Esplinky et le contrôleur ont reçu leur nouveau dataset par USB après
validation et compilation avec ESPHome 2026.10.1. `force_dataset: true`
remplace le dataset conservé en NVS par celui du YAML à chaque démarrage ;
le banc LED hérite de cette option, a été validé et compilé, sans flash.
L'API chiffrée des deux cartes a été vérifiée. Les six zones du contrôleur
étaient à Arrêt après son redémarrage, sans modification de leur logique.
Le diagnostic des mesures Linky manquantes est traité dans une session
distincte ; la connexion Thread d'esplinky fonctionne.

Après la création du réseau, l'annonce mDNS du Border Router était absente.
Un redémarrage de l'application OpenThread Border Router l'a rétablie,
sans nouveau changement de clés. Les identifiants du réseau préféré ont
été synchronisés dans l'application Android avant les réassociations.

| Appareil | Ancien nœud Matter | Nouveau nœud Matter |
| --- | --- | --- |
| GRILLPLATS | 14 | 16 |
| KAJPLATS | 3 | 17 |
| MYGGSPRAY | 4 | 18 |
| TIMMERFLOTTE | 2 | 19 |
| BILRESA | 15 | 20 |

Les identifiants des entités principales ont été repris sur les nouvelles
entités : interrupteur GRILLPLATS, lampe KAJPLATS, occupation et éclairement
MYGGSPRAY, température et humidité TIMMERFLOTTE, événements des deux boutons
BILRESA. Les trois automatisations inspectées conservent leurs références :
« Arrêter le répéteur WiFi », « Démarrer le répéteur WiFi » et « Contrôle lampe ».
Le répéteur n'a pas été actionné par les contrôles. L'utilisateur a confirmé
les événements BILRESA, les mesures TIMMERFLOTTE et le fonctionnement du palier
après réactivation de « Contrôle lampe », précédemment désactivée.

Sauvegardes Home Assistant : `16c32a2c` avant migration, puis `9bf735e7`
avant nettoyage. Les anciens nœuds Matter ont été retirés après vérification
de leur indisponibilité, de la disponibilité des cinq remplaçants et de
l'absence de références aux anciennes entités dans les configurations inspectées.
Home Assistant a été arrêté pour ce retrait, puis relancé : sa version
2026.10.4 supprimerait sinon la fiche partagée avec le nouveau nœud lors
du retrait de l'ancien MYGGSPRAY ou BILRESA. Le retrait des nœuds ne doit
pas être confondu avec le nettoyage des anciennes entités du registre.
Après relance, les cinq nouveaux nœuds sont disponibles et les fiches partagées
préservées. Les 88 anciennes entités et les trois anciennes fiches isolées
ont ensuite été supprimées par l'API administrative Home Assistant, après
un nouveau contrôle des références. Les 88 entités actives et les deux fiches
partagées ont été préservées. Les huit entités principales répondent et
« Contrôle lampe » est activée ; les trois automatisations gardent leurs cibles.
Le jeton créé pour ce nettoyage a été révoqué, son refus confirmé par une
nouvelle tentative d'authentification, puis sa copie locale effacée.

Le renouvellement des clés ne retire pas le dataset de l'historique Git.
L'utilisateur a choisi de conserver cet historique sans assainissement du
dataset désormais compromis et remplacé. Ne pas réutiliser cet ancien dataset,
y compris depuis une sauvegarde ou un ancien firmware. Le retrait des notes
de session de l'historique local est une opération distincte.

## Installation relevée pour préparer la V0.3

Informations fournies par l'utilisateur : les fils pilotes arrivent
individuellement au tableau et ne sont pas raccordés actuellement. Tous
les radiateurs sont compatibles fil pilote ; la prise en charge des six
ordres par chaque modèle reste à vérifier dans les notices.

L'utilisateur confirme une alimentation monophasée et les quatre
disjoncteurs sous le même interrupteur différentiel. Son calibre, sa
sensibilité et son type n'ont pas été relevés.

Les repères C1 à C4 ci-dessous sont documentaires, pas des étiquettes
effectivement relevées au tableau.

| Circuit | Protection annoncée | Appareils | Puissance nominale connue |
| --- | --- | --- | --- |
| C1 | 16 A | Séjour : probablement Sauter Cinto, 2 × 1 500 W à inertie solide | 3 000 W |
| C2 | 16 A | Cuisine : Noirot Karisa 1 000 W ; couloir en réserve | 1 000 W hors réserve |
| C3 | 16 A | SdB : Sauter Santiago 750 W + soufflerie 1 000 W ; chambre 1 : probablement Sauter Madison 1 000 W | 2 750 W, soufflerie comprise |
| C4 | 16 A | Chambres 2 et 3 : probablement Sauter Madison, 1 500 W chacune | 3 000 W |

Total des puissances indiquées : 9 750 W, soufflerie comprise, hors réserve.
Ce total ne décrit ni la consommation instantanée ni une validation du
dimensionnement des circuits. Pour C3, le total de 2 750 W compte les deux
résistances du Santiago et le radiateur de la chambre 1 simultanément.

### Notices et compatibilité des appareils

- Noirot Karisa : la [notice constructeur Karisa programmable](https://medias.noirot.fr/storage/media/shares/Noirot/notice/kfn222-223-233-307-fdaj-karisa-notice-306.pdf)
  décrit les six ordres. La variante exacte de l'appareil reste à identifier.
- Sauter Cinto : la [fiche constructeur diffusée par Mr Bricolage](https://media.mr-bricolage.fr/media/files/AE019261/mode_emploi/fiche-radiateur-cinto-sauter.pdf)
  annonce six ordres. L'identification des radiateurs du séjour est encore
  donnée comme probable par l'utilisateur.
- Sauter Madison : le [portail constructeur](https://www.confort-sauter.com/assistance/espace-de-documentation?gamme_title=Radiateurs&tags=Notice+d%27utilisation)
  répertorie plusieurs générations ; la référence exacte est nécessaire
  pour sélectionner et vérifier la bonne notice. Modèle encore probable.
- Sauter Santiago : la [notice constructeur Santiago Ventilo, copie hébergée](https://manuzoid.fr/manuals/L529R-sauter%20SANTIAGO%20Manuel%20du%20propri%C3%A9taire)
  présente les six ordres fil pilote. Le Turbo avec ventilation se déclenche
  par le bouton local ; le mode 24h auto fonctionne sans ventilateur.
  Aucun ordre de démarrage de la soufflerie par fil pilote n'est documenté
  dans cette notice. Ne pas assimiler Confort à une commande de Turbo.
  Les priorités entre Turbo et ordres externes restent à confirmer sur
  la référence exacte avant de définir les automatismes SdB.

### Zones logiques et voies électriques

Les six zones de la V0.2 restent inchangées à ce stade. La zone logique
« Séjour cuisine » couvre C1 et C2, tandis que le couloir conserve sa
zone de réserve sur C2. Une zone logicielle commune ne justifie pas de
réunir directement les fils pilotes de circuits distincts.

Piste à étudier pour la V0.3 : conserver six zones logiques, avec des voies
électriques distinctes pour séjour et cuisine recevant le même ordre.
Cela donne sept voies potentielles en comptant la réserve, si les deux
radiateurs du séjour partagent une voie validée pour cette utilisation.
Une voie par départ individuel donnerait huit voies avec la réserve.
Le nombre définitif dépendra des notices, des protections et du schéma
d'isolation retenu ; aucun regroupement électrique n'est validé ici.

### Conséquences pour le futur comptage

Une mesure à chaque disjoncteur fournirait quatre totaux de circuits,
sans séparer SdB/chambre 1, chambres 2/3, ou cuisine/future réserve.
Le circuit séjour correspond en revanche aux deux radiateurs du séjour.
Un comptage par zone logique exigera des points de mesure permettant
ces séparations ; le total séjour/cuisine devra agréger les mesures
correspondantes. Il faut vérifier si phases et neutres de chaque départ
sont individuellement accessibles, pas seulement les fils pilotes.

Les puissances nominales et modes fil pilote ne permettent pas de déduire
une mesure réelle d'énergie. L'objectif de puissance active nécessite
une mesure tension/courant appropriée ou un compteur dédié.

### Informations manquantes avant conception matérielle

- Références signalétiques exactes et générations des radiateurs,
  notamment Cinto/Madison dont l'identification reste probable.
- Confirmation des priorités du Santiago entre Turbo et fil pilote.
- Accessibilité des départs phase/neutre et identification des conducteurs.

La V0.3 commencera par un schéma d'architecture avec isolation, alimentation,
protections et sectionnement des commandes, à faire vérifier avant toute
réalisation secteur. Le firmware actuel reste une simulation sans GPIO.

L'[architecture V0.3, révision C](schematics/heating_controller_v03_architecture.md)
propose huit voies indépendantes en quatre modules de deux, six zones
logicielles conservées, seize commandes isolées et une inhibition
matérielle. Elle décrit le repli sur absence de signal (Confort possible),
les états de défaut, les interfaces de mesure et les validations restantes.
Le [module deux voies, étude B](schematics/heating_controller_v03_module.md)
dispose d'un schéma de principe KiCad/SVG et d'un pré-dimensionnement TBT.
Le candidat de commutation est le photorelais MOSFET TLP240JF. L'ERC KiCad
et le contrôle de netlist passent ; les protections secteur, la charge réelle
et l'isolation physique restent à qualifier. Aucun matériel secteur ni
changement du firmware n'a été réalisé pour cette étape.

La [définition logique C](schematics/heating_controller_v03_logic.md)
propose les SN74AHC595, le mapping des seize commandes, six GPIO et une
mémoire de défaut évitant la réactivation automatique après un timeout.
Huit tests du modèle idéal et des calculs passent. L'[analyse des protections](schematics/heating_controller_v03_protection.md)
montre que les hypothèses actuelles ne permettent pas de figer une résistance
série et une coordination des protections secteur. Les mesures ou limites
constructeur des entrées fil pilote restent nécessaires. Aucun résultat
de simulation numérique ne constitue une qualification électrique.

Le [banc quatre paires LED E](schematics/heating_controller_logic_bench.md) dispose
d'un schéma KiCad/SVG, d'une liste de composants et d'une configuration
racine séparée `heating_controller_logic_bench.yaml`. Les quatre paires
rouge/verte et leurs huit résistances se raccordent successivement aux sorties
de U1 (FP1 à FP4), puis U2 (FP5 à FP8), en déplaçant huit fils hors tension.
Les deux registres restent en cascade. Le firmware du banc ne change pas :
son mot de seize bits commande toujours les huit voies, observées en deux passes.
Configuration validée, firmware précédemment compilé ; tests C++ et contrôle
des quarante nets utiles réussis ; ERC sans erreur ni avertissement.
Le banc a été installé par USB le 1er novembre 2026 avec les SN74HC595N
confirmés par l'utilisateur. L'API chiffrée répond : six zones à Arrêt,
activation du banc désactivée, mot `0x5555`. Les quatre paires sur U1 ont
permis de confirmer les modes Arrêt, Confort, Éco et Hors-gel, l'indépendance
Séjour cuisine/Couloir réserve, S1 et les impulsions approximatives de 3 et 7 s.
Les mêmes états fixes sont confirmés sur U2, ainsi que deux motifs indépendants
sur ses quatre voies, S1, la désactivation HA et les impulsions approximatives
de 3 et 7 s sur Sèche-serviettes. Le redémarrage depuis U2 en Éco laisse les
LED éteintes, le banc désactivé et les six zones à Arrêt, mot `0x5555` :
observation utilisateur et contrôle API concordants. L'OTA chiffrée du même
firmware a réussi en 120,30 s depuis un banc activé en Éco ; la reconnexion
API confirme le banc désactivé, six zones à Arrêt et le mot `0x5555`.
L'utilisateur confirme l'extinction des huit LED au début de l'OTA et leur
maintien éteint après redémarrage, S1 relâché. Les essais décrits du banc
LED sont concluants ; la répétition physique à 300 s et les durées instrumentées
ne sont pas vérifiées. Le banc reste désactivé avec six zones à Arrêt.
La V0.2 reste disponible
pour un retour au firmware sans sorties matérielles.
Ce premier banc USB ne comprend pas
le watchdog externe ; GPIO10 y contrôle directement OE_N, contrairement
à son rôle ARM dans l'étude C. Il ne se raccorde à aucun module secteur.

La [prochaine étape TBT](schematics/heating_controller_inhibit_bench.md)
prépare l'inhibition mémorisée : schéma F avec HC74/HC10/HC14 traversants et
TPS3828-33 sur adaptateur, soudure acceptée par l'utilisateur. ERC sans violation,
dix nets contrôlés, dix tests du modèle et des budgets résistifs réussis.
Les broches proposées passent le schéma ESPHome 2026.10.1 ; le firmware ARM/WDI
reste à écrire et à compiler. Les composants sont à acquérir et les niveaux,
fronts et délais à mesurer. Le seuil du TPS3828-33 ne garantit pas l'inhibition
avant la limite basse de 3,0 V du H2 : la supervision d'alimentation reste ouverte.
Le banc LED installé reste désactivé ; aucune modification matérielle n'est
effectuée pour cette nouvelle étude.

## Configuration locale

Le point d'entrée est `heating_controller.yaml`, à la racine du dépôt.
Le fichier partagé `secrets.yaml` est ignoré par Git.

- `api_key_heating_controller` : clé API existante, également utilisée par
  l'OTA chiffrée. Une clé ESPHome doit encoder 32 octets en base64.
- `thread_dataset_tlv` : ajouter le dataset opérationnel actif du réseau
  Thread existant sous forme de chaîne hexadécimale. Ne pas créer un autre
  réseau pour ce prototype, ni publier ce secret.

`inc/auth.yaml` reste inchangé : il utilise un mot de passe OTA, incompatible
avec le mode OTA chiffré choisi ici. Le point d'entrée conserve les conventions
de substitutions du dépôt et configure directement API et OTA.

Le logger utilise l'USB Serial/JTAG natif du H2 ; utiliser le port USB natif
pour ses journaux. L'accès réseau et les mises à jour OTA nécessitent une
route IPv6 fonctionnelle vers le réseau Thread.

## Vérifications effectuées le 31 octobre 2026

- CLI locale : ESPHome 2026.10.1.
- Sources installées : `esp32h2`, ESP-IDF, OpenThread `FTD` et `tlv`,
  logger `USB_SERIAL_JTAG` et OTA `encryption:` sont pris en charge.
- ESP-IDF recommandé par cette version : 5.5.6. La configuration laisse
  ESPHome sélectionner sa version recommandée.
- L'OTA avec `encryption:` vide hérite de la clé API ; aucun mot de passe
  OTA supplémentaire n'est nécessaire.
- `git check-ignore secrets.yaml` confirme l'exclusion du fichier.
- Après ajout local de `thread_dataset_tlv`,
  `esphome config heating_controller.yaml` réussit.
- Compilation sans erreur confirmée par l'utilisateur. Les fichiers
  `firmware.factory.bin`, `firmware.ota.bin` et `firmware.elf` sont présents
  dans `.esphome/build/heating-controller/build/`.
- Premier flash réussi sur `/dev/ttyACM0` avec
  `esphome upload heating_controller.yaml --device /dev/ttyACM0` :
  ESP32-H2 révision 0.1, flash 4 Mo, vérification du hash réussie.
- Journaux USB : `setup() finished successfully!`, activation du dataset
  Thread, puis `SRP client has started`.
- Appareil ajouté dans Home Assistant avec sa clé de chiffrement, confirmé
  par l'utilisateur. Les journaux identifient un client Home Assistant
  2026.10.4 et montrent la disparition de l'avertissement d'attente API.
- Accès IPv6 depuis la machine de développement vérifié avec
  `esphome logs heating_controller.yaml --device heating-controller.local` :
  résolution du nom, connexion et handshake chiffré réussis.
- Test OTA du firmware compilé avec
  `esphome upload heating_controller.yaml --device heating-controller.local` :
  connexion chiffrée établie, puis échec pendant le transfert
  (`receiving chunk result: Unknown error from ESP`). Le journal USB indique
  `Timeout reading 3 bytes` après environ 167 secondes d'opération ; des
  retransmissions TCP ont été observées. La cause exacte reste à diagnostiquer.
  Le firmware initial reste accessible : une nouvelle connexion API chiffrée
  a réussi après cet échec.
- Remontée de l'uptime dans Home Assistant confirmée par l'utilisateur
  (905 secondes observées).
- Redémarrage depuis le bouton Home Assistant confirmé par l'utilisateur :
  la durée de fonctionnement repart à zéro après redémarrage, ce qui valide
  le retour de la connexion et de la remontée des états.
- Deuxième essai OTA avec le même firmware, carte placée par l'utilisateur
  à 20 cm de l'antenne du Border Router : réussite. Durées rapportées par
  ESPHome : préparation 0,07 s, transfert 113,10 s, validation finale 0,38 s,
  total 113,56 s. Connexion OTA chiffrée confirmée.
- Après l'OTA, nouvelle connexion à `heating-controller.local` et handshake
  API chiffré réussis. Aucun changement de configuration n'a été nécessaire.
- Les contrôles de connectivité V0.1 sont validés dans ces conditions de
  proximité. La réussite du deuxième essai suggère une influence possible
  des conditions radio ; elle ne démontre pas la cause du premier échec.
  La fiabilité OTA à l'emplacement final reste à tester.

## Validation et premier flash

Depuis la racine, une fois le secret renseigné :

```sh
esphome version
esphome config heating_controller.yaml
esphome compile heating_controller.yaml
ls -l /dev/serial/by-id/
```

Après réussite de la validation et de la compilation, connecter la carte
par USB uniquement, identifier son port, puis remplacer `PORT_USB_REEL`
ci-dessous par son chemin complet :

```sh
esphome upload heating_controller.yaml --device PORT_USB_REEL
esphome logs heating_controller.yaml --device PORT_USB_REEL
```

Vérifier dans les journaux la connexion au réseau Thread, puis connecter
l'intégration ESPHome de Home Assistant avec la clé API locale. Contrôler
la remontée de l'uptime et le retour de la connexion après redémarrage.
L'absence de découverte automatique nécessite de vérifier le routage IPv6
et la découverte réseau ; elle ne prouve pas un échec d'association Thread.

Tester ensuite l'OTA depuis une machine pouvant joindre l'adresse IPv6
du contrôleur, en remplaçant `IPV6_REELLE` :

```sh
esphome upload heating_controller.yaml --device IPV6_REELLE
```

Références : [OpenThread](https://esphome.io/components/openthread/) et
[OTA ESPHome](https://esphome.io/components/ota/esphome/).
