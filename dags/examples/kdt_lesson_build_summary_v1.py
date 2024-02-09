from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowException

from datetime import datetime
import logging


"""
CTAS를 통해서 ELT작업을 하는 DAG 생성하기.

CTAS를 할 sql문과 새로 생성될 테이블의 이름을 지정하고, 함수형태로 구현한다.
파이썬 함수를 통해서 작업을 하고, PythonOperator를 사용해서 반복적으로 사용 할 수 있다.

---
이후 operator를 생성하고, CTAS부분을 별도의 환경설정으로 분리하여 구현함 -> _v2
+ 테스트
"""

def get_Redshift_connection():
    hook = PostgresHook(postgres_conn_id = 'redshift_dev_db')
    return hook.get_conn().cursor()


def execSQL(**context):
    """
    CTAS를 통해 sql(select)결과 테이블을 생성하는 함수
    -> "CREATE TABLE {table} AS ({select_sql})";

    1. select결과 CTAS 임시테이블을 생성
    2. 문제가 있으면 raise (테이블 레코드 수가 0)
    3. 문제없으면, DROP origin, ALTER tmp RENAME
    """

    schema = context['params']['schema'] 
    table = context['params']['table']
    select_sql = context['params']['sql']

    logging.info(schema)
    logging.info(table)
    logging.info(select_sql)

    cur = get_Redshift_connection()

    sql = f"""DROP TABLE IF EXISTS {schema}.temp_{table};CREATE TABLE {schema}.temp_{table} AS """
    sql += select_sql
    cur.execute(sql)

    cur.execute(f"""SELECT COUNT(1) FROM {schema}.temp_{table}""")
    count = cur.fetchone()[0]
    if count == 0:
        raise ValueError(f"{schema}.{table} didn't have any record")

    try:
        sql = f"""DROP TABLE IF EXISTS {schema}.{table};ALTER TABLE {schema}.temp_{table} RENAME to {table};"""
        sql += "COMMIT;"
        logging.info(sql)
        cur.execute(sql)
    except Exception as e:
        cur.execute("ROLLBACK")
        logging.error('Failed to sql. Completed ROLLBACK!')
        raise AirflowException("")


dag = DAG(
    dag_id="example_kdt_lesson_build_summary_v1",
    start_date=datetime(2024, 1, 1),
    schedule='@once',
    catchup=False,
    default_args= {
        'owner': 'hyuoo',
    },
    tags=["example", "kdt"],
)

sql = """SELECT 
    TO_CHAR(A.ts, 'YYYY-MM') AS month,
    COUNT(DISTINCT B.userid) AS mau
FROM raw_data.session_timestamp A
JOIN raw_data.user_session_channel B ON A.sessionid = B.sessionid
GROUP BY 1 
;"""

exec_sql = PythonOperator(
    task_id = 'mau_summary',
    python_callable = execSQL,
    params = {
        'schema': 'hopeace6',
        'table': 'mau_summary',
        'sql': sql,
    },
    dag = dag
)

# 새로운 SQL ELT 작업을 만들 경우 아래처럼 생성해야 한다.

add_sql = """SELECT
    DISTINCT A.userid,
    FIRST_VALUE(A.channel) over(
        partition by A.userid order by B.ts
        rows between unbounded preceding and unbounded following
        ) AS First_Channel,
    LAST_VALUE(A.channel) over(
        partition by A.userid order by B.ts
        rows between unbounded preceding and unbounded following
        ) AS Last_Channel
FROM raw_data.user_session_channel A
LEFT JOIN raw_data.session_timestamp B ON A.sessionid = B.sessionid;"""

additional_sql = PythonOperator(
    task_id = 'channel_summary',
    python_callable = execSQL,
    params = {
        'schema': 'hopeace6',
        'table': 'channel_summary',
        'sql': add_sql,
    },
    dag = dag
)