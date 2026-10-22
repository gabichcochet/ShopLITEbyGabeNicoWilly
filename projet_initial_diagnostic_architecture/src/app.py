"""ShopLite : application volontairement monolithique pour exercice de diagnostic.

Ce fichier mélange volontairement plusieurs responsabilités :
interface utilisateur, validation, règles métier, persistance et affichage.
"""

import sqlite3
from datetime import datetime

DB_PATH = "shoplite.db"
LOYALTY_DISCOUNT = 0.10
VAT_RATE = 0.20


def create_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            amount_ht REAL NOT NULL,
            discount REAL NOT NULL,
            amount_ttc REAL NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    connection.commit()
    connection.close()


def main():
    # Présentation / collecte des données
    print("=== ShopLite — Enregistrement d'une commande ===")
    customer_name = input("Nom du client : ")
    amount_text = input("Montant HT : ")
    loyalty_answer = input("Client fidèle ? (oui/non) : ")

    # Validation technique et métier mélangées
    if customer_name == "":
        print("Erreur : le nom du client est obligatoire.")
        return

    try:
        amount_ht = float(amount_text)
    except ValueError:
        print("Erreur : le montant doit être un nombre.")
        return

    if amount_ht <= 0:
        print("Erreur : le montant doit être positif.")
        return

    is_loyal_customer = loyalty_answer.lower() == "oui"

    # Règles métier placées dans le point d'entrée
    discount = amount_ht * LOYALTY_DISCOUNT if is_loyal_customer else 0
    amount_after_discount = amount_ht - discount
    amount_ttc = amount_after_discount * (1 + VAT_RATE)

    # Persistance SQLite directement couplée au scénario métier
    create_database()
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO orders
        (customer_name, amount_ht, discount, amount_ttc, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            customer_name,
            amount_ht,
            discount,
            amount_ttc,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    order_id = cursor.lastrowid
    connection.commit()
    connection.close()

    # Affichage du résultat mélangé au traitement
    print("\nCommande enregistrée !")
    print(f"Numéro : {order_id}")
    print(f"Client : {customer_name}")
    print(f"Montant HT : {amount_ht:.2f} €")
    print(f"Remise : {discount:.2f} €")
    print(f"Montant TTC : {amount_ttc:.2f} €")


if __name__ == "__main__":
    main()
