from selenium import webdriver

from lib.adapter.config import Config


class Crawler:
    _webdriver_path = None
    _webdriver_instance = None
    selectors = webdriver.common.by.By

    def __init__(self):
        self._webdriver_path = Config().read()['webdriver_path']
        if self._webdriver_instance is None:
            print('(!) Do not close the chrome window! It will be closed automatically when the script is finished.')
            print('Initializing webdriver...')
            options = webdriver.ChromeOptions()
            options.add_argument("--enable-experimental-web-platform-features")
            self._webdriver_instance = webdriver.Chrome(self._webdriver_path, options=options)
            self._webdriver_instance.minimize_window()

    def __del__(self):
        if self._webdriver_instance is not None:
            print('Closing webdriver...')
            self._webdriver_instance.quit()

    def crawl_webpage(self, url, selector, payload):
        self._webdriver_instance.get(url)
        try:
            element = self._webdriver_instance.find_element(selector, payload)
            data = element.text
            return data
        except Exception as e:
            print(f'(!) Can not find target element: {e}')
            return None
