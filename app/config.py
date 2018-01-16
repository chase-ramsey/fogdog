import boto3
import logging
import os
from base64 import b64decode
from enum import Enum
from logging.handlers import RotatingFileHandler


def _decrypt(key_name):
	if bool(os.environ.get('LOCAL')):
		return os.environ.get(key_name)

	client = boto3.client('kms')
	encrypted = b64decode(os.environ.get(key_name))
	return client.decrypt(CiphertextBlob=encrypted)['Plaintext'].decode('utf8')


class Config(Enum):
	TWILIO_SID = _decrypt('TWILIO_SID')
	TWILIO_KEY = _decrypt('TWILIO_TOKEN')
	PHONE = _decrypt('TWILIO_PHONE')
	DEBUG_PHONE = _decrypt('DEBUG_PHONE')

	DEFAULT_CITY_ID = _decrypt('DEFAULT_CITY_ID')
	DEFAULT_CITY_NAME = _decrypt('DEFAULT_CITY_NAME')
	WEATHER_ZIP = _decrypt('WEATHER_ZIP')
	WEATHER_CITY = _decrypt('WEATHER_CITY')
	WEATHER_KEY = _decrypt('WEATHER_TOKEN')

	@classmethod
	def check_env(cls):
		if not all([attr.value for attr in cls]):
			raise Exception('Environment not properly configured.')


def create_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s: %(levelname)s] - %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
