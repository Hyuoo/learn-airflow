## Dynamic Dag

DAG 코드를 jinja를 사용하여 템플릿으로 만들고, YAML 기반으로 파라미터를 정의하여 동적으로 dag를 생성한다.

비슷한 dag를 매뉴얼하게 계속해서 생성하는것을 방지

다음과 같은 상황에서 dag를 분리시키는게 좋다.
- dag의 오너가 다름
- 한 dag에 태스크가 너무 많음


### 구현 예

주식정보를 처리하는 DAG를 생성함에 있어서 주식에 따라서 실행계획(`schedule`), 종목코드(`symbol`)등이 조금씩 달라진다.

이 때, 몇가지 파라미터를 yaml파일로 지정하여 템플릿으로 생성하는 예제
- `dag_id`, `schedule`, `catchup`, `symbol`에 대해서 파라미터를 지정
- `generator.py`를 통해서 `{dag}.py` 파일을 생성한다.

파이썬으로 해당 코드를 실행시키면 config파일 수 대로 dag파일이 생성된다.