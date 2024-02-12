## [모니터링 (& health check)](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/logging-monitoring/check-health.html)

API를 통해서 airflow 서버에 대한 health check를 하거나, DataDog, Grafana등의 모니터링 툴을 연계하여 사용하는 것이 일반적이다.

- webserver
- scheduler
- metadata db


## 로그 관리

로그 데이터의 양이 상당하기 때문에, 지속적으로 삭제하거나, 백업하는 등의 관리를 할 수 있다.

**로그파일 방치하면 서버 죽는다.**

아래의 두 옵션의 위치에 실행에 대한 로그파일이 쌓인다.

```
[logging]
base_log_folder = /var/lib/airflow/logs

[scheduler]
child_process_log_directory = /var/lib/airflow/logs/scheduler
```

> 임시데이터 폴더도 지속적으로 관리해야함.


## 메타데이터 DB 백업

특히 외부의 데이터베이스를 사용한다면 주기적인 백업이 필요하다.
 ([airflow_backup_metadb_s3.py](./airflow_backup_metadb_s3.py) 참고)

또는 variables와 connections를 주기적으로 백업하는 DAG를 작성할 수 있다.
```
airflow variables export variables.json
airflow variables export connections.json
```

DB내용 백업 할 때 암호화하는 `FURNET_KEY`에 대해서 유념.