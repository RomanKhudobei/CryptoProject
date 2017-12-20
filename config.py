# Info to connect to MySQL database
HOST = ''
USER = ''
PASSWORD = ''

DATABASE_NAME = 'transactions'
MAIN_TABLE_NAME = 'transactions'
LOG_TABLE_NAME = 'log'

API_KEY = '2UPGUXGVPWH9WTCSMB387Z6W1JSQSANPRD'

ADDRESS = ''

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
