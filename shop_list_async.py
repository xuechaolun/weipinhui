# 2024/2/4 12:39
import asyncio
import time

from playwright.async_api import async_playwright
import shop_list


async def get_shop_type_detail_async(semaphore, url):
    await semaphore.acquire()
    async with async_playwright() as pwm:
        browser = await pwm.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        image_name = url.split('=')[-1]
        # await page.screenshot(path=f'{image_name}.png', full_page=False)

        await browser.close()
    semaphore.release()
    return image_name


async def main():
    # 控制协程的并发数量为10
    semaphore = asyncio.Semaphore(10)
    task_list = [asyncio.create_task(get_shop_type_detail_async(semaphore, shop_type['shop_type_url'])) for shop_type in
                 shop_list.get_shop_type_list()[:10]]
    done, pending = await asyncio.wait(task_list)
    for d in done:
        print(d.result())


if __name__ == '__main__':
    now = time.time()
    asyncio.run(main())
    print(f'耗时:{time.time()-now:.2f}s')
