from seleniumwire import webdriver
import time
import json
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from sys import platform
import report
import mutate
from constants import *
#import decompress
from seleniumwire.utils import decode
import sys
import pickle


class Cacher():
    def __init__(self, config_file, firefox=False):
        if firefox:
            self.driver = webdriver.Firefox(options=SELENIUM_OPTIONS_FIREFOX, seleniumwire_options=SELENIUMWIRE_OPTIONS)
        else:
            self.driver = webdriver.Chrome(options=SELENIUM_OPTIONS_CHROME, seleniumwire_options=SELENIUMWIRE_OPTIONS)
        
        self.driver.response_interceptor = self.interceptor_resp
        #self.driver.request_interceptor = self.interceptor_req
        
        self.wait = WebDriverWait(self.driver, 10)
        self.target = None
        self.response_header = {}
        self.cache = {}
        self.response = {}
        self.resp = {}
        self.config = []
        self.parse_config(config_file)
    
    def parse_config(self, config):
        for line in config.split("\n"):
            line = line.strip()
            if line == "":
                continue
            if line.startswith("#"):
                continue
            if line.startswith("TARGET "):
                self.set_target(line[7:])
                continue
            self.config.append(line)
            #process_config(line)
    
    def process_config(self, command):
        if command.startswith("LOAD "):
            self.load(command[5:])
        elif command.startswith("COOKIE "):
            self.set_cookie(command[7:])
        elif command.startswith("WAIT_LOCATE "):
            self.wait_locate(command[12:])
        elif command.startswith("SLEEP "):
            time.sleep(int(command[6:]))
        elif command.startswith("INPUT "):
            self.input(*command[6:].split(" ", 1))
        elif command.startswith("SCROLL "):
            self.scroll(command[7:])
        elif command.startswith("CLICK "):
            self.click(command[6:])
        elif command.startswith("HOVER "):
            self.hover(command[6:])
        elif command[:4] == "FUZZ":
            self.htmlsnap(command[5:])
    
    def interceptor_resp(self, request, response):
        #body = decompress.decompress(response.headers, response.body)
        body = decode(response.body, response.headers.get('Content-Encoding', 'identity'))
        self.cache[request.url] = ({h: response.headers[h] for h in response.headers}, body)
        
        if self.target in request.url:
            #self.temp(request, response)#############
            self.response = {"header": {h: response.headers[h] for h in response.headers}, "body": json.loads(body)}
    
    def interceptor_req(self, request):
        if "Accept-Encoding" in request.headers:
            del request.headers['Accept-Encoding']
        request.headers['Accept-Encoding'] = 'identity, br'
    
    def set_target(self, url):
        self.target = url
    
    def load(self, url):
        self.driver.get(url)
    
    def set_cookie(self, cookie):
        for item in cookie.split(";"):
            key, value = item.strip().split("=", 1)
            self.driver.add_cookie({"name": key, "value": value})
    
    def wait_locate(self, item):
        try:
            #self.wait.until(EC.presence_of_element_located((By.XPATH, item)))
            self.wait.until(EC.visibility_of_element_located((By.XPATH, item)))
        except Exception as e:
            print("Timeout waiting for element to appear: " + item)
    
    def click(self, item):
        #self.wait.until(EC.element_to_be_clickable((By.XPATH, item)))
        button = self.driver.find_element("xpath", item)
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(button).perform()
        except:
            pass
        WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable(button)).click()
    
    def hover(self, item):
        ac = ActionChains(self.driver)
        element = self.driver.find_element("xpath", item)
        ac.move_to_element(element).perform()
        
    def input(self, item, content):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, item)))
        element = self.driver.find_element("xpath", item)
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.DELETE)
        element.clear()
        element.send_keys(content)
    
    def scroll(self, location):
        if location.upper() == "END":
            self.driver.find_element_by_tag_name('html').send_keys(Keys.END)
        elif location.upper() == "PAGE":
            self.driver.find_element_by_tag_name('html').send_keys(Keys.PAGE_DOWN)
    
    def htmlsnap(self, xpath):
        pass
    
    def run(self):
        for command in self.config:
            self.process_config(command)
    
    def finish(self):
        self.driver.quit()
    
    def export(self):
        cache = {}
        cache["target"] = self.target
        cache["cache"] = self.cache
        cache["config"] = self.config
        cache["response"] = self.response
        return cache

def generateCache(target, firefox=False):
    f = open("config/" + target + ".config", "r")
    config = f.read()
    f.close()
    
    c = Cacher(config, firefox=firefox)
    c.run()
    cache = c.export()
    
    c.finish()
    
    f = open("tests/" + target + ".json", "w")
    json.dump(c.response["body"], f)
    f.close()
    
    f = open("tests/" + target + ".data", "wb")
    pickle.dump(cache, f)
    f.close()
    
    return cache

def loadCache(target):
    f = open("tests/" + target + ".data", "rb")
    cache = pickle.load(f)
    f.close()
    return cache

    
