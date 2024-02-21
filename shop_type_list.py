# 2024/1/30 13:55
import hashlib
import random
import time

import pymongo
import redis

from playwright.sync_api import sync_playwright


def get_index_all_shop_page_rule_id_type():
    with sync_playwright() as pw:
        browser = pw.firefox.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        index_page = browser.new_page()
        index_page.goto('https://www.vip.com/')
        time.sleep(random.uniform(2.0, 3.0))
        # 在“商品分类”按钮处悬停
        index_page.locator("//a[text()='商品分类']").hover()

        for i in range(9):
            # 在“商品分类”的9个子项中悬停取值
            index_page.locator(f"//*[@id=\"J_main_nav_category_menu\"]/li[{i + 1}]").hover()
            time.sleep(random.uniform(2.0, 3.0))
            dl_elements = index_page.query_selector_all('//*[@id="J_main_nav_category_pop"]//dl')
            for dl in dl_elements:
                a_elements = dl.query_selector_all('//dd/a')
                for element in a_elements:
                    base_urls = element.get_attribute('href').split('?')
                    rule_id = base_urls[1].split('&')[0]
                    shop_type_url = f'https:{base_urls[0]}?{rule_id}'
                    yield {
                        'shop_type_url': shop_type_url,
                        'shop_type_name': element.text_content()
                    }
        browser.close()


def is_no_repeat(val):
    redis_cli = redis.Redis()
    return redis_cli.sadd('weipinhui:shop_type_list:filter', hashlib.md5(str(val).encode()).hexdigest())


def save_info(gene):
    db = pymongo.MongoClient(host='localhost', port=27017)
    collection = db['weipinhui']['shop_type_list']
    for info in gene:
        if is_no_repeat(info):
            collection.insert_one(info)
            print('写入成功...')
        else:
            print(f'{info} 已采集...')
    db.close()


if __name__ == '__main__':
    now = time.time()
    save_info(get_index_all_shop_page_rule_id_type())
    print(f'耗时:{time.time() - now:.2f}s')
