import logging


def get_module_logger(logger_name, log_level=logging.INFO, file_path=None):
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    fmt = "%(asctime)s|%(name)s|%(levelname)s|FUNC: %(funcName)s|LINE: %(lineno)d|MESSAGE: %(message)s"
    stream_formatter = logging.Formatter(fmt=fmt)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)

    logger.addHandler(stream_handler)

    if file_path:
        file_handler = logging.FileHandler(filename=file_path)
        file_handler.setFormatter(stream_formatter)
        logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":
    logger = get_module_logger(__name__, file_path="ttt.log")
    logger.info("Hellooo")
    logger.warning("Hellooo")
    logger.debug("Hellooo")
