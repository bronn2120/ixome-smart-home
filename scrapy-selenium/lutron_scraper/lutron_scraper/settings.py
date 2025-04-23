# Selenium settings
SELENIUM_DRIVER_NAME = 'chrome'
SELENIUM_DRIVER_ARGUMENTS = ['--headless']
SELENIUM_DRIVER_SERVICE = {'executable_path': '/usr/local/bin/chromedriver'}

# Respect robots.txt
ROBOTSTXT_OBEY = True

# Delay between requests to avoid overloading
DOWNLOAD_DELAY = 2

# User agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'

# Spider modules
SPIDER_MODULES = ['lutron_scraper.spiders']

# Downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800
}
