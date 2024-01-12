from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def print_hello():
    print("hello!")
    return "hello!"

def print_goodbye():
    print("goodbye!")
    return "goodbye!"


dag = DAG(
    dag_id='basic_python_operator',
    start_date=datetime(2024,1,1),
    catchup=False,
    schedule=None,
    tags=['example', 'basic'],
)

print_hello = PythonOperator(
    task_id = 'print_hello',
    #python_callable에 지정된 함수가 task로 실행된다.
    python_callable = print_hello,
    dag = dag
)

print_goodbye = PythonOperator(
    task_id = 'print_goodbye',
    python_callable = print_goodbye,
    dag = dag
)

print_hello >> print_goodbye
