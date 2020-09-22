[(English)](../en/heimdall.md)

Heimdall est un scanner de projet maestro. Trouvez les erreurs, les avertissements, les recommandations et les problèmes d'installation.

# Codes

Quels cas "heimdall" peut-il détecter?

* Erreurs critiques telles que: EntryModule manquant, les dossiers de projet tels que "listes" ont de mauvaises autorisations ou sont manquants.
* Erreurs telles que: la dépendance n'existe pas, XML incorrect, l'état de "dissemination" ne correspond pas au contexte.
* Avertissements comme: fichiers maestro inutilisés (tsk/cfg/xml), pas de statut de support dans une suite opérationnelle, chemins obsolètes comme `hall1`.
* Informations comme: les fichiers maestro (tsk/cfg/xml) sont des liens vers des chemins en dehors du projet, git a des modifications pas dans la repo, des signaux de nodelogger inconnus.
* Meilleures pratiques comme: chemins de dépendance codés en dur ou absolus, informations de support très longues, fichiers non-maestro dans les dossiers de fichiers maestro (tsk/cfg/xml).

Et beaucoup plus! Voir le [CSV délimité par des tabulations](csv/message_codes.csv) pour chaque cas. Chaque cas a un test automatisé.

# Captures d'écran

(La préférence de langue est automatiquement détectée)

![heimdall screenshot](/src/python3/screenshots/heimdall1.png)

# Essaye le

```
~sts271/stable/bin/heimdall --exp=~smco500/.suites/gdps/g0 --level=i --max-repeat=2

cd /home/smco500/.suites/gdps/g0/listings/eccc-ppp3/main/intxfer_g0
~sts271/stable/bin/heimdall

~sts271/stable/bin/heimdall -h
```

# Développement et statut

`heimdall` est disponible dans `maestro` à partir des versions `1.7+`, et la version plus récente de développement se trouve à `~sts271/stable/bin/heimdall`.

Le projet est se trouve sur deux sites:

* Le [sts271/heimdall repo](https://gitlab.science.gc.ca/sts271/heimdall/issues), créé en 2018, contenant un arriéré historique de problèmes et d'idées.
* Le domicile permanent de `heimdall` dans le repo `maestro`.

Une fois que l'arriéré historique des problèmes et des idées dans le [sts271/heimdall repo](https://gitlab.science.gc.ca/sts271/heimdall/issues) sera terminé, ce projet sera fermé.

# Niveaux

Chaque message `heimdall` a un niveau: critique, erreur, avertissement, info, et meilleure pratique. Par exemple "e003" ou "c001". Les niveaux sont basés sur le fait que des outils tels que `xflow` et` mflow` peuvent afficher et exécuter le projet.

Le but de tous les messages `heimdall` est que la plupart des personnes travaillant sur des projets `maestro` soient d'accord avec la norme.

### Critique \ (c)

![image critique de couleur](/src/python3/doc/couleur-critique.png)

Des erreurs critiques empêchent la visualisation ou le lancement de l'ensemble du projet.

### Erreur (e)

![image d'erreur de couleur](/src/python3/doc/color-error.png)

Des erreurs empêchent probablement la visualisation ou le lancement de parties du projet.

### Avertissement (w)

![image d'avertissement de couleur](/src/python3/doc/color-warning.png)

Un message d'avertissement est pour un chose qui est techniquement correct, mais il peut entraîner des problèmes ou un comportement inattendu.

### Info (i)

![image info couleur](/src/python3/doc/color-info.png)

Un message d'information identifie les aspects du projet qu'il est bon de connaître pour les personnes ayant moins d'expérience avec cette projet.

### Meilleures pratiques (b)

![image des meilleures pratiques couleur](/src/python3/doc/color-best-practice.png)

Un message sur les meilleures pratiques suggère des changements à le projet afin qu'elle soit mieux conforme aux normes [ISST](https://wiki.cmc.ec.gc.ca/wiki/ISST) et aux autres pratiques standard de l'industrie. L'objectif est que la plupart des personnes travaillant sur des projets "maestro" soient d'accord avec ces meilleures pratiques.

# Structure du projet

### Tests

```
cd maestro/src/python3/bin
./run_heimdall_tests
```

Chaque code du [CSV messages délimités par des tabulations](/src/python3/csv/message_codes.csv) a au moins un test automatisé. Supposons qu'un nouveau code "i999" soit créé. Il doit également y avoir un exemple du projet qui le génère dans `maestro/src/python3/mock_files/suites_with_codes/i999` et idéalement dans `maestro/src/python3/mock_files/suites_without_codes/i999`. Si cette condition n'est pas remplie, un autre test du échouera.

### Utilitaires

Les fichiers au niveau racine de `maestro/src/python3/src/utilities` sont génériquement utiles dans tout projet Python et peuvent être copiés dans de nouveaux projets sans modification.

### mflow

`heimdall` utilise des composants de `mflow`, comme la classe `MaestroExperiment`. Rarement, le développement dans `heimdall` implique la modification des dépendances de `mflow`. Dans ce cas, il est bon d'exécuter également les tests `mflow`:

```
cd maestro/src/python3/bin
./run_mflow_tests
```

La structure du projet et les tests pourraient être aplatis / fusionnés dans une version à l'avenir.

# Mythe

Dans la mythologie nordique, Heimdall ou Heimdallr est attesté comme possédant une prescience, une vue et une audition aiguës, et surveille les envahisseurs et l'apparition de Ragnarök. Heimdall voit tout.

![avatar heimdall](/src/python3/screenshots/heimdall-avatar.jpg)