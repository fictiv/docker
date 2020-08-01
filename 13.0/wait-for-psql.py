#!/usr/bin/env python3
import argparse
import psycopg2
import sys
import time
import os.path
from os import path
import sh
from sh import psql


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--db_host', required=True)
    arg_parser.add_argument('--db_port', required=True)
    arg_parser.add_argument('--db_user', required=True)
    arg_parser.add_argument('--db_password', required=True)
    arg_parser.add_argument('--database', required=False, default=None)
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

    # this is fatal - oddo will not run without it
    if error:
        print("Database connection failure: {}".format(error), file=sys.stderr)
        sys.exit(1)

    # reset our connection
    # print("connection test completed!")
    conn.close()

    # update our local copy of the active odoo database so that the license
    # does not expire. This is not a fatal error when this update fails.

    # NOTE: this only runs when a default --database is supplied in startup
    # (e.g. it is supplied in environment var or defined in odoo.conf)
    # If you only use the UI to select your default database, then you must
    # update this yourself!
    error = ''
    if not error:
        if args.database:
            try:
                conn = psycopg2.connect(user=args.db_user, host=args.db_host, port=args.db_port, password=args.db_password, dbname=args.database)
            except psycopg2.OperationalError as e:
                error = e
                print("Database failure to update odoo database.expiration_date: {}".format(error), file=sys.stderr)
            else:
                try:
                    cur = conn.cursor()
                    cur.execute("UPDATE ir_config_parameter SET VALUE=(MD5(RANDOM()::text || CLOCK_TIMESTAMP()::text)::uuid) WHERE KEY='database.uuid'")
                    cur.execute("UPDATE ir_config_parameter SET VALUE=(CURRENT_DATE + INTERVAL '30 day') WHERE KEY='database.expiration_date';")
                    conn.commit()
                except psycopg2.OperationalError as e:
                    error = e
                    print("Failed to reset license: {}".format(error), file=sys.stderr)
                    print("Try reseting your license manually if it is required")
            finally:
                conn.close()
                # print("license update completed!")
