import time
from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from browser.download import download_image_
from config.logger_config import setup_logger
from s3.main import S3_Client

logger = setup_logger()
s3_client = S3_Client()


class Firefox():
    def __init__(self, proxy: str = None):
        self.options = webdriver.FirefoxOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('--incognito')

        self.url = r'https://www.topfapgirls1.com/list/'

        self.driver = webdriver.Firefox(options=self.options)
        self.download_driver = webdriver.Firefox(options=self.options)
        self.models = {}
        self.paginating_pages = {}
        logger.info('Запуск основной функции')
        

    def open_start_page(self):
        alphabet = 'abcdefghjklmnopqrstuvwxz'
        for literally in alphabet:
            logger.info(f'Получение актрис на букву - {literally}')
            self.get_pagination_pages(literaly=literally)
            for number in range(1, int(self.paginating_pages.get(literally, 0)) + 1):
                try:
                    if number > 1:
                        self.driver.get(f'{self.url}/{str(literally)}/{str(number)}')

                    time.sleep(3)

                    self.get_models_link(literally=literally)

                except Exception as e:
                    print(e)
                    continue

        self.driver.close()
        self.download_driver.close()
                    

    def get_pagination_pages(self, literaly: str):
        '''
        Получение страниц с актрисами
        '''

        self.driver.get(f'{self.url}/{literaly}/')
        time.sleep(5)

        paginations = self.driver.find_elements(By.XPATH, '//div[@class="pagination"]/a')
        if paginations:
            logger.info(f'Получаем количество страниц по этой букве {paginations[-2].text}')
            self.paginating_pages.update({literaly: paginations[-2].text})
        else:
            self.paginating_pages.update({literaly: 1})

    def get_models_link(self, literally: str):
        '''
        Получаем имена моделей для будущей загрузки
        '''
        try:
            all_models = self.driver.find_element(By.CLASS_NAME, 'letter-items')

            for i in all_models.find_elements(By.XPATH, '//a'):
                if i.get_attribute('href') and i.text.lower().startswith(literally):
                    self.models.update({i.text: i.get_attribute('href')})
                    logger.info(f'Получаем модель для загрузки {i.text}')
                    self.download_images()
                    logger.info(f'Начинаем загрузку {i.text}')
                    s3_client.upload_files()
                    logger.info(f'Файлы загружены')
            return 'Ready'
        except Exception as e:
            print(f'Error - {e}')
            return False
        
    def download_images(self):
        '''
        Загрузка файлов изображений модели
        '''

        for model_name, model_link in self.models.items():
            if 'https://www.topfapgirls1.com/list/' not in model_link: 
                self.download_driver.get(model_link)
                logger.info(f'Начало загрузки {model_name}')
                time.sleep(2)

                for img_link in self.download_driver.find_elements(By.XPATH, "//a[@class='st']/img[1]"):
                    if model_name in img_link.get_attribute('title'):
                        download_image_(img_link=img_link.get_attribute('src'), model_name=model_name)
        self.models.clear()


