from airflow.models import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime

"""
명시적으로 트리거하기 때문에 Explicit Trigger라고도 한단다.

트리거 대상이 되는 dag는 활성화 상태여야 한다.
그렇지 않으면 queued되기만 하고 실행이 안된다.
"""

with DAG(
    dag_id="basic_trigger_dag_run_operator",
    start_date=datetime(2024,1,1),
    schedule=None,
    tags=["example", "basic"]
) as dag:
    
    trigger_task = TriggerDagRunOperator(
        task_id='trigger_task',
        # 존재하는 dag의 dag_id를 통해서 트리거
        trigger_dag_id='basic_trigger_dag_run_target',
        # airflow.cfg dag_ruin_conf_overrides_params=True일 때 사용 가능한 conf전달
        conf={'value': 'something'},
        # trigger dag의 logical_date를 사용해서 트리거
        execution_date='{{ ds }}',
        # 해당 dag가 실행되었더라도 재실행을 할 지 여부
        reset_dag_run=True,
        # target dag가 끝날 때 까지 기다릴 지 여부 (default=False)
        wait_for_completion=True,
    )