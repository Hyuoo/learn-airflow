`/config/airflow.cfg` 파일 참고 (2.6.3버전 기준)

#### airflow 예제 제거
```
[core]
load_examples = False
```

#### dags폴더의 dag가 웹서버에 갱신되는 타이밍

기본 300초(5분)마다 dags폴더 스캔
```
[scheduler]
# How often (in seconds) to scan the DAGs directory for new files. Default to 5 minutes.
dag_dir_list_interval = 300
```

### Executor

executor와 metaDB설정. installation_PyPI를 참고하자.
```
[core]
executor = LocalExecutor
# 워커 수에 상관없이 scheduler당 동시에 동작할 수 있는 task instance의 수
# (parallelism*스케줄러의 클러스터의 수)가 메타db에서 최대로 실행 될 수 있는 task instance의 수가 된다.
parallelism = 32
[database]
sql_alchemy_conn = postgres://...
```

### Airflow Webserver
```
[webserver]
# API로 config 요청할 때 가능여부
expose_config=True
```
