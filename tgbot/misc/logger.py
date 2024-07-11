import logging
import betterlogging as bl

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)


def register_logger():
    logging.basicConfig(
        format="%(filename)s [LINE:%(lineno)d] #%(levelname)-6s [%(asctime)s]  %(message)s",
        datefmt="%d.%m.%Y %H:%M:%S",
        level=log_level,
    )
    logger.info("Starting bot")
