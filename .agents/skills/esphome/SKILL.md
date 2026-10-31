---
name: esphome
description: Create, edit, validate, compile, and diagnose ESPHome YAML firmware in this home-automation repository, including shared packages, ESP32-H2/OpenThread, and heating logic. Use for ESPHome device configuration work; not for unrelated Home Assistant automations or upstream ESPHome development.
---

# ESPHome dans ce dépôt

## Contexte et découverte

Travailler depuis la racine du dépôt. Lire `mise.toml`, les YAML concernés et leurs includes ; vérifier la version avec `esphome version` et les options avec `esphome <commande> --help` si nécessaire. mise est activé dans le shell : utiliser directement `esphome`, sans Docker ni `mise exec -- esphome`.

Conserver les points d'entrée YAML à la racine, les fichiers réutilisables dans `inc/` et le fichier local partagé `secrets.yaml` à la racine. Ne pas créer de hiérarchie parallèle `devices/`. Suivre les `packages`, `!include`, variables d'include et substitutions avant de modifier un fragment commun. Valider tous les points d'entrée affectés par un changement partagé ; les fragments `inc/*.yaml` ne sont pas des configurations autonomes.

Pour le chauffage, lire `HEATING_CONTROLLER.md` et les commentaires des fichiers concernés : privilégier l'état actuel et les validations documentées. Lire `GIT_WORKFLOW.md` pour le versionnement et les contrôles avant commit.

## Modifier une configuration

Préserver le matériel, le framework, les identifiants d'entités et les conventions d'authentification existants, sauf changement demandé. Ne pas remplacer le réseau Thread existant pour résoudre une erreur de configuration. Vérifier les options contre la version installée, en particulier OpenThread, IPv6 et OTA ; ne pas recopier une recette d'une autre version sans validation.

Pour une option inconnue ou une migration, consulter la documentation officielle du composant sous https://esphome.io/components/ et les notes de version pertinentes. Réserver https://developers.esphome.io/ aux composants personnalisés et à leur cycle de vie. Distinguer une erreur de schéma d'une erreur de dépendance, de compilation ou de connexion.

Conserver `!secret` et les références de substitutions existantes. Ne pas afficher `secrets.yaml`, les datasets Thread, les clés API ou les mots de passe dans les sorties partagées. Ne pas utiliser `esphome config --show-secrets`. Si un secret manque, signaler son nom pour qu'il soit renseigné localement ; ne pas inventer une valeur opérationnelle. Vérifier son exclusion avec `git check-ignore secrets.yaml` si le traitement des secrets change.

## Validation locale

Pour chaque point d'entrée concerné, lancer par exemple :

```sh
esphome config heating_controller.yaml
esphome compile heating_controller.yaml
```

Adapter le nom au fichier réellement modifié. Valider d'abord le schéma, puis compiler après modification du firmware. `esphome compile --only-generate <configuration.yaml>` peut isoler une erreur de génération C++, mais ne remplace pas une compilation réussie. Si la compilation est bloquée par le réseau ou une dépendance, rapporter exactement ce qui a été vérifié et ce qui reste à faire.

Pour les changements de logique de chauffage, utiliser les tests hôtes concernés :

```sh
g++ -std=c++17 -Wall -Wextra -Werror tests/fil_pilote_simulation_test.cpp -o /tmp/fil-pilote-simulation-test
/tmp/fil-pilote-simulation-test
g++ -std=c++17 -Wall -Wextra -Werror tests/heating_bench_test.cpp -o /tmp/heating-bench-test
/tmp/heating-bench-test
```

Ne lancer que les contrôles pertinents au changement. Examiner le diff final et vérifier les espaces avec `git diff --check`. Les hooks hk ne remplacent pas la validation ESPHome ni la compilation.

## Opérations sur appareil

Une modification de YAML ou une compilation n'autorise pas un flash. `esphome run` compile, téléverse et démarre les logs ; utiliser `config` et `compile` pour les contrôles locaux. Pour un flash demandé, identifier le fichier, l'appareil et le transport réellement visés, puis utiliser `upload --device <cible>` ou `run` selon la demande. Ne pas reprendre aveuglément un ancien port USB ou nom réseau de la documentation.

`tests/check_heating_controller_api.py` agit sur la carte : il change les modes et redémarre le contrôleur. Ce n'est pas un test local à lancer automatiquement ; son usage concerne la simulation et doit correspondre à la demande de test sur appareil.

Le contrôleur de base simule les sorties fil pilote. Le banc LED ajoute des GPIO pour un montage USB/3,3 V uniquement. Son GPIO10 contrôle directement OE_N ; ce n'est pas l'interface ARM de l'étude secteur. Ne pas convertir un changement logiciel en activation de sorties secteur ou en modification du câblage.

Rapporter la version utilisée, les configurations validées, le résultat de compilation et les éventuels essais sur appareil séparément. Une validation de schéma ou une compilation ne prouve pas le fonctionnement matériel.
