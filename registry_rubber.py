#!/usr/bin/env python
"""
Docker Registry Dynamic Users Service
"""
from flask import Flask
from flask import request
from flask import jsonify
from hashlib import sha1, md5
from base64 import encodestring
import actions
import config

# use sqlite
if config.store_eng == 'sqlite3':
    from sqlite import SqliteConnector as Connector
# use mysql
else:
    from mysql import MysqlConnector as Connector

app = Flask(__name__)
app.debug = config.debug


@app.route('/<action>')
def entry(action):
    """
    registry_user entry point
    execute appropriate action
    """
    user = request.args.get('user') or None
    passwd = request.args.get('passwd') or None
    realm = request.args.get('realm') or None

    # transform password to apache format
    if passwd:
        passwd = apache_hash(passwd, config.hash_type)

    # ## validate input ## #
    # action must be defined
    if user is None or not user.isdigit():
        msg = "Invalid action or user defined in request"
        output = actions.check_response(msg, action)
        return format_response(output, 400)

    # 'add' action requires password
    if action == 'add' and passwd is None:
        msg = "add action requires password"
        output = actions.check_response(msg, action)
        return format_response(output, 400)
    # ## end validate input ## #

    # top level try
    try:
        # get database connection
        conn = db_connect()

        # call passed in action
        call_method = getattr(actions, action)
        output = call_method(conn, config.table,
                             user, passwd)
        return format_response(output, 200)
    # error condition - 400
    except Exception, err:
        # raise exception if debug is enabled
        if config.debug:
            raise
        msg = "%s" % err
        output = actions.check_response(msg=msg, action=action)
        return format_response(output, 400)


def apache_hash(passwd, hash_type='SHA1', user=None, realm=None):
    """
    hash a given password to an apache compatible hash_type
    @param hash_type - type of hash to use.  sha1 for basic or md5 for digest
    http://httpd.apache.org/docs/2.4/misc/password_encryptions.html
    """
    if hash_type == "SHA1":
        # binary digest using sha1
        mysha1 = sha1(passwd).digest()
        # base64 encode binary sha1
        mysha1_base64 = encodestring(mysha1).strip()

        return "{SHA}%s" % format(mysha1_base64)

    # md5 hash_type - needed for digest auth
    elif hash_type == "MD5":
        assert user is not None, "user required for md5 digest auth"
        assert realm is not None, "realm required for md5 digest auth"
        return md5("{0}:{1}:{2}".format(user, realm, passwd).hexdigest())


def format_response(output, code=200):
    """
    return responses
    """
    # append status code to output
    output.update({'status_code': code})
    resp = jsonify(output)
    # set header response
    resp.status_code = code
    return resp


def db_connect():
    """
    fetch connection for configured database type
    """
    try:
        # connect via sqlite
        if config.store_eng == 'sqlite3':
            conn = Connector(config.sqlite_db)
        else:
            # connect to mysql
            conn = Connector(config.host, config.user, config.passwd,
                             config.db, config.port)
        return conn
    except Exception, err:
        raise


if __name__ == '__main__':
    app.run(host='0.0.0.0')
