# Chess Sync Coach — design de la version 1

## Objectif

Créer un outil local qui récupère les parties **déjà terminées** d’un compte Chess.com et les importe dans un espace privé Lichess afin de les analyser et de s’entraîner ensuite sur Lichess.

L’outil ne fournit aucune assistance pendant une partie Chess.com en cours.

## Périmètre de la version 1

- Exécution locale sur le Mac de l’utilisateur.
- Configuration par identifiant Chess.com et jeton Lichess enregistré localement hors de Git.
- Recherche périodique de nouvelles parties terminées à partir de l’API publique Chess.com.
- Import de chaque partie une seule fois dans Lichess, en conservant un état local des identifiants déjà traités.
- Affichage clair des imports réussis, des parties ignorées et des erreurs récupérables.
- Commande de synchronisation manuelle et mode de surveillance facultatif.

## Hors périmètre

- Analyse ou suggestions pendant des parties contre des humains.
- Extension navigateur.
- Hébergement cloud ou synchronisation lorsque le Mac est éteint.
- Partie automatisée contre un bot Lichess et coaching conversationnel en direct.

## Architecture

Le programme est un petit outil en ligne de commande composé de quatre modules isolés :

1. **Configuration** : charge et valide les variables locales.
2. **Source Chess.com** : récupère les archives de parties et sélectionne les parties terminées non encore vues.
3. **Cible Lichess** : importe le PGN de chaque partie avec le jeton du compte Lichess.
4. **État et orchestration** : mémorise les identifiants synchronisés et produit un résumé par exécution.

## Flux de données

1. L’utilisateur lance la synchronisation, ou le mode surveillance déclenche un cycle.
2. L’outil interroge Chess.com pour les parties du compte configuré.
3. Il filtre les parties terminées et les compare à l’état local.
4. Pour chaque nouvelle partie, il envoie le PGN à Lichess.
5. Après confirmation de Lichess, il marque la partie comme synchronisée.
6. Il affiche un résumé, sans enregistrer de secret dans Git.

## Gestion des erreurs

- Une erreur réseau ou d’authentification ne marque jamais une partie comme importée.
- Une erreur sur une partie ne bloque pas l’essai des autres parties.
- L’état est écrit de façon atomique après chaque import réussi.
- Les erreurs expliquent l’action à effectuer : vérifier l’identifiant, le jeton, la connexion ou réessayer plus tard.

## Vérification

- Tests unitaires des filtres de parties et du suivi d’état.
- Tests simulés des réponses Chess.com et Lichess, y compris les erreurs réseau.
- Test manuel avec une partie Chess.com existante et un import Lichess réel après fourniture du jeton.

## Évolutions prévues

- Créer un parcours d’analyse et des exercices à partir des parties importées.
- Ajouter une extension qui déclenche la synchro dès la fin d’une partie.
- Ajouter un espace d’entraînement contre un bot Lichess.
