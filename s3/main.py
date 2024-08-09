import boto3
import os

from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from config.config import PATH_TO_SAVE, options
from config.logger_config import setup_logger
from config.clear_temp import clean_temp_folder

logger = setup_logger()


class S3_Client:
    def __init__(self,
                 aws_access_key_id: str = options.ACCESS_KEY,
                 aws_secret_access_key: str = options.SECRET_KEY,
                 region_name: str = options.S3_ENDPOINT,
                 bucket_name: str = options.BUCKET_NAME,
                 ):
        self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    endpoint_url=region_name
                )
        
        self.bucket_name = bucket_name
        logger.info(f'Создание подключение с s3, bucket - {bucket_name}')

    def upload_files(self):
        for root, dirs, files in os.walk(PATH_TO_SAVE):
            for file in files:
                file_path = os.path.join(root, file)
                s3_key = os.path.relpath(file_path, PATH_TO_SAVE)
                try:
                    logger.info(f'Начинается загрузка - {file}')
                    self.s3_client.upload_file(file_path, self.bucket_name, s3_key)

                    logger.info(f'Файлы загружен на сервер - {file}')

                except FileNotFoundError:
                    logger.error(f'Файл {file_path} не найден')
                except NoCredentialsError:
                    logger.error('Credentials not available')
                except PartialCredentialsError:
                    logger.error('Incomplete credentials provided')
        logger.info('Начинаем очистку файлов')
        clean_temp_folder()
    
    def get_blacklist(self):
        '''
        Получение уже загруженных моделей
        '''
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=self.bucket_name)
            
            folders = set()
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        key = obj['Key']
                        if '/' in key:
                            folder = key.split('/')[0]
                            folders.add(folder)
            
            return list(folders)
        
        except NoCredentialsError:
            logger.error('Credentials not available')
            return []
        except PartialCredentialsError:
            logger.error('Incomplete credentials provided')
            return []
        except Exception as e:
            logger.error(f'Error retrieving blacklist: {e}')
            return []