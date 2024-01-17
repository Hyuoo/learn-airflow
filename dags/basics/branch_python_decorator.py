from airflow.models import DAG
from airflow.decorators import task
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime


# task decorator를 사용하는것과 같이 branch도 데코레이터로 선언이 가능하다.
@task.branch(task_id="branch_task")
def branch_func(ti=None):
    xcom_value = int(ti.xcom_pull(task_ids="start_task"))
    if xcom_value >= 5:
        return "continue_task"
    elif xcom_value >= 3:
        return "stop_task"
    else:
        return None

dag = DAG('basic_branch_python_decorator',
          start_date=datetime(2024,1,1),
          schedule=None,
          catchup=False,
          tags=["example", "basic"])

start_op = BashOperator(
    task_id="start_task",
    bash_command="echo 5",
    dag=dag,
)

branch_op = branch_func()

continue_op = EmptyOperator(task_id="continue_task", dag=dag)
stop_op = EmptyOperator(task_id="stop_task", dag=dag)


start_op >> branch_op >> [continue_op, stop_op]