from fogdog import Fogdog
from config import Config, create_logger


def go_get_em_fogdog(event, context):
	Config.check_env()

	logger = create_logger()

	dog = Fogdog(logger)
	dog.fetch()
