# [Airflow APIs](https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html)


대부분의 API는 json으로 응답을 주고받는다.   
해당되는 api는 헤더를 포함해야 한다.
```
Content-type: application/json
Accept: application/json
```

## DAG (Runs)

### List DAGs

모든 DAG의 목록, 메타데이터를 리턴

**endpoint:** `https://airflow.apache.org/api/v1/dags`

**curl example**
```
curl -X GET --user "airflow:airflow" \
    https://localhost:8080/api/v1/dags
```


### Trigger DAG

**endpoint:** `https://airflow.apache.org/api/v1/dags/{dag_id}/dagRuns`

**payload**
```
{
"dag_run_id": "string",
"logical_date": "2019-08-24T14:15:22Z",
"execution_date": "2019-08-24T14:15:22Z",
"conf": { },
"note": "string"
}
```

**curl example**
```
curl -X POST --user "airflow:airflow" \
    -H 'Content-Type: application/json' \
    -d ' {"execution_date":"2024-01-01T00:00:00Z"}' \
    "https://localhost:8080/api/v1/dags/MYDAG_ID/dagRuns"
```

## Variables

> 환경변수를 통한 variable은 응답되지 않는다.

**endponint:** `https://airflow.apache.org/api/v1/variables`

**curl example**
```
curl -X GET --user "airflow:airflow" \
    http://localhost:8080/api/v1/variables
```


## Config

> #### API를 통해서 config 정보 요청 가능 여부
>
> api를 통해서 config 리스트를 요청하는 경우, 기본적으로 차단되어 있음. `expose_config` 값을 수정하여 반환 가능하도록 설정할 수 있다.
>
> ```
> [webserver]
> expose_config=True
> ```

**endponint:** `https://airflow.apache.org/api/v1/config`

**curl example**
```
curl -X GET --user "airflow:airflow" \
    http://localhost:8080/api/v1/config
```