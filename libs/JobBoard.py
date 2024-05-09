from selenium.webdriver.common.by import By
import numpy as np
import pandas as pd
from selenium import webdriver
import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common import NoSuchElementException, ElementNotInteractableException, \
    StaleElementReferenceException, ElementClickInterceptedException, WebDriverException

import traceback

errors = [NoSuchElementException,
          ElementNotInteractableException,
          ElementClickInterceptedException,
          StaleElementReferenceException,
          TimeoutError]




class Job_Board:

    def launch_browser(self):
        global browser
        browser = webdriver.Chrome()
        browser.get(self.link)
        global wait
        wait = WebDriverWait(browser, timeout=10, poll_frequency=1, ignored_exceptions=errors)

    def get_postings(self, max_pages=-1):

        postings = []
        more = True
        pages = 1

        while more:
            print("Reading page: " + str(pages))
            for i in browser.find_elements(By.CSS_SELECTOR, self.post_name):
                try:
                    postings.append(i.get_attribute('href'))
                except:
                    time.sleep(1)
                    postings.append(i.get_attribute('href'))
            pages += 1
            if (pages == max_pages + 1):
                more = False
            else:
                more = self.paginator.run()
                time.sleep(self.cooldown)

        return postings

    def get_descriptions(self, postings):
        descriptions = []
        # titles = []
        try:
            # Chrome runs out of memory sometimes. We need to restart the browser if it crashes.
            for p in postings:
                try:
                    browser.get(p)
                except WebDriverException:
                    del browser
                    self.launch_browser()
                    browser.get(p)

                try:
                    wait.until(
                        lambda d: (browser.find_element(By.CSS_SELECTOR, self.descript_name).text is not None) or True)
                    description = browser.find_element(By.CSS_SELECTOR, self.descript_name)
                    descriptions.append(description.text)
                    # titles.append(browser.find_element(By.CSS_SELECTOR, job_title).text)
                except Exception as e:
                    error = traceback.format_exception(e)
                    # ToDo: Make this not bad.
                    descriptions.append(error)
        except Exception as e:
            print(traceback.format_exception(e))
            return descriptions
        else:
            return descriptions

    def get_df(self, max_pages=-1):
        postings = self.get_postings(max_pages)
        descriptions = self.get_descriptions(postings)
        # TODO: There might be some mismatch handling that needs to happen?
        df = pd.DataFrame(np.column_stack([postings, descriptions[0:len(postings)]]),
                          columns=["Link", "Description"])
        return df

    def __init__(self, link, post_name, descript_name, paginator_next=None, paginator_stop=None, cooldown=0):

        self.link = link
        self.post_name = post_name
        self.descript_name = descript_name
        self.cooldown = cooldown
        self.paginator = Paginator(post_name=post_name,
                                   next_element=paginator_next,
                                   cooldown=cooldown)
        self.launch_browser()
        # TODO: on launch apply javascript filtering options? - these aren't often editable in the url.


class Paginator():

    def __init__(self, post_name=None, next_element=None, mode="page", cooldown=0):
        self.next_element = next_element
        self.post_name = post_name
        self.cooldown = cooldown
        self.mode = mode

    def run(self):
        try:
            # ToDo: Maybe move max_pages down here so it can work with scroll?
            if self.mode == "page":
                # Do normal pagination
                wait.until(lambda d: browser.find_element(By.CSS_SELECTOR, self.next_element).is_displayed() or True)
                wait.until(lambda d: (browser.find_element(By.CSS_SELECTOR, self.next_element).click() or True))
                if len(browser.find_elements(By.CSS_SELECTOR, self.next_element)) > 0:
                    return browser.find_elements(By.CSS_SELECTOR, self.next_element)[0].is_enabled()
                else:
                    return False

            elif self.mode == "scroll":
                # For infinite scroll:
                from selenium.webdriver import ActionChains
                # get the last post name
                iframe = None
                while iframe != browser.find_elements(By.CSS_SELECTOR, self.post_name)[-1]:
                    # scroll to bottom and load all postings
                    ActionChains(browser).scroll_to_element(iframe).perform()
                    if len(browser.find_elements(By.CSS_SELECTOR, self.next_element)) == 0:
                        break
                    if self.next_element is not None:
                        wait.until(lambda d: (browser.find_element(By.CSS_SELECTOR, self.next_element).click() or True))
                        # if previous last is different from current, there may be more
                        iframe = browser.find_elements(By.CSS_SELECTOR, self.post_name)[-1]
                    time.sleep(self.cooldown)
                return False

            # TODO: This is actually half paginator, the other half might belong in get_postings.
            # move it and make it work?
            elif self.mode == "individual":
                try:
                    wait.until(lambda d:
                               browser.find_element(By.CSS_SELECTOR, next).is_enabled()
                               or True)
                    hasnext = browser.find_element(By.CSS_SELECTOR, next).is_enabled()
                except Exception as e:
                    print(e)
                    traceback.print_exc()
                finally:
                    return hasnext

        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

        else:
            print("No exception was thrown but no action was performed. Check what mode was selected.")
            return False
