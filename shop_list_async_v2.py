# 2024/2/4 21:22
import asyncio
import time

from playwright.async_api import async_playwright, Browser

# 获取任务列表的url
import shop_list


# 打开多个标签页面
async def task(browser: Browser, url):
    page = await browser.new_page()
    await page.goto(url)
    await page.evaluate('window.scrollTo(0, 3000)')
    await asyncio.sleep(3)
    print(url)
    await page.screenshot(path=f'{url}.png')


# 创建一个浏览器，并打开多个标签页面
async def main():
    async with async_playwright() as apw:
        browser = await apw.chromium.launch(headless=True)
        # 单个task
        # await task(browser, 'https://list.vip.com/autolist.html?rule_id=59450718')

        # 多个task 取30个url
        # 通过协程把多个url分发到多个页面上打开访问
        await asyncio.wait([asyncio.create_task(task(browser, shop_type['shop_type_url'])) for shop_type in
                            shop_list.get_shop_type_list()[500:520]])
        await browser.close()


if __name__ == '__main__':
    now = time.time()
    asyncio.run(main())
    print(f'耗时:{time.time() - now:.2f}s')
