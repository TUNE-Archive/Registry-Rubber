"""
configuration file for registry_rubber
"""

# set storage engine parameters
# (sqlite3 or mysql)
store_eng = 'sqlite3'
if store_eng == 'sqlite3':
    # sqlite uses ? for substitution
    store_eng_symbol = """?"""
else:
    # mysqldb uses %s for substitution
    store_eng_symbol = """%s"""

# mysql config
user = """dev"""
passwd = """developme"""
db = """registry_rubber"""
port = 3306
host = """localhost"""

# sqlite3 config
sqlite_db = """/tmp/registry_rubber.sqlite"""
sqlite_schema = """CREATE TABLE IF NOT EXISTS `users` (""" \
                """`username` integer NOT NULL,""" \
                """`password` varchar(64) NOT NULL,PRIMARY KEY (`username`));"""

# SHA1 for basic or MD5 for digest
# http://httpd.apache.org/docs/2.4/misc/password_encryptions.html
hash_type = 'SHA1'

# set sql table
table = """users"""

# default threhold to delete users (10m)
user_del_threshold = 600

# set debug mode
debug = False
