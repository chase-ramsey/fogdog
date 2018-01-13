from app.fogdog import Fogdog
from app.config import Config, create_logger


def go_get_em_fogdog():
	Config.check_env()

	logger = create_logger()
	dog = Fogdog(logger, debug=True)
	dog.fetch()
