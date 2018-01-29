import requests


ELSEVIER_API_KEY_FILE_PATH = './resource/elsevier_api_key.txt'


class Elsevier:
    SEARCH_BASE_URL = 'https://api.elsevier.com/content/search/scidir'
    ARTICLE_BASE_URL = 'https://api.elsevier.com/content/article/doi/'

    def __init__(self):
        with open(ELSEVIER_API_KEY_FILE_PATH) as fp:
            self.api_key = fp.readline().strip()

    def send_request(self, base_url, options):
        option_str = '&'.join(options)
        response = requests.get(base_url + '?APIKey=' + self.api_key + '&' + option_str)
        return response

    def search_request(self, options):
        response = self.send_request(self.SEARCH_BASE_URL, options)
        return response.content

    def text_request(self, doi, options=[]):
        response = self.send_request(self.ARTICLE_BASE_URL + doi, options)
        return response.content


