E-Commerce Graph Recommendations
Project Overview
This project demonstrates an e-commerce recommendation engine using PostgreSQL, Neo4j, and Python (FastAPI), orchestrated with Docker Compose. Relational transactional data is transformed into a graph database to generate personalized product recommendations.

Key Features
Load e-commerce dataset (Olist subset + synthetic events)
ETL from Postgres to Neo4j

Graph-based recommendations:
Collaborative filtering (co-occurrence of product interactions)
Content-based (category similarity)
Graph algorithms (PageRank, similarity measures)
FastAPI endpoints to serve recommendations
Fully containerized stack for easy deployment

Repository Structure
.
├── docker-compose.yml
├── postgres/
│ └── init/
│ ├── 01_schema.sql
│ └── 02_seed.sql
├── neo4j/
│ ├── data/
│ └── import/
├── app/
│ ├── main.py
│ ├── etl.py
│ ├── queries.cypher
│ ├── start.sh
│ └── requirements.txt
└── README.txt

Prerequisites
Docker Desktop
At least 4 GB free RAM
Available ports: 5432 (Postgres), 7474 & 7687 (Neo4j), 8000 (FastAPI)
Setup and Run

Start the stack:
docker compose up -d

Check logs:
docker compose logs -f

Verify Postgres tables:
docker compose exec -T postgres psql -U app -d shop -c "\dt"

Run ETL:
docker compose exec -it app python etl.py

Check FastAPI health:
curl http://localhost:8000/health

API Endpoints
GET /health – service status
GET /recs/{customer_id} – recommendations for a customer
GET /popular – globally popular products

ETL Workflow
Wait for Postgres and Neo4j readiness
Create Neo4j schema & constraints
Extract data from Postgres tables
Transform relational data into graph structure
Load nodes and relationships into Neo4j:
Customer -> Order (PLACED)
Order -> Product (CONTAINS)
Product -> Category (IN_CATEGORY)
Customer -> Product (VIEWED, CLICKED, ADDED_TO_CART)

Testing
Run the helper script to verify the stack:
chmod +x scripts/check_containers.sh
bash scripts/check_containers.sh

Future Improvements
Incremental ETL for large datasets
Neo4j indexing and query optimization
Unit and integration tests
CI/CD pipelines and Kubernetes deployment
Enhanced recommendation strategies (hybrid, embeddings)

For the result, please check the "Result 1" and "Result 2"
