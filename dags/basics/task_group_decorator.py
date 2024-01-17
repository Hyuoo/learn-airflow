from airflow.decorators import dag, task, task_group
from datetime import datetime

# dag, task, task_group 전부 데코레이터로 하니까 import구문이 깔끔하네


@task
def start_task():
    return "[start_task]"

@task
def end_task() -> None:
    print("[ end_task ]")

@task
def task1(value: int) -> str:
    return f"[ task1 {value} ]"
@task
def task2(value: str) -> str:
    return f"[ task2 {value} ]"
@task
def task3(value: str) -> None:
    print(f"[ task3 {value} ]")

@task_group
def task_group_function(value: int) -> None:
    task3(task2(task1(value)))


@dag(
    dag_id="basic_task_group_decorator",
    start_date=datetime(2024,1,1),
    schedule=None,
    tags=["example", "basic"]
    )
def basic_task_group_decorator_function():
    start = start_task()
    end = end_task()
    for i in range(3):
        start >> task_group_function(i) >> end

basic_task_group_decorator_function()