#!/usr/bin/env python

import logging
import os
import random
import sys

from logging.handlers import RotatingFileHandler
from twilio.rest import Client


def load_file(filename):
	with open(filename, 'r') as f:
		return f.read().splitlines()

NUMBERS = load_file('numbers.txt')
NOPE = load_file('nope.txt')
YEAH = load_file('yeah.txt')


LOGFILE = 'fogdog.log'

def create_logger():
    logger = logging.getLogger('__main__')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s: %(levelname)s] - %(message)s')

    file_handler = RotatingFileHandler(LOGFILE, maxBytes=1000, backupCount=2)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


def dispatch(client, from_phone, message):
	for num in NUMBERS:
		client.messages.create(
			num,
			from_=from_phone,
			body=message
		)		


def check_fog():
	"""
	Returns true if fog, false if not fog
	"""
	return False


def main():
	logger = create_logger()

	ACCOUNT_SID = os.environ.get('TWILIO_SID')
	APIKEY = os.environ.get('TWILIO_TOKEN')
	PHONE = os.environ.get('TWILIO_PHONE')

	if not all((ACCOUNT_SID, APIKEY, PHONE)):
		err_msg = 'Environment not properly configured.'
		logger.warning(err_msg)
		raise Exception(err_msg)

	client = Client(ACCOUNT_SID, APIKEY)

	if check_fog():
		dispatch(client, PHONE, random.choice(YEAH))
		logger.info(random.choice(YEAH))
	else:
		dispatch(client, PHONE, random.choice(NOPE))
		logger.info(random.choice(NOPE))


if __name__ == '__main__':
	main()
