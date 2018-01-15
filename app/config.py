import logging
import os
from logging.handlers import RotatingFileHandler


class Config(object):
	TWILIO_SID = os.environ.get('TWILIO_SID')
	TWILIO_KEY = os.environ.get('TWILIO_TOKEN')
	PHONE = os.environ.get('TWILIO_PHONE')
	DEBUG_PHONE = os.environ.get('DEBUG_PHONE')

	DEFAULT_CITY_ID = os.environ.get('DEFAULT_CITY_ID')
	DEFAULT_CITY_NAME = os.environ.get('DEFAULT_CITY_NAME')
	WEATHER_ZIP = os.environ.get('WEATHER_ZIP')
	WEATHER_CITY = os.environ.get('WEATHER_CITY')
	WEATHER_KEY = os.environ.get('WEATHER_TOKEN')

	@classmethod
	def check_env(cls):
		config_vars = (
			cls.TWILIO_SID,
			cls.TWILIO_KEY,
			cls.PHONE,
			cls.DEBUG_PHONE,
			cls.DEFAULT_CITY_ID,
			cls.DEFAULT_CITY_NAME,
			cls.WEATHER_ZIP,
			cls.WEATHER_CITY,
			cls.WEATHER_KEY
		)

		if not all(config_vars):
			raise Exception('Environment not properly configured.')


def create_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('[%(asctime)s: %(levelname)s] - %(message)s')

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
