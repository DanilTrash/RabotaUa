import logging


def logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)
    logger.addHandler(consoleHandler)
    fileHandler = logging.FileHandler('log.log', encoding='utf-8')
    fileHandler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s ~ %(name)s ~ %(levelname)s: %(message)s')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger
