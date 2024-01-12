from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime


dag = DAG(
    "basic_bash_operator",
    start_date=datetime(2024,1,1),
    catchup=False,
    schedule=None,
    tags=["example", "basic"],
)

task1 = BashOperator(
    task_id="bash_task1",
    bash_command="pwd",
    dag=dag
)

task2 = BashOperator(
    task_id="bash_task2",
    bash_command='echo "hello"'
    'exit 99',
    dag=dag
)

last_task = EmptyOperator(task_id="last_task", dag=dag)

[task1, task2] >> last_task