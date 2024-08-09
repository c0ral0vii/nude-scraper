import logging
import sys
import multiprocessing

from browser.main import Firefox
from config.logger_config import setup_logger

logger = setup_logger()

def run_firefox(part):
    firefox = Firefox()
    logger.info(f'Запускаем браузер и скачивание для части {part}')
    firefox.open_start_page(part)

if __name__ == '__main__':
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    num_parts = 3 # Количество частей, на которые нужно разделить алфавит
    
    # Разделяем алфавит на части
    part_length = len(alphabet) // num_parts
    parts = [alphabet[i:i+part_length] for i in range(0, len(alphabet), part_length)]
    
    # Создаем список процессов
    processes = []
    
    for part in parts:
        process = multiprocessing.Process(target=run_firefox, args=(part,))
        processes.append(process)
        process.start()
        logger.info(f"Запустили firefox для части {part}")
    
    # Ждем завершения всех процессов
    for process in processes:
        process.join()
    
    logger.info("Все процессы завершены")