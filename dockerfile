FROM python:3.7-slim-buster as airflow
# local executor를 사용하는 것으로 가정하고 작성함.
# used: docker-compose.local.yaml

# 프로덕션 airflow는 airflow유저를 사용함.
# root를 통해서 필수패키지 등 설치 후
# 작업 완료 후 airflow 유저로 바꿔놓아야 한다.
USER root

# airflow 환경변수
ARG AIRFLOW_VERSION=2.6.3
ARG CONSTRAINT_URL=https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt
ENV AIRFLOW_HOME=/var/lib/airflow
# ENV PATH=${PATH}:${AIRFLOW_HOME}/.local/bin

# 선행 USER root
# apt package install
# build-essential: gcc, make 등 빌드도구와 라이브러리 (c, cpp 코드 컴파일, 빌드)
# # libmysqlclient-dev -> default-libmysqlclient-dev  # https://github.com/puckel/docker-airflow/issues/187#issuecomment-394149643
# default-libmysqlclient-dev: MySQL 상호작용 (클라이언트) (c 라이브러리)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nano \
        vim \
        build-essential \
        default-libmysqlclient-dev \
        apt-utils \
        curl \
        rsync \
        netcat \
        locales \
    && apt-get install -y  \
    && pip install -U pip setuptools wheel \
    && pip install pytz \
    && pip install pendulum \
    && pip install pyopenssl --upgrade \
    && pip install launchpadlib \
    && pip install --ignore-installed apache-airflow[celery,mysql,postgres,amazon,google]==${AIRFLOW_VERSION} \
    && pip install oauth2client gspread pandas \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# airflow:airflow 계정 생성 - airflow이미지 사용 시 기본 세팅
RUN groupadd airflow
RUN useradd -s /bin/bash airflow -g airflow -d ${AIRFLOW_HOME} -m

COPY ./entrypoint.sh /entrypoint.sh
COPY /config/airflow.cfg ${AIRFLOW_HOME}/airflow.cfg

RUN chmod +x /entrypoint.sh
RUN chown -R airflow: ${AIRFLOW_HOME}


FROM airflow

# requirements를 통한 패키지 설치
# pip 설치는 root계정보단 airflow 계정으로 하는 것이 좋음
COPY ./requirements.txt .
# pip는 ~/.local에 캐시를 저장함.
# --no-cache-dir을 통해서 이미지 크기 최소화
RUN pip install --no-cache-dir -r requirements.txt

# DAG를 아예 이미지에 포함시키기
# COPY ./dags ${AIRFLOW_HOME}/dags
# COPY ./plugins ${AIRFLOW_HOME}/plugins

# 8080: webserver
# 5555: flower
# 8793: worker
EXPOSE 8080
# EXPOSE 5555 8793

USER airflow
WORKDIR ${AIRFLOW_HOME}

ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["webserver"]