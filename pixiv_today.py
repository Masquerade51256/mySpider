from Spider import MultiThreadPixivSpider
import datetime
import os

delay = input()
mode = input()
try:
    date = datetime.datetime.now()
    spider = MultiThreadPixivSpider()
    spider.get_pixiv_images(date - datetime.timedelta(int(delay)), mode)
except:
    print('some error was traced.')