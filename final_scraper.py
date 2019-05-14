"""
    Importing the libraries that we are going to use
    for loading the settings file and scraping the website
"""
import configparser
import time
from selenium import webdriver

class WhatsAppScraper():  
    # Define variable
    LAST_MESSAGES = 6
    WAIT_FOR_CHAT_TO_LOAD = 2 # in secs

    def run_scraper(self):
        setting = WhatsAppScraper.load_settings()
        my_driver = WhatsAppScraper.load_driver(WhatsAppScraper.load_settings())
        my_driver.get(setting['page'])
        WhatsAppScraper.find(my_driver, setting)

        
    @staticmethod
    def load_settings():
        """
            Loading and assigning global variables from our settings.txt file
        """
        config_parser = configparser.RawConfigParser()
        config_file_path = 'final/settings.txt'
        config_parser.read(config_file_path)

        browser = config_parser.get('your-config', 'BROWSER')
        browser_path = config_parser.get('your-config', 'BROWSER_PATH')
        name = config_parser.get('your-config', 'NAME')
        page = config_parser.get('your-config', 'PAGE')
        output = config_parser.get('your-config', 'Output')

        settings = {
            'browser': browser,
            'browser_path': browser_path,
            'name': name,
            'page': page,
            'output' : output
        }
        return settings
    
    @staticmethod
    def load_driver(settings):
        """
        Load the Selenium driver depending on the browser
        (Edge and Safari are not running yet)
        """
        driver = None
        if settings['browser'] == 'firefox':
            firefox_profile = webdriver.FirefoxProfile(settings['browser_path'])
            driver = webdriver.Firefox(firefox_profile)
        elif settings['browser'] == 'edge':
            pass
        elif settings['browser'] == 'chrome':
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument(
                "user-data-dir=" + settings['browser_path'])
            driver = webdriver.Chrome(settings['browser_path'])
            # driver.maximize_window()
        elif settings['browser'] == 'safari':
            pass

        return driver    

    @staticmethod
    def detect_messages(driver, Output):
        # scrape specific person/group
        # driver.execute_script("window.scrollTo(300, 1000);")
        message_dic = {}
        person_name = driver.find_element_by_xpath("//*[@id='main']/header/div[2]/div/div").text
        content = driver.find_element_by_xpath("//div[@class='_3zb-j ZhF0n']/span").text
        m_arg = '//div[@class="_9tCEa"]/div'
        messages = driver.find_elements_by_xpath(m_arg)  
        top_messages = messages[-1*WhatsAppScraper.LAST_MESSAGES:]
        message_dic[content] = [m.text for m in messages]
        image = driver.find_element_by_xpath("//*[@id='main']/header/div[1]/div/img")
        message_dic[content].append(image.get_attribute('src'))
        print(message_dic[content])

        WhatsAppScraper.write_file(Output, message_dic[content])
        # driver.quit()
    
    @staticmethod
    def write_file(file_name, content):
        with open(file_name, 'a', encoding = "utf-8") as file:
            file.writelines(content) 
            file.close()
    
    @staticmethod
    def find(driver, settings):
        """
        Function that search the specified user and activates his chat
        """
        while True:
            for chatter in driver.find_elements_by_xpath("//div[@class='_2wP_Y']"):
                chatter_name = chatter.find_element_by_xpath(
                    ".//span[@class='_1wjpf']").text

                if settings['name'] == '':
                    WhatsAppScraper.scrape(None, driver, settings["output"])
                    return

                if chatter_name == settings['name']:
                    chatter.find_element_by_xpath(
                        ".//div[@tabindex='-1']").click()
                    WhatsAppScraper.detect_messages(driver, settings["output"])
                    return
    

    @staticmethod
    def scrape(prev, driver, output):
        # scrape all user and group
        recentList = driver.find_elements_by_xpath("//div[@class='_2wP_Y']")
        recentList.sort(key=lambda x: int(x.get_attribute('style').split("translateY(")[1].split('px')[0]), reverse=False)

        next_focus = None
        start = 0
        for idx,tab in enumerate(recentList):
            if tab == prev:
                start = idx
                break

        for l in recentList[start:]:
            try:
                l.click()
                time.sleep(WhatsAppScraper.WAIT_FOR_CHAT_TO_LOAD)
                WhatsAppScraper.detect_messages(driver, output)
                next_focus = l
            except:
                pass
        if prev == next_focus:
            return
        WhatsAppScraper.scrape(next_focus, driver, output)

