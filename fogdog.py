#!/usr/bin/env python

import json
import logging
import os
import random
import requests

from datetime import datetime
from logging.handlers import RotatingFileHandler
from pytz import timezone
from twilio.rest import Client


LOGFILE = 'fogdog.log'

def create_logger():
    logger = logging.getLogger('__main__')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s: %(levelname)s] - %(message)s')

    file_handler = RotatingFileHandler(LOGFILE, maxBytes=100000, backupCount=2)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

logger = create_logger()


YEAH_MSG = 'Yeah dog. Found fog:'
NOPE_MSG = 'Sorry dog. No fog.'

with open('numbers.txt', 'r') as f:
	NUMBERS = f.read().splitlines()


def dispatch(client, from_phone, message):
	if not message:
		return

	for num in NUMBERS:
		client.messages.create(
			num,
			from_=from_phone,
			body=message
		)


def check_send_no():
	"""
	Only send NOPE_MSG once a day at 10am central.
	"""
	tz = timezone('US/Central')
	_date = datetime.now(tz=tz)

	if _date.strftime('%H') == '10':
		return True


def check_fog(zip_code, api_key):
	"""
	Returns true if fog, false if not fog
	"""
	get_str = 'https://api.openweathermap.org/data/2.5/weather?zip={},us&APPID={}'
	res = requests.get(get_str.format(zip_code, api_key))
	if res.ok:
		data = res.json()
		logger.debug(data)
	else:
		logger.error(res.text)
		return False

	_main = 'fog' in data['weather'][0]['main'].lower()
	_desc = 'fog' in data['weather'][0]['description'].lower()
	_code = '741' == data['weather'][0]['id']

	return any([_main, _desc, _code])


def main():
	TWILIO_SID = os.environ.get('TWILIO_SID')
	TWILIO_KEY = os.environ.get('TWILIO_TOKEN')
	PHONE = os.environ.get('TWILIO_PHONE')

	WEATHER_API = os.environ.get('WEATHER_API')
	WEATHER_KEY = os.environ.get('WEATHER_TOKEN')

	with open('zips.json', 'r') as f:
		ZIP_CODES = json.load(f)

	if not all((TWILIO_SID, TWILIO_KEY, PHONE, WEATHER_KEY)):
		err_msg = 'Environment not properly configured.'
		logger.warning(err_msg)
		raise Exception(err_msg)

	client = Client(TWILIO_SID, TWILIO_KEY)

	fog_spots = set()
	for zip_code, spot in ZIP_CODES.items():
		if check_fog(zip_code, WEATHER_KEY):
			fog_spots.add(spot)

	if len(fog_spots) > 0:
		message = YEAH_MSG
		for spot in fog_spots:
			message += ' {},'.format(spot)
		message = message[:-1]
	else:
		if check_send_no():
			message = NOPE_MSG
		else:
			message = None

	dispatch(client, PHONE, message)
	logger.info(message)


if __name__ == '__main__':
	main()
