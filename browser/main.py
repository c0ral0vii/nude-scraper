import time
from selenium import webdriver
import multiprocessing


from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent

from browser.download import download_image_
from config.logger_config import setup_logger
from s3.main import S3_Client


logger = setup_logger()
s3_client = S3_Client()


class Firefox():
    def __init__(self, proxy: str = None, user_agent = UserAgent().random):
        self.options = webdriver.FirefoxOptions()
        self.options.add_argument(f'--user-agent={user_agent}')
        self.options.add_argument('--incognito')
        self.options.add_argument('--headless')

        # self.options.add_argument('--proxy-server=http://166.1.149.228:62822@g8yXtTSEV:XQszN1yaS')
        self.url = r'https://www.topfapgirls1.com/list/'
        self.driver = webdriver.Firefox(options=self.options, service=FirefoxService(GeckoDriverManager().install()))
        self.driver.set_window_size(1920, 1080)
        self.download_driver = webdriver.Firefox(options=self.options, service=FirefoxService(GeckoDriverManager().install()))
        self.driver.set_window_size(1920, 1080)
        
        self.models = {}
        self.paginating_pages = {}
        self.blacklist = s3_client.get_blacklist()
        logger.info('Запуск основной функции')
        

    def open_start_page(self, alphabet: str = 'abcdefghjklmnopqrstuvwxstz'):

        for literally in alphabet:
            logger.info(f'Получение актрис на букву - {literally}')
            self.get_pagination_pages(literaly=literally)
            for number in range(1, int(self.paginating_pages.get(literally, 0)) + 1):
                try:
                    if number > 1:
                        self.driver.get(f'{self.url}/{str(literally)}/{str(number)}')

                    WebDriverWait(self.driver, 10).until(
                        lambda x: x.execute_script("return document.querySelectorAll(\"div\").length > 0")
                    )

                    self.get_models_link(literally=literally)
                    self.download_images()
                    
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
        WebDriverWait(self.driver, 5).until(
                        EC.visibility_of_element_located((By.XPATH, '//div'))
                    )
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
                if i.get_attribute('href') and i.text.lower().startswith(literally) and i.text not in self.blacklist:
                    self.models.update({i.text: i.get_attribute('href')})
                    logger.info(f'Получаем модель для загрузки {i.text}')
                    
            return 'Ready'
        except Exception as e:
            print(f'Error - {e}')
            return False
        
    def download_images(self):
        '''
        Загрузка файлов изображений модели
        '''

        for model_name, model_link in self.models.items():
            if model_name not in self.blacklist:
                logger.info(f'Начинаем загрузку {model_name}') 
                if 'https://www.topfapgirls1.com/list/' not in model_link: 
                    self.download_driver.get(model_link)
                    logger.info(f'Начало загрузки {model_name}')
                    
                    try:
                        # Ожидание появления элементов с изображениями
                        WebDriverWait(self.download_driver, 10).until(
                            lambda x: x.execute_script("return document.querySelectorAll(\"a.st > img\").length > 0")
                        )
                    except Exception as e:
                        logger.error(f'Элементы с изображениями не были найдены для {model_name} в течение 10 секунд')
                        continue

                    for img_link in self.download_driver.find_elements(By.XPATH, "//a[@class='st']/img[1]"):
                        if model_name in img_link.get_attribute('title'):
                            download_image_(img_link=img_link.get_attribute('src'), model_name=model_name)

                            p = multiprocessing.Process(target=s3_client.upload_files())
                            p.start()
                            logger.info('Запуск процесса с загрузкой файлов на s3 сервер')
                            p.join()
                            logger.info(f'Файлы загружены')
        self.models.clear()


