import re
import os
import time
from multiprocessing import Process, Queue
from bs4 import BeautifulSoup
import threading
from urllib import request, error, parse
from tqdm import tqdm
import http.client
import http.cookiejar
import conf
import utils
import log

class Spider:
    def __init__(self):
        pass


class MultiThreadPixivSpider(Spider):
    R18 = 'r'
    NORMAL = 'n'
    R18_page = 'https://www.pixiv.net/ranking.php?mode=daily_r18&'
    NORMAL_page = 'https://www.pixiv.net/ranking.php?mode=daily&'
    def __init__(self):
        Spider.__init__(self)
        self.lock = threading.Lock()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                                      '(KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
                        'Connection': 'keep-alive',
                        'Referer': ''}
        self.timeout = 1000

    def get_html(self, url):
        print('get_html')
        opener = self.CreateOpener()
        #print (url)
        response = opener.open(url)
        html = utils.Gzip(response.read())
        #print(html)
        return html

    def GenerateOpener(self, header):
        #print('GenerateOpener')
        if os.path.exists(conf.GetCookiePath()):
            os.remove(conf.GetCookiePath())
        global GlobalCookie

        GlobalCookie = http.cookiejar.MozillaCookieJar(conf.GetCookiePath())
        cp = request.HTTPCookieProcessor(GlobalCookie)
        op = request.build_opener(cp)
        h = []
        for key, value in list(header.items()):
            elem = (key, value)
            h.append(elem)
        op.addheaders = h
        return op

    def UpdatePostKey(self, opener):
        #print('UpdatePostKey')
        LoginPage = "https://accounts.pixiv.net/login"
        response = opener.open(LoginPage)
        data = utils.Gzip(response.read())
        response.close()
        post_key = re.findall('name="post_key" value="(.*?)"', data, re.S)
        if len(post_key) == 0:
            log.warn('not found post_key! maybe is logged in.')
            return ''
        else:
            return post_key[0]

    def CreateOpener(self):
        #print('CreateOpener')
        Header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Connection': 'keep-alive',
            'Host': 'accounts.pixiv.net',
            'Referer': 'http://www.pixiv.net/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/73.0.3683.86 Safari/537.36'
        }
        log.info('init connection...')
        opener = self.GetOpenerFromCookie(Header)
        if not self.IsLoggedIn(opener):
            log.info('cookie file not found or invalid, loggin...')
            opener = self.get_login()
            global GlobalCookie
            GlobalCookie.save()

        if self.IsLoggedIn(opener):
            log.info('login Succeess.')
            return opener
        else:
            log.info('login Error.')
            return None

    def GetOpenerFromCookie(self, header):
        #print('GetOpenerFromCookie')
        global GlobalCookie
        GlobalCookie = http.cookiejar.MozillaCookieJar()
        if os.path.exists(conf.GetCookiePath()):
            GlobalCookie.load(conf.GetCookiePath())
        cp = request.HTTPCookieProcessor(GlobalCookie)
        op = request.build_opener(cp)
        h = []
        for key, value in list(header.items()):
            elem = (key, value)
            h.append(elem)
        op.addheaders = h
        return op

    def IsLoggedIn(self, opener):
        #print('IsLoggedIn')
        MainPage = "http://www.pixiv.net/"
        res = opener.open(MainPage)
        status = re.findall('pixiv.user.loggedIn = ([\w]*);', utils.Gzip(res.read()), re.S)
        res.close()
        assert len(status) > 0
        b = re.search('true', status[0], re.IGNORECASE)
        return bool(b)

    def get_login(self):
        #print('getLogin')
        pixiv_url_login_post = "https://accounts.pixiv.net/api/login"
        Header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Connection': 'keep-alive',
            'Host': 'accounts.pixiv.net',
            'Referer': 'http://www.pixiv.net/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/73.0.3683.86 Safari/537.36'
        }

        opener = self.GenerateOpener(Header)
        pixiv_key = self.UpdatePostKey(opener)

        post_data = {
            'pixiv_id': conf.GetAccountName(),
            'password': conf.GetAccountPwd(),
            'post_key': pixiv_key,
            'source': 'accounts'
        }
        post_data = parse.urlencode(post_data).encode('utf-8')

        try:
            op_login = opener.open(pixiv_url_login_post, post_data)
            op_login.close()
        except urllib.error.URLError as e:
            PrintUrlErrorMsg(e)
        except:
            log.exception('others error occurred while loggin.')
        else:
            return opener

    @staticmethod
    def get_pixiv_id(url):
        reg = r'.+/(\d+)_p0'
        return re.findall(reg, url)[0]

    def get_referer(self, url):
        reference = "https://www.pixiv.net/member_illust.php?mode=medium&illust_id="
        return reference + self.get_pixiv_id(url)

    def save_image(self, urls, save_path, q, pbar):
        # self.lock.acquire()  # Make sure the lock will be released.
        # try:
        i = 0
        fails = 0
        repeat_times = 2

        for url in urls:
            url = url.replace('c/240x480/img-master', 'img-original')
            url = url.replace('_master1200', '')
            url = url.replace('.jpg', '.png')
            self.headers['Referer'] = self.get_referer(url)
            # begin_time1 = time.time()
            fail = 0
            try:
                try:
                    req = request.Request(url, None, self.headers)
                    res = request.urlopen(req, timeout=self.timeout)
                    res.close()
                except error.URLError as e:
                    # if hasattr(e, 'code'):
                    #     print("HTTPError")
                    #     print(e.code)
                    # elif hasattr(e, 'reason'):
                    #     print("URLError")
                    #     print(e.reason)
                    url = url.replace('.png', '.jpg')
                    req = request.Request(url, None, self.headers)
                    res = request.urlopen(req, timeout=self.timeout)
                    res.close()
            except:
                pbar.update(1)
                i += 1
                fails += 1
                continue
            i += 1
            image_path = save_path + '/%s%s' % (self.get_pixiv_id(url), os.path.splitext(url)[1])

            for _ in range(0, repeat_times):

                try:
                    res = request.urlopen(req, timeout=self.timeout)
                    rstream = res.read()
                    res.close()
                    break
                except error.URLError as e:
                    if hasattr(e, 'code'):
                        print("HTTPError")
                        print(e.code)
                    elif hasattr(e, 'reason'):
                        print("URLError")
                        print(e.reason)
                    res.close()
                    fail += 1
                    # print('repeat index %d -- %d.' % (index + i, fail))
                except http.client.IncompleteRead as e:
                    rstream = e.partial
                    res.close()
                    break

            if fail == repeat_times:
                # print('%d\t%s\tdownload image failed.'
                #       % (index + i, url))
                fails += 1
            else:
                with open(image_path, 'wb') as f:
                    f.write(rstream)
                    # end_time1 = time.time()
                    # print('%d\t%s\tdownload image costs %.2f seconds'
                    #       % (index + i, url, end_time1 - begin_time1))
            pbar.update(1)

        # print('Index %d to %d have been saved into files\t%d failed.\tProcess Over!...'
        #       % (index + 1, index + i, fails))
        q.put(fails)
        # finally:
        #     self.lock.release()

    def get_pixiv_images(self, date, mode):
        try:
            start = time.time()
            pagecount = 10
            page = 1
            index = 0
            folder_name = 'images_r18'
            list_page = self.R18_page
            if mode == self.NORMAL:
                folder_name = 'images_normal'
                list_page = self.NORMAL_page
            save_path = './'+folder_name+'/%s%02d%02d' % (date.year, date.month, date.day)
            if not (os.path.exists(save_path)):
                print(save_path + " now starts.")
                os.makedirs(save_path)
            else:
                print(save_path[-8::] + ' has been already retrieved.')
                return None

            q = Queue()  # The communication between threadings, mainly the number of failings when catching image
            ps = []  # As we didn't know how much threads needed, a dynamic list is necessary.
            indexes = []  # Beginning indexes for each threading.
            imgurls = []
            reg = re.compile(
                r'class="new".+?data-filter="thumbnail-filter lazy-image"data-src="(.+?\.jpg)"data-type="illust"')
            while page <= pagecount and index < 100:
                try:
                    html = self.get_html(list_page+"content=illust&p=%d&date=%s%02d%02d" % (page, date.year, date.month, date.day))
                except:
                    print ('error:268')

                imgurl = re.findall(reg, html)
                # print(len(imgurl))
                imgurls.append(imgurl)
                indexes.append(index)
                index += len(imgurl)
                page += 1

            pbar = tqdm(total=index, ascii=True)
            for i in range(len(indexes)):
                p = threading.Thread(target=self.save_image, args=(imgurls[i], save_path, q, pbar))
                p.start()
                ps.append(p)
            for p in ps:
                p.join()
            end = time.time()
            pbar.close()

            fails = 0
            while not q.empty():
                item = q.get()
                fails += item

            if index != 0:
                print('Processing costs %.2f second with %d images, %.2f second in average\n'
                      '%d images failed.' % ((end - start), index, (end - start) / index, fails))
            else:
                print('%s%02d%02d has no new images...' % (date.year, date.month, date.day))
                os.rmdir(save_path)
        except:
            raise Exception("Exception occured when scatching images.")

