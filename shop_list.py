# 2024/1/31 10:38
import hashlib
import random
import time

import pymongo
import redis

from playwright.sync_api import sync_playwright


def get_shop_type_list():
    cli = pymongo.MongoClient(host='localhost', port=27017)
    collection = cli['weipinhui']['shop_type_list']
    # 连接时间过长，游标会自动关闭，将no_cursor_timeout设置为True就不会自动关闭游标了，需要手动关闭
    # shop_type_list = collection.find(no_cursor_timeout=True)
    shop_type_list = [ite for ite in collection.find()]
    cli.close()
    return shop_type_list


def get_shop_type_name_price(url):
    with sync_playwright() as pwc:
        with pwc.firefox.launch(headless=True) as browser:
            page = browser.new_page()
            page.goto(url)
            count = 1
            print(f'正在采集第{count}页')
            while True:
                # 向下滚动3次
                for i in range(3):
                    height = random.randint(5000, 10000)
                    page.evaluate(f'window.scrollTo(0,{height * (i + 1)})')
                    time.sleep(random.uniform(2.0, 3.0))

                elements = page.query_selector_all('//div[@id="J_wrap_pro_add"]/div')
                for index, element in enumerate(elements):

                    try:
                        name_element = element.query_selector('//a/div[2]/div[2]')
                        name = name_element.text_content()
                    except Exception as e:
                        print(name, e)
                        name = None
                    try:
                        price_element = element.query_selector('//a/div[2]/div[1]/div[1]/div[2]')
                        price = int(price_element.text_content().replace('¥', ''))
                    except Exception as e:
                        print(price, e)
                        price = None
                    try:
                        shop_url = element.query_selector('//a').get_attribute('href')
                        shop_url = f'https:{shop_url}'
                    except Exception as e:
                        print(shop_url, e)
                        shop_url = None

                    # print(index, name, price, shop_url)
                    yield {
                        'name': name,
                        'price': price,
                        'shop_url': shop_url
                    }

                # 获取总页数
                tot = page.query_selector('//*[@id="J-pagingWrap"]/span[1]').text_content()
                print(tot)
                print()
                if tot == f'共{count}页':
                    print(f'{page.url} 采集完毕...')
                    print()
                    print()
                    break

                # 翻页
                time.sleep(random.uniform(2.0, 3.0))
                count += 1
                print(f'正在采集第{count}页')
                elements = page.query_selector_all('//*[@id="J-pagingWrap"]/a')
                for element in elements:
                    print(element.text_content())
                    if element.text_content() == str(count):
                        try:
                            element.click()
                        except Exception as e:
                            print(e)
                        break


def is_no_crawl(key, val):
    redis_cli = redis.Redis()
    return redis_cli.sadd(key, hashlib.md5(str(val).encode()).hexdigest())


def save_info(gene):
    mongo_cli = pymongo.MongoClient(host='localhost', port=27017)
    collection = mongo_cli['weipinhui']['shop_list']
    for info in gene:
        if is_no_crawl('weipinhui:shop_list:filter', info):
            collection.insert_one(info)
            print('写入成功...')
        else:
            print('已经采集过了...')
    mongo_cli.close()


if __name__ == '__main__':
    now = time.time()
    shop_type_list = get_shop_type_list()
    for _ in range(len(shop_type_list)):
        item = random.choice(shop_type_list)
        shop_type_list.remove(item)
        print(item)
        if is_no_crawl('weipinhui:shop_type_list:filter', item):
            shop_list_gene = get_shop_type_name_price(item['shop_type_url'])
            save_info(shop_list_gene)
        else:
            print(f'{item} 已经采集过了...')
    print(f'耗时:{time.time() - now:.2f}s')
