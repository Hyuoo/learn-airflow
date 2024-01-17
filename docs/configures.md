`/config/airflow.cfg` 파일 참고 (2.6.3버전 기준)

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


## Executor

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

## Airflow Webserver

#### dags폴더의 dag가 웹서버에 갱신되는 타이밍

기본 300초(5분)마다 dags폴더 스캔
```
[scheduler]
# How often (in seconds) to scan the DAGs directory for new files. Default to 5 minutes.
dag_dir_list_interval = 300
```

#### API를 통해서 config 정보 요청 가능 여부
```
[webserver]
expose_config=True
```
