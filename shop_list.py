# 2024/1/31 10:38
import random
import time

import pymongo

from playwright.sync_api import sync_playwright


def get_shop_type_list():
    cli = pymongo.MongoClient(host='localhost', port=27017)
    collection = cli['weipinhui']['shop_type_list']
    shop_type_list = collection.find()
    # for index, shop_type in enumerate(shop_type_list):
    #     print(index+1, shop_type)
    return shop_type_list


def get_shop_type_name_price(url):
    with sync_playwright() as pwc:
        with pwc.firefox.launch(headless=True) as browser:
            page = browser.new_page()
            page.goto(url)
            # 向下滚动3次
            for _ in range(3):
                page.evaluate('window.scrollTo(0,document.body.scrollHeight)')
                time.sleep(random.uniform(1.0, 2.0))

            elements = page.query_selector_all('//div[@id="J_wrap_pro_add"]/div')
            for index, element in enumerate(elements):
                shop_url = element.query_selector('//a').get_attribute('href')
                name_element = element.query_selector('//a/div[2]/div[2]')
                price_element = element.query_selector('//a/div[2]/div[1]/div[1]/div[2]')
                print(index, name_element.text_content(), price_element.text_content(), f'https:{shop_url}')
                # yield {
                #     'name': name_element.text_content(),
                #     'price': price_element.text_content(),
                #     'shop_url': f'https:{shop_url}'
                # }

            # 翻页


if __name__ == '__main__':
    now = time.time()
    for item in get_shop_type_list():
        print(item['shop_type_url'])
        get_shop_type_name_price(item['shop_type_url'])
        break
    print(f'耗时:{time.time()-now:.2f}s')
