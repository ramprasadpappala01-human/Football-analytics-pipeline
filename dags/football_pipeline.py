from airflow.sdk import dag, task
from datetime import datetime

# Correct paths pointing to the new mounted volume inside the container
SCRIPT_PATH = "/opt/football_project/extract_load.py"
DBT_PROJECT_PATH = "/opt/football_project/football_dbt"

@dag(
    dag_id="football_pipeline",
    start_date=datetime(2026, 7, 25),
    schedule='@weekly',
    catchup=False,
)
def football_pipeline():
    
    @task.bash
    def extract_load():
        # Runs the script using the container's built-in Linux Python environment
        return f"python {SCRIPT_PATH}"
    
    @task.bash
    def bronze():
        # Points directly to the dbt project folder and passes profiles path if needed
        return f"cd {DBT_PROJECT_PATH} && dbt run --select bronze --profiles-dir ."
        
    @task.bash
    def silver():
        return f"cd {DBT_PROJECT_PATH} && dbt run --select silver --profiles-dir ."
        
    @task.bash
    def gold():
        return f"cd {DBT_PROJECT_PATH} && dbt run --select gold --profiles-dir ."
    
    extract_load() >> bronze() >> silver() >> gold()

football_pipeline()
