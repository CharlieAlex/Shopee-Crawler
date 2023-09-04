import time
from selenium import webdriver
from selenium.webdriver.common.by import By

def open_browser(shopee_url='https://shopee.tw/'):
    '''
    Open the shopee website.
    '''
    driver_path = '/Users/alexlo/Desktop/Project/Internship_Ruten/Alex/Project_Crawler/driver/msedgedriver'
    driver = webdriver.Edge(executable_path=driver_path)
    driver.get(shopee_url)
    return driver

def close_ads(driver):
    '''
    Close the ads on the shopee website.
    '''
    close_ad_button = "document.querySelector('shopee-banner-popup-stateful').shadowRoot.querySelector('.shopee-popup__close-btn').click()"
    driver.execute_script(close_ad_button)
    driver.maximize_window()
    # driver.set_window_size(600,1000)
    return driver

def open_shopee():
    '''
    Open the shopee website & Close the ads.

    Return a Selenium webdriver.
    '''
    driver = open_browser(shopee_url='https://shopee.tw/')
    time.sleep(2)
    driver = close_ads(driver)
    driver.find_element(By.XPATH, "//*[contains(text(), '登入')]").click()
    time.sleep(2)
    driver.find_elements(By.CLASS_NAME, "Bq4Bra")[1].click()
    return driver

if __name__ == "__main__":
    driver = open_shopee()