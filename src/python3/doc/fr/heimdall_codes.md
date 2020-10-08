[(English)](../en/heimdall_codes.md)

# Heimdall Codes de Message

Cette page liste tous les codes et messages Heimdall. Voir aussi le [Heimdall README](https://gitlab.science.gc.ca/CMOI/maestro/blob/integration/src/python3/HEIMDALL.md).




# Niveau: Critique
![color c image](../color-critical.png)

### [c001](#c001): Pas de EntryModule

Lien EntryModule n'existe pas: '{entry_module}'


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/EntryModule)



![color c image](../color-critical.png)

### [c002](#c002): Mauvais EntryModule

EntryModule n'est pas un lien: '{entry_module}'


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/EntryModule)



![color c image](../color-critical.png)

### [c003](#c003): Aucune expérience ici

Impossible de trouver une expérience pour le chemin: '{path}'. Un dossier d'expérience valide contient un lien 'EntryModule'.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/EntryModule)



![color c image](../color-critical.png)

### [c004](#c004): Pas de EntryModule flow.xml

Le fichier requis flow.xml de EntryModule n'existe pas: '{flow_xml}'


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/EntryModule)



![color c image](../color-critical.png)

### [c005](#c005): Mauvais EntryModule flow.xml

Le fichier requis flow.xml de EntryModule n'a pas réussi à analyser comme XML: '{flow_xml}'


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/EntryModule)



![color c image](../color-critical.png)

# Niveau: Erreur
![color e image](../color-error.png)

### [e001](#e001): Dossiers manquants dans la suite

Toutes les suites ont besoin des dossiers: 'listings', 'sequencing', and 'logs'. Cette suite est manquante: {folders}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro_Files_and_Folders)



![color e image](../color-error.png)

### [e002](#e002): Mauvais XML

Impossible d'analyser XML '{xml}'



![color e image](../color-error.png)

### [e003](#e003): Nom de nœud non valide

Nom de nœud non valide '{node_name}' en flow XML '{flow_path}'. Les noms de nœuds doivent être alphanumériques avec comme caractères spéciaux des points, des tirets ou des sous-tirets. Doit correspondre à regex: {regex}


[Plus d'info](https://regex101.com/)



![color e image](../color-error.png)

### [e004](#e004): Lien symbolique brisé

Le cible du lien symbolique '{link}' n'existe pas.


[Plus d'info](https://www.google.com/search?q=linux+find+broken+symlinks)



![color e image](../color-error.png)

### [e005](#e005): 'flow' du module est éparpillé

Les enfants de flow XML pour le module '{module_name}' sont définis dans plus d'un fichier flow.xml:\n{flow_xmls}


[Plus d'info](https://gitlab.science.gc.ca/CMOI/mflow-prototype/issues/23#note_189290)



![color e image](../color-error.png)

### [e007](#e007): Fichier de ressource nécessaire manquant

La tâche '{task_path}' n'a pas de fichier de ressources à '{resource_path}'. Cela est nécessaire pour le '{context}' contexte.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color e image](../color-error.png)

### [e008](#e008): Accolades manquantes dans un xml de ressource

Les variables dans les fichiers XML de ressources doivent utiliser des accolades comme '${{ABC}}' et non '$ABC'. Le fichier '{file_path}' contient:\n{matching_string}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color e image](../color-error.png)

### [e009](#e009): Accolades déséquilibrées dans un xml ressource

Trouvé un nombre impair {attribute_value} d'accolades dans un fichier de ressources: '{file_path}'



![color e image](../color-error.png)

### [e010](#e010): Chemin dur codé dans le fichier de configuration

Le chemin '{bad_path}' défini dans '{config_path}' est absolue et ne commence pas par une variable comme '${{SEQ_EXP_HOME}}'. Ceci est une façon moins portable et plus fragile pour configurer une expérience.



![color e image](../color-error.png)

### [e011](#e011): Mauvaise dépendance d'expérience

Le 'exp' attribut '{exp_value}' dans le fichier de ressources '{resource_path}' n'est pas un chemin à un dossier qui existe.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color e image](../color-error.png)

### [e012](#e012): Variables indéfinies de xml ressource

Le XML ressources '{resource_path}' utilise des variables qui ne sont pas définies dans les fichiers de ressources comme 'resources/resources.def'. Variables:\n{variable_names}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color e image](../color-error.png)

### [e013](#e013): État de diffusion ne correspond pas à contexte

L'expérience semble avoir le '{context}' contexte, mais les variables dans '{cfg_path}' ne correspond pas à ce qui est attendu: {unexpected}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Dissemination)



![color e image](../color-error.png)

### [e014](#e014): Non-liens dans hub

Les expériences avec le '{context}' contexte ne peuvent avoir des dossiers de liens souples dans leur dossier 'hub':\n{bad}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/hub)



![color e image](../color-error.png)

### [e015](#e015): Valeur des ressources plus que le maximum

La valeur de la ressource '{value}' pour '{attribute}' dans '{xml_path}' est plus que le maximum de '{maximum}' défini dans 'jobctl-qstat' pour la file d'attente '{queue}'.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color e image](../color-error.png)

### [e016](#e016): Pas de dêpot git

Il n'y a pas de dépôt git pour cette expérience. Les expériences avec le '{context}' contexte devraient toujours avoir le contrôle de version git.



![color e image](../color-error.png)

### [e017](#e017): Nom en double dans le conteneur flow

Le contenant '{container_name}' dans un flow XML a plus d'un élément avec le 'name' ou 'sub_name' '{duplicate_name}'. Tous les enfants directs dans un conteneur doit avoir un 'name' ou 'sub_name' unique.



![color e image](../color-error.png)

### [e018](#e018): Élément submits a l'attribut name

Tous les éléments de SUBMITS doivent avoir un attribut 'sub_name' et non un attribut 'name'. Le fichier '{file_path}' contient:\n{matching_string}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/SUBMITS)



![color e image](../color-error.png)

### [e019](#e019): Élément non-submits a l'attribut sub_name

Seuls les éléments de SUBMITS doivent avoir un attribut 'sub_name'. Vous devrez peut-être utiliser l'attribut 'name' au lieu. Le fichier '{file_path}' contient:\n{matching_string}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/SUBMITS)



![color e image](../color-error.png)

### [e020](#e020): Inconsistant propriétaires ou autorisations du dossier log

Le dossier du journal '{path}' a la propriété et les autorisations '{ugp}' qui est différent des autres dossiers de journaux. Les permissions des dossiers journaux temporaires devraient être les mêmes: {folders}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro_Files_and_Folders)



![color e image](../color-error.png)

### [e021](#e021): Définitions ressources en double

La variable '{variable}' est défini plus d'une fois dans le fichier '{path}'. Des outils tels que getdef peuvent se comporter de façon inattendue.



![color e image](../color-error.png)

### [e022](#e022): Dossier stats manquante

Le dossier 'stats' est manquante, mais nécessaire parce que les variables de ressources SEQ_RUN_STATS_ON et SEQ_AVERAGE_WINDOW sont utilisés: '{required}'


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/stats)



![color e image](../color-error.png)

### [e023](#e023): Mauvais expression de boucle

Le fichier '{path}' a une mauvaise expression de boucle '{loop_expression}'. Cela devrait être des virgules qui séparent les nombres dans le format 'début:fin:étape:set'.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/1.5.0/Release_Notes#Multi-definition_numeric_loops)



![color e image](../color-error.png)

### [e024](#e024): Mauvaises autorisations sur les dossiers de log opérationnels

Le dossier du journal '{folder}' doit avoir les autorisations '{expected}' mais il a '{ugp}'.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro_Files_and_Folders)



![color e image](../color-error.png)

### [e025](#e025): Realpath lien est chemin non opérationnel

L'expérience semble avoir le '{context}' contexte, mais le fichier '{path}' contient des références à un utilisateur non opérationnel:\n{bad}



![color e image](../color-error.png)

### [e026](#e026): Chaîne de lien contient un chemin non opérationnel

L'expérience semble avoir le '{context}' contexte, mais le fichier '{path}' est une chaîne de liens, qui contient un chemin d'un utilisateur non opérationnel. Le 'realpath' pour le lien est correct, mais pas en traversant:\n{bad}



![color e image](../color-error.png)

### [e027](#e027): Mauvaise syntaxe de script shell

La commande '{verify_cmd}' a trouvé des erreurs dans le script shell '{path}'. Sortie:\n{output}



![color e image](../color-error.png)

### [e028](#e028): Dépendance externe est relative

Le fichier '{resource_path}' a un attribut relatif 'dep_name' '{dep_name}' mais 'exp' est externe. Les dépendances externes ne peuvent pas être relatives.



![color e image](../color-error.png)

# Niveau: Avertissment
![color w image](../color-warning.png)

### [w001](#w001): Fichier de ressources manquante

La tâche '{task_path}' n'a pas de fichier de ressources à '{resource_path}'. Créer un fichier de ressources pour éviter d'utiliser les valeurs défaut et inconnus.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color w image](../color-warning.png)

### [w002](#w002): Fichier de ressources boucle manquante

La boucle ou un switch '{node_path}' n'a pas de fichier de ressources à '{resource_path}'. Créer un fichier de ressources pour éviter d'utiliser les valeurs défaut et inconnus.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color w image](../color-warning.png)

### [w003](#w003): Obsolète site1/site2

Les chemins 'site1' et 'site2' ne sont plus disponibles après les mises à jour au début de 2020. Le fichier '{file_path}' contient:\n{matching_string}



![color w image](../color-warning.png)

### [w004](#w004): Obsolète hall1/hall2

Les chemins 'hall1' et 'hall2' ne sont plus disponibles après les mises à jour au début de 2020. Le fichier '{file_path}' contient:\n{matching_string}



![color w image](../color-warning.png)

### [w005](#w005): Plusieurs chemins pour le projet

L'expérience maestro se trouve dans le dossier de '{real_home}' mais les fichiers maestro principaux sont des liens souples vers d'autres utilisateurs. Cela peut être considéré comme trop instable pour installer opérationnellement. Exécutez realpath sur ces liens:\n{bad_links}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/User:Maciaa/home_references)



![color w image](../color-warning.png)

### [w006](#w006): Chemin codé dur dans le fichier de configuration

Le chemin '{bad_path}' défini dans '{config_path}' est absolue et ne commence pas par une variable comme '${{SEQ_EXP_HOME}}'. Ceci est une façon moins portable et plus fragile pour configurer une expérience.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/SEQ_EXP_HOME)



![color w image](../color-warning.png)

### [w007](#w007): Aucun statut de soutien dans l'expérience opérationnelle

Il n'y a pas d'attribut 'SupportInfo' dans le XML '{xml_path}' ou le XML n'existe pas. Cela est nécessaire pour les expériences opérationnelles.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/ExpOptions.xml)



![color w image](../color-warning.png)

### [w008](#w008): Multiples statuts de soutien

Le XML '{xml_path}' a plus d'un élément SupportInfo.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/ExpOptions.xml)



![color w image](../color-warning.png)

### [w009](#w009): Variable de ressource faute de frappe

La variable ressource '{maybe_typo}' est défini, mais le nom de la variable standard '{expected}' n'est pas. Peut-être que vous vouliez écrire cela à la place.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/User:Lims/projects/tech_transfer_improvements#Using_standard_variables_for_machine_and_queue_definitions)



![color w image](../color-warning.png)

### [w010](#w010): Valeur incorrecte de file d'attente pour variable ressource

La valeur '{value}' pour la variable ressource '{name}' est pas une file d'attente disponible en qstat. Files d'attente:\n{queues}



![color w image](../color-warning.png)

### [w011](#w011): Expérience n'est pas en overview XML

L'expérience semble avoir le '{context}' contexte, mais il n'a pas été trouvé dans les expériences de {exp_count} dans le fichier XML overview: {xml_path}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/overview_xml)



![color w image](../color-warning.png)

### [w012](#w012): Expérience dans un overview XML inattendu

L'expérience semble avoir le '{context}' contexte, mais il n'a pas été trouvé dans les {exp_count} expériences dans le '{xml_context} XML overview: {xml_path}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/overview_xml)



![color w image](../color-warning.png)

### [w013](#w013): Variables de diffusion égaré

Les variables {variables} appartiennent uniquement dans 'experiment.cfg' fichiers, mais ont été trouvés dans: '{cfg_path}'


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Dissemination)



![color w image](../color-warning.png)

### [w014](#w014): Paires hub ont des chemins différents

Les liens de dossier hub '{folder1}' et '{folder2}' devraient avoir des cibles similaires. Au contraire, ils sont très différents:\n{target1}\n{target2}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/hub)



![color w image](../color-warning.png)

### [w015](#w015): Dêpot git avec des changements pas engagé

Il y a des changements non engagé dans le dépôt git. Les expériences avec le '{context}' contexte devrait toujours avoir rien à engager et à un arbre de travail propre de 'git status'.



![color w image](../color-warning.png)

### [w016](#w016): Tâche run_orji est désactivée

La ressource de tâche '{resource_path}' a une valeur de catchup '{catchup}', mais les tâches 'run_orji' doivent toujours être activés. De cette façon, les utilisateurs peuvent décider de souscrire ou désabonner.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/orji)



![color w image](../color-warning.png)

### [w017](#w017): Fichier d'archive n'est pas un lien

Le fichier archive '{bad}' n'est pas un lien. Les fichiers nommés '.protocole_*' ou '.archive_monitor_*' doivent être des liens pour que les mainteneurs du système d'archivage peuvent gérer plus facilement ses paramètres.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Archive)



![color w image](../color-warning.png)

### [w018](#w018): Mauvais lignes dans gitignore

Le fichier gitignore '{gitignore_path}' ne doit pas contenir la ligne '{line}'. Il est important que ces fichiers sont dans le dépôt git donc une projet complète peut être partagé.



![color w image](../color-warning.png)

### [w019](#w019): Lignes manquants dans gitignore

Le fichier gitignore '{gitignore_path}' doit contenir {content}. Ceci permet d'ignorer les fichiers générés lors de l'exécution de cette suite qui ne font pas partie du projet contrôlé version.



![color w image](../color-warning.png)

### [w020](#w020): Pas de gitignore

Il devrait y avoir un fichier gitignore ici: '{gitignore_path}'. Pas de '.gitignore' permet d'avoir des grandes quantités de fichiers temporaire et sans importance qui sont accidentellement partagés ou ajoutés au projet.



![color w image](../color-warning.png)

### [w021](#w021): Fichier maestro dans $CMCCONST

Le realpath pour le fichier '{path}' est dans le dossier $CMCCONST '{cmcconst}'. Tâche, configuration, flow et les fichiers XML de ressources utilisés dans une suite ne devrait pas être dans le dossier $CMCCONST.


[Plus d'info](https://gitlab.science.gc.ca/CMOI/best-practices/blob/master/fr/constants.md)



![color w image](../color-warning.png)

### [w022](#w022): Ressources de la machine est codé en dur

L'expérience semble avoir le '{context}' contexte, mais la valeur '{machine_value}' de 'machine' dans '{resource_path}' est codé en dur. Un switchover peut briser cette suite. Utilisez une variable comme $FRONTEND à la place.



![color w image](../color-warning.png)

### [w023](#w023): Utilisateur opérationnelle peut écrire sur l'expérience 

L'utilisateur opérationnel '{user}' a des autorisations en écriture sur le fichier de projet permanent '{path}'. Pour plus de sécurité au cours de passes opérationnelles, '{user}' devrait seulement avoir les autorisations de lire, et non d'exécution pour les fichiers de projet permanents.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/CMOI/Suite_Management_Process)



![color w image](../color-warning.png)

### [w024](#w024): Utilisateur parallèle dans le contexte opérationnel

L'expérience semble avoir le '{context}' contexte, mais le fichier '{file_path}' a des références au systèmes parallèles avec la texte '{par_string}'.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/CMOI/Suite_Management_Process)



![color w image](../color-warning.png)

### [w025](#w025): Dossiers opérationnels ont propriétaire incorrect

L'expérience semble avoir le '{context}' contexte, mais le fichier '{path}' est la propriété de '{owner}' mais '{expected}' est attendu.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/CMOI/Suite_Management_Process)



![color w image](../color-warning.png)

### [w026](#w026): Wallclock beaucoup plus grand que l'histoire exige

Le wallclock pour '{node_path}' est '{wallclock_seconds}' secondes dans '{resource_xml}' mais la dernière course réussie sur '{datestamp}' a pris '{latest_seconds}' secondes. Ceci est {factor} fois plus gros (le seuil de ce message est {threshold}). Le wallclock devrait probablement être abaissé.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Wallclock)



![color w image](../color-warning.png)

### [w027](#w027): Paquets SSM écrasés

Les différentes versions du paquet SSM '{package}' sont utilisés: {versions}. La même version doit être utilisée par tous, ou le paquet ne doit être ajouté à l'environnement dans un endroit racine. Fichiers:\n{paths}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Ssm)



![color w image](../color-warning.png)

### [w028](#w028): Chemin d'expérience en ressources sans datestamp

Le fichier de ressources '{resource_path}' a des références génériques aux chemins de projet maestro qui n'utilisent pas la suffixe de date comme '_20200401'. Cela peut provoquer des problèmes avec le dépannage, l'histoire et les transferts. Chemins:\n{bad}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/CMOI/Suite_Management_Process)



![color w image](../color-warning.png)

### [w029](#w029): Aucun lien souple sur la maison opérationnelle

Le chemin d'expérience '{target}' est l'endroit où les suites opérationnelles sont installées, mais il n'y a pas un lien doux '{source}' pointant vers elle.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/CMOI/Suite_Management_Process)



![color w image](../color-warning.png)

### [w030](#w030): Obsolète système uspmadt

Les options '-r' ou '-t' utilisés dans '{path}' avec 'fname', 'fgen+' ou 'dtstmp' ne devrait pas être une variable 'run'. Cela utilise le système obsolète 'uspmadt'. Utilisez 'CMCSTAMP' à la place. Lignes:\n{lines}


[Plus d'info](https://gitlab.science.gc.ca/CMOI-Service-Desk/General/issues/5)



![color w image](../color-warning.png)

### [w031](#w031): Manquantes variables dans resources.def

Le fichier '{path}' doit définir les variables {required} mais ceux-ci étaient manquants: {missing}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/CMDI/Good_practices)



![color w image](../color-warning.png)

### [w032](#w032): Mauvais chemin de noeud de dépendance

Le fichier '{resource_path}' décrit un chemin de noeud '{node_path}' qui n'existe pas. Il est possible que maestro ignore cette dépendance.



![color w image](../color-warning.png)

### [w033](#w033): Mauvais chemin de noeud de dépendance relative

Le fichier '{resource_path}' a un attribute 'dep_name' '{dep_name}' qui décrit un chemin de nœud relatif '{node_path}' qui n'existe pas par rapport à '{node_folder}'. Il est possible que maestro ignore cette dépendance.



![color w image](../color-warning.png)

### [w034](#w034): Mauvais chemin du nœud de dépendance externe

Le fichier '{resource_path}' décrit un chemin de nœud '{node_path}' qui n'existe pas dans l'expérience '{exp}'. Il est possible que maestro ignore cette dépendance.



![color w image](../color-warning.png)

### [w035](#w035): Mauvais éxperience de dépendance externe

Le fichier '{resource_path}' décrit une expérience '{exp}' qui n'existe pas ou qui est brisée. Maestro pourrait ignorer cette dépendance.



![color w image](../color-warning.png)

### [w036](#w036): Pas d'archivage dans le hub

Le dossier 'hub' semble contenir des sous-dossiers contenant plus de {file_count} fichiers de plus de {day_count} jours mais pas de fichier d'archivage '.protocole_*'. Ces fichiers peuvent s'accumuler:\n{folders}



![color w image](../color-warning.png)

# Niveau: Info
![color i image](../color-info.png)

### [i001](#i001): Plusieurs chemins pour le projet

L'expérience maestro se trouve dans le dossier de '{real_home}' mais les fichiers maestro principaux sont des liens souples vers d'autres utilisateurs. Cela peut être instable. Liens:\n{bad_links}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/User:Maciaa/home_references)



![color i image](../color-info.png)

### [i002](#i002): Nom du module et chemin diffèrent

Le dossier du module '{folder_name}' diffère du nom du module '{attribute_name}' dans le flow XML '{xml_path}'. Cela peut aider à organiser un projet, mais il peut aussi être un source de confusion.



![color i image](../color-info.png)

### [i003](#i003): Fichiers temporaires d'un éditeur de texte

Fichiers temporaire d'un éditeur de texte ont été trouvés, par exemple pour vim ou emacs. Si votre éditeur est fermé, vous pouvez les récupérer ou supprimer:\n{swaps}


[Plus d'info](https://www.google.com/search?q=what+is+a+text+editor+swap+file)



![color i image](../color-info.png)

### [i004](#i004): Dêpot git avec des changements pas engagé

Il y a des changements non-engagé dans la dépôt git.



![color i image](../color-info.png)

### [i005](#i005): Signal inconnu de nodelogger

Le 'nodelogger' exécutable a été donné un signal pour son argument '-s' qui n'est pas un signal connu: {signals}. Ce message n'apparaîtra dans le centre de messages. Si vous ne voulez pas qu'il apparaisse dans le centre de message, utilisez 'infox'.\n{details}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Nodelogger)



![color i image](../color-info.png)

### [i006](#i006): Développeurs principaux de l'histoire git

En regardant l'histoire git pour ce projet (commit fréquence, récence, continuité) ceux-ci semblent être les développeurs principaux:\n{developers}



![color i image](../color-info.png)

### [i007](#i007): Chemins développeurs absolus

Le fichier '{path}' contient des chemins absolus à un utilisateur non opérationnel. Cela ne peut pas être installé opérationnellement:\n{bad}



![color i image](../color-info.png)

### [i008](#i008): Ancienne version SSM

Le fichier '{path}' utilise un paquet SSM '{old}', mais une version plus récente '{new}' est disponible.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Ssm)



![color i image](../color-info.png)

### [i009](#i009): Ressources avec des heures valides

Les tâches de ce projet ont des configurations de ressources qui changent selon l'heure du jour. Recherchez le 'valid_hour' ou 'valid_dow' attributs:\n{paths}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color i image](../color-info.png)

### [i010](#i010): Pas de hcrons

Aucun fichier de configuration actifs pour '{suite_name}' ont été trouvés dans '{hcron_folder}'. La suite pourrait ne pas rouler automatiquement.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Hcron)



![color i image](../color-info.png)

# Niveau: Meilleures pratiques
![color b image](../color-best-practice.png)

### [b001](#b001): Chemin de dépendance codé en dur

L'attribut 'exp' '{exp_value}' dans le fichier de ressources '{resource_path}' est codé en dur. Cela est moins portable et plus fragile. Pensez à utiliser une variable à la place.



![color b image](../color-best-practice.png)

### [b002](#b002): SupportInfo est trop long

L'attribut SupportInfo dans le fichier XML '{xml_path}' est '{char_count}' caractères, mais devrait être plus court. Le maximum recommandé est {max_chars}.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/ExpOptions.xml)



![color b image](../color-best-practice.png)

### [b003](#b003): SupportInfo n'a pas de URL

L'attribut SupportInfo dans le fichier XML '{xml_path}' doit contenir une URL. Ceci est la méthode recommandée pour fournir de l'information détaillée sur l'état du support et des étapes de dépannage.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/ExpOptions.xml)



![color b image](../color-best-practice.png)

### [b004](#b004): Texte SupportInfo non-standard

L'attribut SupportInfo dans le fichier XML '{xml_path}' doit commencer par une valeur comme 'Full Support'. Débuts de textes recommandées:\n{substrings}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/ExpOptions.xml)



![color b image](../color-best-practice.png)

### [b005](#b005): Fichier ou un dossier obsolète

Le fichier ou le dossier '{path}' est dépréciée et devrait être supprimé.



![color b image](../color-best-practice.png)

### [b006](#b006): Les fichiers non maestro dans des dossiers de maestro

Le dossier maestro '{folder}' ne doit contenir que des fichiers maestro comme tsk, cfg, xml. Ces fichiers ont été trouvés:\n{filenames}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro_Files_and_Folders)



![color b image](../color-best-practice.png)

### [b007](#b007): Commentaires dans le fichier de configuration

La section pseudo-xml (contenant 'input', 'executables', et 'output') du fichier de configuration '{file_path}' contient des lignes de commentaires {count} commençant par '##'. Celles-ci semblent être des lignes de configuration et non des commentaires, et peuvent être supprimées.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/.cfg)



![color b image](../color-best-practice.png)

### [b008](#b008): Alias de file d'attente cachés utilisés

La valeur '{value}' pour la variable ressource '{name}' est un alias de file d'attente cachée et pas facilement visible dans qstat. Pensez à utiliser une de ces files d'attente à la place:\n{queues}



![color b image](../color-best-practice.png)

### [b009](#b009): Attribut obsolète dans l'élément de SUBMITS

Le fichier '{xml_path}' a l'attribut 'type' dans un élément SUBMITS. Ceci est dépréciée et peut être retiré.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/SUBMITS)



![color b image](../color-best-practice.png)

### [b010](#b010): Caractères non-standard dans le nom exécutable

Le chemin de configuration '{bad}' dans '{config_path}' a des caractères non standard qui ne correspondent pas au regex '{regex}'. Cela peut causer des coquilles avec les outils, les systèmes d'exploitation ou parseurs. Pensez à les renommer. {dollar_msg}


[Plus d'info](https://regex101.com/)



![color b image](../color-best-practice.png)

### [b011](#b011): Référence a la racine du dossier CMCCONST 

Il y a des références à des fichiers ou des dossiers dans la racine du dossier CMCCONST. Il est recommandé d'utiliser plutôt des dossiers dans CMCCONST. Le fichier '{file_path}' contient:\n{matching_string}


[Plus d'info](https://gitlab.science.gc.ca/CMOI/best-practices/blob/master/fr/constants.md)



![color b image](../color-best-practice.png)

### [b012](#b012): Fichier d'archive dépréciée

Le fichier '{bad}' est un fichier d'archive dépréciée et doit être supprimé. Si le 'hub' n'a pas d'autres fichiers d'archive, son état d'archivage devrait être examiné.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Archive)



![color b image](../color-best-practice.png)

### [b013](#b013): Nom du dossier pas claire

Le dossier '{unclear}' devrait avoir un lien symbolique descriptif à côté. Par exemple 'forecast -> e1. Cela donne les débutants une chose de moins à mémoriser.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Obfuscation)



![color b image](../color-best-practice.png)

### [b014](#b014): Nom du nœud mauvais

Mauvais nom du noeud '{node_name}' en flow XML '{flow_path}'. Ce nom fonctionne, mais la recommandation est de faire correspondre cette regex: {regex}


[Plus d'info](https://regex101.com/)



![color b image](../color-best-practice.png)

### [b015](#b015): Noms de variables non standard dans les ressources BATCH

L'attribut '{attribute_name}' dans l'élément BATCH de '{resource_path}' utilise une variable non-standard '{attribute_value}'. Pensez à utiliser une variable standard à la place si la configuration est plus facile à suivre et changer: {recommended}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Maestro/folders/resources)



![color b image](../color-best-practice.png)

### [b016](#b016): Propriétaires ou autorisations de fichiers inconsistants

Le fichier '{path}' a la propriété et les autorisations '{ugp}', mais la plupart des fichiers d'expérience ont '{expected}'. Le propriétaire, le groupe et les permissions des fichiers d'expérience permanents devraient être les mêmes.



![color b image](../color-best-practice.png)

### [b017](#b017): Trouvé SEQ_ au lieu de MAESTRO_

La variable dépréciée '{old}' a été trouvée dans '{path}'. Pensez à utiliser la variable équivalente '{new}' disponible dans maestro 1.8+ à la place. Cela aide les débutants à comprendre votre projet, car ils sauront cette variable est liée à maestro.



![color b image](../color-best-practice.png)

### [b018](#b018): Variable en majuscule est redéfinie

La variable majuscule '{variable}' est défini plus d'une fois dans le fichier '{path}'. Les variables en majuscules bash doivent être considérés comme constants et non modifiés. Notez que "const" dans d'autres langages de programmation ne peut être défini qu'une seule fois.


[Plus d'info](https://google.github.io/styleguide/shellguide.html#s7.3-constants-and-environment-variable-names)



![color b image](../color-best-practice.png)

### [b019](#b019): Readme n'est pas en markdown

Le fichier '{readme}' ressemble à un fichier 'readme'. Considérez écrire dans 'markdown' et renommant '{suggested}' pour qu'il apparaisse automatiquement et formaté sur des plateformes comme GitLab.


[Plus d'info](https://www.youtube.com/watch?v=SCAfcuQ0dBE)



![color b image](../color-best-practice.png)

### [b020](#b020): Chemin littérales au lieu de CMCPROD

Chemins littérales à 'hall3' ou 'hall4' ont été trouvés. Pensez à utiliser la variable CMCPROD à la place afin que votre projet suit les 'switchover' des configurations. Le fichier '{file_path}' contient:\n{matching_string}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Cmcprod)



![color b image](../color-best-practice.png)

### [b021](#b021): Chemin absolu dans la configuration au lieu de getdef

Le fichier de configuration '{config}' doit utiliser getdef au lieu de chemins codés en dur absolus. Par exemple: ABC=$(getdef resource ABC)\nChemins absolute:\n{values}


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/User:Lims/projects/tech_transfer_improvements#Making_variables_configurable_from_high_level)



![color b image](../color-best-practice.png)

### [b022](#b022): Fichiers identiques dans le module

Le contenu des fichiers dans le même module sont identiques. Envisager de remplacer les fichiers en double avec des liens souples, alors que un mise à jour s'applique à tous. Ou, distinguer les fichiers avec des commentaires. Fichiers:\n{paths}


[Plus d'info](https://fr.wikipedia.org/wiki/Ne_vous_r%C3%A9p%C3%A9tez_pas)



![color b image](../color-best-practice.png)

### [b023](#b023): Variables etiket non définies dans etikets.cfg

Les variables etiket {etikets} ont été définis dans '{bad_path}' mais ils doivent être définis dans '{good_path}'. Les variables etiket sont découverts par ce scanner en fonction de leur 'ETIK' nom et l'utilisation de 'pgsm' et 'editfst'.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/Etikets.cfg)



![color b image](../color-best-practice.png)

### [b024](#b024): Variables de configuration sont défini mais pas utilisées

Le fichier de configuration '{config}' définit les variables '{unused}', mais ils ne sont pas utilisés. Envisager de les supprimer.



![color b image](../color-best-practice.png)

### [b025](#b025): Mauvais git remote origin

L'expérience semble avoir le '{context}' contexte, mais la git remote 'origin' pointe vers '{bad}'. Au lieu de cela la remote doit commencer par '{good}'.



![color b image](../color-best-practice.png)

### [b026](#b026): Recommandations pour le script shell

La commande '{verify_cmd}' a trouvé des recommandations dans le script shell '{path}'. Sortie:\n{output}



![color b image](../color-best-practice.png)

### [b027](#b027): Chemin non-standard pour outil maestro 

La commande '{cmd}' dans '{path}' pour l'outil maestro '{tool}' doit être précédée par '{prefix1}' ou '{prefix2}' comme '{expected}'.



![color b image](../color-best-practice.png)

### [b028](#b028): Mauvais cible de EntryModule

La cible pour le lien '{path}' doit être '{good}' au lieu de '{bad}'.


[Plus d'info](https://wiki.cmc.ec.gc.ca/wiki/CMDI/Good_practices)



![color b image](../color-best-practice.png)

### [b029](#b029): Lien products_dbase obsolète

Le dossier '{bad}' dans 'hub' ne doit pas être un lien. Ce style de dossier de produits est obsolète.


[Plus d'info](https://gitlab.science.gc.ca/CMOI/maestro/issues/219)



![color b image](../color-best-practice.png)

### [b030](#b030): Mauvais nom de variable de domaine SSM

Le fichier '{path}' utilise des variables comme domaines SSM, mais les noms ne commencent pas par 'SSM _':\n{variables}



![color b image](../color-best-practice.png)

### [b031](#b031): Exécutable compilé dans le projet

Le fichier "{path}" semble être un exécutable compilé. Ceux-ci appartiennent à l'extérieur du projet maestro, ou peut-être dans un package SSM.


![color b image](../color-best-practice.png)

# Page Générée

Cette page a été générée par le script 'generate_messages_markdown.py' du repo 'https://gitlab.science.gc.ca/CMOI/maestro' le '2020-10-08'.
