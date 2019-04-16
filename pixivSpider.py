from Spider import MultiThreadPixivSpider
import datetime
import os
import argparse

delay = 2
mode = 'n'
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", default='n')
    parser.add_argument("-d", default=2)
    args = parser.parse_args()
    delay = args.d
    mode = args.m
else:
    print("enter the mode (r/n):")
    mode = input()
    print("enter how many days you want to collect the list before today:")
    delay = input()
try:
    date = datetime.datetime.now()
    spider = MultiThreadPixivSpider()
    spider.get_pixiv_images(date - datetime.timedelta(int(delay)), mode)
except:
    print("Some error was traced, try to delete the exist folder or check your connect.")