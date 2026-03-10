"""
My first Airflow DAG - a simple smoke test.
"""
from airflow.sdk import DAG, task
from datetime import datetime

with DAG(
    dag_id="hello_airflow",
    start_date=datetime(2024, 1, 1),
    schedule=None,           # Manual trigger only
    catchup=False,           # Don't backfill old dates
    tags=["example"],
) as dag:

    @task
    def say_hello():
        print("Hello from Airflow! If you see this in the logs, everything works.")
        return "success"

    @task
    def say_goodbye(result):
        print(f"Previous task returned: {result}")
        print("Goodbye! Your Airflow setup is working correctly.")

    result = say_hello()
    say_goodbye(result)