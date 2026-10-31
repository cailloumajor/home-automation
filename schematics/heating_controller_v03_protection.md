# Protections des sorties fil pilote — analyse C

Cette analyse complète le schéma de principe B. Elle ne valide pas une
résistance, un fusible ou un écrêteur précis pour réalisation secteur.
Le courant d'entrée des modèles installés et leur tolérance aux chutes
de tension restent inconnus.

## Ce qu'une résistance série peut et ne peut pas résoudre

Sous les hypothèses d'une alimentation de commande à 253 V RMS et d'une
résistance limitant seule le courant, une borne conservatrice est :

```text
R_min_effective = sqrt(2) × 253 / I_limite_crête
R_max_effective = chute_admissible / I_normal
```

La première formule ne crédite aucune résistance du photorelais. Elle
borne conservativement la crête d'un court-circuit FP/neutre, mais pas
un transitoire, la température ou tous les défauts possibles.
La seconde suppose qu'on borne le courant normal ; une vraie entrée
redressée/capacitive ne se réduit pas forcément à cette hypothèse.

Les deux contraintes doivent être simultanément compatibles, avec
tolérances, avant même de choisir la puissance et la tenue en tension.

Exemples de sensibilité calculés, **pas des caractéristiques des radiateurs** :

| Courant normal supposé | Limite crête d'étude | Chute autorisée supposée | Intervalle nominal R, ±1 % |
| --- | --- | --- | --- |
| 0,1 mA | 36 mA | 10 V | 10,04 à 99,01 kΩ |
| 0,5 mA | 36 mA | 10 V | 10,04 à 19,80 kΩ |
| 1 mA | 36 mA | 10 V | Aucun : minimum 10,04 kΩ, maximum 9,90 kΩ |
| 5 mA | 90 mA | 10 V | Aucun : minimum 4,02 kΩ, maximum 1,98 kΩ |
| 5 mA | 36 mA | 10 V | Aucun : minimum 10,04 kΩ, maximum 1,98 kΩ |

Les 90 mA de la [fiche TLP240JF](https://toshiba.semicon-storage.com/info/docget.jsp?did=13997&prodName=TLP240JF)
sont une limite absolue de fiche, pas un courant de conception
recommandé. L'exemple 36 mA illustre l'effet du déclassement de 0,9 mA/°C
de 25 à 85 °C donné pour le candidat ; il ne valide pas une utilisation
permanente à cette limite. La limite finale devra être inférieure aux
bornes applicables et inclure les incertitudes.

Conclusion : l'hypothèse antérieure de 5 mA ne permet pas de figer une
simple résistance de protection sous ces contraintes. Cela ne prouve
pas que le photorelais est inutilisable : le courant réel pourrait être
différent, ou une autre protection/topologie pourrait être retenue.

## Énergie de défaut et fusible

Une protection doit aussi supporter ou interrompre l'énergie de défaut.
Par exemple, 253 V RMS appliqués durablement à 10 kΩ produiraient environ
6,4 W en pleine alternance, ou 3,2 W en demi-alternance idéale. Une petite
résistance prévue seulement pour le régime normal ne convient pas à ce
scénario. Ces puissances supposent que le circuit continue à conduire.

Le calibre nominal d'un fusible ne prouve pas qu'il protège un photorelais.
Il faut comparer sa courbe temps/courant et son énergie laissée passer
avec une tenue transitoire utilisable du composant. La valeur de courant
impulsionnel pour une durée donnée ne fournit pas à elle seule une courbe
de coordination complète.

Si la protection protège seulement contre l'incendie en admettant la
destruction du semi-conducteur, il faut l'énoncer et étudier les modes de
défaillance, dont le court-circuit. L'inhibition des LED ne peut alors
pas garantir la disparition d'une tension de commande.

## Surtensions et fuites

Une crête sinusoïdale de 358 V ne démontre pas la tenue d'un composant
600 V dans le tableau. Pour un écrêteur éventuel, vérifier au minimum :

- Tension continue admissible au maximum de l'alimentation secteur.
- Tension maximale de limitation au courant de surtension considéré,
  avec tolérance, température et inductance du routage.
- Énergie, vieillissement, fin de vie et protection thermique associée.
- Coordination entre branches, alimentation et sortie, y compris les
  perturbations provenant du câble fil pilote.

Un réseau RC ou une autre protection peut augmenter le courant au repos
et perturber l'ordre Confort. Les capacités et fuites des deux branches
doivent donc entrer dans les critères de reconnaissance des six ordres.
Les [recommandations Toshiba pour photorelais](https://toshiba-semicon-storage.com/info/TLP3407SRB_application_note_en_20240205_AKX01280.pdf?did=156465&prodName=TLP3407SRB)
expliquent le besoin d'évaluer surintensités, surtensions et composants
de protection ; elles ne remplacent pas le dimensionnement de ce montage.

## Informations nécessaires pour lever ces points

Pour chaque référence réellement installée, obtenir du fabricant ou d'un
rapport d'essai réalisé sur un banc adapté :

| Donnée | Utilité |
| --- | --- |
| Référence et révision de l'appareil | Relier le résultat à une entrée réelle |
| Courants RMS et crête, six ordres | Dimensionner commutateur et limitation |
| Reconnaissance des ordres aux limites de tension | Fixer la chute admissible |
| Courant/tension résiduelle admissible en Confort | Qualifier fuites et protections |
| Transitoires d'entrée et commutations | Évaluer les surtensions locales |
| Conditions thermiques du coffret | Déclasser les composants |

Le protocole de mesure secteur est à établir par une personne compétente
avec un banc et une instrumentation adaptés. Aucune mesure directe au
GPIO, à un analyseur logique USB ou avec la masse d'un oscilloscope
ordinaire n'est proposée ici.

En parallèle, le [prototype de carte logique TBT](heating_controller_v03_logic.md)
peut progresser sans ces données. Ni le PCB secteur ni une nomenclature
d'achat de protections ne sont gelés.

Calculs et tests :

```sh
python -B schematics/heating_design_checks.py
python -B tests/test_heating_design_checks.py
```
