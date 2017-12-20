import sys
import json
import datetime

import requests
import MySQLdb

import config

# Powered by Etherscan.io APIs

def check_existence(cursor):
    '''Checks if database and tables exists, creates them otherwise'''
    cursor.execute('SET sql_notes = 0')     # turning off warnings temporarily

    global database_name
    cursor.execute('CREATE DATABASE IF NOT EXISTS {};'.format(database_name))

    cursor.execute('use {};'.format(database_name))

    global main_table_name
    cursor.execute("""CREATE TABLE IF NOT EXISTS {} (
                      TxHash VARCHAR(66), 
                      Block VARCHAR(7), 
                      Age DATETIME, 
                      TxFrom VARCHAR(42), 
                      TxTo VARCHAR(42), 
                      Value VARCHAR(20),
                      PRIMARY KEY ( TxHash, Block, Age ));""".format(main_table_name))

    global log_table_name
    cursor.execute("""CREATE TABLE IF NOT EXISTS {} (
                      TxHash TEXT, 
                      Block TEXT, 
                      Age DATETIME, 
                      TxFrom TEXT, 
                      TxTo TEXT, 
                      Value TEXT,
                      ErrorCode TINYINT,
                      ErrorDescription TEXT);""".format(log_table_name))

    cursor.execute('SET sql_notes = 1')     # turning on warnings

def create_insert_templates():
    '''Creates templates of insert command in order to further add data into tables'''
    table_insert_template = """
        INSERT INTO transactions (TxHash, Block, Age, TxFrom, TxTo, Value)
        VALUES ('{TxHash}', '{Block}', '{Age}', '{TxFrom}', '{TxTo}', '{Value}');
    """

    log_insert_template = """
        INSERT INTO log (TxHash, Block, Age, TxFrom, TxTo, Value, ErrorCode, ErrorDescription)
        VALUES ('{TxHash}', '{Block}', '{Age}', '{TxFrom}', '{TxTo}', '{Value}', {ErrorCode}, '{ErrorDescription}');
    """

    return table_insert_template, log_insert_template

def check_oldness(dt):
    '''Checks whether or not tx is older than time_to_check'''
    global time_to_check
    time_to_check = datetime.timedelta(**time_to_check)  # 24 hours or 1 day
    now = datetime.datetime.now()

    if (now - dt) > time_to_check:      # if tx older than time_to_check
        return True

    return False

def write2database(data):
    '''Writes data into table'''
    global host, user, password
    connection = MySQLdb.connect(host=host, 
                                 user=user, 
                                 passwd=password)

    cursor = connection.cursor()

    check_existence(cursor)

    error_code = 0      # holds encode of error in order to select them from table
    error_description = ''

    global address      # to check type of tx's (we need only "IN")

    for tx in reversed(data['result']):     # reverse in order to iterate descending
        if tx['to'] != address:
            continue

        # we need datetime object to compare it
        age = convert2datetime( tx['timeStamp'] )

        if check_oldness(age):
            break

        # datetime to str in format 'YY-MM-DD HH:MM:SS' in order to insert into table
        age = age.strftime('%Y-%m-%d %H:%M:%S')

        table_insert, log_insert = create_insert_templates()

        try:
            insert = table_insert.format(TxHash=tx['hash'],
                                         Block=tx['blockNumber'],
                                         Age=age,
                                         TxFrom=tx['from'],
                                         TxTo=tx['to'],
                                         Value=tx['value'])
            cursor.execute(insert)

        except MySQLdb.DataError as e:
            error_code = 2      # Lenght of some col is exceeded a limit
            # single quote to double in order to avoid MySQL ProgrammingError
            error_description = str(e).replace("'", '"')
            connection.rollback()

        except MySQLdb.IntegrityError as e:
            error_code = 1      # Can't write data into table (mostly dublicate)
            # single quote to double in order to avoid MySQL ProgrammingError
            error_description = str(e).replace("'", '"')
            connection.rollback()

        else:
            connection.commit()

        if error_code and error_description:
            try:
                insert = log_insert.format(TxHash=tx['hash'],
                                           Block=tx['blockNumber'],
                                           Age=age,
                                           TxFrom=tx['from'],
                                           TxTo=tx['to'],
                                           Value=tx['value'],
                                           ErrorCode=error_code,
                                           ErrorDescription=error_description)
                cursor.execute(insert)
            except:
                connection.rollback()
                raise
            else:
                connection.commit()

    cursor.close()
    connection.close()

def convert2datetime(timestamp, to_str=True):
    '''Converts timestamp to datetime'''
    if timestamp.isdigit():
        result = datetime.datetime.fromtimestamp( int(timestamp) )
        return result

def parse_transactions(address, apikey, startblock=0, endblock=99999999):
    '''
    Requests transactions from Etherscan.io API
        Argumets:
            address - address of ethereum
            apikey - your api key to access the API
            startblock - from which block start collecting tx's
            endblock - where to stop collecting tx's
    '''
    # first variant of 'normal' transactions API
    api = 'http://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock={startblock}&endblock={endblock}&sort=asc&apikey={apikey}'
    api = api.format(address=address, startblock=startblock, endblock=endblock, apikey=apikey)

    response = requests.get(api)
    data_string = response.text

    data = json.loads(data_string)

    if data['message'] == 'OK' and data['status'] == '1':
        write2database(data)


if __name__ == '__main__':
    host = config.HOST
    user = config.USER
    password = config.PASSWORD

    database_name = config.DATABASE_NAME
    main_table_name = config.MAIN_TABLE_NAME
    log_table_name = config.LOG_TABLE_NAME

    api_key = config.API_KEY

    address = config.ADDRESS

    time_to_check = config.TIME_TO_CHECK

    # tx - transaction
    parse_transactions(address, api_key)
