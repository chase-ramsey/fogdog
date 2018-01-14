import boto3
import json
import requests
import sys

from config import Config, create_logger
from datetime import datetime
from dateutil.parser import parse
from pytz import timezone
from twilio.rest import Client


NOPE_MSG = 'Sorry dog. No fog.'


class Fogdog:
	def __init__(self, logger, debug=False, debug_data=None, send_msg=True):
		self.client = Client(Config.TWILIO_SID, Config.TWILIO_KEY)
		self.phone = Config.PHONE
		self.weather_api = Config.WEATHER_API
		self.weather_key = Config.WEATHER_KEY
		self.zips = self._load_zips()
		self.logger = logger

		# Debug attrs
		self.debug = debug
		self.debug_data = debug_data
		self.send_msg = send_msg
		self.debug_phone = Config.DEBUG_PHONE

	def _load_zips(self):
		s3_cli = boto3.client('s3')
		try:
			res = s3_cli.get_object(Bucket='foggydoggy', Key='zips.json')
			return json.loads(res['Body'].read().decode('utf8'))
		except Exception as ex:
			self.logger.error(ex)
			return None


	def check_send_no(self):
		"""
		Only send NOPE_MSG once a day at 10am central.
		"""
		if self.debug_data and 'time' in self.debug_data.keys():
			_date = parse(self.debug_data['time'])
			print(_date)
		else:
			tz = timezone('US/Central')
			_date = datetime.now(tz=tz)

		if _date.strftime('%H') == '10':
			return True

	def get_fog_data(self, zip_code):
		if self.debug_data:
			return self.debug_data

		res = requests.get(self.weather_api.format(zip_code, self.weather_key))
		if res.ok:
			data = res.json()
			self.logger.debug(data['weather'])
		else:
			raise Exception(res.text)

	def check_fog(self, zip_code):
		"""
		Returns true if fog, false if not fog
		"""
		data = self.get_fog_data(zip_code)
		if not data:
			return False

		found_fog = list()
		for condition in data['weather']:
			found_fog.append('fog' in condition['main'].lower())
			found_fog.append('fog' in condition['description'].lower())
			found_fog.append('741' == str(condition['id']))

		return any(found_fog)

	def dispatch(self, message):
		if message == NOPE_MSG and not self.check_send_no():
			return

		if self.debug:
			phones = [self.debug_phone]
		else:
			phones = [phone.num for phone in self.client.outgoing_caller_ids.list()]

		for num in phones:
			self.client.messages.create(
				num,
				from_=self.phone,
				body=message
			)

	def fetch(self):
		self.logger.info('Checking for fog...')
		if not self.zips:
			self.logger.error('There was an error retrieving zip codes.')
			return

		fog_spots = set()
		for zip_code, spot in self.zips.items():
			if self.check_fog(zip_code):
				fog_spots.add(spot)

		if len(fog_spots) > 0:
			message = 'Yeah dog. Found fog:'
			for spot in fog_spots:
				message += ' {},'.format(spot)
			message = message[:-1]
		else:
			message = NOPE_MSG

		if self.send_msg:
			self.dispatch(message)

		self.logger.info(message)


if __name__ == '__main__':
	logger = create_logger()
	if len(sys.argv) > 1:
		debug_file = sys.argv[1]
		with open(debug_file, 'r') as f:
			data = json.load(f)['debug']

		send_msg = bool(data['dispatch'])
		logger.info('Running in debug: {}'.format(debug_file))
	else:
		data = None
		send_msg = False

	dog = Fogdog(logger, debug=True, debug_data=data['data'], send_msg=send_msg)
	dog.fetch()
