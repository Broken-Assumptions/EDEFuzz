from selenium.webdriver.chrome.options import Options
from selenium.webdriver import FirefoxOptions


MODE_INITIAL = 0
MODE_FUZZING = 1


SELENIUMWIRE_OPTIONS = {
            #'disable_encoding': True,
            'request_storage': 'memory', # Store requests and responses in memory only
}

SELENIUM_OPTIONS_CHROME = Options()
SELENIUM_OPTIONS_CHROME.add_argument("--disable-application-cache")
SELENIUM_OPTIONS_CHROME.add_argument("--disable-gpu")
#SELENIUM_OPTIONS_CHROME.add_argument("--headless=new")
SELENIUM_OPTIONS_CHROME.add_argument("--no-sandbox")
SELENIUM_OPTIONS_CHROME.add_argument("--window-size=2560,1440")
SELENIUM_OPTIONS_CHROME.add_argument('--ignore-certificate-errors')
SELENIUM_OPTIONS_CHROME.add_argument('--allow-running-insecure-content')
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
SELENIUM_OPTIONS_CHROME.add_argument(f'user-agent={user_agent}')

SELENIUM_OPTIONS_FIREFOX = FirefoxOptions()
SELENIUM_OPTIONS_FIREFOX.add_argument("--disable-application-cache")
SELENIUM_OPTIONS_FIREFOX.add_argument("--disable-gpu")
SELENIUM_OPTIONS_FIREFOX.add_argument("--headless")
SELENIUM_OPTIONS_FIREFOX.add_argument("--no-sandbox")
SELENIUM_OPTIONS_FIREFOX.add_argument("--window-size=1920,1280")


DATABASE_MYSQL = 1
DATABASE_SQLITE = 2


DATABASE_TYPE = DATABASE_MYSQL
DATABASE_MYSQL_SOCKET = False
DATABASE_MYSQL_HOST = "edefuzz-mysql"
DATABASE_MYSQL_USER = "edefuzz"
DATABASE_MYSQL_PASS = "password"
