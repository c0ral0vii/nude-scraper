import logging
import sys
import multiprocessing

from browser.main import Firefox

from config.logger_config import setup_logger



def run_firefox():
    firefox = Firefox()
    logger.info('Запускаем браузер и скачивание')
    firefox.open_start_page()


if __name__ == '__main__':
    logger = setup_logger()

    firefox_process = multiprocessing.Process(target=run_firefox)    
    firefox_process.start()

    logger.info("Запустили firefox")
    firefox_process.join()
    