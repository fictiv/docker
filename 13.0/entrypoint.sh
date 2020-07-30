#!/bin/bash

set -e

# set the postgres database host, port, user and password according to the environment
# and pass them as arguments to the odoo process if not present in the config file
: ${HOST:=${DB_PORT_5432_TCP_ADDR:='db'}}
: ${PORT:=${DB_PORT_5432_TCP_PORT:=5432}}
: ${USER:=${DB_ENV_POSTGRES_USER:=${POSTGRES_USER:='odoo'}}}
: ${PASSWORD:=${DB_ENV_POSTGRES_PASSWORD:=${POSTGRES_PASSWORD:='odoo'}}}
: ${DATABASE:=${DB_ENV_DATABASE:=${DATABASE:='odoo'}}}
: ${TEMPLATE:=${DB_ENV_TEMPLATE:=${TEMPLATE:='odoo_fictiv_no_data'}}}
: ${UPDATE_ALL}:=${ENV_UPDATE_ALL:=${UPDATE_ALL:='True'}}

DB_ARGS=()
STARTUP_CMDS=()
function check_config() {
    param="$1"
    value="$2"
    if grep -q -E "^\s*\b${param}\b\s*=" "$ODOO_RC" ; then
        value=$(grep -E "^\s*\b${param}\b\s*=" "$ODOO_RC" |cut -d " " -f3|sed 's/["\n\r]//g')
    fi;

    if [[ "${param}" == *"update_all"* && "${value}" == "True" ]]; then
        STARTUP_CMDS+=("-u all")
    elif [[ "${param}" == *"database"* ]]; then
        DB_ARGS+=("--${param}")
        DB_ARGS+=("${value}")
    elif [[ "${param}" == *"db"* ]]; then
        DB_ARGS+=("--${param}")
        DB_ARGS+=("${value}")
    fi;
}
check_config "db_host" "$HOST"
check_config "db_port" "$PORT"
check_config "db_user" "$USER"
check_config "db_password" "$PASSWORD"
check_config "database" "$DATABASE"
check_config "db-template" "$TEMPLATE"
check_config "update_all" "$UPDATE_ALL"

echo ${DB_ARGS[@]}
echo ${STARTUP_CMDS[@]}

case "$1" in
    -- | odoo)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            exec odoo "$@"
        else
            wait-for-psql.py ${DB_ARGS[@]} --timeout=30
            exec odoo "$@" "${DB_ARGS[@]}" "${STARTUP_CMDS[@]}"
        fi
        ;;
    -*)
        wait-for-psql.py ${DB_ARGS[@]} --timeout=30
        exec odoo "$@" "${DB_ARGS[@]}" "${STARTUP_CMDS[@]}"
        ;;
    *)
        exec "$@"
esac

exit 1
