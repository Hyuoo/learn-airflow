"""
ETL 구현하기.
- MySQL의 테이블을 Redshift로 적재하는 ETL

data flow: [ MySQL -> S3 -> Redshift ]
- Full refresh 구현
- Incremental update 구현

(x) 방법1. MySQL에서 SELECT하여 Redshift로 INSERT
    - low performance
(o) 방법2. MySQL에서 csv로 저장하여 S3에 적재 후 S3에서 Redshift로 벌크업데이트(COPY)

- csv는 airflow가 동작하는 서버에서 저장되어 S3로 업로드한다.
- Connections
    - MySQL
    - S3
        (*S3에 대한 커넥션은 Amazon Web Services로 User에 대해서 연결함)
- Security
    - Airflow -> S3 (w)
        - IAM에서 별도의 User를 생성
        - User에 S3에 대한 권한 부여
        - User의 Access Key, Secret Key 사용
    - Redshift -> S3 (r)
"""

"""
amazon provider로 제공되는 오퍼레이터를 사용함.

# SqlToS3Operator (https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/transfer/sql_to_s3.html)
MySQL의 SQL쿼리 결과를 S3로 저장함
    ("S3://{s3_bucket}/{s3_key}" 형식)

# S3ToRedshiftOperator (https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/transfer/s3_to_redshift.html)
S3의 파일로 Redshift에 COPY
    ("S3://{s3_bucket}/{s3_key}"
     -> {schema}.{table})
"""


from airflow import DAG
from airflow.providers.amazon.aws.transfers.sql_to_s3 import SqlToS3Operator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator

from datetime import datetime
from datetime import timedelta


dag = DAG(
    dag_id = 'example_kdt_lesson_mysql_to_redshift',
    start_date = datetime(2022,4,24),
    schedule = '0 9 * * *',
    max_active_runs = 1,  # 
    catchup = False,
    default_args = {
        'owner': 'hyuoo',
        'retries': 1,
        'retry_delay': timedelta(minutes=3),
    },
    tags=["example", "kdt"],
)

schema = "hopeace6"
table = "nps"
s3_bucket = "grepp-data-engineering"
s3_key = schema + "-" + table
# SqlToS3Operator > s3://grepp-data-engineering/hopeace6-nps
# S3ToRedshiftOperator > hopeace6.nps

mysql_to_s3_nps = SqlToS3Operator(
    task_id = 'mysql_to_s3_nps',
    # 쿼리 결과를 파일로 저장.
    # query = "SELECT * FROM prod.nps",  # full refresh -> incremental update
    query = "SELECT * FROM prod.nps WHERE DATE(created_at) = DATE('{{ logical_date }}')",
    s3_bucket = s3_bucket,
    s3_key = s3_key,
    sql_conn_id = "mysql_conn_id",
    aws_conn_id = "aws_conn_id",
    verify = False,
    replace = True,  # key에 대해서 덮어쓰기. False일 경우 이미 존재하면 에러발생
    pd_kwargs={"index": False, "header": False},  # 쿼리 결과 저장 포맷 옵션.
    # 내부적으로 pandas를 사용하기 때문에 pandas에 주는 옵션이 됨. (pd)
    dag = dag
)

s3_to_redshift_nps = S3ToRedshiftOperator(
    task_id = 's3_to_redshift_nps',
    s3_bucket = s3_bucket,
    s3_key = s3_key,
    schema = schema,
    table = table,
    copy_options=['csv'],  # 대상파일 포맷
    redshift_conn_id = "redshift_dev_db",
    aws_conn_id = "aws_conn_id",
    # 메서드 REPLACE, APPEND, UPSERT
    # method = 'REPLACE',  # full refresh -> incremental update
    method = "UPSERT",
    # UPSERT일 경우 기준컬럼으로 있으면 REPLACE(UPDATE), 없으면 INSERT
    upsert_keys = ["id"],
    dag = dag
)

mysql_to_s3_nps >> s3_to_redshift_nps