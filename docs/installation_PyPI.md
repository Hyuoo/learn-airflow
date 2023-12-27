# Installation from PyPI

> [데이터엔지니어링 airflow-setup](https://github.com/keeyong/airflow-setup/blob/main/docs/Airflow%202%20Installation.md)

- 컨테이너를 사용하지 않고 직접적으로 Apache Airflow를 설치하는 방법.
- `AWS EC2 Ubuntu Server 20.04 LTS`에서 `Airflow 2.6.3` 설치를 진행하였다.

(일단무모하게 1기가에서 시도.)

Airflow의 모든 구성요소를 직접 설치하고 개발 및 처리해야 하기 때문에 다음 사항들이 익숙해야 한다.
- 파이썬
    - 파이썬 애플리케이션의 설치, 설정
    - 파이썬 환경의 관리 및 종속성 관리
    - 사용자 지정 배포를 통한 소프트웨어 실행
- 데이터베이스
    - `airflow db` 커맨드를 통한 데이터베이스 및 스키마 설정/관리
    - 자동화된 시작 및 회복
- 리소스 모니터링 설정
- 설치와 피드백루프를 기반으로 적합한 리소스 구성과 관리 (Memory, CPU 등)


## airflow모듈 설치

#### 패키지 업데이트 및 pip설치

```
sudo apt-get update
# 파이썬을 사용해서 직접 pip를 설치
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py
# 패키지 매니저를 통해서 설치
sudo apt-get install -y python3-pip
```

```
# 이후 airflow설치 중 의존성 충돌이 있을 경우
# 충돌문제를 해결한다.
sudo pip3 install pyopenssl --upgrade
sudo pip3 install launchpadlib
sudo pip3 install setuptools --upgrade
```

#### airflow 설치 및 기타 모듈 설치

```
# sql의존성 에러남
sudo apt-get install -y libmysqlclient-dev
# 여러 공급자를 한번에 설치
sudo pip3 install --ignore-installed "apache-airflow[celery,mysql,postgres,amazon,google]==2.6.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.6.3/constraints-3.7.txt"
# 추가로 필요한 모듈 설치
sudo pip3 install oauth2client gspread pandas
```

## airflow:airflow 계정 생성

airflow서비스를 ubuntu유저가 아닌, airflow유저를 기반으로 실행할 것이기 때문에 계정 설정을 한다.
계정의 홈디렉토리는 `/var/lib/airflow`로 설정한다.
```
sudo groupadd airflow
sudo useradd -s /bin/bash airflow -g airflow -d /var/lib/airflow -m
```

## [Airflow의 메타DB용 Postgres설치](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-up-database.html#setting-up-a-postgresql-database)

SQLite를 기본으로 설치하는데, 싱글스레드이기 때문에 다수 DAG, Task를 위해서는 MySQL이나 Postgres로 교체해야 한다.

여기서는 Postgres를 설치 후 이후 교체한다.

#### Postgres 설치
```
sudo apt-get install -y postgresql postgresql-contrib
```

#### Airflow가 Postgres를 접속할 때의 계정 생성

계정을 Postgres위에서 생성하고, 등록한다.

```
# postgres에 접속하기 위해서 계정을 변경
$ sudo su postgres
$ psql
psql (12.17 (Ubuntu 12.17-0ubuntu0.20.04.1))
Type "help" for help.

postgres=# CREATE USER airflow PASSWORD 'airflow';
CREATE ROLE
postgres=# CREATE DATABASE airflow;
CREATE DATABASE
postgres=# \q
$ exit
```

#### postgres 재시작

위에서 exit를 사용하여 ubuntu 계정으로 나와야 사용 가능함.

```
sudo service postgresql restart
```

## Airflow 초기화

#### Airflow접속 후 기본환경 생성

```
sudo su airflow
cd
mkdir dags
AIRFLOW_HOME=/var/lib/airflow airflow db init

# 아래처럼 홈 설정과 따로 명령을 실행하면 airflow 디렉토리가 하나 더 생긴다.
# (/var/lib/airflow/airflow/airflow.cfg이런식으로,,)
# AIRFLOW_HOME=/var/lib/airflow
# airflow db init

# $AIRFLOW_HOME airflow db init 이래도 안됨.
```

명령 실행 시 `/var/lib/airflow`에 아래와 같이 초기화된다.

이후 postgres설정 후 다시 `airflow db init`을 실행 할 예정이지만, 한번 실행 해야 `airflow.cfg`가 생성된다.

```
$ ls -l
total 544
-rw------- 1 airflow airflow  58979 Dec 27 13:52 airflow.cfg
-rw-r--r-- 1 airflow airflow 475136 Dec 27 13:52 airflow.db
drwxrwxr-x 2 airflow airflow   4096 Dec 27 13:54 dags
drwxrwxr-x 3 airflow airflow   4096 Dec 27 13:52 logs
-rw-rw-r-- 1 airflow airflow   4771 Dec 27 13:52 webserver_config.py
```

#### airflow.cfg 환경파일 수정 (executor, db)

- 기본설정은 SequentialExecutor인데, 이는 싱글스레드 전용이라 병렬처리를 위해 LocalExecutor로 바꿔줘야한다.
- DB연결스트링을 postgres로 바꾼다.
    - 여기서는 ID:PW를 모두 airflow로 사용했다.
    - DB 위치는 localhost

```
[core]
executor = LocalExecutor
...
[database]
sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@localhost:5432/airflow
```
포맷은 다음과 같다 `postgresql+psycopg2://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE]`

#### 변경내용으로 Airflow 재설정

다시 `init`하게 되면 설정 한 postgres의 스키마 내에 테이블들이 생성된다.

```
AIRFLOW_HOME=/var/lib/airflow airflow db init
```

[!이미지]<img>

## Airflow 웹서버, 스케줄러 실행

웹서버와 스케줄러를 백그라운드 서비스로 등록하여 사용한다.
*(ubuntu계정에서 실행되어야 한다.)*

#### 웹서버 스케줄러 서비스 등록

`sudo nano /etc/systemd/system/airflow-webserver.service`

```
[Unit]
Description=Airflow webserver
After=network.target

[Service]
Environment=AIRFLOW_HOME=/var/lib/airflow
User=airflow
Group=airflow
Type=simple
ExecStart=/usr/local/bin/airflow webserver -p 8080
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

`sudo nano /etc/systemd/system/airflow-scheduler.service`

```
[Unit]
Description=Airflow scheduler
After=network.target

[Service]
Environment=AIRFLOW_HOME=/var/lib/airflow
User=airflow
Group=airflow
Type=simple
ExecStart=/usr/local/bin/airflow scheduler
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

#### 서비스 활성화

*systemctl은 부팅부터 서비스관리 로그관리를 담당한다.
목록을 확인하려면 `systemctl list-unit-files`

```
sudo systemctl daemon-reload
sudo systemctl disable airflow-webserver
sudo systemctl disable airflow-scheduler
```

#### 서비스 시작

```
sudo systemctl start airflow-webserver
sudo systemctl start airflow-scheduler
```

#### 서비스 상태 확인

```
sudo systemctl status airflow-webserver
sudo systemctl status airflow-scheduler
```

## Airflow webserver 로그인 계정 생성

airflow 계정에서 실행되어야 한다.

```
sudo su airflow
AIRFLOW_HOME=/var/lib/airflow airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin4321
```

다른 계정에서 실행했을 경우 아래 명령으로 계정을 지운다.
```
AIRFLOW_HOME=/var/lib/airflow airflow users delete --username admin
```

계정 설정이 완료되었다면, 8080포트로 접근하여 로그인 가능하다.   
https(SSL)을 통해서 접근하도록 하고 싶다면 [링크](https://airflow.apache.org/docs/apache-airflow/1.10.1/security.html?highlight=celery#ssl)를 참고

## 이후 Github를 통해서 dags복사

airflow계정으로 홈디렉토리의 dags폴더(`/var/lib/airflow/dags/`)로 복사해야 한다.
`sudo su airflow`를 통해서 계정전환을 하고 하자.

`git clone`, `git pull`, `cp`

## Airflow 계정 로그인 시 홈디렉토리 자동 설정

`sudo su airflow`등으로 airflow유저로 로그인 할 경우 AIRFLOW_HOME과같은 환경변수를 자동으로 설정한다.

`~/.bashrc`파일에 다음 내용을 추가한다.
```
ARIRFLOW_HOME=/var/lib/airflow
export AIRFLOW_HOME
cd ~
```