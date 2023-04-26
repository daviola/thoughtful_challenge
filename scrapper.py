from abc import abstractmethod
import configparser
from RPA.Browser.Selenium import Selenium
from loguru import logger


class Scrapper:
    def __init__(self, config_file, logs_file) -> None:
        # start selenium
        self.browser_lib = Selenium()

        # read config file
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
         # start logging
        self.logger = logger
        self.logger.add(logs_file, retention="10 days")
        self.setup()

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def run(self):
        pass

    def finish(self):
        self.browser_lib.close_all_browsers()
        self.logger.info("finished all the browsers")
