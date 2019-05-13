from lib.readers.mysql_reader import mysql
from lib.readers.oracle_reader import oracle
from lib.readers.sheets_reader import sheets
from lib.readers.salesforce_reader import salesforce


readers_list = {
    "mysql": mysql,
    "oracle": oracle,
    "sheets": sheets,
    "salesforce": salesforce
}
