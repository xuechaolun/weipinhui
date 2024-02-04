# 2024/2/4 13:35
import time

from playwright.sync_api import sync_playwright
import shop_list


def main(url):
    with sync_playwright() as pwm:
        with pwm.webkit.launch(headless=True) as browser:
            page = browser.new_page()
            page.goto(url)
            image_name = url.split('=')[-1]
    return image_name


if __name__ == '__main__':
    now = time.time()
    for shop_type in shop_list.get_shop_type_list()[:10]:
        print(main(shop_type['shop_type_url']))
    print(f'耗时:{time.time() - now:.2f}s')
