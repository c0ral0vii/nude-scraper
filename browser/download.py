import requests
import os
import random
import string

from config.config import PATH_TO_SAVE


def create_directory(model_name: str):
    try:
        if model_name not in os.listdir(path=f'{PATH_TO_SAVE}'):
            os.mkdir(path=f'{PATH_TO_SAVE}/{model_name}', mode=511)
        return True
    except Exception as e:
        print(e)
        return False

def download_image_(img_link: str, model_name: str):
    '''
    Скачивание фотографии модели

    img_link: ссылка на фотографию, str
    model_name: имя модели для помещения в папку, str
    '''


    try:
        check = create_directory(model_name=model_name)
        if check:
            response = requests.get(img_link)
            name = generate_name(length=12)
            with open(f'{PATH_TO_SAVE}/{model_name}/{name}.jpg', 'wb') as file:
                file.write(response.content)

    except Exception as e:
        print(e)
        return f'Error - {e}'
    finally:
        return 'Download'


def generate_name(length: int):
    '''
    Генерация имени для фотографии

    length: длина имени, int
    '''

    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))
