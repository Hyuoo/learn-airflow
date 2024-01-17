from airflow import DAG
from airflow.decorators import task
from datetime import datetime

# decorator를 통해 정의하면 함수이름이 task_id가 된다.
@task
def print_hello():
    print("hello!")
    return "hello!"

with DAG(
    dag_id = 'basic_python_decorator',
    start_date=datetime(2024,1,1),
    catchup=False,
    schedule=None,
    tags=['example', 'basic'],
) as dag:

    # 선언 위치는 상관 없음
    # task_id를 직접 지정할수도 있다.
    @task(task_id='deco_task_goodbye')
    def print_goodbye():
        print("goodbye!")
        return "goodbye!"
    
    # decorator task는 인스턴스화를 해야한다.
    print_hello() >> print_goodbye()
