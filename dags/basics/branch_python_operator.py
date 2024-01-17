from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.operators.python import BranchPythonOperator
from datetime import datetime, timedelta


"""
조건에 따라 task 간의 branch를 정의할 수 있는 오퍼레이터

BranchTask >> [A, B, C]
이런식으로 의존성을 설정해준 뒤, BranchTask의 리턴값으로 branch를 설정한다.
- return 'A'
- return ['B', 'C']
등과 같이 'task_id'를 리턴해주면 해당 태스크가 실행된다.
- return None
None값을 리턴하게 되면 모든 다운스트림은 Skip이 된다.


이런식으로 됨.
Following branch ['even_task', 'extra_task', 'dangling_task']
Skipping tasks ['odd_task', 'no_returned_task']

- return되지 않는 모든 태스크는 실행되지 않음.
- 의존성이 설정 안된 태스크는 넘겨줘도 실행되지 않음.
    (에러는 발생하지 않고 무시됨)
"""

def decide_branch(**context):
    current_minute = context["logical_date"].minute
    print(f"current minute: {current_minute}")
    
    if current_minute%15 == 0:  # None을 반환하면 다운스트림 스킵
        return None

    if current_minute%2:  # task_id에 해당하는 문자열을 리턴한다.
        return 'odd_task'
    else:  # list로 리턴해도 된다.
        return ['even_task', 'extra_task', 'dangling_task']


dag = DAG(
    'basic_branch_python_operator',
    start_date=datetime(2024,1,1),
    schedule=timedelta(minutes=3),
    catchup=False,
    tags=["example", "basic"],
)
    
start_task = EmptyOperator(task_id='start_task', dag=dag)

odd_task = EmptyOperator(task_id='odd_task', dag=dag)
even_task = EmptyOperator(task_id='even_task', dag=dag)
extra_task = EmptyOperator(task_id='extra_task', dag=dag)
no_returned_task = EmptyOperator(task_id='no_returned_task', dag=dag)

decide_branch_task = BranchPythonOperator(
    task_id='decide_branch_task',
    python_callable=decide_branch,
    dag=dag,
    )


not_work_task = BashOperator(task_id='not_work_task', bash_command='exit 9', dag=dag)
dangling_task = EmptyOperator(task_id='dangling_task', dag=dag)


start_task >> decide_branch_task

decide_branch_task >> [even_task, odd_task]
decide_branch_task >> extra_task
decide_branch_task >> no_returned_task

not_work_task >> dangling_task