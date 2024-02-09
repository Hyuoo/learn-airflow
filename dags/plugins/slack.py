from airflow.models import Variable

import logging
import requests

"""
슬랙의 web hook을 사용하여 메시지를 요청할 수 있다.

요청 방식은 http
curl -X POST -H 'Content-type: application/json' --data '{"text":"Hello, World!"}'
https://hooks.slack.com/services/[service_url]
"""

# def send_message_to_a_slack_channel(message, emoji, channel, access_token):
def send_message_to_a_slack_channel(message, emoji):
    # url = "https://slack.com/api/chat.postMessage"
    url = "https://hooks.slack.com/services/"+Variable.get("slack_url")
    headers = {
        'content-type': 'application/json',
    }
    data = { "username": "PY_SCRIPT", "text": message, "icon_emoji": emoji }
    res = requests.post(url, headers=headers, json=data)
    return res


def on_failure_callback(context):
    """
    https://airflow.apache.org/_modules/airflow/operators/slack_operator.html
    Define the callback to post on Slack if a failure is detected in the Workflow
    :return: operator.execute
    """
    text = str(context['task_instance'])
    text += "\n```" + str(context.get('exception')) +"```"
    send_message_to_a_slack_channel(text, ":scream:")



if __name__=="__main__":
    on_failure_callback({"task_instance":"HYUOO","exception":"TEST"})
    on_failure_callback({"task_instance":"ASD","exception":"hello world"})