import urllib.error
from urllib.request import Request as HttpRequest, urlopen as UrlOpen
from json import (loads as jsLoads, dumps as jsDumps)

def get_photo_by_fixtureident(guid):
    """ Соединение с сервисом tassphoto.com и получение информации об уже добавленной фото
    :param url: ссылка для получения информации о фото
    :return: объект с информацией о фото на сайте
    """

    service_url = 'http://msk-oft-app2.corp.tass.ru:8080/photos/extbyfixid/{0}'.format(guid)
    try:
        with UrlOpen(service_url) as service_response:
            if service_response is not None:
                photos = jsLoads(service_response.read().decode('utf-8'))

                if 'data' in photos and photos['data']:
                    if isinstance(photos['data'], list):
                        return photos['data'](1)
                    elif isinstance(photos['data'], dict):
                        return photos['data']
                    else:
                        raise ValueError("Wrong object in response: {}".format(str(photos['data'])))
                else:
                    return None

    except urllib.error.HTTPError as http_error:
        raise(SystemError("Request error, code: {}, message: {}".format(http_error.code, http_error.msg)))
