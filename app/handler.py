from fogdog import Fogdog
from config import Config, create_logger


def go_get_em_fogdog(event, context):
	Config.check_env()

	logger = create_logger()

	if 'debug' in event.keys():
		dog = Fogdog(
			logger,
			debug=True,
			debug_data=event['debug']['data'],
			send_msg=bool(event['debug']['dispatch'])
		)
	else:
		dog = Fogdog(logger)

	dog.fetch()
