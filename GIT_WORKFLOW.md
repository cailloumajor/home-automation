# Versionnement du contrôleur de chauffage

## Branche et jalons

`main` est la référence stable. Les travaux de chauffage sont préparés sur
`heating/v0.3-led-bench`, sans fusion ni publication automatique.
Les étapes suivantes utiliseront des branches distinctes si leur périmètre
diffère : banc TBT, commutation secteur, puis comptage.

Le tag annoté local `heating-v0.2` désigne uniquement le firmware de
simulation validé sur carte : Thread/API, six zones, commandes simulées,
redémarrage, interruption Home Assistant et interruption du Border Router.
Il ne qualifie aucun étage électrique.

Le firmware du banc LED est validé et compilé, mais non flashé ni testé
physiquement. Les schémas V0.3 sont des études. Aucun tag de validation
matérielle ne sera créé avant les essais correspondants.

Les commits distinguent : protection des secrets, firmware V0.2, firmware
du banc, puis schémas/tests et documentation. Éviter de mélanger une nouvelle
fonction avec une modification du câblage ou des fichiers personnels.

## Fichiers suivis et fichiers locaux

Suivre les YAML racine, les includes `inc/`, les tests, les sources KiCad,
les bibliothèques locales, les générateurs, les SVG de lecture et les
documents décrivant les validations. Suivre aussi la configuration des
outils et leur verrouillage existants.

Les SVG et sources générées doivent être régénérés avec leur générateur
dans le même commit. Les générateurs utilisent des identifiants stables.
Ne pas modifier seulement le SVG pour corriger un schéma.
Après un export KiCad, normaliser les espaces de fin de ligne des SVG avec
`python -B schematics/normalize_svg.py schematics/*.svg` avant de les ajouter à Git.

Ignorer `secrets.yaml`, `.esphome/`, les caches Python, les journaux, les
préférences KiCad `*.kicad_prl`, les verrous et sauvegardes KiCad. Les
réglages d'éditeur déjà suivis dans le dépôt restent soumis aux conventions
existantes ; ne pas les supprimer automatiquement.

## Secrets

Les YAML utilisent `!secret`. Le dataset d'esplinky a été déplacé dans
`thread_dataset_tlv_esplinky` en conservant sa valeur locale, indépendamment
du secret `thread_dataset_tlv` du contrôleur de chauffage.

Le contrôle hk/betterleaks existant est complété par des règles locales
pour les datasets Thread inline et les clés API ESPHome inline. Ne pas
neutraliser ces règles pour faire passer un commit. Ne jamais utiliser
`esphome config --show-secrets` dans les sorties partagées ou une CI.

Le dataset d'esplinky était déjà présent dans le commit `d9874d5`.
La correction de l'arbre courant ne l'efface pas de l'historique ni des
copies du dépôt. Prévoir son renouvellement si cet historique a été
partagé ; celui-ci peut impliquer les appareils du réseau Thread et doit
être planifié séparément. Aucun renouvellement, changement du réseau,
réécriture de l'historique ou force-push n'est effectué par ce versionnement.

## Contrôles avant commit

Respecter les hooks hk installés ; ne pas utiliser `--no-verify` ni `HK=0`.

```sh
hk check --all
git diff --check
python -B tests/test_heating_design_checks.py
g++ -std=c++17 -Wall -Wextra -Werror tests/fil_pilote_simulation_test.cpp -o /tmp/fil-pilote-simulation-test
/tmp/fil-pilote-simulation-test
g++ -std=c++17 -Wall -Wextra -Werror tests/heating_bench_test.cpp -o /tmp/heating-bench-test
/tmp/heating-bench-test
```

Valider avec `esphome config` les points d'entrée concernés, sans afficher
les secrets. Compiler après modification du firmware. Pour les schémas,
suivre les commandes ERC et de contrôle de netlist dans leurs guides.
Les tests API sur carte sont actifs : ils changent les modes et redémarrent
l'appareil ; ils ne sont pas des contrôles Git à lancer automatiquement.

Avant publication, examiner `git diff --cached`, vérifier l'exclusion des
secrets et les résultats des hooks. La création de commits et de tags
locaux ne vaut pas autorisation de push, de fusion ou de flash.
