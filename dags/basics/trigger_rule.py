from airflow.models import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
from airflow.utils.trigger_rule import TriggerRule

from datetime import datetime


"""
트리거 룰을 익히기 전에, 에어플로우 태스크는 특정 상태를 갖는다.
https://airflow.apache.org/docs/apache-airflow/2.6.3/core-concepts/tasks.html#task-instances

전체 실행 상태에 따라서 none, scheduled, queued .. 등 있지만
작업이 끝난 이후의 상태를 기준으로 트리거되며 다음과 같은 상태가 있다.
- success
- failed
- skipped

트리거 조건에 따라서 발생하는 상태
- upstream_failed: 트리거 판별에서 failed와 같은 취급


선행되는(바로 앞의) 태스크의 상태에 따라 trigger rule대로 작업 실행 여부를 결정하게 된다.
default값은 ALL_SUCCESS.

- success의 경우, skip과 success가 구분되어 있기 때문에
  not fail이면 되는게 아니라, 정말 success만 있어야 함.
  (ALL_FAILED역시 skip은 다른 상태이기 때문에 헷갈리지 말자)
    - 디폴트가 ALL_SUCCESS이기 때문에, 스킵도 정상경우로 처리하려면
      NONE_FAILED를 사용하는 것이 좋음


!!
트리거 조건이 만족하지 않는 경우에 upstream_failed와 skipped가 모두 존재하기 때문에
성공(ALL_SUCCESS)의 경우엔 상관없으나, 실패에 관한 태스크를 만들 경우
종료상태를 명확하게 정의하지 못한다면, 태스크 하나를 더 달아서 처리하는 것이 좋아보임.
"""

"""
# trigger_list = [f"{i.name:30}{i.value}" for i in TriggerRule]

===== TriggerRule enum list =====
ALL_SUCCESS                   all_success
ALL_FAILED                    all_failed
ALL_DONE                      all_done
ALL_SKIPPED                   all_skipped
ONE_SUCCESS                   one_success
ONE_FAILED                    one_failed
ONE_DONE                      one_done
# ONE_*의 경우에는 모든 선행작업이 종료되기 전 조건이 만족되면 실행된다.
NONE_FAILED                   none_failed
NONE_FAILED_OR_SKIPPED        none_failed_or_skipped (deprecated; none_failed_min_one_success)
NONE_FAILED_MIN_ONE_SUCCESS   none_failed_min_one_success
# 모든 작업에 FAILED가 없으며, 최소 1개의 작업이 SUCCESS일 경우 실행
NONE_SKIPPED                  none_skipped
DUMMY                         dummy                  (deprecated; always)
ALWAYS                        always
"""

with DAG(
    'basic_trigger_rule',
    start_date=datetime(2024,1,1),
    schedule='@daily',
    catchup=False,
    tags=["example", "basic"],
) as dag:
    
    dummy = EmptyOperator(task_id="dummy")

    success_task = EmptyOperator(task_id="success_task")
    fail_task = BashOperator(task_id="fail_task", bash_command="exit 1")
    skip_task = EmptyOperator(task_id="skip_task", trigger_rule=TriggerRule.ALL_SKIPPED)

    dummy >> skip_task

    for trigger in TriggerRule:
        task = EmptyOperator(task_id=f"rule_{trigger.value}", trigger_rule=trigger)
        [success_task, fail_task, skip_task] >> task

    """
    success, fail, skip 하나씩 해서 각 트리거를 실행 했을 때
    rule_all_success                    : skiped  -> skip이 포함되지 않으면 upstream_failed
    rule_all_failed                     : skiped
    rule_all_done                       : skiped
    rule_all_skipped                    : skiped
    rule_one_success                    : success
    rule_one_failed                     : success
    rule_one_done                       : success
    rule_none_failed                    : upstream failed
  X rule_none_failed_or_skipped         : upstream failed
    rule_none_failed_min_one_success    : upstream failed
    rule_none_skipped                   : skiped
  X rule_dummy                          : success
    rule_always                         : success
    """


"""
if trigger_rule == "dummy":
    warnings.warn(
        "dummy Trigger Rule is deprecated. Please use `TriggerRule.ALWAYS`.",
        RemovedInAirflow3Warning,
        stacklevel=2,
    )
    trigger_rule = TriggerRule.ALWAYS

if trigger_rule == "none_failed_or_skipped":
    warnings.warn(
        "none_failed_or_skipped Trigger Rule is deprecated. "
        "Please use `none_failed_min_one_success`.",
        RemovedInAirflow3Warning,
        stacklevel=2,
    )
    trigger_rule = TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
"""