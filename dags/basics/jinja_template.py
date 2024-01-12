from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from datetime import datetime
from textwrap import dedent

# https://airflow.apache.org/docs/apache-airflow/2.6.3/templates-ref.html#templates-ref
"""
jinja template
presentation logic, application logic의 분리
장고에서 맨 처음 썼다가 진자로 만들어지고 플라스크에서도 엄청 쓴다고 함.

변수: {{ ~~~ }}
제어문: {%  %}

특정 operator, param에 대해서 적용할 수 있다.
지원되는 파라미터는 reference docs에서 파라미터 설명 뒤에 (templated)가 쓰여있음.
"""

"""
예시
{{ ds }}
    YYYY-MM-DD 형태의 logical_date.
    {{ dag_run.logical_date | ds }}와 동일하다.
{{ ds_nodash }}
    YYYYMMDD 형태의 logical date.
    {{ dag_run.logical_date | ds_nodash }}와 동일하다.
{{ ts }}
    2018-01-01T00:00:00+00:00 형태
{{ dag }}
    현재 실행중인 DAG id
{{ task }}
    현재 실행중인 Task id
{{ macros }}
    {{ macros.ds_add(ds, days) }} 형식으로 ds기준 날짜를 구할 수 있다.
    {{ macros.ds_format(ds, input, output) }} 날짜 포맷 변경
        ds_format('2015-01-01', "%Y-%m-%d", "%m-%d-%y") -> '01-01-15'
        ds_format('1/5/2015', "%m/%d/%Y",  "%Y-%m-%d") -> '2015-01-05'
    이 외 datetime, timedelta, time, uuid, random은 파이썬표준라이브러리 모듈을 사용할 수 있다.
{{ dag_run }}

{{ task_instance }}
    {{ ti }}와 동일. 파이썬 코드로 ti호출해서 하는것과 동일하게 사용 가능.
{{ params }}

{{ conf }}
    AirflowConfigParser 객체접근으로 airflow.cfg 내용을 조회 할 수 있다.

{{ var.value }}
    variables get
    {{ var.value.get('my.var', 'fallback') }}
{{ var.json }}
    {{ var.json.my_dict_var.key1 }}
{{ conn }}
    {{ conn.my_conn_id.login }}, {{ conn.my_conn_id.password }}
"""


dag = DAG(
    "basic_jinja_template",
    start_date=datetime(2024,1,1),
    schedule=None,
    tags=[ "example", "basic" ],
)

command_jinja = dedent("""
        echo "ds: {{ ds }}, logical_date: {{ logical_date }}"
        echo "ds_nodash: {{ ds_nodash }}"
        echo "dag: {{ dag }}, task: {{ task }}"
        echo "ti: {{ ti }}"
        echo "dag_run: {{ dag_run }}"
        """)
# 대충 결과값
# ds: 2024-01-12, logical_date: 2024-01-12T15:12:13.602881+00:00
# ds_nodash: 20240112
# dag: <DAG: basic_jinja_template>, task: <Task(BashOperator): templated_jinja>
# ti: <TaskInstance: basic_jinja_template.templated_jinja manual__2024-01-12T15:12:13.602881+00:00 [running]>
# dag_run: <DagRun basic_jinja_template @ 2024-01-12 15:12:13.602881+00:00: manual__2024-01-12T15:12:13.602881+00:00, state:running, queued_at: 2024-01-12 15:12:13.628236+00:00. externally triggered: True>

t1 = BashOperator(
    task_id="jinja_variables",
    bash_command=command_jinja,
    dag=dag,
)

t2 = BashOperator(
    task_id="jinja_for",
    bash_command=dedent(
        """
        echo "{{ ds }}"
        {% for i in range(5) %}
           echo "{{ macros.ds_add(ds, i+1) }}"
        {% endfor %}
        """
        ),
    dag=dag,
)

t3 = BashOperator(
    task_id="jinja_params",
    bash_command='echo "안녕하세요, {{ params.name }}!__ {{ params.three.two }} __ {{ params.multi }}"',
    params={'name': 'John',
            'three':{'two':'one'},
            'multi':{'a':95,'b':96}
            },  # 사용자 정의 가능한 매개변수
    dag=dag,
)

t4 = BashOperator(
    task_id="jinja_module",
    bash_command=dedent(
        """
        {% for i in range(5) %}
           echo "{{ macros.random() }}"
        {% endfor %}
        """
        ),
    dag=dag,
)


t1, t4
t2, t3