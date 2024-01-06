# Using Production Docker Images

> [데이터엔지니어링 airflow-setup Docker](https://github.com/keeyong/airflow-setup/blob/main/docs/Airflow%20Docker%20Local%20Setup.md#docker-settings)   

프로덕션 도커 이미지를 사용하여 Airflow를 실행
- `Ubuntu 22.04.3 LTS` (`WSL2`)
- `Docker 24.0.7`, `Docker compose 2.21.0`
- `Airflow 2.6.3`

컨테이너에 익숙하고 컨테이너 이미지 빌드를 이해하고 있어야 한다.
 의존성이나 확장은 PyPI를 다루는 방법이 익숙하면 된다.

- 컨테이너
    - 이미지 빌드파일 정의
    - compose와 같은 멀티 컨테이너 구축
- 데이터베이스
    - `airflow db` 커맨드를 통한 데이터베이스 및 스키마 설정/관리
    - 자동화된 시작 및 회복
- 리소스 모니터링 설정
- 설치와 피드백루프를 기반으로 적합한 리소스 구성과 관리 (Memory, CPU 등)


## Docker install 확인

도커가 설치되어 있다는 가정 하에 진행한다.
설치가 안되었다면 [링크](https://historical-medicine-5c0.notion.site/Install-Docker-Engine-on-Ubuntu-fb209b19fdbd4459a8e9ed2f074dd21b?pvs=4)를 참고하여 설치한다.
```
$ docker compose version
Docker Compose version v2.21.0
```

## compose.yaml 다운로드 및 실행

#### 2.6.3버전 yaml파일 다운로드

url중간의 버전을 바꿔서 설치 가능.

```
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.6.3/docker-compose.yaml'
```

#### airflow 실행

`airflow-init`서비스를 먼저 실행해서 환경설정을 해준다.
에어플로우 초기화와 redis, postgres 초기화 및 실행이 진행된다.

> init을 먼저 호출하지 않아도 알아서 먼저 실행된다.
> ```
> hyuoo-airflow-init-1  | User "airflow" created with role "Admin"
> hyuoo-airflow-init-1  | 2.6.3
> hyuoo-airflow-init-1 exited with code 0
> ```
> init이 정상적으로 완료되면 위와 같은 메시지로 끝난다.

```
# docker compose up airflow-init
docker compsoe up
```

이후 `docker ps`를 사용하여 postgres와 redis가 실행중인걸 볼 수 있다.

![docker_airflow_init](/images/installation_airflow_docker_01.png)

모든 컨테이너를 제대로 실행시키면 아래와 같다.
(`postgres`, `redis`, `webserver`, `scheduler`, `worker`, `triggerer`)

![docker_ps](/images/installation_airflow_docker_02.png)

정상적으로 실행되면 http://localhost:8080 으로 ID:PW `airflow:airflow`로 접속할 수 있다.

#### 컨테이너에 직접 로그인

```
docker exec -it <CONTAINER_ID> sh
```

쉘 내에서 airflow 명령어를 직접 실행할 수 있다.

#### 루트로 로그인하려면

```
docker exec -it -u root <CONTAINER_ID> sh
```

> 예를들어 `No module named 'MySQLdb'`에러가 발생하면, root로 로그인하여 패키지관리자 업데이트, 패키지 설치 등의 작업을 수행할 수 있다.

## 뒷정리

컨테이너, 볼륨, 데이터베이스 데이터, 다운로드 이미지 모두 삭제하기
```
docker compose down --volumes --rmi all
```