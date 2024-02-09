from airflow import DAG
from airflow.macros import *
from airflow.operators.python import PythonOperator
import os
import sys

sys.path.append("../")
from plugins import slack, redshift_summary

"""
summary_v1의 내용을 다음 딕셔너리 형태를 갖는 *.py파일을 생성하여 각 파일별로 CTAS ELT를 구현 함.
{"table": "", "schema": "", "main_sql": "SELECT ~", "input_check": [], "output_check": [],}

- RedshiftSummaryOperaotr라는 커스텀 오퍼레이터를 생성
- build_summary_table 함수를 통해서 오퍼레이터를 사용함. (helper function)

이 일련의 과정은 이후 dbt를 통해서 구현할 수 있다.
"""

"""
dags/
+--examples/
|  +--kdt_lesson_build_summary_v2.py
|
+--plugins/
|  +--redshift_summary.py
|
+--config/
   +--mau_summary.py
   +--nps_summary.py
"""

DAG_ID = "example_kdt_lesson_build_summary_v2"
dag = DAG(
    DAG_ID,
    start_date=datetime(2024, 1, 1),
    schedule="@once",
    max_active_runs=1,
    concurrency=1,      # 동시성. 모든 실행중인 DAG에서의 최대 TASK 수  # default: max_active_tasks_per_dag
    catchup=False,
    default_args= {
        'owner': 'hyuoo',
        'on_failure_callback': slack.on_failure_callback,
        'retries': 1,
        'retry_delay': timedelta(minutes=1),
    },
    tags=["example", "kdt"],
)

# this should be listed in dependency order (all in analytics)
tables_load = [
    "mau_summary",
    "nps_summary",
]

# dag_root_path = os.path.dirname(os.path.abspath(__file__))
# 파일을 dags/examples/로 옮겨놔서 상위디렉토리가 dags/
dag_root_path = os.path.dirname(os.path.abspath(__file__+"/.."))
redshift_summary.build_summary_table(dag_root_path, dag, tables_load, "redshift_dev_db")