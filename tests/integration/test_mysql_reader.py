import os
from nck.readers.mysql_reader import MySQLReader


class TestMySQlReader:

    # using tests/resources/employees.sql database

    basic_query = "SELECT * FROM firstname"

    # +---------+
    # | myfield |
    # +---------+
    # | Pierre  |
    # | Julien  |
    # +---------+

    sql_env = {
        "user" : os.environ["MYSQL_USER"],
        "password" : os.environ["MYSQL_PASSWORD"],
        "host" : os.environ["MYSQL_HOST"],
        "port": os.environ["MYSQL_PORT"],
        "database" : os.environ["MYSQL_DATABASE"]
    }

    sql_env["query"] = basic_query

    mySQLReader = MySQLReader(**sql_env)

    def test_one(self):
        # MySQLReader.read() returns a generator object we need to extract
        json_stream = list(self.mySQLReader.read())
        request_result = list(json_stream[0].readlines())
        assert request_result == [{'myfield': 'Pierre'}, {'myfield': 'Julien'}]
