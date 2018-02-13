# Info to connect to MySQL database
HOST = ''
USER = ''
PASSWORD = ''
PORT = ''

DATABASE_NAME = 'transactions'
MAIN_TABLE_NAME = 'transactions'
LOG_TABLE_NAME = 'log'

API_KEY = '2UPGUXGVPWH9WTCSMB387Z6W1JSQSANPRD'

ADDRESS = '0xf872e98dbe7e7f2a6abfa35e5c8c2bc9fe4e2ca7'

# Time to check oldness of transaction
# How old transactions you want to add to your table
# Example:
# if transaction older than TIME_TO_CHECK, then script will stop iterating
# *NOTE: order of transactions is descending (from new to old)
TIME_TO_CHECK = {
    'days': 1,
    'seconds': 0,
    'microseconds': 0,
    'milliseconds': 0,
    'minutes': 0,
    'hours': 0,
    'weeks': 0
}

APP_SECRET_KEY = 'super_secret_key'		# For session creation
APP_HOST = '0.0.0.0'	# localhost
APP_PORT = 5000
