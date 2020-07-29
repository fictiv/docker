#!/usr/bin/env python3
import argparse
import psycopg2
import sys
import time
import os.path
from os import path
import sh
from sh import pg_restore


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

    # this is fatal - oddo will not run without it
    if error:
        print("Database connection failure: {}".format(error), file=sys.stderr)
        sys.exit(1)

    # reset our connection
    # print("connection test completed!")
    conn.close()

    # run any db scripts to create template databases for testing
    # NOTE: if any of these fail we continue and do not stop (e.g no sys.exit)
    # the assumption is that none of these are critical to the operation of the
    # main odoo container
    # TODO: add a template that is pre-loaded with Cypress test data
    templates = [
        'odoo_base',          # only base open source odoo modules installed
        'odoo_enterprise',    # base + licensed enterprise modules
        'odoo_fictiv_no_data' # base + enterprise + fictiv-odoo modules (no data)
    ]

    for database in templates:
        source = './sql/'+database+'.sql'
        # print("checking {} source file...".format(source))
        try:
            # see if the template database already exists
            conn = psycopg2.connect(user=args.db_user, host=args.db_host, port=args.db_port, password=args.db_password, dbname=database)
        except psycopg2.OperationalError as e:
            # see if the definition sql file exists
            # do nothing if there is no definition sql file
            if path.exists(source):
                try:
                    process = subprocess.Popen(
                        ['pg_restore',
                         '--no-owner',
                         '--dbname=postgresql://{}:{}@{}:{}/{}'.format(args.db_user,
                                                                       args.db_password,
                                                                       args.db_host,
                                                                       args.db_port,
                                                                       database),
                         '-v',
                         source],
                        stdout=subprocess.PIPE
                    )
                    output = process.communicate()[0]
                    if int(process.returncode) != 0:
                        print("pg_restore command failed. Return code : {}".format(process.returncode), file=sys.stderr)
                except Exception as e:
                    error = e
                    print("Database restore failure:  {}".format(error), file=sys.stderr)
        else:
            # nothing to do here for this template... move on
            # print("{} connection test completed!".format(database))
            conn.close()

    # update our local copy of the active odoo database so that the license
    # does not expire. This is also not a fatal error when this update fails.
    # NOTE: this only runs when a default --db_database is supplied in startup
    # (e.g. it is supplied in environment var or defined in odoo.conf)
    # If you only use the UI to select your default database, then you must
    # update this yourself!
    if args.db_database:
        try:
            conn = psycopg2.connect(user=args.db_user, host=args.db_host, port=args.db_port, password=args.db_password, dbname=args.db_database)
            error = ''
            cur = conn.cursor()
            cur.execute("UPDATE ir_config_parameter SET VALUE=(MD5(RANDOM()::text || CLOCK_TIMESTAMP()::text)::uuid) WHERE KEY='database.uuid'")
            cur.execute("UPDATE ir_config_parameter SET VALUE=(CURRENT_DATE + INTERVAL '30 day') WHERE KEY='database.expiration_date';")
            conn.commit()
        except psycopg2.OperationalError as e:
            error = e

    if error:
        print("Database failure to update odoo database.expiration_date: %s" % error, file=sys.stderr)
        sys.exit(1)
    # print("license update completed!")
    conn.close()
