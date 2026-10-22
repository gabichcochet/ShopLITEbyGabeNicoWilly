# ShopLite — Partie 2 : compléter le CRUD

ShopLite ne savait faire que le C (Create) : enregistrer une commande. Nous ajoutons le R (Read), le U (Update) et le D (Delete) en réutilisant le même cœur, le même port sortant et les mêmes adaptateurs.

## 1. Features métier ajoutées

- **C : enregistrer une commande** (port `RegisterOrder`)
  - Le nom du client est obligatoire ; un nom composé uniquement d'espaces est refusé.
  - Le montant HT doit être un nombre fini et strictement positif.
  - Remise de 10 % si le client est fidèle, puis TVA de 20 % sur le montant remisé.
  - La date de création est fournie par l'horloge.
- **R : consulter une commande** (port `GetOrder`)
  - Renvoie la commande correspondant au numéro donné.
  - Erreur « aucune commande n°X » si le numéro n'existe pas.
- **R : lister les commandes** (port `ListOrders`)
  - Renvoie toutes les commandes, par numéro croissant.
  - Affiche « Aucune commande. » s'il n'y en a pas.
- **U : modifier une commande** (port `UpdateOrder`)
  - Seuls le montant HT et la fidélité peuvent changer.
  - La remise et le TTC sont toujours recalculés, jamais saisis.
  - Le nom du client, la date et le numéro restent inchangés.
  - Erreur si le numéro n'existe pas ; un montant invalide ne modifie rien.
- **D : supprimer une commande** (port `DeleteOrder`)
  - Suppression définitive.
  - Erreur si le numéro n'existe pas.

## 2. Ports et adaptateurs ajoutés au schéma

- **Ports entrants (PE)** : `GetOrder`, `ListOrders`, `UpdateOrder`, `DeleteOrder` s'ajoutent à `RegisterOrder`. Ce sont des contrats, implémentés par `GetOrderService`, `ListOrdersService`, `UpdateOrderService` et `DeleteOrderService`.
- **Port sortant (PS)** : `OrderRepository` reçoit les méthodes `find_by_id`, `find_all`, `update` et `delete`, en plus de `save`.
- **Adaptateurs sortants (AS)** : `SqliteOrderRepository` et `InMemoryOrderRepository` implémentent ces nouvelles méthodes.
- **Adaptateur entrant (AE)** : `ConsoleCli` propose un menu (1 enregistrer, 2 consulter, 3 lister, 4 modifier, 5 supprimer, 0 quitter).
- **Domaine** : ajout de l'erreur `OrderNotFoundError` et de la méthode `Order.change_amount`, qui recalcule le prix lors d'une modification.
- Le port `Clock` ne change pas : seule la création d'une commande a besoin de la date.

Toutes les flèches pointent vers le centre : les adaptateurs dépendent des ports, et le domaine ne dépend de rien d'extérieur. Chaque PE est implémenté par un cas d'utilisation (`…Service`).

## 3. Tests unitaires

40 tests, tous au vert. Pour les lancer, depuis `projet_initial_diagnostic_architecture/` :

    python -m unittest discover -s tests -t . -v

- **`test_pricing.py`** (3 tests) : remise puis TVA ; 50 € fidèle donne 54 € TTC, et non 55 €.
- **`test_order.py`** (9 tests) : nom vide ou en espaces refusé, montant ≤ 0 refusé, `nan` et `inf` refusés, modification qui recalcule la remise et le TTC tout en gardant le nom, la date et le numéro.
- **`test_use_cases.py`** (11 tests) : les 5 cas d'utilisation testés avec `InMemoryOrderRepository` et `FixedClock`, donc sans base ni horloge réelle. Commande invalide jamais sauvegardée, numéro inexistant, modification invalide sans effet, suppression.
- **`test_sqlite_repository.py`** (4 tests) : sur une base temporaire, écriture dans la table `orders`, ids qui s'incrémentent, relecture, mise à jour et suppression.
- **`test_console_cli.py`** (6 tests) : saisie illisible qui n'atteint pas le cas d'utilisation, virgule refusée, parcours CRUD complet dans le menu, numéro non entier, choix inconnu.
- **`test_characterization.py`** (7 tests) : non-régression sur le vrai `main()`, écrits sur le code d'origine avant toute modification. Ils vérifient que le comportement est préservé (Alice → 108,00 €, Bob → 120,00 €, messages d'erreur) et que les corrections d'entrées fonctionnent.

Les tests du domaine et des cas d'utilisation sont possibles grâce aux ports : on remplace SQLite et l'horloge par de faux adaptateurs, sans toucher au code métier.

## 4. Justification des choix d'architecture

- **Un cas d'utilisation par opération**, plutôt qu'un gros `OrderService` : chaque classe a une seule raison de changer, et la console comme une future API HTTP appellent exactement les mêmes.
- **Des ports entrants explicites** : chaque opération a un contrat (`RegisterOrder`, `GetOrder`…) et une implémentation (`RegisterOrderService`…). La console ne dépend que des contrats et n'appelle aucune règle métier directement.
- **Pas de dépendance entre cas d'utilisation** : `UpdateOrderService` lit directement dans le repository au lieu de passer par un autre service.
- **Un seul port `OrderRepository`, enrichi**, plutôt qu'un port par opération : les cinq opérations portent sur la même donnée, et découper ajouterait des interfaces sans variation réelle.
- **Le recalcul est dans l'entité** (`change_amount`) : le TTC ne peut jamais devenir incohérent avec le HT, quel que soit l'appelant.
- **Suppression définitive** plutôt qu'une annulation : c'est le strict nécessaire du CRUD. Une annulation avec statut serait une évolution métier à part (nouvelle colonne, nouvelles règles).
- **Modification limitée au montant et à la fidélité** : ce sont les seules données qui influencent le prix ; le nom et la date identifient la commande d'origine.
- **Conversion du texte dans la console, règles dans le domaine** : la console vérifie le format de la saisie (`parse_amount`), le domaine décide si la commande est valide. Une API HTTP pourrait ainsi réutiliser les mêmes règles.
