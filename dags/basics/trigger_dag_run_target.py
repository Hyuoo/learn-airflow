from airflow.models import DAG
from airflow.decorators import task
from airflow.operators.bash import BashOperator
from datetime import datetime
import logging

@task
def triggered_task_function(**context):
    logging.info(f'dag_run: {context["dag_run"]}')
    logging.info(f'conf: {context["dag_run"].conf.get("value")}')
    logging.info(f'ti: {context["ti"]}')
    logging.info(f'data_interval_start: {context["data_interval_start"]}')
    logging.info(f'logical_date: {context["logical_date"]}')

with DAG(
    dag_id="basic_trigger_dag_run_target",
    start_date=datetime(2024,1,1),
    schedule=None,  # 트리거로 실행되기 때문에 None으로 설정한다.
    tags=["example", "basic"]
) as dag:
    
    task1 = BashOperator(
        task_id='task1',
        bash_command='echo "{{ ds }}, {{ dag_run.conf.get("value", "none") }}"'
    )

    task2 = triggered_task_function()
