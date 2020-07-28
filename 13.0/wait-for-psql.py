#!/usr/bin/env python3
import argparse
import psycopg2
import sys
import time


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--db_host', required=True)
    arg_parser.add_argument('--db_port', required=True)
    arg_parser.add_argument('--db_user', required=True)
    arg_parser.add_argument('--db_password', required=True)
    arg_parser.add_argument('--db_database', required=False)
    arg_parser.add_argument('--timeout', type=int, default=5)

    args = arg_parser.parse_args()

    start_time = time.time()
    while (time.time() - start_time) < args.timeout:
        try:
            conn = psycopg2.connect(user=args.db_user, host=args.db_host, port=args.db_port, password=args.db_password, dbname='postgres')
            error = ''
            break
        except psycopg2.OperationalError as e:
            error = e
        else:
            conn.close()
        time.sleep(1)

    if error:
        print("Database connection failure: %s" % error, file=sys.stderr)
        sys.exit(1)

    # try to update odoo database key for development environment so it does not expire
    # if the odoo database does not exist this will fail, but should not stop the server from coming up correctly
    # so we swallow the error
    if args.db_database:
        try:
            conn = psycopg2.connect(user=args.db_user, host=args.db_host, port=args.db_port, password=args.db_password, dbname=args.db_database)
            error = ''

            cur = conn.cursor()
            cur.execute("UPDATE ir_config_parameter SET VALUE=(MD5(RANDOM()::text || CLOCK_TIMESTAMP()::text)::uuid) WHERE KEY='database.uuid'")
            cur.execute("UPDATE ir_config_parameter SET VALUE=(CURRENT_DATE + INTERVAL '30 day') WHERE KEY='database.expiration_date';")

            # you run any db migration scripts that must be run as SQL commands here
            # but only do this if odoo will not start without these changes

            break
        except psycopg2.OperationalError as e:
            error = e
        else:
            conn.commit()
            conn.close()
