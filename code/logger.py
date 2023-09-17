import os
import logging

def log_data(data):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')

    if not os.path.exists('log'):
        os.makedirs('log')

    file_handler = logging.FileHandler('log/music_data.log')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    logger.info(data)

    
def log_multiple_data(*args):
    for data in args:
        log_data(data)
