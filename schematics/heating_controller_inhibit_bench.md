# Prochain banc : inhibition mémorisée, étude TBT

Date : 1er novembre 2026. Proposition de composants et protocole à détailler.
Ce document ne demande aucune modification du câblage ou du firmware installé.
Le [banc quatre paires E](heating_controller_logic_bench.md) reste la référence
testée ; ses sorties sont laissées désactivées. Alimentation USB/3,3 V uniquement.

## Objectif du prochain montage

Retirer l'autorisation des deux registres si l'activité logicielle s'arrête,
si le 3,3 V devient insuffisant ou si un défaut est injecté manuellement.
Après disparition du défaut, maintenir les sorties inhibées jusqu'à une
nouvelle demande explicite d'armement. Le réseau Thread peut rester absent
sans provoquer de défaut si la boucle locale continue normalement.

Le modèle de la [définition C](heating_controller_v03_logic.md) reste applicable :

```text
Défaut : HEALTH_N = 0 → effacement asynchrone de Q
Armement : nouveau front montant ARM, défaut absent → Q = 1
OE_N = NON(Q ET ARM ET HEALTH_N)
```

Un retour automatique du watchdog au repos ne crée pas de front ARM.
Il ne doit donc pas réautoriser un ancien mot présent dans les registres.
Le signal du superviseur commande la logique d'inhibition ; il n'est pas
prévu de le raccorder au reset du H2 pour ce banc.

## Candidats pour une réalisation sur breadboard

| Quantité | Candidat | Rôle | Point pratique |
| --- | --- | --- | --- |
| 1 | SN74HC74N, PDIP-14 | Mémoire d'armement, effacement asynchrone | Traversant ; seconde bascule inutilisée à fixer à des niveaux définis |
| 1 | SN74HC10N, PDIP-14 | NAND trois entrées vers OE_N | Traversant ; entrées inutilisées à fixer, sorties inutilisées libres |
| 1 | TPS3828-33DBVR | Supervision du 3,3 V et watchdog, sortie à drain ouvert | SOT-23-5, nécessite un adaptateur ou module correctement documenté |
| Au moins 3 | Condensateurs céramique 100 nF supplémentaires | Découplage local de ces circuits | Les deux condensateurs existants restent près des 595 |
| À définir | Résistances de rappel, points de test et éventuellement mise en forme | Niveaux définis et fronts compatibles | Valeurs à dimensionner au schéma |

Les HC74 et HC10 fonctionnent de 2 à 6 V selon les fiches
[TI HC74](https://www.ti.com/lit/ds/symlink/sn74hc74.pdf) et
[TI HC10](https://www.ti.com/lit/ds/symlink/sn74hc10.pdf).
Ils proposent ici une variante traversante des petites portes LVC de l'étude C.
Les SN74LVC244AN disponibles ne fournissent pas ces fonctions de mémorisation
ou de NAND. Les SN74HC595N du banc LED sont conservés.

La [fiche TI TPS382x](https://www.ti.com/lit/ds/symlink/tps3823.pdf)
distingue le TPS3828 à drain ouvert des variantes à sortie push-pull.
Son watchdog est nominalement de 1,6 s ; la table donne 0,9 à 2,5 s dans
ses conditions de spécification. Ne pas réutiliser la borne 1,36 s du TPS3431.
Le mode désactivé sur WDI flottant exige un rappel externe dimensionné pour
maintenir une valeur définie quand le GPIO est déconnecté ou en haute impédance.
Un rappel ne doit pas être choisi sans tenir compte du courant d'entrée WDI.

Le TPS3431 de l'étude C est en VSON-8, moins commode sur breadboard.
Le TPS3828 est une alternative pour ce prototype, pas un remplacement validé
de toute l'étude C. Un adaptateur SOT-23 est plus accessible, mais demande
encore une soudure ou un module déjà assemblé.

## Points à résoudre avant un schéma de montage

1. Confirmer les circuits disponibles et la possibilité de souder le SOT-23.
2. Vérifier les bornes du seuil de la variante -33, l'hystérésis et la marge
    de l'alimentation réelle ; ne pas prendre le seul seuil nominal comme preuve.
3. Dimensionner les rappels ARM, WDI et HEALTH_N. Vérifier les temps de montée
    du drain ouvert avec la capacité de la breadboard et les limites des entrées HC.
    Prévoir une mise en forme à hystérésis si nécessaire ; ne pas ajouter un gros
    condensateur directement sur une entrée HC pour temporiser l'armement.
4. Définir le traitement des entrées inutilisées, le découplage et les points
    de mesure ; vérifier le comportement pendant la montée et la chute du 3,3 V.
5. Préparer une configuration ESPHome distincte et la valider avant raccordement.
    ARM, WDI et les retours de diagnostic devront avoir des niveaux définis au reset.

Le GPIO10 du banc actuel commande directement OE_N, actif bas. Le futur ARM
sera actif haut : les deux interfaces ne sont pas interchangeables. Le poussoir
actuel relie OE_N au 3,3 V ; un futur poussoir de défaut vers GND aura un autre
point de raccordement et ne doit pas être déplacé avant schéma validé.

Le signal WDI devra dépendre du calcul et du transfert des commandes, sans
générateur PWM autonome. La proposition de basculement toutes les 100 ms
donne un front descendant toutes les 200 ms ; l'ordonnancement réel et les
marges devront être vérifiés. Après défaut, continuer les diagnostics sans
boucle de réarmement automatique ; vérifier les conditions avant tout front ARM.

## Protocole à prévoir

| Essai | Résultat recherché |
| --- | --- |
| Mise sous tension, sans armement | LED éteintes |
| Défaut absent, commande valide, armement explicite | Affichage du mot demandé |
| WDI figé bas, puis essai séparé figé haut | Inhibition dans les limites du watchdog et de la logique |
| WDI débranché au niveau prévu | Rappel effectif, watchdog non désactivé par entrée flottante |
| Reprise de WDI, ARM laissé haut | Aucune réactivation automatique |
| Défaut manuel puis relâchement | Mémoire de défaut conservée |
| Nouvel armement, défaut réellement absent | Réactivation après contrôles |
| Redémarrage et OTA | ARM bas et sorties inhibées |
| Baisse contrôlée du seul rail TBT | Inhibition puis réarmement explicite après stabilisation |

Ce premier montage ne supervisera pas un rail 5 V de photorelais. Il ne couvre
ni leurs courants, ni les protections secteur, ni toutes les défaillances internes.
Les essais de défaut se feront avec les LED, sans aucun fil pilote raccordé.

Les huit tests du modèle idéal se lancent avec
`python -B tests/test_heating_design_checks.py`. Ils ne valident pas les fronts,
les seuils analogiques, le câblage ou les délais des composants proposés.
