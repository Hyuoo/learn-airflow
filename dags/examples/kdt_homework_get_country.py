from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime

import requests
import json
import logging
import psycopg2

"""
나라 정보 API는 아래 링크 참고.
(*별도의 API Key 필요없음)
https://restcountries.com/#about-this-project-important-information
"""

"""
과제 목표:
API 결과에서
- country: ["name"]["official"]
- population: ["population"]
- area: ["area"]
세 항목 추출하여 full-refresh 형식으로 적재하기
schedule: 매주 토요일 오전 6시 30분
"""


def get_connection(autocommit=True):
    # **caution: airflow metadata db를 그대로 사용함.
    host = "postgres"
    user = "airflow"
    password = "airflow"
    port = "5432"
    db_name = "airflow"
    conn = psycopg2.connect(f"dbname={db_name} user={user} host={host} password={password} port={port}")
    conn.set_session(autocommit=autocommit)

    # AIRFLOW_CONN 생성 시 사용
    # hook = PostgresHook(postgres_conn_id='postgres')
    # conn = hook.get_conn()
    # conn.autocommit = autocommit

    return conn.cursor()


@task
def get_country_info(url):
    logging.info("api-get ..")
    res = requests.get(url)
    logging.info("OK")
    countries = res.json()
    records = []
    for country in countries:
        record = [
                # Query 문자열에 따옴표(') 있으면 이상. >> 2개로 하면 정상적으로 들어감
                country["name"]["official"].replace("'","''"),
                country["population"],
                country["area"],
                country["region"],
                country["timezones"][0],
                country["translations"].get("kor", {}).get("common", "NULL")
        ]
        records.append(record)
    logging.info("end api-get")
    return records

@task
def load_to_db(table, records, schema=None):
    cur = get_connection()
    try:
        logging.info("start load")
        table_name = (f"{schema}.{table}" if schema else f"{table}")

        cur.execute("BEGIN;")
        cur.execute(f"DROP TABLE IF EXISTS {table_name}")
        cur.execute(f"""
        CREATE TABLE {table_name} (
            country varchar(256) primary key,
            population integer,
            area float,
            region varchar(256),
            timezone varchar(256),
            name_kor varchar(256)
        );""")
        c=0
        for record in records:
            sql = f"INSERT INTO {table_name} VALUES ( \
                '{record[0]}', {record[1]}, {record[2]}, \
                '{record[3]}', '{record[4]}', '{record[5]}' \
                );"
            # print(sql)
            cur.execute(sql)
            c+=1
            # print(".. GOOD")
        cur.execute("COMMIT;")
        
        logging.info("end load .. successfully (COMMIT)")
        logging.info(f"loaded data count : {c}")

    except Exception as e:
        logging.error(e)
        cur.execute("ROLLBACK;")
        logging.info("end load .. failed (ROLLBACK)")
        raise

    return table_name

@task
def print_result(table_name):
    cur = get_connection()
    cur.execute(f"SELECT * FROM {table_name};")

    for record in cur.fetchall():
        print(record)


@dag(
    dag_id="example_kdt_homework_get_country",
    start_date=datetime(2024,1,1),
    schedule="30 6 * * 6",
    catchup=False,
    tags=["example", "kdt"],
    default_args={"owner": "hyuoo"},
)
def kdt_homework_get_country_dag():

    end_point = "https://restcountries.com/v3.1/all"
    fields = "fields=name,population,area,timezones,region,translations"
    # schema = "airflow"
    table = "country_hw"
    
    records = get_country_info(f"{end_point}?{fields}")
    table_name = load_to_db(table=table, records=records)
    print_result(table_name)


kdt_homework_get_country_dag()