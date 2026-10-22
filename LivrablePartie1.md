# ShopLite — Diagnostic et cible d’architecture hexagonale
## Scénario métier

ShopLite sert à enregistrer une commande client depuis le terminal. L’utilisateur saisit le nom du client, le montant HT et indique si le client est fidèle. Le programme calcule la remise et le TTC, enregistre la commande dans SQLite, puis affiche un récapitulatif.

Les règles métier que nous avons relevées dans le code :

le nom du client est obligatoire ;
le montant HT doit être strictement positif ;
un client fidèle a 10 % de remise sur le HT ;
la TVA de 20 % s’applique après la remise ;
chaque commande reçoit un numéro et une date de création.

Nous avons lancé l’application avec l’exemple du README : Alice, 100 € HT, fidèle → 10,00 € de remise et 108,00 € TTC. Sans fidélité (Bob, 100 €), on obtient 120,00 € TTC.



## Diagnostic

Tout le programme tient dans un seul fichier, et presque tout dans une seule fonction : main(). C’est une source directe de dette technique : cette fonction mélange les trois couches, présentation, métier et infrastructure.


### Problèmes observés

Pour chaque responsabilité, nous indiquons la couche à laquelle elle devrait appartenir.

- **P1 — Le calcul de la remise et de la TVA est écrit directement dans `main()`**
  - Couche concernée : Métier
  - Conséquence : on ne peut pas tester la remise sans lancer le programme interactif.
- **P2 — La lecture clavier (`input()`) est mélangée au scénario**
  - Couche concernée : Présentation
  - Conséquence : impossible de réutiliser le scénario depuis une API HTTP.
- **P3 — La conversion `float()` et la règle « montant > 0 » sont au même endroit**
  - Couche concernée : Présentation et Métier
  - Conséquence : la règle métier dépend de la console.
- **P4 — Le SQL (`sqlite3.connect`, `INSERT`) est dans le scénario**
  - Couche concernée : Infrastructure
  - Conséquence : pour passer à une API ou à un stockage en mémoire, il faut réécrire `main()`.
- **P5 — `create_database()` est appelé à chaque commande**
  - Couche concernée : Infrastructure
  - Conséquence : l'initialisation de la base n'a rien à faire dans le scénario.
- **P6 — `datetime.now()` est appelé directement**
  - Couche concernée : Infrastructure
  - Conséquence : la date ne peut pas être fixée dans un test.
- **P7 — Le récapitulatif est affiché avec `print()` au lieu d'être renvoyé**
  - Couche concernée : Présentation
  - Conséquence : le résultat n'est utilisable que dans la console.
- **P8 — Les taux de remise et de TVA sont des constantes globales du fichier**
  - Couche concernée : Métier
  - Conséquence : ils sont liés au script plutôt qu'au domaine.

Entrées invalides mal gérées, constatées en exécutant le programme :

- **Nom `"   "` (espaces)**
  - Comportement actuel : commande enregistrée avec un nom vide.
  - Attendu : erreur « nom obligatoire ».
- **Montant `nan`**
  - Comportement actuel : plantage `sqlite3.IntegrityError`.
  - Attendu : erreur « montant invalide ».
- **Montant `inf`**
  - Comportement actuel : plantage `sqlite3.IntegrityError`.
  - Attendu : erreur « montant invalide ».
- **Montant `100,50`**
  - Comportement actuel : refusé (« doit être un nombre »).
  - Attendu : comportement conservé, seul le point est accepté.
- **Fidélité `Oui ` (espace final)**
  - Comportement actuel : traité comme non fidèle, sans message.
  - Attendu : accepté comme « oui ».
- **Fidélité `o`, `n`, autre**
  - Comportement actuel : silencieusement non fidèle.
  - Attendu : comportement conservé, tout ce qui n'est pas « oui » vaut « non ».


### Justification

Tous ces problèmes viennent du même endroit : le métier dépend directement des outils techniques. Le couplage est fort, et la moindre modification de la console, de la base ou d’une règle oblige à toucher main().

Concrètement :

pour tester la remise, il faut simuler le clavier, avoir une base SQLite et lire la sortie ;
pour ajouter une API HTTP ou changer de stockage, il faut dupliquer ou réécrire main() ;
chaque modification touche le même bloc de code, sans aucun test pour vérifier qu’on n’a rien cassé.

L’application est petite et elle fonctionne. Une réécriture complète n’est donc pas justifiée : nous proposons de la découper étape par étape.


### Composants cibles

- **Entité métier : `Order`**
  - Porte le nom, le montant HT, la remise, le TTC et la date.
  - Refuse un nom vide ou un montant ≤ 0.
- **Règle métier : `compute_price(amount_ht, is_loyal)`**
  - Applique la remise de 10 % puis la TVA de 20 %.
  - Fonction pure, sans dépendance.
- **Erreur métier : `InvalidOrderError`**
  - Levée quand une règle n'est pas respectée.
- **Cas d'utilisation : `RegisterOrderService`**
  - Implémente le port `RegisterOrder` : crée la commande, la date, l'enregistre et la renvoie.
- **AE – Console : `ConsoleCli`**
  - Lit le clavier, convertit le texte, appelle les ports entrants, affiche le résultat ou l'erreur.
  - Aucune règle métier.
- **AS – SQLite : `SqliteOrderRepository`**
  - Crée la table au démarrage, fait l'`INSERT`, renvoie l'id.
- **AS – Horloge : `SystemClock`**
  - Renvoie `datetime.now()`.
- **Assemblage : `main()`**
  - Crée les adaptateurs et les injecte dans les cas d'utilisation.

  ### Tests à créer

- **Non-régression**
  - Quand : avant l'étape 1.
  - Ce qu'on teste : `main()` en entier.
  - Exemples : Alice 100 € fidèle → 108,00 € ; Bob 100 € → 120,00 € ; nom vide ; `abc` ; `-5` ; `0`.
- **Unitaire domaine**
  - Quand : étapes 1 et 2.
  - Ce qu'on teste : `compute_price`, `Order`.
  - Exemples : fidèle → remise 10 €, TTC 108 € ; non fidèle → 120 € ; nom vide ou montant ≤ 0 → `InvalidOrderError`.
- **Intégration**
  - Quand : étape 3.
  - Ce qu'on teste : `SqliteOrderRepository`.
  - Exemples : sur une base temporaire, écriture dans la table `orders`, ids qui s'incrémentent.
- **Unitaire cas d'utilisation**
  - Quand : étape 4.
  - Ce qu'on teste : `RegisterOrderService`.
  - Exemples : avec `InMemoryOrderRepository` et `FixedClock`, commande enregistrée, bon id, bonne date ; commande invalide → rien n'est enregistré.
- **Adaptateur console**
  - Quand : étape 5.
  - Ce qu'on teste : `ConsoleCli`.
  - Exemples : `abc` ou `100,50` → « le montant doit être un nombre » ; récapitulatif à 2 décimales.
- **Régression des corrections**
  - Quand : étape 6.
  - Ce qu'on teste : domaine et console.
  - Exemples : nom `"   "` refusé ; `nan` et `inf` refusés sans plantage.