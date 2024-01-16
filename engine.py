from seleniumwire import webdriver
import time
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import report
import mutate
from constants import *
import sys
import copy


class Engine():
    def __init__(self, cache=None, firefox=False):
        if firefox:
            self.driver = webdriver.Firefox(options=SELENIUM_OPTIONS_FIREFOX, seleniumwire_options=SELENIUMWIRE_OPTIONS)
        else:
            self.driver = webdriver.Chrome(options=SELENIUM_OPTIONS_CHROME, seleniumwire_options=SELENIUMWIRE_OPTIONS)
        
        self.driver.request_interceptor = self.interceptor
        self.wait = WebDriverWait(self.driver, 10)
        self.source = ""
        self.mutation_path = []
        self.mutation_resp = copy.deepcopy(cache["response"]["body"])
        self.mutation_header = copy.deepcopy(cache["response"]["header"])
        self.config = cache["config"]
        self.target = cache["target"]
        self.cache = cache["cache"]
    
    def set_target(self, url):
        self.target = url
    
    def set_config(self, config):
        self.config = config
    
    def set_cache(self, cache):
        self.cache = cache
    
    def set_mutation(self, mutation):
        self.mutation_path = mutation
        if self.mutation_path:
            n = len(self.mutation_path) - 1
            i = 0
            t = self.mutation_resp
            while i < n:
                t = t[self.mutation_path[i]]
                i += 1
            del t[self.mutation_path[-1]]
    
    def process_config(self, command):
        if command.startswith("LOAD "):
            self.load(command[5:])
        elif command.startswith("COOKIE "):
            self.set_cookie(command[7:])
        elif command.startswith("SLEEP "):
            time.sleep(int(command[6:]))
        elif command.startswith("WAIT_LOCATE "):
            self.wait_locate(command[12:])
        elif command.startswith("INPUT "):
            self.input(*command[6:].split(" ", 1))
        elif command.startswith("CLICK "):
            self.click(command[6:])
        elif command.startswith("HOVER "):
            self.hover(command[6:])
        elif command.startswith("SCROLL "):
            self.scroll(command[7:])
        elif command[:4] == "FUZZ":
            self.htmlsnap(command[5:])
    
    def load(self, url):
        try:
            self.driver.get(url)
        except Exception as e:
            self.driver.quit()
            raise Exception("Could not load URL (this should never happen): " + url + str(e))
    
    def set_cookie(self, cookie):
        return # during fuzzing phase, there is no need to set cookies
        try:
            for item in cookie.split(";"):
                key, value = item.strip().split("=", 1)
                self.driver.add_cookie({"name": key, "value": value})
        except Exception as e:
            self.driver.quit()
            raise Exception("Error when setting cookies (this should never happen) " + str(e))
    
    def wait_locate(self, item):
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, item)))
        except Exception as e:
            self.driver.quit()
            raise Exception("Timeout locating element: " + item + str(e))
    
    def click(self, item):
        try:
            button = self.driver.find_element("xpath", item)
            try:
                actions = ActionChains(self.driver)
                actions.move_to_element(button).perform()
            except:
                pass
            WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable(button)).click()
        except Exception as e:
            self.driver.quit()
            raise Exception("Failed to click element: " + item + str(e))
    
    def input(self, item, content):
        try:
            element = self.driver.find_element("xpath", item)
            element.clear()
            element.send_keys(content)
        except Exception as e:
            self.driver.quit()
            raise Exception("Failed to fill in textbox: " + item + str(e))
    
    def hover(self, item):
        try:
            ac = ActionChains(self.driver)
            element = self.driver.find_element("xpath", item)
            ac.move_to_element(element).perform()
        except Exception as e:
            self.driver.quit()
            raise Exception("Cannot hover mouse on element: " + item + str(e))
    
    def scroll(self, location):
        try:
            if location.upper() == "END":
                self.driver.find_element(By.TAG_NAME, 'html').send_keys(Keys.END)
            elif location.upper() == "PAGE":
                self.driver.find_element(By.TAG_NAME, 'html').send_keys(Keys.PAGE_DOWN)
        except Exception as e:
            self.driver.quit()
            raise Exception("Cannot scroll the page (this should never happen) " + str(e))
    
    def htmlsnap(self, xpath):
        time.sleep(2)
        if xpath == "":
            xpath = "//html"
        try:
            element = self.driver.find_element("xpath", xpath)
            self.source = element.get_attribute("outerHTML")
        except:
            self.source = ""
    
    def interceptor(self, request):
        if self.target in request.url:
            request.create_response(
                status_code=200,
                headers=self.mutation_header,
                body=json.dumps(self.mutation_resp).encode("utf8")+b"\r\n"
            )
        elif request.url in self.cache:
            request.create_response(
                status_code=200,
                headers=self.cache[request.url][0],
                body=self.cache[request.url][1]
            )
        else:
            #print("Unseen request: " + request.url)
            #if "googel-analytics" in request.url:
            request.create_response(
                status_code=404,
                headers={},
                body="\r\n\r\n"
            )
    
    def run(self):
        for command in self.config:
            self.process_config(command)
    
    def finish(self):
        self.driver.quit()

def runInstance(cache, mutation, firefox=False):
    f = Engine(cache, firefox=firefox)
    
    f.set_mutation(mutation)
    
    f.run()
    
    source = f.source
    
    f.finish()
    
    return source
    #report.back(mutatin, s)
    
