# Airflow basic reference

Airflow에 대한 기본적인 개념 또는 오퍼레이터에 대해서 공부할 내용을 분류해 놓은 문서

## DAG

- schedule [[ Notion ]](https://historical-medicine-5c0.notion.site/Schedule-b42c5c2c38094799a96bad043f572e06?pvs=4)
- on_failure_callback (on_success_callback)
- Incremental update
    - logical_date
    - Backfill
    - partitioning
- [Dynamic Dag](./dynamic_dag/)

## Operator/Task

- [`BashOperator`](./bash_operator.py)
- [`PythonOperator`](./python_operator.py)
- [Jinja template](./jinja_template.py)
- [Context](./task_context.py)
- [Xcom](./xcom.py)
- [Trigger rule](./trigger_rule.py)
- [TaskGroup](./task_group.py) ([decorator](./task_group_decorator.py))
- Task Dependency
    - [`BranchPythonOperator`](./branch_python_operator.py) ([decorator](./branch_python_decorator.py))
    - [`LatestOnlyOperator`](./latest_only_operator.py)
- Dag Dependency
    - [`TriggerDagRunOperator`](./trigger_dag_run_operator.py) ([target](./trigger_dag_run_target.py))
        - Explicit Trigger
        - DAG(A -> B)
    - [`ExternalTaskSensor`](./external_task_sensor.py)
        - Reactive Trigger
        - DAG(A wait B)
- Provider