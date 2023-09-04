from func.open import open_shopee
import re
import pandas as pd
import time
from tqdm import tqdm, trange
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import warnings
warnings.filterwarnings('ignore')
warnings.warn('DelftStack')
warnings.warn('Do not show this message')

class Shopee_driver:
    def __init__(self):
        self.shopee_url = 'https://shopee.tw/'
        self.driver = open_shopee()
        self.category_url_df = pd.DataFrame()

    def get_cat_url_list(self):
        '''
        Get the category's url from the Shopee homepage.

        Save the result in the Shopee_driver object.
        '''
        #get the name of each category
        self.driver.maximize_window()
        self.driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(2)
        category_name_list = []
        category_url_list = []
        cat_list = self.driver.find_elements(By.CLASS_NAME, "K34m1x")
        for cat in cat_list:
            category_name_list.append('/' + cat.text.split('/')[0])
        #get the url of each category
        for i in range(len(category_name_list)):
            category_url = self.driver.execute_script(f" \
                var t = document.querySelector('a[href*=\"{category_name_list[i]}\"]');  \
                return t.attributes[1].textContent; \
            ")
            if category_url != '_blank':
                category_url_list.append(self.shopee_url + category_url[1:])
        self.category_url_df = pd.DataFrame(category_url_list, columns=['url'])
        self.category_url_df['category'] = (
            self
            .category_url_df['url']
            .apply(lambda x: re.search(r'/([^/]+)-cat\.\d+', x).group(1))
        )
        # self.driver.set_window_size(600,1000)

    def get_item_url_(self, cat_rank_page, url_list) -> list:
        '''
        Temp function for get_item_url_list().

        This is used to add all the item's url into the item_url_list.

        Parameters
        ----------
        cat_rank_page: bs4 object comes from one page of one specific category.
        '''
        num = len(cat_rank_page.find_all('div', class_="col-xs-2-4 shopee-search-item-result__item"))
        for i in trange(num):
            try:
                temp_url = cat_rank_page.find_all('div', class_="col-xs-2-4 shopee-search-item-result__item")[i].find('a')['href']
                url_list.append(self.shopee_url + temp_url)
            except:
                break
        return url_list

    def get_item_url_list(self, page_start=1, page_end=3, cat_start=0, cat_end=5):
        '''
        For each category and for each page, get the url for each item on the page, and return a result list.

        Parameters
        ----------
        page_start: the starting page number for each category.
        page_end: the ending page number for each category.
        cat_start: the starting index of categories.
        cat_end: the ending index of categories.

        Notes
        ----------
        These parameters are used for controling the running time.

        Example
        ----------
        `get_item_url_list(self, page_start=1, page_end=3, cat_start=0, cat_end=5)` means:

        From the 0th category to 5th category, only look at the first 3 pages of each category.
        '''
        item_url_list = []
        for cat in self.category_url_df['url'].iloc[cat_start:cat_end+1]:
            print('正在爬取商品分類:', cat[18:], '...')
            for page_num in range(page_start, page_end+1):
                #get into the category page
                self.driver.get(cat + f'?page={page_num}')
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.driver.execute_script("document.body.style.zoom='0.1'")
                time.sleep(2)
                #open bs4 page
                cat_rank_page = BeautifulSoup(self.driver.page_source, 'html.parser')
                time.sleep(2)
                #get the item url
                item_url_list = self.get_item_url_(cat_rank_page, item_url_list)
        return item_url_list

    def open_item_page_and_bs4_(self, url):
        '''
        Temp function for get_seller_url().

        This is used to turn the selenium website into a bs4 object, which is more convenient to search for the tag.
        '''
        self.driver.get(url)
        self.driver.execute_script("document.body.style.zoom='0.1'")
        time.sleep(3)
        item_page = BeautifulSoup(self.driver.page_source, 'html.parser')
        time.sleep(1)
        return item_page

    def get_seller_url(self, item_url_list):
        '''
        Get the seller's url according to '查看賣場' in each item page.

        Return a list for recording all the failed seller so that it is possible to run once again only for them.
        '''
        num = len(item_url_list)
        seller_url_list = []
        fail_seller_url_list = []
        for i in trange(num):
            try:
                item_page = self.open_item_page_and_bs4_(item_url_list[i])
                if item_page.find('div', class_='K1dDgL') != None:
                    #go to the login page
                    print(f'第{i+1}個商品爬取失敗')
                    fail_seller_url_list += item_url_list[i:]
                    time.sleep(3)
                    break
                #find the url of the seller
                temp_url = item_page.find('span', string='查看賣場').parent['href']
                seller_url_list.append(self.shopee_url + temp_url[1:])
            except:
                print(f'第{i+1}個商品爬取失敗')
                fail_seller_url_list.append(item_url_list[i])
                time.sleep(3)
        return seller_url_list, fail_seller_url_list

    def get_seller_dataset(self, seller_url) -> pd.DataFrame:
        '''
        Get the necessary information on each seller page and turn all of them into a one-row pd.dataframe.
        '''
        self.driver.get(seller_url)
        time.sleep(3)
        seller_page = BeautifulSoup(self.driver.page_source, 'html.parser')
        seller_name = seller_page.find('h1', class_='section-seller-overview-horizontal__portrait-name').text
        seller_info = seller_page.find('div', class_='section-seller-overview-horizontal__seller-info-list')
        temp_dict = {'賣家:' : [seller_name], '賣場網址:' : [seller_url]}
        for item in seller_info.contents:
            value_index = len(item.contents[1]) - 1 #有些賣家的不良率前面有個奇怪標誌，為了避開而做的調整
            info_name = item.contents[1].contents[0].text
            info_value = item.contents[1].contents[value_index].text
            temp_dict[info_name] = [info_value]
        seller_info_df = pd.DataFrame(temp_dict)
        return seller_info_df

    def get_seller_dataset_all(self, seller_url_list):
        '''
        Use get_seller_dataset() on all the seller's url on the list.
        '''
        seller_num = len(seller_url_list)
        seller_dataset = pd.DataFrame()
        fail_seller_dataset_list = []
        error_times = 0
        t = 0
        for i in trange(seller_num):
            t = i
            try:
                seller_info_df = self.get_seller_dataset(seller_url_list[i])
                seller_info_df['名次:'] = i + 1
                seller_dataset = seller_dataset.append(seller_info_df)
                print(seller_info_df)
            except:
                fail_seller_dataset_list.append(seller_url_list[i])
                print('發生錯誤')
                error_times += 1
                time.sleep(3)
            if error_times > 3:
                break
        fail_seller_dataset_list += seller_url_list[t+1:]
        seller_dataset = seller_dataset.reset_index(drop=True)
        seller_dataset.head()
        return seller_dataset, fail_seller_dataset_list