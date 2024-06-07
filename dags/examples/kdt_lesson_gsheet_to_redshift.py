"""
구글 스프레드시트의 데이터를 레드시프트로 업데이트하는 예제.

- 구글 스프레드시트 내용을 "{table}.csv"파일로 저장
- csv파일을 S3에 업로드
- S3ToRedshiftOperator를 사용해서 bulk update

need pip
- pip3 install oauth2client
- pip3 install gspread
"""


"""
메인이 되는 함수는 get_google_sheet_to_csv()

기능사항:
- google sheet API를 통해서 구글 스프레드시트에 대한 읽기쓰기 작업이 가능하다.
- 접근을 위해서, 구글 서비스 어카운트를 생성하고 해당 파일(스프레드시트)이 어카운트에 공유되어야 함.
    (서비스 계정은 "{account_name}@{project}.iam.gserviceaccount.com" 형식)
    - 현재 airflow에서는 service account의 .json파일을 Variables에 저장하여 사용함. -> "google_sheet_access_token"
    - Variables의 내용을 코드단에서 파일로 저장하고, 이 파일을 통해서 인증을 하는 방식.
      (임시 데이터 디렉토리에 대한 volumes, Variables를 설정하여 해당 위치에 저장함. -> DATA_DIR="/opt/airflow/data")

- 어카운트 만들기 참고 링크: https://denisluiz.medium.com/python-with-google-sheets-service-account-step-by-step-8f74c26ed28e

인자설명:
- :param url: 스프레드시트의 링크. 해당 스프레드시트를 생성한 service account와 공유해야한다.
- :param tab: 시트에서 읽어 올 탭의 이름을 지정.
- :param filename: 로컬에서 파일이 저장될 경로 및 파일명. "~/test.csv"
예) gsheet.get_google_sheet_to_csv('https://docs.google.com/spreadsheets/d/[service_url]', 'Test', 'test.csv')


- 이 예제에서는 redshift에 아래와 같이 테이블을 만들어두고 이를 구글스프레드시트로부터 채운다.
CREATE TABLE hopeace6.spreadsheet_copy_testing (
    col1 int,
    col2 int,
    col3 int,
    col4 int
);
"""


from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator
from airflow.models import Variable

from datetime import datetime
from datetime import timedelta
from plugins import s3, gsheet


def download_tab_in_gsheet(**context):
    url = context["params"]["url"]
    tab = context["params"]["tab"]
    table = context["params"]["table"]
    data_dir = Variable.get("DATA_DIR")

    gsheet.get_google_sheet_to_csv(
        url,
        tab,
        data_dir+'{}.csv'.format(table)
    )


def copy_to_s3(**context):
    table = context["params"]["table"]
    s3_key = context["params"]["s3_key"]

    s3_conn_id = "aws_conn_id"
    s3_bucket = "grepp-data-engineering"
    data_dir = Variable.get("DATA_DIR")
    local_files_to_upload = [ data_dir+'{}.csv'.format(table) ]
    replace = True

    s3.upload_to_s3(s3_conn_id, s3_bucket, s3_key, local_files_to_upload, replace)


dag = DAG(
    dag_id = 'example_kdt_lesson_gsheet_to_redshift',
    start_date = datetime(2024,1,1),
    schedule = '0 9 * * *',
    max_active_runs = 1,
    max_active_tasks = 2,
    catchup = False,
    default_args = {
        'owner':'Hyuoo',
        'retries': 1,
        'retry_delay': timedelta(minutes=3),
    },
    tags=["example", "kdt"],
)

# gssheet(url, tab) -> redshift(schema, table)
sheets = [
    {
        "url": "https://docs.google.com/spreadsheets/d/[sheet_url]",
        "tab": "SheetToRedshift",
        "schema": "hopeace6",
        "table": "spreadsheet_copy_testing"
    }
]

for sheet in sheets:
    # 각 task이름은 sheet["table"]로 생성함.
    download_tab_in_gsheet = PythonOperator(
        task_id = 'download_{}_in_gsheet'.format(sheet["table"]),
        python_callable = download_tab_in_gsheet,
        params = sheet,
        dag = dag
        )

    s3_key = sheet["schema"] + "_" + sheet["table"]

    copy_to_s3 = PythonOperator(
        task_id = 'copy_{}_to_s3'.format(sheet["table"]),
        python_callable = copy_to_s3,
        params = {
            "table": sheet["table"],
            "s3_key": s3_key
        },
        dag = dag
        )

    run_copy_sql = S3ToRedshiftOperator(
        task_id = 'run_copy_sql_{}'.format(sheet["table"]),
        s3_bucket = "grepp-data-engineering",
        s3_key = s3_key,
        schema = sheet["schema"],
        table = sheet["table"],
        copy_options=['csv', 'IGNOREHEADER 1'],
        method = 'REPLACE',
        redshift_conn_id = "redshift_dev_db",
        aws_conn_id = 'aws_conn_id',
        dag = dag
    )

    download_tab_in_gsheet >> copy_to_s3 >> run_copy_sql
