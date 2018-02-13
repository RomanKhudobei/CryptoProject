import MySQLdb

import config


def check_existence(cursor):
	cursor.execute('SHOW DATABASES;')

	result = cursor.fetchall()

	if ('coins',) not in result:
		return False
	else:
		cursor.execute('USE coins;')
		cursor.execute('SHOW TABLES;')

		result = cursor.fetchall()
		if ('coins',) not in result:
			return False

	return True
	

def write_coins():
	connection = MySQLdb.connect(host=config.HOST,
				     user=config.USER,
				     passwd=config.PASSWORD)
	cursor = connection.cursor()

	assert check_existence(cursor) == True, "There's no database or table to write into"

	with open('key.dat', 'r', encoding='utf-8') as file:
		coins = file.read()

		coins = [tuple(coin.split(';')) for coin in coins.split('\n')][:-1]		# except last element, because he is invalid ('',) because of the last '\n' in file
		for coin_id, private_key in coins:
			query = "INSERT INTO coins (coin_id, entire_key) VALUES (%s, %s);"
			cursor.execute(query, (coin_id, coin_id + '-' + private_key))

	connection.commit()

	cursor.close()
	connection.close()

if __name__ == '__main__':
	write_coins()
