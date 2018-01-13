import json
import requests

from app.config import Config
from datetime import datetime
from pytz import timezone
from twilio.rest import Client


class Fogdog:
	def __init__(self, logger, debug=False):
		self.client = Client(Config.TWILIO_SID, Config.TWILIO_KEY)
		self.phone = Config.PHONE
		self.weather_api = Config.WEATHER_API
		self.weather_key = Config.WEATHER_KEY
		self.zips = self._load_zips()
		self.logger = logger
		self.debug = debug

	def _load_zips(self):
		# TODO: Load file from S3
		with open('zips.json', 'r') as f:
			return json.load(f)

	def check_send_no(self):
		"""
		Only send NOPE_MSG once a day at 10am central.
		"""
		tz = timezone('US/Central')
		_date = datetime.now(tz=tz)

		if _date.strftime('%H') == '10':
			return True

	def check_fog(self, zip_code):
		"""
		Returns true if fog, false if not fog
		"""
		res = requests.get(self.weather_api.format(zip_code, self.weather_key))
		if res.ok:
			data = res.json()
			self.logger.debug(data['weather'])
		else:
			self.logger.error(res.text)
			return False

		found_fog = list()
		for condition in data['weather']:
			found_fog.append('snow' in condition['main'].lower())
			found_fog.append('fog' in condition['description'].lower())
			found_fog.append('741' == str(condition['id']))

		return any(found_fog)

	def dispatch(self, message):
		if not message:
			return

		for num in self.client.outgoing_caller_ids.list():
			self.client.messages.create(
				num.phone_number,
				from_=self.phone,
				body=message
			)

	def fetch(self):
		self.logger.info('Checking for fog...')
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
			if self.check_send_no():
				message = 'Sorry dog. No fog.'
			else:
				message = None

		if not self.debug:
			self.dispatch(message)
			
		self.logger.info(message)
