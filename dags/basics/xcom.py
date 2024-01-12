from airflow.decorators import dag
from airflow.decorators import task
from airflow.operators.bash import BashOperator
# from airflow import XComArg
from datetime import datetime

# XCom은 cross-communication의 약자이다.
"""
task들 간에 데이터를 주고받기 위해서
metadata db를 사용한 방법인 xcom을 사용한다.

metadata db를 사용하기 때문에 대용량의 데이터는 외부 저장소를 이용하는 것이 좋다.

xcom은 {key, value, timestamp, dag id, task id, run id, map index, execution date}형태로
metadata db에 저장됨.
"""

"""
Xcom을 사용해서 데이터를 push하는 방법
- Python: 
    ti.xcom_push(key="", value=value)
    return value
- Bash:
    '{{ ti.xcom_push(key="", value="") }}'
    'echo return value'  # 마지막 라인 출력이 return 값이 된다.


Xcom을 사용해서 데이터를 pull하는 방법
    return 값이라면 "return_value"를 사용한다.
    혹은 key를 비워두면 return값을 사용한다.
- Python:
    value = ti.xcom_pull(task_ids="", key="")
- Bash:
    '{{ ti.xcom_pull(task_ids="", key="") }}'

혹은 @task를 통해 작업을 생성하면 파이썬 함수리턴을 주고받듯 사용할 수 있다.
ex) task2(task1())


---- 사용안함.
from airflow import XComArg를 사용할 수도 있지만,
jinja template을 써서 통일된 구조를 사용하도록 하자.
    (최근 버전의 문서에서 XComArg내용이 없기도 함)
- Bash: '{XComArg(push_bash_xcom, key="manually_pushed_value")}'  # key값으로 pull
- Bash: '{XComArg(push_bash_xcom)}'  # return 값을 사용한다.

첫 파라미터로 오브젝트를 줘야하는지 task_id를 줘야하는지도 불명확해서 쓰기 싫었음.
"""


def _compare_values(pulled_value, check_value):
    if pulled_value != check_value:
        raise ValueError(f"The two values differ {pulled_value} and {check_value}")

@dag(
    dag_id="basic_xcom",
    start_date=datetime(2024,1,1),
    schedule=None,
    tags=["example", "basic"],
)
def xcom():
    value1 = 1004
    value2 = [1, 2, 3]
    value3 = {"a":"hello", "b":300}

    push_bash_xcom = BashOperator(
        # bash에서 jinja template을 사용해서 ti.xcom_push사용. 방법 동일.
        task_id="push_bash_xcom",
        bash_command='echo "push_bash_xcomarg" && '
        'echo "Manually set xcom value '
        '{{ ti.xcom_push(key="manually_pushed_value", value="manually_pushed_value") }}" && '
        'echo "value_by_return" && '
        'echo {{ ds }}',
        # 마지막 출력이 리턴값이 된다.
    )

    @task
    def push_xcom(ti=None):
        # ti를 선언해주어야 코드 작성 시 에러가 안난다.
        ti.xcom_push(key="value from push_xcom", value=value1)
    
    @task
    def push_return(**context):
        context["ti"].xcom_push(key="value from push_xcom", value=value2)
        return value3

    pull_bash_xcomarg = BashOperator(
        task_id="pull_bash_xcomarg",
        bash_command='echo "bash pull demo" && '
        # f'echo "The xcom pushed manually is {XComArg(push_bash_xcom, key="manually_pushed_value")}" && '
        'echo "The xcom pushed manually is {{ ti.xcom_pull(task_ids="push_bash_xcom", key="manually_pushed_value") }}" && '
        # f'echo "The returned_value xcom is {XComArg(push_bash_xcom)}" && '
        'echo "The returned_value xcom is {{ ti.xcom_pull(task_ids="push_bash_xcom") }}" && '
        'echo "finished"',
        do_xcom_push=False,
    )

    @task
    def pull_xcom(pulled_value3, ti=None, **context):
        pulled_value1 = ti.xcom_pull(task_ids="push_xcom", key="value from push_xcom")
        # ti를 매개변수로 받으니까 context에서 "ti"가 안되네??
        pulled_value2 = context["task_instance"].xcom_pull(task_ids="push_return", key="value from push_xcom")
        
        _compare_values(value1, pulled_value1)
        _compare_values(value2, pulled_value2)
        _compare_values(value3, pulled_value3)
    
    @task
    def pull_from_bash(ti=None):
        # bash에서 push한 xcom 변수들도 동일한 방법으로 pull할 수 있다.
        bash_return_value = ti.xcom_pull(task_ids="push_bash_xcom", key="return_value")
        bash_pushed_value = ti.xcom_pull(task_ids="push_bash_xcom", key="manually_pushed_value")
        print(f"The xcom value pushed by task push via return value is {bash_return_value}")
        print(f"The xcom value pushed by task push manually is {bash_pushed_value}")


    push_bash_xcom >> [pull_bash_xcomarg, pull_from_bash()]
    
    push_xcom() >> pull_xcom(push_return())

xcom()