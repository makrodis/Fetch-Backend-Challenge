from flask import Flask, request
import json 
import db 

app = Flask(__name__)
DB = db.DatabaseDriver()

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/add', methods=['POST'])
def add():
    """
    Extracts payer, points, and timestamp from the request body and inserts a new transaction into the database.
    """

    body = json.loads(request.data)
    payer = body['payer']
    points = body['points']
    timestamp = body['timestamp']
    DB.insert_transaction(payer, points, timestamp)
    return "", 200


@app.route('/spend', methods=['POST'])
def spend():
    """
    Extracts points from the request body and checks if the user has enough points in their account.
    If the user has enough points, it spends the points from the payers in order of when the transactions occured.

    Returns:
        - If the user has enough points:
            - Processed transactions and the number of points spent.
            - A status code of 200.
        - If the user does not have enough points:
            - A string response indicating that the user does not have enough points.
            - A status code of 400.
    """

    body = json.loads(request.data)
    points = body['points']
    list_of_transactions = DB.get_all_transactions()
    total = DB.get_total()
    if (total is None or total < points):
        return "User does not have enough points", 400
    points_removed = 0
    txn = 0
    update_transactions = []
    while points_removed < points:
        if (list_of_transactions[txn]['points'] != 0):
            points_removed += list_of_transactions[txn]['points']
            update_transactions.append(list_of_transactions[txn])
        txn+=1
    return process_used_transactions(update_transactions, points_removed, points)


def process_used_transactions(update_transactions, points_removed, points):
    """
    This function processes the transactions that were used to spend points.
    The function updates the transactions in the database to reflect the points that were spent, 
    and returns a list of the transactions with their points subtracted and a status code of 200.

    Returns:
        A list of dictionaries with payer and points information.
    """
    if (points_removed != points):
        last_transaction = update_transactions[-1]
        remaining_points = points_removed - points
        spent_points = last_transaction['points'] - remaining_points 
        last_transaction['points'] = spent_points
        DB.update_transaction(last_transaction['id'], remaining_points)
    transaction_subtracted = [{'payer' : last_transaction['payer'], 'points' : -last_transaction['points'], 'timestamp' : last_transaction['timestamp']}]
    update_transactions.pop()
    for transaction in update_transactions:
        DB.update_transaction(transaction['id'], 0)
        transaction_subtract = { 'payer' : transaction['payer'], 'points' : -transaction['points'], 'timestamp' : transaction['timestamp']}
        transaction_subtracted.append(transaction_subtract)

    return format_transacitons(transaction_subtracted), 200

def format_transacitons(transactions):
    """
    Format the given transactions into a list of dictionaries with payer and points information.

    Returns:
        A list of dictionaries with payer and points information.   
    """
    formated = {}
    for transaction in transactions:
        payer = transaction['payer']
        points = transaction['points']
        if payer in formated:
            formated[payer] += points
        else:
            formated[payer] = points
    return [{"payer": payer, "points": points} for payer, points in formated.items()]


@app.route('/balance')
def balance():
    """
    Retrieves the current balance of points for each payer.

    Returns:
        A dictionary with payer names as keys and their respective point balances as values.
    """

    return DB.get_amount_by_payer(), 200
    

app.run(port=8000)

