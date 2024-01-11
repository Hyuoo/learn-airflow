#!/bin/bash

TRY_LOOP="20"

# : "${AIRFLOW__CORE__FERNET_KEY:=${FERNET_KEY:=$(python -c "from cryptography.fernet import Fernet; FERNET_KEY = Fernet.generate_key().decode(); print(FERNET_KEY)")}}"

: "${POSTGRES_HOST:="postgres"}"
: "${POSTGRES_PORT:="5432"}"
: "${POSTGRES_USER:="airflow"}"
: "${POSTGRES_PASSWORD:="airflow"}"
: "${POSTGRES_DB:="airflow"}"

export \
    AIRFLOW_HOME \
    AIRFLOW__CORE__EXECUTOR \
    AIRFLOW__CORE__FERNET_KEY \
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN \
    AIRFLOW__CORE__LOAD_EXAMPLES \
    

wait_for_port() {
  local name="$1" host="$2" port="$3"
  local j=0
  while ! nc -z "$host" "$port" >/dev/null 2>&1 < /dev/null; do
    j=$((j+1))
    if [ $j -ge $TRY_LOOP ]; then
      echo >&2 "$(date) - $host:$port still not reachable, giving up"
      exit 1
    fi
    echo "$(date) - waiting for $name... $j/$TRY_LOOP"
    sleep 5
  done
}

create_www_user() {
    local local_password=""
    # Warning: command environment variables (*_CMD) have priority over usual configuration variables
    # for configuration parameters that require sensitive information. This is the case for the SQL database
    # and the broker backend in this entrypoint script.
    if [[ -n "${_AIRFLOW_WWW_USER_PASSWORD_CMD=}" ]]; then
        local_password=$(eval "${_AIRFLOW_WWW_USER_PASSWORD_CMD}")
        unset _AIRFLOW_WWW_USER_PASSWORD_CMD
    elif [[ -n "${_AIRFLOW_WWW_USER_PASSWORD=}" ]]; then
        local_password="${_AIRFLOW_WWW_USER_PASSWORD}"
        unset _AIRFLOW_WWW_USER_PASSWORD
    fi
    if [[ -z ${local_password} ]]; then
        echo
        echo "ERROR! Airflow Admin password not set via _AIRFLOW_WWW_USER_PASSWORD or _AIRFLOW_WWW_USER_PASSWORD_CMD variables!"
        echo
        exit 1
    fi

    airflow users create \
       --username "${_AIRFLOW_WWW_USER_USERNAME="admin"}" \
       --firstname "${_AIRFLOW_WWW_USER_FIRSTNAME="Airflow"}" \
       --lastname "${_AIRFLOW_WWW_USER_LASTNAME="Admin"}" \
       --email "${_AIRFLOW_WWW_USER_EMAIL="airflowadmin@example.com"}" \
       --role "${_AIRFLOW_WWW_USER_ROLE="Admin"}" \
       --password "${local_password}" || true
}

wait_for_port "Postgres" "$POSTGRES_HOST" "$POSTGRES_PORT"

case "$1" in
  webserver)
    airflow db init
    create_www_user
    if [ "$AIRFLOW__CORE__EXECUTOR" = "LocalExecutor" ]; then
      # With the "Local" executors it should all run in one container.
      airflow scheduler &
    fi
    exec airflow webserver
    ;;
#   worker)
#     echo "Executing worker section"
#     airflow db init

#     # Give the webserver time to run initdb.
#     sleep 10
#     exec airflow celery "$@"
#     ;;

#   scheduler)
#     airflow db init

#     # Give the webserver time to run initdb.
#     sleep 10
#     exec airflow "$@"
#     ;;
#   version)
#     exec airflow "$@"
#     ;;
#   *)
#     # The command is something like bash, not an airflow subcommand. Just run it in the right environment.
#     exec "$@"
#     ;;
esac