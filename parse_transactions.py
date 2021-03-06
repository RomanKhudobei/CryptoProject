#!/usr/bin/python2

import sys
import json
import datetime

import requests
import MySQLdb

import config

# Powered by Etherscan.io APIs

def check_existence(cursor):
    '''Checks if database and tables exists, creates them otherwise'''
    cursor.execute('SHOW DATABASES;')

    result = cursor.fetchall()

    if ('crypto_project',) not in result:
        return False
    else:
        cursor.execute('USE crypto_project;')
        cursor.execute('SHOW TABLES;')

        result = cursor.fetchall()
        if ('transactions',) not in result or ('log',) not in result:
            return False

    return True

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

    to_check = datetime.timedelta(**time_to_check)
    now = datetime.datetime.now()

    if (now - dt) > to_check:      # if tx older than time_to_check
        return True

    return False

def write2database(data):
    '''Writes data into table'''
    global host, user, password
    connection = MySQLdb.connect(host=host, 
                                 user=user, 
                                 passwd=password)

    cursor = connection.cursor()

    assert check_existence(cursor) == True, "There's no database or table to write into. Import the 'import.sql' file to MySQL"

    is_error = False    # holds error emergence

    global address      # to check type of tx's (we need only "IN")

    for tx in reversed(data['result']):     # reverse in order to iterate descending
        if tx['to'] != address:
            continue

        error_code = 0      # holds encode of error in order to select them from table
        error_description = ''

        # we need datetime object to compare it
        age = convert2datetime( tx['timeStamp'] )

        if check_oldness(age):
            break

        # datetime to str in format 'YY-MM-DD HH:MM:SS' in order to insert into table
        age = age.strftime('%Y-%m-%d %H:%M:%S')

        table_insert, log_insert = create_insert_templates()

        try:
            assert tx['isError'] != '1', 'Unknown Error ("isError" == "1")'

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

        except MySQLdb.IntegrityError as e:
            pass

        except AssertionError as e:
            error_code = 3      # 'isError' == '1', unknown
            error_description = str(e)

        if error_code and error_description:
            try:
                select = """SELECT TxHash, Block, Age, ErrorCode 
                            FROM log 
                            WHERE TxHash = '{TxHash}'
                            AND Block = '{Block}'
                            AND Age = '{Age}'
                            AND ErrorCode = {ErrorCode};
                         """.format(TxHash=tx['hash'],
                                    Block=tx['blockNumber'],
                                    Age=age,
                                    ErrorCode=error_code)

                cursor.execute(select)
                data = cursor.fetchone()

                if not data:
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
                is_error = True

    if is_error:
        connection.rollback()
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

    api_key = config.API_KEY

    address = config.ADDRESS

    time_to_check = config.TIME_TO_CHECK

    # tx - transaction
    parse_transactions(address, api_key)