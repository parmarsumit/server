import requests
import requests_html
from collections import OrderedDict
# http://html.python-requests.org/

class Player():
    identity = {}
    akey = None
    origin = None
    session = None

    history = OrderedDict({})

    def __init__(self, identity):
        self.identity = identity
        self.session = requests_html.HTMLSession()

    def get(self, referer, url, params, callback):
        # navigate to the provided url
        # kwargs are parameters
        headers = {'Referer':referer}
        result = self.session.get(url, data=params, verify=False, headers=headers)
        # assert return code is 200
        self.history[url] = result
        current_id, redirect_url = self.get_uid_url(result)
        callback(current_id, redirect_url)

    def get_uid_url(self, result):

        main_content_attrs = result.html.find('#content-main', first=True).attrs
        current_id = main_content_attrs['data-id']
        redirect_url = main_content_attrs.get('data-redirect', result.url)

        return current_id, redirect_url


    def post(self, referer, url, params, callback):
        # navigate to the provided url
        # kwargs are parameters
        headers = {'Referer':referer}
        result = self.session.post(url, data=params, verify=False, headers=headers)

        # assert return code is 200
        self.history[url] = result
        current_id, redirect_url = self.get_uid_url(result)
        callback(current_id, redirect_url)
