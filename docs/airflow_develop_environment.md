## Airflow develop environment

에어플로우를 계속해서 전체 서비스를 띄워놓고 하기엔 번거롭다.

파이썬 환경에서 설치하고 실행을 빠르게 해보자.

#### airflow 설치

`pip install apache-airflow==2.6.3`

#### [extra package 설치](https://airflow.apache.org/docs/apache-airflow/stable/extra-packages-ref.html)

추가로 필요한 패키지가 있을 경우 `pip`를 통해 설치한다.

```
pip install 'apache-airflow[google]'
```

#### airflow db init

처음 meta db 초기화

```
airflow db init
```

#### airflow 실행

웹서버만 있어도 `airflow dags ..`등 커맨드 실행이 가능하다.

```
airflow webserver -p 8080
```

웹 UI로 접속하고 싶다면 아래 명령으로 유저를 생성해야 함.

```
airflow users create --role Admin --username airflow --email airflow --firstname airflow --lastname airflow --password airflow
```
