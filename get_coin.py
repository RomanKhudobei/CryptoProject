from flask import Flask, render_template, request, jsonify
from flask import session as app_session

import random, string
import requests
import datetime as dt

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Coin, IP

import sys

app = Flask(__name__)

engine = create_engine('mysql://root:1619982014automan@localhost:3306/coins?charset=utf8')
Base.metadata.bind = engine

DBsession = sessionmaker(bind=engine)
session = DBsession()

@app.route('/', strict_slashes=False)
def show_get_coin():
	state = ''.join( random.choice(string.ascii_lowercase + string.digits) for x in range(32) )
	app_session['state'] = state
	return render_template('get_coin.html', STATE=state)

@app.route('/get_coin', strict_slashes=False)
def get_coin():
	if app_session['state'] != request.args.get('state'):
		return jsonify(status="Error", description='Invalid state token')

	client_ip = request.remote_addr

	try:
		ip = session.query(IP).filter_by(ip=client_ip).first()
		assert ip != None

		to_check = dt.timedelta(1)		# days=1

		if dt.datetime.now() - ip.date_time > to_check:
			ip.count = 1
			session.add(ip)

		elif ip.count < 5:
			ip.count += 1
			session.add(ip)

		else:
			session.rollback()
			return jsonify(status="Error", description='Daily limit is exhausted')

	except:
		new_ip = IP(ip=client_ip)
		session.add(new_ip)

	session.commit()

	try:
		coin = session.query(Coin).filter_by(valid='X').first()
		assert coin != None
		coin.valid = ' '
		session.add(coin)
	except:
		session.rollback()
		return jsonify(status="Error", description='Coins are over')

	session.commit()
	
	return jsonify(status="OK", coin=coin.entire_key, description='Coin received successful')


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)