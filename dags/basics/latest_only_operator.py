from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.latest_only import LatestOnlyOperator
from datetime import datetime


"""
백필 수행 시 불필요한 반복 태스크를 스킵하기 위함.
예를들어 메일링 작업

Task의 실행 시간이 아래 조건을 만족 할 경우에만 실행한다.
(logical_date + 1) < now <= (logical_date + 2)

즉, 실행중인 task가 현재 슬롯에서 실행되었어야 할 job일 경우에만 실행한다.

- LatestOnly 자체는 success상태로 종료되고, 이후 태스크가 skipped가 된다.
- 모든 downstream이 연쇄적으로 skipped 됨.


# BaseBranchOperator를 상속하여 다음과 같이 구현됨.
# downstream을 모두 skip되게 함.
if not left_window < now <= right_window:
   return []
else:
   return list(context["task"].get_direct_relative_ids(upstream=False))
"""

"""
ex)
- 스케줄링이 1시간 간격
- Task가 각각 13:00, 14:00, 15:00, 16:00 에 실행 될 계획
- 현재 시각은 15:20
- backfill을 사용해서 13:00, 14:00, 15:00 작업이 실행된다고 가정

현재 시각에 해당하는 작업시간은 15:00이고,
15:00에 실행되는 작업의 logical_date는 14:00이다.

그래서 15:00 < (15:20) <= 16:00이 성립되어 15:00작업은 실행된다.

13:00, 14:00은 범위에 해당되지 않아 실행되지 않음.
"""

"""
schedule이 None인 경우에는 무조건 성공한다.
"""


with DAG(
    dag_id="basic_latest_only_operator",
    start_date=datetime(2024,1,10),
    schedule='@daily',
    catchup=True,
    tags=["example", "basic"]
) as dag:
    
    t1 = EmptyOperator(task_id='task1')
    t2 = LatestOnlyOperator(task_id='latest_only')
    t3 = EmptyOperator(task_id='task3')
    t4 = EmptyOperator(task_id='task4')
    t5 = EmptyOperator(task_id='task5')

    t1 >> t2 >> [t3, t4] >> t5