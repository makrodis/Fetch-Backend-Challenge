import os 
import sqlite3

def singleton(cls):
    "Ensures only one instance of the database is ever created."
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance

class DatabaseDriver(object):
    def __init__(self):
        self.conn = sqlite3.connect("transactions.db", check_same_thread=False)
        self.create_transactions_table()

    def create_transactions_table(self):
        self.conn.execute("""CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payer TEXT,
        points INTEGER,
        timestamp DATETIME
        );
        """)
    
    def insert_transaction(self, payer, points, timestamp):
        """
        Inserts a new transaction into the database.
        """
        cursor = self.conn.execute("INSERT INTO transactions(payer, points, timestamp) VALUES(?,?,?)", (payer, points, timestamp))
        self.conn.commit()

    def get_all_transactions(self):
        """
        Retrieves all transactions from the database, ordered by timestamp in ascending order.

        Returns: A list of dictionaries, where each dictionary represents a single transaction.
        """
        #return a list of dictionaries
        cursor = self.conn.execute("""SELECT * FROM transactions ORDER BY timestamp ASC;""")
        transactions = []
        for row in cursor:
            transactions.append({
                "id" : row[0],
                "payer" : row[1],
                "points" : row[2],
                "timestamp" : row[3],
            })
        return transactions

    def get_total(self):
        """
        Retrieves the total sum of points from all transactions in the database.

        Returns: An integer of the total sum of points.
        """
        cursor = self.conn.execute("""SELECT SUM(points) FROM transactions;""")
        total = cursor.fetchone()[0]
        return total
        

    def update_transaction(self, id, points):
        """
        Updates the points for a specific transaction in the database.
        """
        cursor = self.conn.execute("UPDATE transactions SET points = ? WHERE id = ?", (points, id))
        self.conn.commit()

    def get_amount_by_payer(self):
        """
        Retrieves the total amount of points for each payer from the transactions table in the database.

        Returns:
            dict: A dictionary where the key is the payer and the value is the total amount of points.
        """
        cursor = self.conn.execute("""SELECT payer, SUM(points) FROM transactions GROUP BY payer;""")
        results = {}
        for row in cursor:
            results[row[0]] = row[1]
        return results

DatabaseDriver = singleton(DatabaseDriver)