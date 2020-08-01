#!/bin/bash

set -e

# set the postgres database host, port, user and password according to the environment
# and pass them as arguments to the odoo process if not present in the config file
: ${HOST:=${DB_PORT_5432_TCP_ADDR:='db'}}
: ${PORT:=${DB_PORT_5432_TCP_PORT:=5432}}
: ${USER:=${DB_ENV_POSTGRES_USER:=${POSTGRES_USER:='odoo'}}}
: ${PASSWORD:=${DB_ENV_POSTGRES_PASSWORD:=${POSTGRES_PASSWORD:='odoo'}}}
: ${DATABASE:=${DB_ENV_DATABASE:=${DATABASE:='None'}}}
: ${TEMPLATE:=${DB_ENV_TEMPLATE:=${TEMPLATE:='None'}}}
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
        # update existing db only
        STARTUP_CMDS+=("-u all")
        # base odoo + enterprise + fictiv
        # STARTUP_CMDS+=("-i fictiv_application")
    elif [[ "${param}" == *"database"* && "${value}" != "None"  ]]; then
        DB_ARGS+=("--${param}")
        DB_ARGS+=("${value}")
        STARTUP_CMDS+=("--${param}")
        STARTUP_CMDS+=("${value}")
    elif [[ "${param}" == *"db-template"* && "${value}" != "None" ]]; then
        STARTUP_CMDS+=("--db-template")
        STARTUP_CMDS+=("${value}")
    elif [[ "${param}" == *"db_"* ]]; then
        DB_ARGS+=("--${param}")
        DB_ARGS+=("${value}")
        STARTUP_CMDS+=("--${param}")
        STARTUP_CMDS+=("${value}")
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

            # run any db scripts to create template databases for testing
            # NOTE: create database command is in the sql template file so it does
            # not matter where this connection goes
            exec psql --dbname=postgres://"$USER":"$PASSWORD"@"$HOST":"$PORT"/postgres -q --file="/mnt/sql/odoo_base.sql" & (sleep 30) & wait
            exec psql --dbname=postgres://"$USER":"$PASSWORD"@"$HOST":"$PORT"/postgres -q -c "CREATE DATABASE odoo WITH TEMPLATE odoo_base" & (sleep 5) & wait
            exec mkdir -p /var/lib/odoo/filestore & (sleep 1) & wait
            exec cp -rp /mnt/files/odoo_base /var/lib/odoo/filestore/odoo_base & (sleep 5) & wait
            exec cp -rp /mnt/files/odoo_base /var/lib/odoo/filestore/odoo & (sleep 1) & wait
            exec chown -R odoo.odoo /var/lib/odoo/filestore & (sleep 1) & wait

            exec odoo "$@" "${STARTUP_CMDS[@]}"
        fi
        ;;
    -*)
        wait-for-psql.py ${DB_ARGS[@]} --timeout=30

        # run any db scripts to create template databases for testing
        # NOTE: create database command is in the sql template file so it does
        # not matter where this connection goes
        exec psql --dbname=postgres://"$USER":"$PASSWORD"@"$HOST":"$PORT"/postgres -q --file="/mnt/sql/odoo_base.sql" & (sleep 30) & wait
        exec psql --dbname=postgres://"$USER":"$PASSWORD"@"$HOST":"$PORT"/postgres -q -c "CREATE DATABASE odoo WITH TEMPLATE odoo_base" & (sleep 5) & wait
        exec mkdir -p /var/lib/odoo/filestore & (sleep 1) & wait
        exec cp -rp /mnt/files/odoo_base /var/lib/odoo/filestore/odoo_base & (sleep 5) & wait
        exec cp -rp /mnt/files/odoo_base /var/lib/odoo/filestore/odoo & (sleep 1) & wait
        exec chown -R odoo.odoo /var/lib/odoo/filestore & (sleep 1) & wait

        exec odoo "$@" "${STARTUP_CMDS[@]}"
        ;;
    *)
        exec "$@"
esac

export GRAPHQL_ENDPOINT=http://localhost:4000/api/graphql
# set this to the appropriate value and uncomment before starting containers
# export GRAPHQL_API_KEY=
export ODOO_HOST=localhost
export ODOO_PROTOCOL=http
export ODOO_PORT=8069
export ODOO_USER='erp-api@fictiv.com'
export ODOO_PASS='3DPrinting2014!'
export ODOO_DB=$DATABASE
export ODOO_ROOT=http://localhost:8069/xmlrpc/2/
export LOG_LEVEL=debug
export S3_EVENT_BUCKET='fictiv-events-dev'
export S3_EVENT_PATH='events/fictiv-dev/'
export S3_EVENT_ORDER_PATH='system-v1/order_paid-v1/'
export S3_PART_BUCKET='fictiv-dev-envs-dev'
export S3_PART_PATH='localdev/parts/'
# set this to the appropriate value and uncomment before starting containers
# export GRAPHIQL_USER_EMAIL=

exit 1
