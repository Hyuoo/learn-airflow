from airflow import DAG
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task

from datetime import datetime
from datetime import timedelta

import requests
import psycopg2
import logging

"""
다음의 날씨 API를 통해서 진행
https://openweathermap.org/api/one-call-api

위도/경도를 기반으로 해당 지역의 기후 정보를 알려주는 api
- key를 발급받아 variable로 저장하여 사용
    - "open_weather_api_key"
- 서울의 위도와 경도를 사용해서 날짜, 낮 온도(day), 최소 온도(min), 최대 온도(max)를 저장.
- 호출시점 기준으로 향후 8일간의 예측 데이터가 나온다.
- 날짜에 대해서 UPSERT를 하여 incremental update. (최근의 예보가 더 정확)
    - INSERT INTO를 사용한 Full Refresh방식을 사용
        - 매번 테이블을 지우고 다시 빌드함
    - S3에 업로드 후 bulk update를 통한 full refresh는 이후 학습

날짜PK 유지방법
- 예보날짜(date)외에 데이터 생성 날짜인 created_date를 만들고
  예보날짜를 기준으로 그룹핑하여 created_date가 최신인 데이터를 선택
    - ROW_NUMBER() OVER (PARTITION BY date ORDER BY create_date DESC) as seq
    - WHERE seq=1

# DISTINCT를 사용하는 것보다 이 방법이 더 안전하다?


1. 원본을 복사하여 임시테이블 생성
2. 새로운 데이터를 임시테이블에 삽입 (중복 발생)
3. created_date를 통해 중복데이터 구분하는 SQL작성
4. 원본테이블의 데이터를 삭제 후, 3의 SQL로 데이터 복사
"""

""" API response.json()
{
    'clouds': 44,
    'dew_point': 7.56,
    'dt': 1622948400,  # epoch time
    'feels_like': {
        'day': 26.59,
        'eve': 26.29,
        'morn': 15.36,
        'night': 22.2
        },
    'humidity': 30,
    'moon_phase': 0.87,
    'moonrise': 1622915520,
    'moonset': 1622962620,
    'pop': 0,
    'pressure': 1003,
    'sunrise': 1622923873,
    'sunset': 1622976631,
    'temp': {
        'day': 26.59,
        'eve': 26.29,
        'max': 28.11,
        'min': 15.67,
        'morn': 15.67,
        'night': 22.68
        },
    'uvi': 3,
    'weather': [{
        'description': 'scattered clouds',
        'icon': '03d',
        'id': 802,
        'main': 'Clouds'
        }],
    'wind_deg': 250,
    'wind_gust': 9.2,
    'wind_speed': 4.05
}
"""

def get_Redshift_connection(autocommit=True):
    hook = PostgresHook(postgres_conn_id='redshift_dev_db')
    hook.set_autocommit(autocommit)
    return hook.get_conn().cursor()


@task
def etl(schema, table, lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={api_key}&units=metric&exclude=current,minutely,hourly,alerts"
    response = requests.get(url)
    # data = json.loads(response.text)
    data = response.json()

    ret = []
    for d in data["daily"]:
        # 타임스탬프를 YYYY-MM-DD패턴으로 변경
        day = datetime.fromtimestamp(d["dt"]).strftime('%Y-%m-%d')
        # 아래 테이블 포맷에 맞춘 문자열
        ret.append("('{}',{},{},{})".format(
            day,
            d["temp"]["day"],
            d["temp"]["min"],
            d["temp"]["max"]
            ))

    cur = get_Redshift_connection(autocommit=False)

    # 원본 테이블이 없다면 생성 쿼리
    create_table_sql = f"""CREATE TABLE IF NOT EXISTS {schema}.{table} (
    date date,
    temp float,
    min_temp float,
    max_temp float,
    created_date timestamp default GETDATE()
);"""

    # 임시 테이블 생성 쿼리
    create_t_sql = f"""CREATE TEMP TABLE t AS SELECT * FROM {schema}.{table};"""

    try:
        logging.info(create_table_sql)
        cur.execute(create_table_sql)
        logging.info(create_t_sql)
        cur.execute(create_t_sql)

        cur.execute("COMMIT;")
    except Exception as e:
        cur.execute("ROLLBACK;")
        raise

    # 임시 테이블 데이터 입력
    insert_sql = f"INSERT INTO t VALUES " + ",".join(ret)
    try:
        logging.info(insert_sql)
        cur.execute(insert_sql)
        cur.execute("COMMIT;")
    except Exception as e:
        cur.execute("ROLLBACK;")
        raise

    # 기존 테이블 대체
    # ROW_NUMBER를 통해서 같은날짜를 제외하고 INSERT한다.
    alter_sql = f"""DELETE FROM {schema}.{table};
        INSERT INTO {schema}.{table}
        SELECT date, temp, min_temp, max_temp FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY date ORDER BY created_date DESC) seq
            FROM t
        )
        WHERE seq = 1;"""
    try:
        logging.info(alter_sql)
        cur.execute(alter_sql)

        cur.execute("COMMIT;")
    except Exception as e:
        cur.execute("ROLLBACK;")
        raise

with DAG(
    dag_id = 'example_kdt_homework_weather_api_etl',
    start_date = datetime(2024,1,1),
    schedule = '0 2 * * *',
    max_active_runs = 1,
    catchup = False,
    default_args = {
        'owner': 'hyuoo',
        'retries': 1,
        'retry_delay': timedelta(minutes=3),
    },
    tags=["example", "kdt"],
) as dag:
    
    # 위도 (latitude)
    lat = 37.5665
    # 경도 (longitude)
    lon = 126.9780
    api_key = Variable.get("open_weather_api_key")

    etl("hopeace6", "weather_forecast_v2", lat=lat, lon=lon, api_key=api_key)