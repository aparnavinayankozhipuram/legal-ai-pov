import sqlite3

DATABASE_PATH = "data/legal_ai.db"


def create_database():
    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            company_name TEXT,
            contract_type TEXT,
            upload_date TEXT
        )
    """)

    connection.commit()
    connection.close()

    print("Database created successfully.")
def add_contract(filename, company_name, contract_type, upload_date):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO contracts
        (filename, company_name, contract_type, upload_date)
        VALUES (?, ?, ?, ?)
    """, (filename, company_name, contract_type, upload_date))

    connection.commit()
    connection.close()

    print("Contract added successfully.")

def get_contracts():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, filename, company_name, contract_type, upload_date
        FROM contracts
    """)

    contracts = cursor.fetchall()

    connection.close()

    return contracts

if __name__ == "__main__":
    create_database()

    contracts = get_contracts()

    for contract in contracts:
        print(contract)