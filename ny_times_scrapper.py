from RPA.Browser.Selenium import By
from scrapper import Scrapper
import requests
import pandas
from time import sleep
from datetime import datetime, timedelta
import json
from ny_times_resources import (
    SEARCH_BUTTON,
    SECTION_ITEMS,
    SECTION_BUTTON,
    SORT_BY_SELECT,
    CALENDAR_OPEN,
    START_DATE,
    SPECIFIC_DATES,
    END_DATE,
    NEWS_LIST,
    NEWS_TITLE_CLASS,
    NEWS_DATE_CLASS,
    NEWS_DESCRIPTION_CLASS,
    NEWS_PICTURE_CLASS,
)


class ScrapperNYTimes(Scrapper):
    def __init__(self, config_file, logs_file) -> None:
        super().__init__(config_file, logs_file)

    def setup(self):
        self.SEARCH_PHRASE = self.config.get("DEFAULT", "SEARCH_PHRASE")
        self.CATEGORY = json.loads(self.config.get("DEFAULT", "CATEGORY"))
        self.MONTHS = int(self.config.get("DEFAULT", "MONTHS"))
        self.FILENAME = self.config.get("DEFAULT", "FILENAME")       

        self.logger.info("initializing")
        self.logger.info(f"Search Phrase: {self.SEARCH_PHRASE}")
        self.logger.info(f"Category: {self.CATEGORY}")
        self.logger.info(f"Months: {self.MONTHS}")
        self.logger.info(f"Filename: {self.FILENAME}")

    def get_start_date(self):
        if self.MONTHS:
            days = self.MONTHS * 30
        else:
            days = 30

        return (datetime.now() - timedelta(days=days)).strftime("%m/%d/%Y")

    def open_the_website(self, url):
        self.browser_lib.open_available_browser(url)

    def search_for(self):
        self.logger.info("searching")
        search_input = "name:query"
        self.browser_lib.click_element_when_visible(SEARCH_BUTTON)
        self.browser_lib.input_text(search_input, self.SEARCH_PHRASE)
        self.browser_lib.press_keys(search_input, "ENTER")
        self.logger.success("searching")

    def select_sections(self):
        self.logger.info("selecting sections")
        self.browser_lib.click_element_when_visible(SECTION_BUTTON)
        section_items = self.browser_lib.get_webelements(SECTION_ITEMS)
        [
            i.click()
            for i in section_items
            for x in self.CATEGORY
            if x in self.browser_lib.get_text(i)
        ]
        self.logger.success("sections selected")

    def sort_by_newest(self):
        self.logger.info("sorting")
        self.browser_lib.click_element_when_visible(SORT_BY_SELECT)
        self.browser_lib.get_webelement(
            f"{SORT_BY_SELECT} >> xpath: //*[contains(text(), 'Sort by Newest')]"
        ).click()
        self.logger.success("sorted")

    def set_date_range(self):
        self.logger.info("setting date range")
        self.browser_lib.get_webelement(CALENDAR_OPEN).click()
        self.browser_lib.get_webelement(SPECIFIC_DATES).click()
        self.browser_lib.input_text(START_DATE, self.get_start_date())
        self.browser_lib.press_keys(END_DATE, "ENTER")
        self.logger.success("date range set")

    def get_news(self):
        # TODO: we should be handling pagination, currently we are retrieving only the first page
        self.logger.info("scraping the news")
        results = {
            "Title": [],
            "Date": [],
            "Description": [],
            "Image Filename": [],
            "Search Phrase Count": [],
            "Contains Money": [],
        }

        news = self.browser_lib.get_webelements(NEWS_LIST)
        for item in news:
            title = self.browser_lib.get_text(
                item.find_element(By.CLASS_NAME, NEWS_TITLE_CLASS)
            )
            date = self.browser_lib.get_text(
                item.find_element(By.CLASS_NAME, NEWS_DATE_CLASS)
            )
            description = self.browser_lib.get_text(
                item.find_element(By.CLASS_NAME, NEWS_DESCRIPTION_CLASS)
            )
            self.logger.info(f"title, date and description found for: {title}")
            try:
                image_source = item.find_element(
                    By.CLASS_NAME, NEWS_PICTURE_CLASS
                ).get_attribute(name="src")
                img_filename = image_source[: image_source.index("?")].split("/")[-1]
                with open(f"results/img/{img_filename}", "wb") as file:
                    file.write(requests.get(image_source).content)
                self.logger.info(f"image downloaded successfully for: {title}")
            except Exception as e:
                print(f"failed to find the image: {e}")
                img_filename = "no image"
                self.logger.error(f"exception downloading image for: {title}. {e}")

            search_phrase_count = title.count(self.SEARCH_PHRASE) + description.count(
                self.SEARCH_PHRASE
            )

            # this can be replaced by a regex
            contains_money = "$" in title or "$" in description
            contains_money = (
                contains_money
                or "dollars" in title.lower()
                or "dollars" in description.lower()
            )
            contains_money = (
                contains_money or "usd" in title.lower() or "usd" in description.lower()
            )

            results["Title"].append(title)
            results["Date"].append(date)
            results["Description"].append(description)
            results["Image Filename"].append(img_filename)
            results["Search Phrase Count"].append(search_phrase_count)
            results["Contains Money"].append(contains_money)

        pandas.DataFrame(results).to_excel(f"results/excel/{self.FILENAME}")
        self.logger.success("scraping finished successfully")

    def run(self):
        self.open_the_website("www.nytimes.com")
        self.search_for()
        self.select_sections()
        self.set_date_range()
        self.sort_by_newest()
        sleep(2)
        self.get_news()
