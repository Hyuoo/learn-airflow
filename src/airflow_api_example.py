"""
airflow api를 파이썬 코드를 활용하여 조작하는 예

get_health():
    호스트 airflow의 상태 체크

get_list_for(attr, auth):
    dags, variables, connections, config 옵션을 attr로 받아서 목록을 출력
    endpoint가 동일하여 일괄된 구조로 구현

print_active_dags():
    get_list_for("dags", ..)를 사용하여 dag목록을 받아온 뒤, active상태의 dag만 출력

run_dag(DAG_ID, auth):
    dag_id를 입력하여 해당 dag를 실행
    request data를 통해서 execution_date와 같이 실행정보를 줄 수 있다.
"""

import requests
import json
# HTTPBasicAuth 없이 튜플로 (id,pw)해도 정상동작
from requests.auth import HTTPBasicAuth
from datetime import datetime

'''
https://airflow.apache.org/docs/apache-airflow/stable/stable-rest-api-ref.html
'''

HOST_URL = "http://localhost:8080"

def prettify_dict(json_text, indent=4):
    """json data prettyfy indent"""
    return json.dumps(json_text, indent=indent)

def get_health():
    """
    curl -X GET --user "monitor:MonitorUser1" http://localhost:8080/health

    {
        "metadatabase": {
            "status": "healthy"
        },
        "scheduler": {
            "latest_scheduler_heartbeat": "2023-06-22T07:03:11.513967+00:00",
            "status": "healthy"
        }
    }
    """
    print("get_health() ..",end=" ")
    url = HOST_URL + "/health"
    headers = {
        'user':'monitor:MonitorUser1',
    }
    res = requests.get(url, headers=headers)
    if res.status_code==200:
        print(f"request OK: {res.status_code}")
        # print(prettify_dict(res.json()))
        return res.json()
    else:
        print(f"request BAD: {res.status_code}")
        return None

def get_list_for(attr, auth):
    """
    curl -X GET --user "airflow:airflow" http://localhost:8080/api/v1/[attr]

    :param attr: ( dags | variables | connections | config )
    :param auth: "userid@password"
    """
    url = HOST_URL + "/api/v1/" + attr
    print(f"request to <{url}> .. ",end="")
    user_id, user_pw = auth.split(":")

    # auth = HTTPBasicAuth(id,pw)로 안해도 됨
    res = requests.get(url, auth=(user_id, user_pw))
    if res.status_code==200:
        print(f"OK: {res.status_code}")

        if attr=="config":
            return res.text

        # print(prettify_dict(res.json()))
        return res.json()
    else:
        print(f"BAD: {res.status_code}")
        return None

def print_active_dags():
    """
    is_paused가 False인, active상태의 dag_id만 출력
    """
    dags = get_list_for("dags", "airflow:airflow")["dags"]
    for dag in dags:
        if dag["is_paused"]==False:
            print(dag["dag_id"])
            # print(prettify_dict(dag))

def run_dag(DAG_ID:str, auth:str):
    """
    curl -X POST --user "airflow:airflow" -H 'Content-Type: application/json' -d '{"execution_date":"2023-05-24T00:00:00Z"}' "http://localhost:8080/api/v1/dags/HelloWorld/dagRuns"

    :param DAG_ID: "DAG_ID"
    :param auth: "userid@password"
    :return: response status
    """
    url = HOST_URL + f'/api/v1/dags/{DAG_ID}/dagRuns'
    print(f"request to <{url}> .. ",end="")

    user_id, user_pw = auth.split(":")

    headers = {
        'Content-Type':'application/json',
    }
    data = {
        # datetime.now() 안댐
        'execution_date':"2023-06-20T00:00:00Z"
    }
    res = requests.post(url, headers=headers, json=data, auth=(user_id,user_pw))
    print(res.text)
    return res.status_code

# print(prettify_dict(get_health()))
# print(run_dag("HelloWorld", "airflow:airflow"))
print(get_list_for("config","airflow:airflow"))
# print_active_dags()