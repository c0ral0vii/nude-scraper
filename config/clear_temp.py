import os
import shutil
from config.logger_config import setup_logger
from config.config import PATH_TO_SAVE

logger = setup_logger()


def clean_temp_folder():
    logger.info(f'Очистка папки {PATH_TO_SAVE}')
    
    if os.path.exists(PATH_TO_SAVE):
        try:
            for filename in os.listdir(PATH_TO_SAVE):
                file_path = os.path.join(PATH_TO_SAVE, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        logger.info(f'Удаляем папки в temp')
                except Exception as e:
                    logger.error(f'Ошибка при удалении {file_path}: {e}')
            logger.info(f'Папка {PATH_TO_SAVE} успешно очищена')
        except Exception as e:
            logger.error(f'Ошибка при очистке папки {PATH_TO_SAVE}: {e}')
    else:
        logger.error(f'Папка {PATH_TO_SAVE} не существует')