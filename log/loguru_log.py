from loguru import logger

logger.add("logs/logs_{time}.log", format="{time}, {level}, {message}", level="DEBUG", rotation="06:00", retention="10 days", compression="zip")
logger.debug('Error')
logger.info('Information message')
logger.warning('Warning')