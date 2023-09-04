from func.shopee_driver import *
import os

def get_seller_url_multi(maxtimes, shopee_driver, seller_url_list, item_url_list):
    #根據item url抓出賣家url
    seller_url_list1, fail_seller_url_list = shopee_driver.get_seller_url(item_url_list)
    seller_url_list += seller_url_list1
    #出現bug時，重新抓取
    get_seller_url_times = 0
    while ((len(fail_seller_url_list) > 0) & (get_seller_url_times < maxtimes)):
        time.sleep(10)
        seller_url_list1, fail_seller_url_list = shopee_driver.get_seller_url(fail_seller_url_list)
        seller_url_list += seller_url_list1
        get_seller_url_times += 1
    print('最終失敗商品數:', len(fail_seller_url_list))
    return seller_url_list, fail_seller_url_list

def drop_duplicate_seller(seller_url_list):
    #刪除重複的賣家
    seller_df_temp = pd.DataFrame({'url' : seller_url_list})
    seller_df_temp['username'] = seller_df_temp['url'].str.extract(r"https://shopee\.tw/([^?]+)\?")
    seller_url_list = seller_df_temp.drop_duplicates(subset='username')['url'].to_list()
    print('刪除重複賣家後，共有', len(seller_url_list), '個賣家')
    return seller_url_list