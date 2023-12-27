`/examples/airflow.cfg` 파일 참고 (2.6.3버전 기준)

#### dags폴더의 dag가 웹서버에 갱신되는 타이밍

기본 300초(5분)마다 dags폴더 스캔
```
[scheduler]
# How often (in seconds) to scan the DAGs directory for new files. Default to 5 minutes.
dag_dir_list_interval = 300
```
