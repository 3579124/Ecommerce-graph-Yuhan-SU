import time
from pathlib import Path
import psycopg2
from neo4j import GraphDatabase
import pandas as pd


def wait_for_postgres():
    print(" Waiting for PostgreSQL to be ready...")
    for i in range(10):
        try:
            conn = psycopg2.connect(
                dbname="shop",
                user="user",
                password="password",
                host="postgres",
                port="5432"
            )
            conn.close()
            print(" PostgreSQL is ready!")
            return
        except Exception:
            time.sleep(3)
    raise Exception(" PostgreSQL is not responding.")


def wait_for_neo4j():
    print(" Waiting for Neo4j to be ready...")
    for i in range(10):
        try:
            driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "password"))
            with driver.session() as session:
                session.run("RETURN 1")
            driver.close()
            print(" Neo4j is ready!")
            return
        except Exception:
            time.sleep(3)
    raise Exception(" Neo4j is not responding.")


# Cypher
def run_cypher_file(session, file_path):
    print(f" Running Cypher file: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        queries = f.read().split(";")
        for query in queries:
            query = query.strip()
            if query:
                session.run(query)
    print(" Cypher schema applied.")


# Main ETL
def etl():
    wait_for_postgres()
    wait_for_neo4j()

    # Connect to PostgreSQL
    pg_conn = psycopg2.connect(
        dbname="shop",
        user="user",
        password="password",
        host="postgres",
        port="5432"
    )
    pg_cursor = pg_conn.cursor()

    # Connect to Neo4j
    neo4j_driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "password"))

    # Apply Neo4j schema
    queries_path = Path(__file__).with_name("queries.cypher")
    with neo4j_driver.session() as session:
        run_cypher_file(session, queries_path)

        # Extract data from PostgreSQL
        print(" Extracting data from PostgreSQL...")
        tables = ["categories", "products", "customers", "orders", "order_items", "events"]
        data = {}
        for t in tables:
            pg_cursor.execute(f"SELECT * FROM {t};")
            colnames = [desc[0] for desc in pg_cursor.description]
            rows = pg_cursor.fetchall()
            data[t] = pd.DataFrame(rows, columns=colnames)
        print(" Data extracted.")

        # Load into Neo4j
        print(" Loading data into Neo4j...")

        # Categories
        for _, row in data["categories"].iterrows():
            session.run("""
                MERGE (c:Category {id: $id})
                SET c.name = $name
            """, id=row["id"], name=row["name"])

        # Products
        for _, row in data["products"].iterrows():
            session.run("""
                MERGE (p:Product {id: $id})
                SET p.name = $name, p.price = $price
                WITH p
                MATCH (c:Category {id: $category_id})
                MERGE (p)-[:IN_CATEGORY]->(c)
            """, id=row["id"], name=row["name"], price=float(row["price"]), category_id=row["category_id"])

        # Customers
        for _, row in data["customers"].iterrows():
            session.run("""
                MERGE (c:Customer {id: $id})
                SET c.name = $name, c.join_date = $join_date
            """, id=row["id"], name=row["name"], join_date=row["join_date"])

        # Orders
        for _, row in data["orders"].iterrows():
            session.run("""
                MERGE (o:Order {id: $id})
                SET o.order_date = $order_date
                WITH o
                MATCH (c:Customer {id: $customer_id})
                MERGE (c)-[:PLACED]->(o)
            """, id=row["id"], order_date=row["ts"], customer_id=row["customer_id"])

        # Order items
        for _, row in data["order_items"].iterrows():
            session.run("""
                MATCH (o:Order {id: $order_id})
                MATCH (p:Product {id: $product_id})
                MERGE (o)-[:CONTAINS {quantity: $quantity}]->(p)
            """, order_id=row["order_id"], product_id=row["product_id"], quantity=row["quantity"])

        # Events
        for _, row in data["events"].iterrows():
            session.run("""
                MATCH (c:Customer {id: $customer_id})
                MATCH (p:Product {id: $product_id})
                MERGE (c)-[r:EVENT {type: $event_type}]->(p)
            """, customer_id=row["customer_id"], product_id=row["product_id"], event_type=row["event_type"])

        print(" ETL process completed successfully!")

    pg_cursor.close()
    pg_conn.close()
    neo4j_driver.close()


if __name__ == "__main__":
    etl()
