from fastapi import FastAPI 
import psycopg2

app = FastAPI()

@app.get("/health")
def health_check():
    return {"ok": True}  

@app.get("/customers")
def get_customers():
    conn = psycopg2.connect(
        host="postgres",
        dbname="shop",
        user="user",
        password="password"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM customers;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"customers": rows}
