# from airflow.models import DAG
# from airflow.operators.bash import BashOperator
# from airflow.sensors.external_task import ExternalTaskSensor

# from datetime import datetime

"""
다른 dag의 task가 실행됨을 기다려서 반응하기 때문에 reactive trigger라고도 한다.

file, http, sql, time, external 등의 조건을 써서 wait한다.
(listen이라고 하는게 더 적합한가)

mode=(poke|reschedule)
- poke: (default) worker를 점유하고 있는 상태 (sleep)
- reschedule: worker를 릴리즈하고 다시 스케줄링


schedule 실행 주기를 맞춰줘야 함.

실행주기 어긋나는 경우는
execution_delta=timedelta(minutes=5)
이런 식으로 싱크를 맞추면 되는데
주기 자체가 다른 경우는 ExternalTaskSensor 자체 사용이 불가. 
"""

# with DAG(
#     "basic_external_task_sensor",
#     start_date=datetime(2024, 1, 1),
#     schedule=None,
#     tags=[ "example", "basic" ],
# ) as dag:

#     waiting_for_end_of_dag = ExternalTaskSensor(
#         task_id='ExternalTaskSensor',
#         external_dag_id='basic_trigger_dag_run_operator',
#         external_task_id='trigger_task',
#         timeout=5*60,
#         mode='reschedule'
#     )

#     task = BashOperator(
#         task_id='task',
#         bash_command='''echo "ds: {{ ds }}"
#         echo "ti: {{ task_instance }}, {{ ti }}"
#         echo "dag: {{ dag }}, task: {{ task }}"
#         echo "dag_run: {{ dag_run }}"
#         '''
#     )

#     waiting_for_end_of_dag >> task