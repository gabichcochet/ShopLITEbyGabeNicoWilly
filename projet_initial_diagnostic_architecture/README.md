# Projet fil rouge — Diagnostic d'architecture

## Contexte

Vous rejoignez l'équipe qui maintient **ShopLite**, une petite application en ligne de commande permettant d'enregistrer des commandes clients.

Le programme fonctionne, mais il est devenu difficile à modifier et à tester. Votre mission initiale n'est **pas** de le réécrire : vous devez comprendre son fonctionnement, repérer les problèmes d'architecture et proposer une cible plus maintenable.

## Prérequis

- Python 3.10 ou supérieur
- Aucune dépendance externe

## Lancer l'application

Depuis la racine du projet :

```bash
python src/app.py
```

La base SQLite `shoplite.db` est créée automatiquement à la première exécution.

Le programme demande un nom de client, un montant hors taxes et si le client bénéficie d'une remise fidélité. Il enregistre ensuite la commande et affiche un récapitulatif.

Exemple de scénario :
- Client : `Alice`
- Montant HT : `100`
- Client fidèle : `oui`

Comportement attendu : nom non vide ; montant HT strictement positif ; remise fidélité de 10 % ; TVA de 20 % appliquée après remise ; commande enregistrée puis récapitulatif affiché.

## Travail demandé — Diagnostic initial

Sans modifier le code au premier passage :

1. Exécutez l'application et résumez le scénario métier.
2. Dessinez l'architecture actuelle et identifiez les composants réellement présents.
3. Repérez au moins **trois** responsabilités mélangées ou dépendances problématiques.
4. Identifiez une règle métier qui devrait pouvoir être testée sans base de données ni saisie clavier.
5. Proposez une architecture cible comprenant, selon votre analyse, présentation, cas d'utilisation, domaine métier, ports et adaptateurs techniques.
6. Proposez un plan de refactorisation progressif qui préserve le comportement existant.

## Questions à discuter

- Où se trouvent les règles de calcul ?
- Peut-on tester la remise sans lancer l'application interactive ?
- Que faudrait-il changer pour remplacer SQLite par une API distante ou un stockage en mémoire ?
- Que faudrait-il changer pour appeler le même cas d'utilisation depuis une API HTTP ?
- Le programme gère-t-il correctement toutes les entrées invalides ? Comment le vérifier ?

## Important

Le code de départ est volontairement imparfait pour les besoins pédagogiques. **Ne corrigez pas tout immédiatement** : commencez par observer, formuler des hypothèses et justifier vos choix.
