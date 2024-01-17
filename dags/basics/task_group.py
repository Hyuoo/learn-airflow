from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime

"""
TaskGroup을 사용해서 그룹핑을 수행 할 수 있다.
[A, B, C] >> [D, E]처럼 list to list로 의존성 설정을 할 수 없음. (error)

group 내에 속한 task는 'group.task'라는 task_id를 갖게 된다.
중첩된 그룹의 경우에는 'group.sub_group.task'

그렇기 때문에 task 이름은 중복되어도 상관없음.


그룹단위로 시작과 종료를 명확히 하는게 좋다.
[ group_start >> [ group_tasks ] >> group_end ]


(taskgroup을 옛날엔 subDAG라고 불렀다.)
"""

with DAG(
    dag_id="basic_task_group",
    start_date=datetime(2024,1,1),
    schedule=None,
    tags=["example", "basic"]
) as dag:

    start_task = EmptyOperator(task_id="start_task")
    end_task = EmptyOperator(task_id="end_task")

    with TaskGroup("group_1", tooltip="group_description") as group_1:
        task1 = EmptyOperator(task_id="task1")
        task2 = EmptyOperator(task_id="task2")
        task3 = EmptyOperator(task_id="task3")

        task1 >> [task2, task3]

    with TaskGroup("group_2") as group_2:
        task1 = EmptyOperator(task_id="task1")
        task2 = EmptyOperator(task_id="task2")

        with TaskGroup("sub_group", tooltip="is_sub_group_task") as sub_group:
            sub_task1 = EmptyOperator(task_id="sub_task1")
            sub_task2 = EmptyOperator(task_id="sub_task2")
            sub_task3 = EmptyOperator(task_id="sub_task3")

            [sub_task1, sub_task2] >> sub_task3

        task1 >> sub_group >> task2
    
    start_task >> group_1 >> group_2 >> end_task