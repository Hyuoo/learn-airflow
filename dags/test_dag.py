from airflow.models.dag import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.datetime import BranchDateTimeOperator
from airflow.providers.amazon.aws.transfers import s3_to_redshift

from datetime import datetime, timedelta
import pendulum


dag = DAG(
    "test_dag",
    schedule=None,
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=[ "test" ],
)

start = EmptyOperator(task_id="start", dag=dag)
end = EmptyOperator(task_id="end", dag=dag)

start >> end