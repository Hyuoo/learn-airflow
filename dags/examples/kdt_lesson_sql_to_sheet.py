"""
redshift에서 SQL의 결과를 google spread sheet로 업데이트하는 예제.

- gsheet_to_redshift예제의 서비스 어카운트를 설정해야 함. (같은 파일 그대로 사용)
- redshift에서 SQL의 실행 결과를 pandas.dataframe으로 읽음
- sheet의 내용을 지우고, dataframe을 sheet에 저장.

need pip
- pip3 install oauth2client
- pip3 install gspread
"""

from airflow import DAG
from airflow.operators.python import PythonOperator

from plugins import gsheet
from datetime import datetime


def update_gsheet(**context):
    # sql의 결과를 sheetfilename의 sheetgid 탭에 업데이트
    sql = context["params"]["sql"]
    sheetfilename = context["params"]["sheetfilename"]
    sheetgid = context["params"]["sheetgid"]

    gsheet.update_sheet(sheetfilename, sheetgid, sql, "redshift_dev_db")


with DAG(
    dag_id = 'example_kdt_lesson_sql_to_sheet',
    start_date = datetime(2024,1,1),
    schedule = '@once',
    catchup = False,
    default_args = {
        'owner': 'hyuoo',
    },
    tags=["example", "kdt"],
)as dag:
    
    sheet_update = PythonOperator(
        task_id="update_sql_to_sheet",
        python_callable=update_gsheet,
        params={
            # "sql": "SELECT * FROM analytics.nps_summary",
            "sql": "SELECT date, round AS nps FROM analytics.nps_summary ORDER BY date",
            "sheetfilename": "kdt-w12-spreadsheet",
            "sheetgid": "RedshiftToSheet",
        }
    )

    sheet_update
    
