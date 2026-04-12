import pendulum
from airflow.sdk import dag, task

@dag(
    schedule=None,
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example"],
)
def hello_world_dag():
    @task()
    def say_hello():
        print("Hello World!")

    # Invoke the task
    say_hello()

# Register the DAG
hello_world_dag()

