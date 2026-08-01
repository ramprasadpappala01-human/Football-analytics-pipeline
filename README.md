# Football Analytics Pipeline 🏆

A fully automated data engineering pipeline that extracts live Premier League 
data, transforms it using dbt medallion architecture, and orchestrates 
everything with Apache Airflow — all containerized with Docker.

## Architecture
API-Football → Python/Pandas → PostgreSQL → dbt → Airflow → Docker

## Tech Stack
- **Extraction**: Python, Requests, Pandas
- **Storage**: PostgreSQL (star schema)
- **Transformation**: dbt Core (bronze/silver/gold)
- **Orchestration**: Apache Airflow
- **Containerization**: Docker + Docker Compose

## Data Models
- `bronze` → raw copies of source tables
- `silver` → cleaned and joined match + player data
- `gold` → league standings, team performance, top scorers

## Key Features
- Incremental load with upsert logic for player stats
- Medallion architecture with dbt
- Weekly scheduling via Airflow DAG
- Fully containerized with Docker Compose

## Pipeline DAG
extract_load → dbt_bronze → dbt_silver → dbt_gold

## Gold Layer Outputs
- `gold_league_standings` — points table (verified against real 2023/24 data)
- `gold_team_performance` — win rate, avg goals, goal difference
- `gold_top_scorers` — ranked by goals with goals per game metric
