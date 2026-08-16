# Exercices Lichess ciblés — conception

## But

Transformer un petit échantillon des parties récentes de Wuraang en exercices
Lichess réellement jouables. L'entraînement doit cibler des schémas d'erreurs
récurrents, y compris dans des victoires, au lieu de répéter mécaniquement une
position ou d'afficher une analyse libre.

## Périmètre

- Analyser les dix dernières parties terminées de Chess.com, quelle que soit
  leur issue.
- Retenir quelques moments pédagogiques représentatifs, regroupés par thème
  (pièce laissée en prise, menace adverse ignorée, tactique, développement ou
  ouverture).
- Créer un chapitre Lichess par exercice dans un programme privé dédié.
- Faire jouer à l'utilisateur sa couleur dans la partie originale.
- Prévoir une courte ligne de correction : Lichess joue automatiquement les
  coups adverses préenregistrés et demande uniquement les coups de l'utilisateur.
- Ne pas mettre d'explication détaillée dans le chapitre : le coaching et le
  débrief se font à la voix dans Codex.

## Expérience Lichess

Chaque chapitre est importé avec l'API officielle `POST /api/study/{studyId}/import-pgn`
et l'option `mode=gamebook` (leçon interactive), ainsi que l'orientation de la
couleur que Wuraang jouait. La ligne PGN commence juste avant l'erreur à
entraîner et contient la bonne continuation courte.

Le programme d'entraînement interdit le moteur et l'explorateur dans ses
paramètres de création. Le chapitre n'affiche donc pas les flèches ou une
évaluation qui donnent la réponse. Lichess marque une réponse erronée comme à
réessayer et joue la réponse adverse lorsqu'un coup correct est trouvé.

## Sélection des exercices

L'analyse ne génère pas dix copies de la même erreur. Elle conserve au plus un
exercice par partie et déduplique les thèmes. Un cycle de dix parties donne en
général trois à cinq exercices, priorisés ainsi :

1. une erreur tactique directe et répétée ;
2. une menace adverse non vérifiée ;
3. un problème de développement ou d'ouverture récurrent ;
4. un exercice de consolidation si un seul thème domine.

Un changement clair de niveau d'analyse doit rester séparé du synchroniseur de
parties : l'import léger continue toutes les dix minutes, tandis que la
construction du programme est exécutée à la demande ou une fois par jour.

## Analyse des positions

Le générateur doit analyser les positions localement avec Stockfish et parser
les PGN avec `python-chess`. Il compare l'évaluation avant et après les coups
de Wuraang afin d'isoler le premier écart significatif dans chaque partie. Les
thèmes sont ensuite classés à partir de la position et du type de coup. Cela
évite de dépendre du moteur Lichess dans l'interface et limite la consommation
du Mac à la génération du programme.

## Données et sécurité

Le jeton Lichess reste dans le fichier local ignoré par Git. Les identifiants
de programme et des exercices générés sont enregistrés dans l'état local pour
éviter les doublons. Le dépôt ne contient ni token, ni PGN privé, ni rapport
personnel de parties.

## Vérification

- tests unitaires de création de chapitre `gamebook`, orientation et paramètres
  anti-moteur ;
- tests de déduplication et de limite d'exercices ;
- test d'intégration avec un PGN de démonstration ;
- vérification manuelle d'un chapitre : pas de flèche, un seul camp à jouer,
  réponse adverse automatique.
