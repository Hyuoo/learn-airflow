from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.python import get_current_context

from datetime import datetime
from pprint import pprint

def print_context(ti=None, **context):
    # ti=None을 명시해서 task instance를 사용하거나
    # **context를 명시해서 여러 정보를 사용할 수 있다.
    # # ! ti=None 이렇게 인스턴스를 아예 받아버리면 context에는 ti가 포함되지 않는다.
    # # 또한 'ti'와 'task_instance'가 별개로 들어와서, ti=None 해도 task_instance를 사용할 수는 있다.
    print("== context_print ==")
    print(context.keys(), "\n")
    pprint(context)
    print("== end ==")
    print("ti:",ti)

def get_context_function():
    # context를 이렇게 사용하는걸 추천한다고 함.
    # (2.6.3의 소스코드에 써있는 주석에서.)
    # 그리고 이렇게 사용할 경우 ti=None을 써도 context["ti"]가 가능하다.
    context = get_current_context()
    print(context["ds"])
    print(context["params"])

    ti = context["ti"]
    print(ti)
    print(f"task: {ti.dag_id} {ti.task_id} {ti.execution_date}")
    print(f"{ti.log_url}")


# dict_keys(['conf', 'dag', 'dag_run', 'data_interval_end', 'data_interval_start', 'ds', 'ds_nodash', 'execution_date', 'expanded_ti_count', 'inlets', 'logical_date', 'macros', 'next_ds', 'next_ds_nodash', 'next_execution_date', 'outlets', 'params', 'prev_data_interval_start_success', 'prev_data_interval_end_success', 'prev_ds', 'prev_ds_nodash', 'prev_execution_date', 'prev_execution_date_success', 'prev_start_date_success', 'run_id', 'task', 'task_instance', 'task_instance_key_str', 'test_mode', 'ti', 'tomorrow_ds', 'tomorrow_ds_nodash', 'triggering_dataset_events', 'ts', 'ts_nodash', 'ts_nodash_with_tz', 'var', 'conn', 'yesterday_ds', 'yesterday_ds_nodash', 'templates_dict'])
# dag : <DAG: basic_task_context>
# ds : 2024-01-12
# ts : 2024-01-12T08:56:37.215851+00:00
# # execution_date와 logical_date는 동일하나, logical_date를 사용하는 것이 좋음.
# execution_date : 2024-01-12T08:56:37.215851+00:00
# logical_date : 2024-01-12T08:56:37.215851+00:00
# params : {'val1': 10, 'val2': 20}
# task : <Task(PythonOperator): print_context>
# # task에 대한 정보는 task_instance (ti)로 접근 가능.
# ti : <TaskInstance: basic_task_context.print_context manual__2024-01-12T08:56:37.215851+00:00 [running]>


dag = DAG(
    dag_id='basic_task_context',
    start_date=datetime(2024,1,1),
    catchup=False,
    schedule='* 0 * * *',
    tags=['example', 'basic'],
)

t1 = PythonOperator(
    task_id="print_context",
    python_callable=print_context,
    # Operator에서 params로 넘겨준 kwargs는
    # context["params"]["val1"] 과 같은 형식으로 접근할 수 있다.
    params={"val1":10, "val2":20},
    dag=dag,
)

t2 = PythonOperator(
    task_id="get_context_function",
    python_callable=get_context_function,
    params={"a":1, "b":2},
    dag=dag,
)


t1, t2