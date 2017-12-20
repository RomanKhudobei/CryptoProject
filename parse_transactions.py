import sys
import json
import datetime
from pprint import pprint

import requests
import MySQLdb

# Powered by Etherscan.io APIs

def check_existence(cursor):
    '''Checks if database and tables exists, creates them otherwise'''
    cursor.execute('SET sql_notes = 0')     # turning off warnings temporarily

    database_name = 'transactions'
    cursor.execute('CREATE DATABASE IF NOT EXISTS {};'.format(database_name))

    cursor.execute('use {};'.format(database_name))

    table_name = 'transactions'
    cursor.execute("""CREATE TABLE IF NOT EXISTS {} (
                      TxHash VARCHAR(66), 
                      Block VARCHAR(7), 
                      Age DATETIME, 
                      TxFrom VARCHAR(42), 
                      TxTo VARCHAR(42), 
                      Value VARCHAR(20),
                      PRIMARY KEY ( TxHash, Block, Age ));""".format(table_name))

    log_table_name = 'log'
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
    '''Creates templates of commands to insert into tables'''
    table_insert_template = """
        INSERT INTO transactions (TxHash, Block, Age, TxFrom, TxTo, Value)
        VALUES ('{TxHash}', '{Block}', '{Age}', '{TxFrom}', '{TxTo}', '{Value}');
    """

    log_insert_template = """
        INSERT INTO log (TxHash, Block, Age, TxFrom, TxTo, Value, ErrorCode, ErrorDescription)
        VALUES ('{TxHash}', '{Block}', '{Age}', '{TxFrom}', '{TxTo}', '{Value}', {ErrorCode}, '{ErrorDescription}');
    """

    return table_insert_template, log_insert_template

def check_oldness(dt, time_to_check=(1,)):      # time_to_check holds args to timedelta func. To know order check docs
    '''Checks whether or not tx is older than time_to_check (24 hours default)'''
    time_to_check = datetime.timedelta(*time_to_check)  # 24 hours or 1 day
    now = datetime.datetime.now()

    if (now - dt) > time_to_check:      # if tx older than 1 day
        return True

    return False

def write2database(data):
    '''Writes data into table'''
    connection = MySQLdb.connect(host='', 
                                 user='', 
                                 passwd='')

    cursor = connection.cursor()

    check_existence(cursor)

    error_code = 0      # holds encode of error in order to select them from table
    error_description = ''

    for tx in reversed(data['result']):     # reverse in order to iterate descending
        # we need datetime object to compare it
        age = convert2datetime( tx['timeStamp'] )

        if check_oldness(age):
            break

        # datetime to str in format 'YY-MM-DD HH:MM:SS'
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
            error_description = str(e)
            connection.rollback()

        except MySQLdb.IntegrityError as e:
            error_code = 1      # Can't write data into table (mostly dublicate)
            error_description = str(e).replace("'", '"')    # single quote to double
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

def parse_transactions(address, apikey, startblock=0, endblock=99999999, sort='asc'):   # sort='asc'/'des'
    '''
    Requests transactions from Etherscan.io API
        Argumets:
            address - address of ethereum
            apikey - your api key to access the API
            startblock - from which block start collecting tx's
            endblock - where to stop collecting tx's
            sort - 'asc'/'des' (ascending order/descending order)

            *sort doesn't work actually
    '''
    # first variant of 'normal' API
    api = 'http://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock={startblock}&endblock={endblock}&sort={sort}&apikey={apikey}'
    api = api.format(address=address, startblock=startblock, endblock=endblock, sort=sort, apikey=apikey)

    response = requests.get(api)
    data_string = response.text

    data = json.loads(data_string)
    
    write2database(data)


if __name__ == '__main__':
    address = '0x8ca0d43a6b32ce29e78538ea6faaa633e3ff8b41'
    api_key_token = '2UPGUXGVPWH9WTCSMB387Z6W1JSQSANPRD'
    # tx - transaction
    parse_transactions(address, api_key_token)