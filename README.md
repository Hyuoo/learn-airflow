# Learning Airflow

에어플로우를 공부하며 기록한 레포지토리.

## 에어플로우 환경

학습을 위한 Airflow: Docker compose를 이용해 scheduler, webserver, postgres로 구성
- `PyPI`를 통해 Airflow를 설치
- Dockerfile
    - Base Iamge: `python:3.7-slim-buster`
    - Airflow Version: `2.6.3`
    - Airflow Home: `/var/lib/airflow`
    - Providers: `[celery,mysql,postgres,amazon,google]`
- `Postgres`를 사용한 `LocalExecutor`
    - Postgres Version: `13`

(
    [docs/installation_PyPI.md](/docs/installation_PyPI.md)와 [git:puckel/docker-airflow](https://github.com/puckel/docker-airflow)레포지토리를 참고하여 작성함.
)


#### Image pull

```
docker pull hopeace6/airflow-local:2.6.3-python3.7
```

#### LocalExecutor Airflow compose up :

```
docker compose -f docker-compose.local.yaml up -d
```



> 공부 소스들
> 
> [image building (Dockerfile)](https://airflow.apache.org/docs/docker-stack/build.html)
> 