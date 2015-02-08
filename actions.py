"""
action definitions for registry_rubber
"""
import config
from datetime import datetime, timedelta


def delete(conn, table, user, passwd=None):
    """
    alias action delete -> remove
    """
    return remove(conn, table, user, passwd)


def remove(conn, table, user, passwd=None):
    """
    remove a user from the mysql table
    """
    # build query
    query = "DELETE FROM {0} WHERE username={1}"
    query = query.format(table, config.store_eng_symbol)
    params = (user,)

    # execute query
    conn.trans_query(query, params)
    msg = "removed user {0}".format(user)
    return check_response(msg, action='remove', success=True)


def add(conn, table, user, passwd):
    """
    add a user to the mysql table
    """
    # build query
    query = "SELECT * FROM {0} WHERE username={1}"
    query = query.format(table, config.store_eng_symbol)
    params = (user,)

    # if record exists delete it
    if len(conn.query(query, params)) != 0:
        remove(conn, table, user, passwd)

    # build query
    query = "INSERT INTO {0} (username, password) VALUES({1},{1})"
    query = query.format(table, config.store_eng_symbol)
    params = (user, passwd)

    # execute query
    conn.trans_query(query, params)
    msg = "Added user {0}".format(user)
    return check_response(msg, action='add', success=True)


def cleanup(conn, table, user=None, passwd=None,
            threshold=config.user_del_threshold):
    """
    cleanup users a user from the mysql table given a threshold
    """
    cutoff = datetime.now() - timedelta(seconds=threshold)

    # build query
    query = "DELETE FROM {0} WHERE username < {1}"
    query = query.format(table, config.store_eng_symbol)
    params = (cutoff.strftime('%s'),)

    # execute query
    conn.trans_query(query)
    msg = "removed users older than epoch {0}".format(cutoff.strftime('%c'))
    return check_response(msg, action='cleanup', success=True)


def check_response(msg, action, success=False):
    """
    functions to faciliate json response
    @param msg - message to return
    @param action - dict of check specific variables to return
    @param success - boolean representing healthcheck status
    """
    dict_return = {'msg': msg, 'action': action}
    # successful healthchecks return
    if success:
        dict_return['response'] = 'OKAY'
        return dict_return
    # bad healthchecks raise an Exception
    else:
        dict_return['response'] = 'ERROR'
        return dict_return
