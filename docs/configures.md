`/config/airflow.cfg` 파일 참고 (2.6.3버전 기준)

cfg파일에 대한 변경이 있을 경우, webserver와 scheduler를 재실행 해 주어야 함.


#### airflow 예제 제거
```
[core]
load_examples = False
```

## 코드작성


#### Operator에서 param형식으로 conf전달 가능 여부

값을 사용하여 코드에서 `context["dag_run"].conf.get('value')` 또는 `{{ dag_run.conf["value"] }}`와 같이 conf값을 가져올 수 있다.
- operator에서 전달
    - `conf: dict = {"a": "b"}`
- cli에서 전달
    - `--conf '{"a": "b"}'`

혹은 web UI에서 테스트할 때 configuration JSON을 넘겨줄 때도 이 설정값이 True여야 한다.

```
[core]
dag_run_conf_overrides_params=True
```


## Execute

executor와 metaDB설정. installation_PyPI를 참고하자.
```
[core]
# Local, Celery, Kube 등의 executor 지정
executor = LocalExecutor
# 워커 수에 상관없이 scheduler당 동시에 동작할 수 있는 전체 task instance의 수
# (parallelism*스케줄러의 클러스터의 수)가 메타db에서 최대로 실행 될 수 있는 task instance의 수가 된다.
# 0으로 설정 할 경우 무제한
parallelism = 32
# 최대 활성화 dag 수
max_active_runs_per_dag = 16
# 하나의 dag당 동시에 실행될 수 있는 최대 task 수
max_active_tasks_per_dag = 16
[database]
sql_alchemy_conn = postgres://...
```

## Airflow Webserver

#### dags폴더의 dag가 웹서버에 갱신되는 타이밍

기본 300초(5분)마다 dags폴더 스캔
```
[core]
# dag를 스캔 할 폴더 위치
dags_folder = /var/lib/airflow/dags
[scheduler]
# How often (in seconds) to scan the DAGs directory for new files. Default to 5 minutes.
dag_dir_list_interval = 300
```

#### API를 통해서 config 정보 요청 가능 여부
```
[webserver]
expose_config=True
```

## Loggig

#### 로깅 위치

```
[logging]
base_log_folder = /var/lib/airflow/logs
[scheduler]
child_process_log_directory = /var/lib/airflow/logs/scheduler
```

#### [민감정보를 로그에서 UI나 작업로그에서 마스킹](https://airflow.apache.org/docs/apache-airflow/stable/security/secrets/mask-sensitive-values.html)

variable의 값이나 connection의 json필드(extra json)를 마스킹한다.   
> Xcom이나 다른 채널을 통해서 들어오는 민감정보는 마스킹되지 않음에 주의
>
> 예를들어 task1에서 password를 xcom을 통해 task2로 전달하면 이는 마스킹되지 않는다.
- connection의 password는 항상 마스킹
- 다음 키워드들이 들어가는 경우 마스킹
    - `access_token`, `api_key`, `apikey`, `authorization`, `passphrase`, `passwd`, `password`, `private_key`, `secret`, `token`

태스크나 오퍼레이터의 런타임에서 마스킹 할 키워드를 추가할수도 있다. (링크참고)

```
[core]
# comma로 구분된 키워드 목록 > variables names or connection’s extra JSON.
sensitive_var_conn_names = comma,separated,sensitive,names
# 모두 이 값이 활성화 될 경우에만 마스킹
hide_sensitive_var_conn_fields = True
```