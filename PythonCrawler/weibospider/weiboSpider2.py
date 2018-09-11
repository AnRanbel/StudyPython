#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
import requests
import sys
import time
import traceback
import json
from datetime import datetime
from datetime import timedelta
from lxml import etree
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import wordcloud
import jieba
from pyecharts import Bar
from pyecharts import Page
import locale

class Weibo:
    headers = {
        "User-Agent": "your user_agent",
        "Cookie": "your_cookie"
    }
    
    # Weibo类初始化
    def __init__(self, user_id, filter=0):
        self.web_url = ''  # 互联网版网址
        self.phone_url = ''  # 手机版网址
        self.user_id = user_id  # 用户id，即需要我们输入的数字，如昵称为“Dear-迪丽热巴”的id为1669879400
        self.filter = filter  # 取值范围为0、1，程序默认值为0，代表要爬取用户的全部微博，1代表只爬取用户的原创微博
        self.username = ''  # 用户名，如“Dear-迪丽热巴”
        self.weibo_num = 0  # 用户全部微博数
        self.weibo_num2 = 0  # 爬取到的微博数
        self.following = 0  # 用户关注数
        self.followers = 0  # 用户粉丝数
        self.weibo_content = []  # 微博内容
        self.weibo_place = []  # 微博位置
        self.publish_time = []  # 微博发布时间
        self.up_num = []  # 微博对应的点赞数
        self.retweet_num = []  # 微博对应的转发数
        self.comment_num = []  # 微博对应的评论数
        self.publish_tool = []  # 微博发布工具
        self.year_list=[]   #年
        self.month_list = []    #年—>月
        self.number_list = []   #年—>月发布数
        self.sum_number_list = []   #年发布数

    #  获取用户昵称
    def get_username(self):
        try:
            url = "https://weibo.cn/%d/info" % (self.user_id)
            source_code = requests.get(url, headers=self.headers).content
            d = pq(source_code)
            # 昵称
            base_info = d(".c").eq(3).html()
            base_info = base_info.replace("<br />", " ")
            lastindex = base_info.index(" ")
            firstindex = base_info.index(":")
            self.username = base_info[firstindex + 1:lastindex]
            print(u"用户名: " + self.username)
            # 手机版网址
            other_info = d(".c").eq(4).html()
            other_info = other_info.replace("<br />", " ")
            firstindex = other_info.index("手机版:")
            lastindex = other_info.index(" ", firstindex)
            self.phone_url = other_info[firstindex + 4:lastindex]
            print(self.phone_url)
            # 互联网版网址
            firstindex = other_info.index("互联网:")
            lastindex = other_info.index(" ", firstindex)
            self.web_url = other_info[firstindex + 4:lastindex]
            print(self.web_url)
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()

    # 获取用户微博数、关注数、粉丝数
    def get_user_info(self):
        try:
            url = self.phone_url + '?filter=%d&page=1' % self.filter
            source_code = requests.get(url, headers=self.headers).content
            d = pq(source_code)
            pattern = r'\d+'
            content_number = d(".tc").html()
            other_number = list(d(".tip2").items("a"))
            
            # 微博数
            self.weibo_num = re.search(pattern, content_number).group()
            print(u"微博数: " + str(self.weibo_num))
            
            # 关注数
            self.following = re.search(pattern, other_number[0].html()).group()
            print(u"关注数: " + str(self.following))
            
            # 粉丝数
            self.followers = re.search(pattern, other_number[1].html()).group()
            print(u"粉丝数: " + str(self.followers))
            print("===========================================================================")
        
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()
    
    # 获取"长微博"全部文字内容
    def get_long_weibo(self, weibo_link):
        try:
            html = requests.get(weibo_link, headers=self.headers).content
            selector = etree.HTML(html)
            info = selector.xpath("//div[@class='c']")[1]
            wb_content = info.xpath("div/span[@class='ctt']")[0].xpath(
                "string(.)").encode(sys.stdout.encoding, "ignore").decode(
                sys.stdout.encoding)
            wb_content = wb_content[1:]
            return wb_content
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()
    
    # 获取用户微博内容及对应的发布时间、点赞数、转发数、评论数
    def get_weibo_info(self):
        try:
            url = self.phone_url + '?filter=%d&page=1' % self.filter
            html = requests.get(url, headers=self.headers)
            selector = etree.HTML(html.content)
            if selector.xpath("//input[@name='mp']") == []:
                page_num = 1
            else:
                page_num = (int)(selector.xpath(
                    "//input[@name='mp']")[0].attrib["value"])
            pattern = r"\d+\.?\d*"
            for page in range(1, page_num + 1):
                url2 = self.phone_url + '?filter=%d&page=%d' % (self.filter, page)
                html2 = requests.get(url2, headers=self.headers, timeout=10)
                if html2.status_code != 200:
                    html2 = requests.get(url2, headers=self.headers, timeout=10)
                selector2 = etree.HTML(html2.content)
                info = selector2.xpath("//div[@class='c']")
                is_empty = info[0].xpath("div/span[@class='ctt']")
                if is_empty:
                    for i in range(0, len(info) - 2):
                        # 微博内容
                        str_t = info[i].xpath("div/span[@class='ctt']")
                        if info[i].xpath("div/span[@class='cmt']"):     #转发
                            continue
                        weibo_content = str_t[0].xpath("string(.)").encode(     #当前节点文本内容
                            sys.stdout.encoding, "ignore").decode(
                            sys.stdout.encoding)
                        weibo_content = weibo_content[:-1]
                        weibo_id = info[i].xpath("@id")[0][2:]
                        a_link = info[i].xpath(
                            "div/span[@class='ctt']/a/@href")
                        if a_link:      #长微博
                            if (a_link[-1] == "/comment/" + weibo_id or
                                    "/comment/" + weibo_id + "?" in a_link[-1]):
                                weibo_link = "https://weibo.cn" + a_link[-1]
                                wb_content = self.get_long_weibo(weibo_link)
                                if wb_content:
                                    weibo_content = wb_content
                        self.weibo_content.append(weibo_content)
                        print(u"微博内容: " + weibo_content)
                        
                        # 微博位置
                        div_first = info[i].xpath("div")[0]
                        a_list = div_first.xpath("a")
                        weibo_place = u"无"
                        for a in a_list:
                            if ("http://place.weibo.com/imgmap/center" in a.xpath("@href")[0] and
                                    a.xpath("text()")[0] == u"显示地图"):
                                weibo_place = div_first.xpath(
                                    "span[@class='ctt']/a")[-1]
                                if u"的秒拍视频" in div_first.xpath("span[@class='ctt']/a/text()")[-1]:
                                    weibo_place = div_first.xpath(
                                        "span[@class='ctt']/a")[-2]
                                weibo_place = weibo_place.xpath("string(.)").encode(
                                    sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
                                break
                        self.weibo_place.append(weibo_place)
                        print(u"微博位置: " + weibo_place)
                        
                        # 微博发布时间
                        str_time = info[i].xpath("div/span[@class='ct']")
                        str_time = str_time[0].xpath("string(.)").encode(
                            sys.stdout.encoding, "ignore").decode(
                            sys.stdout.encoding)
                        publish_time = str_time.split(u'来自')[0]
                        if u"刚刚" in publish_time:
                            publish_time = datetime.now().strftime(     #“当前”发布
                                '%Y-%m-%d %H:%M')
                        elif u"分钟" in publish_time:     #"x"分钟前发布
                            minute = publish_time[:publish_time.find(u"分钟")]
                            minute = timedelta(minutes=int(minute))
                            publish_time = (
                                    datetime.now() - minute).strftime(
                                "%Y-%m-%d %H:%M")
                        elif u"今天" in publish_time:     #今天发布
                            today = datetime.now().strftime("%Y-%m-%d")
                            time = publish_time[3:]     #时分秒
                            publish_time = today + " " + time
                        elif u"月" in publish_time:      #今年发布
                            year = datetime.now().strftime("%Y")
                            month = publish_time[0:2]
                            day = publish_time[3:5]
                            time = publish_time[7:12]
                            publish_time = (
                                    year + "-" + month + "-" + day + " " + time)
                        else:       #今年以前发布
                            publish_time = publish_time[:16]
                        self.publish_time.append(publish_time)
                        print(u"微博发布时间: " + publish_time)
                        
                        # 微博发布工具
                        if len(str_time.split(u'来自')) > 1:
                            publish_tool = str_time.split(u'来自')[1]
                        else:
                            publish_tool = u"无"
                        self.publish_tool.append(publish_tool)
                        print(u"微博发布工具: " + publish_tool)
                        
                        str_footer = info[i].xpath("div")[-1]
                        str_footer = str_footer.xpath("string(.)").encode(
                            sys.stdout.encoding, "ignore").decode(sys.stdout.encoding)
                        #str.rfind(str,beg=0,end=len(str)) 返回字符串最后一次出现的位置（从右向左查询，如果没有匹配项则返回-1）
                        str_footer = str_footer[str_footer.rfind(u'赞'):]
                        #re.l:忽略大小写
                        #re.L表示特殊字符集,依赖于当前环境
                        #re.M多行模式
                        #re.S即为.并且包括换行符在内的任意字符(.不包括换行符)
                        #re.U表示特殊字符集,依赖于Unicode字符属性数据库
                        #re.X为了增加可读性，忽略空格和#后面的注释
                        guid = re.findall(pattern, str_footer, re.M)
                        
                        # 点赞数
                        up_num = int(guid[0])
                        self.up_num.append(up_num)
                        print(u"点赞数: " + str(up_num))
                        
                        # 转发数
                        retweet_num = int(guid[1])
                        self.retweet_num.append(retweet_num)
                        print(u"转发数: " + str(retweet_num))
                        
                        # 评论数
                        comment_num = int(guid[2])
                        self.comment_num.append(comment_num)
                        print(u"评论数: " + str(comment_num))
                        print("===========================================================================")
                        
                        self.weibo_num2 += 1
            
            if not self.filter:
                print(u"共" + str(self.weibo_num2) + u"条微博")
            else:
                print(u"共" + str(self.weibo_num) + u"条微博，其中" +
                      str(self.weibo_num2) + u"条为原创微博"
                      )
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()
    
    #获取发布数（时间——数量）
    def get_weibo_num(self):
        url = self.web_url + '?is_all=1'  # 未登录状态（微博主页）
        url2 = "https://passport.weibo.cn/signin/login"  # 登录网址
        # options = webdriver.ChromeOptions()
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')  # 无头模式运行chrome
        options.add_argument('--disable-gpu')
        # options.add_argument(
        #     'user-agent="Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"')
        options.add_argument(
            'user-agent="Mozilla/5.0 (Windows NT 6.3; WOW64; rv:61.0) Gecko/20100101 Firefox/61.0"')
        # browser = webdriver.Chrome(chrome_options=options)
        browser = webdriver.Firefox(firefox_options=options)
        # browser = webdriver.Chrome()
        # browser = webdriver.Firefox()
        try:
            # 登录微博
            browser.get(url2)
            wait = WebDriverWait(browser, 60)
            wait.until(EC.visibility_of_element_located((By.ID, 'loginName')))
            wait.until(EC.visibility_of_element_located((By.ID, 'loginPassword')))
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#loginAction')))
            browser.find_element_by_id("loginName").send_keys("1483013380@qq.com")
            browser.find_element_by_id("loginPassword").send_keys("Qw123456.")
            browser.find_element_by_id("loginAction").click()
            time.sleep(3)

            # 存储cookie
            # dictCookies = browser.get_cookies()
            # jsonCookies = json.dumps(dictCookies)
            # file_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + "weibo"
            # if not os.path.isdir(file_dir):
            #     os.mkdir(file_dir)
            # file_path = file_dir + os.sep + "%d_cookies" % self.user_id + ".json"
            # with open(file_path, 'w') as f:
            #     f.write(jsonCookies)

            # browser.delete_all_cookies()
        
            # browser.get(url)
            # time.sleep(20)
            
            # #取出cookie
            # file_dir=os.path.split(os.path.realpath(__file__))[0] + os.sep + "weibo"
            # file_path=file_dir+os.sep+"%d_cookies" %self.user_id+".json"
            # with open(file_path,'r',encoding='utf-8') as f:
            #     listCookies=json.loads(f.read())
            # for cookie in listCookies:
            #     browser.add_cookie({
            #         'expiry':cookie['expiry'],
            #         'httpOnly':cookie['httpOnly'],
            #         'name':cookie['name'],
            #         'path':cookie['path'],
            #         'secure':cookie['secure'],
            #         'value':cookie['value']
            #     })
            # browser.get(url)

            try:
                browser.get(url)  # 请求目标页
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.WB_timeline')))
            except exceptions.TimeoutException as e:
                # browser.get(url)  # 请求目标页
                browser.refresh()
                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.WB_timeline')))
            soup = BeautifulSoup(browser.page_source, "lxml")
            self.year_list = soup.find_all('li', attrs={'node-type': 'year'})
            year_num = len(self.year_list)
            temp = 0
            for i in self.year_list:
                self.year_list[temp] = i.get_text()
                temp = temp + 1
        
            pattern = r'\d+'
            for j in range(0, year_num):
                temp = self.year_list[j][4:]
                self.year_list[j] = self.year_list[j][0:4]
                result = re.findall(pattern, temp)
                self.month_list.append(result)
                month_list_len=len(result)
                #self.number_list.append([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                self.number_list.append([0]*month_list_len)
                self.sum_number_list.append(0)
            p = 0
            # 确定每年发博次数
            for i in self.year_list:
                q = 0
                for j in self.month_list[p]:
                    print(i + "年" + self.month_list[p][q] + "月")
                    url = self.web_url + '?is_all=1&stat_date=' + i + self.month_list[p][q]  # 目标页
                    try:
                        browser.get(url)  # 请求目标页
                        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.WB_timeline')))
                    except exceptions.TimeoutException as e:
                        # browser.get(url)  # 请求目标页
                        browser.refresh()
                        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.WB_timeline')))
                    # 获取xxx年/xxx月的微博数
                    # 加载滚动条
                    js1 = 'var q=document.documentElement.scrollTop=document.body.scrollHeight;var lenOfPage=document.body.scrollHeight;return lenOfPage;'  # 纵向滚动条滑到底部（微博45条/满页，滑动两次/满页）
                    lenOfPage1 = browser.execute_script(js1)
                    # wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[node-type='lazyload'] .W_loading")))
                    time.sleep(4)
                    js2 = 'var lenOfPage=document.body.scrollHeight;return lenOfPage;'
                    lenOfPage2 = browser.execute_script(js2)
                    # 判断滚动条是否加载失败
                    soup = BeautifulSoup(browser.page_source, "lxml")
                    lazyload = soup.find('div', attrs={'node-type': 'lazyload'})
                    loadfail = None
                    if lazyload:
                        loadfail = lazyload.find('a')
                    while lenOfPage1 != lenOfPage2 or loadfail or lazyload:
                        if lenOfPage1 != lenOfPage2:
                            lenOfPage1 = browser.execute_script(js1)
                            # wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[node-type='lazyload'] .W_loading")))
                            time.sleep(4)
                            lenOfPage2 = browser.execute_script(js2)
                        elif lazyload:
                            browser.refresh()
                            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.WB_timeline')))
                            lenOfPage1 = browser.execute_script(js1)
                            # wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[node-type='lazyload'] .W_loading")))
                            time.sleep(4)
                            lenOfPage2 = browser.execute_script(js2)
                        else:
                            browser.find_element_by_link_text("点击重新载入").click()
                            time.sleep(5)
                        soup = BeautifulSoup(browser.page_source, "lxml")
                        lazyload = soup.find('div', attrs={'node-type': 'lazyload'})
                        loadfail = None
                        if lazyload:
                            loadfail = lazyload.find('a')
                    # x月包含多少页微博
                    soup = BeautifulSoup(browser.page_source, "lxml")
                    has_list_page = len(soup.find_all('a', attrs={'action-type': 'fl_nextTimeBase'}))  # "查看更早微博"
                    has_weibo_content=len(soup.find_all('div',attrs={'class':'WB_result_null_v2'}))
                    if has_list_page:  # 一页
                        tbinfo_num = len(soup.find_all('div', tbinfo=re.compile('.')))
                        print(tbinfo_num)
                        self.number_list[p][q] = tbinfo_num
                        self.sum_number_list[p] = self.sum_number_list[p] + tbinfo_num
                    elif has_weibo_content: #本月没有内容
                        self.number_list[p][q]=0
                    else:  # 不止一页
                        page_list = soup.find('div', attrs={'action-type': 'feed_list_page_morelist'})
                        page_num = len(page_list.find_all('li'))
                        url = url + '&page=%d' % page_num
                        try:
                            browser.get(url)  # 请求目标页
                            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.WB_timeline')))
                        except exceptions.TimeoutException as e:
                            # browser.get(url)  # 请求目标页
                            browser.refresh()
                            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.WB_timeline')))
                        # 加载滚动条
                        lenOfPage1 = browser.execute_script(js1)
                        # wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[node-type='lazyload'] .W_loading")))
                        time.sleep(4)
                        lenOfPage2 = browser.execute_script(js2)
                        # 判断滚动条是否加载失败
                        soup = BeautifulSoup(browser.page_source, "lxml")
                        lazyload = soup.find('div', attrs={'node-type': 'lazyload'})
                        loadfail = None
                        if lazyload:
                            loadfail = lazyload.find('a')
                        while lenOfPage1 != lenOfPage2 or loadfail or lazyload:
                            if lenOfPage1 != lenOfPage2:
                                lenOfPage1 = browser.execute_script(js1)
                                # wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[node-type='lazyload'] .W_loading")))
                                time.sleep(4)
                                lenOfPage2 = browser.execute_script(js2)
                            elif lazyload:
                                browser.refresh()
                                wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.WB_timeline')))
                                lenOfPage1 = browser.execute_script(js1)
                                # wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[node-type='lazyload'] .W_loading")))
                                time.sleep(4)
                                lenOfPage2 = browser.execute_script(js2)
                            else:
                                browser.find_element_by_link_text("点击重新载入").click()
                                # wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[node-type='lazyload'] .W_loading")))
                                time.sleep(5)
                            soup = BeautifulSoup(browser.page_source, "lxml")
                            lazyload = soup.find('div', attrs={'node-type': 'lazyload'})
                            loadfail = None
                            if lazyload:
                                loadfail = lazyload.find('a')
                        soup = BeautifulSoup(browser.page_source, "lxml")
                        tbinfo_num = len(soup.find_all('div', tbinfo=re.compile('.'))) + (page_num - 1) * 45
                        print(tbinfo_num)
                        self.number_list[p][q] = tbinfo_num
                        self.sum_number_list[p] = self.sum_number_list[p] + tbinfo_num
                    q = q + 1
                p = p + 1
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()
            browser.quit()
        else:
            browser.quit()
        
    # 将爬取的信息写入文件
    def write_txt(self):
        try:
            # 将微博内容写入文件
            if self.filter:
                result_header = u"\r\n\r\n原创微博内容: \r\n"
            else:
                result_header = u"\r\n\r\n微博内容: \r\n"
            result = (u"用户信息\r\n用户昵称：" + self.username +
                      u"\r\n用户id: " + str(self.user_id) +
                      u"\r\n微博数: " + str(self.weibo_num) +
                      u"\r\n关注数: " + str(self.following) +
                      u"\r\n粉丝数: " + str(self.followers) +
                      result_header
                      )
            for i in range(1, self.weibo_num2 + 1):
                text = (str(i) + ":" + self.weibo_content[i - 1] + "\r\n" +
                        u"微博位置: " + self.weibo_place[i - 1] + "\r\n" +
                        u"发布时间: " + self.publish_time[i - 1] + "\r\n" +
                        u"点赞数: " + str(self.up_num[i - 1]) +
                        u"	 转发数: " + str(self.retweet_num[i - 1]) +
                        u"	 评论数: " + str(self.comment_num[i - 1]) + "\r\n"
                                                                       u"发布工具: " + self.publish_tool[i - 1] + "\r\n\r\n"
                        )
                result = result + text
            weibo_dir = os.path.split(os.path.realpath(__file__))[
                           0] + os.sep + "weibo"
            if not os.path.isdir(weibo_dir):
                os.mkdir(weibo_dir)
            file_path = weibo_dir + os.sep + "%d" % self.user_id + ".txt"
            f = open(file_path, "wb")
            f.write(result.encode(sys.stdout.encoding))
            f.close()
            print(u"微博写入文件完毕，保存路径:")
            print(file_path)

            # 将微博发布数写入文件
            result = ''
            p = 0
            for i in self.year_list:
                q = 0
                text = (i + u"年\r\n")
                for j in self.month_list[p]:
                    if self.number_list[p][q]!=0:
                        text = text + self.month_list[p][q] + u"月: %d\r\n" % self.number_list[p][q]
                    q = q + 1
                result = result + text + u"总计: %d\r\n\r\n" % self.sum_number_list[p]
                p = p + 1
            weibo_dir = os.path.split(os.path.realpath(__file__))[0] + os.sep + "weibo"
            if not os.path.isdir(weibo_dir):
                os.mkdir(weibo_dir)
            file_path = weibo_dir + os.sep + "%d_2" % self.user_id + ".txt"
            with open(file_path, "wb") as f:
                f.write(result.encode(sys.stdout.encoding))
            print(u"各年月发布数写入文件完毕，保存路径:")
            print(file_path)
        except Exception as e:
            print("Error: ", e)
            traceback.print_exc()
    
    # 运行爬虫
    def start(self):
        try:
            self.get_username()
            self.get_user_info()
            self.get_weibo_info()
            self.get_weibo_num()
            self.write_txt()
            self.analyse()
            print(u"信息抓取完毕")
            print("===========================================================================")
        except Exception as e:
            print("Error: ", e)
    
    # 分析数据
    def analyse(self):
        # 词汇统计——词云
        weibo_dir = os.path.split(os.path.realpath(__file__))[
                       0] + os.sep + "weibo"
        file_path = weibo_dir + os.sep + "%d" % self.user_id + ".txt"
        f = open(file_path, "r",encoding='utf-8')
        #创建image文件
        image_dir = os.path.split(os.path.realpath(__file__))[
                       0] + os.sep + "image"
        if not os.path.isdir(image_dir):
            os.mkdir(image_dir)

        index=8
        result=''
        contentlist=f.readlines()
        while True:
            try:
                content = contentlist[index]
                #content=content.strip()
                content=content[2:-1]+" "
                result=result+content
                index=index+6
            except IndexError as e:
                # print("Error: ", e)
                f.close()
                w = wordcloud.WordCloud(width=1000, font_path="msyh.ttc", height=700,background_color="white")  # 字体为微软雅黑
                w.generate(" ".join(jieba.lcut(result)))
                image_path = image_dir + os.sep + "%d.png" % self.user_id
                w.to_file(image_path)
                break
        
        #发布数统计——条形图
        weibo_dir = os.path.split(os.path.realpath(__file__))[
                       0] + os.sep + "weibo"
        file_path = weibo_dir + os.sep + "%d_2" % self.user_id + ".txt"
        f = open(file_path, "r", encoding='utf-8')
        # 创建image文件
        image_dir = os.path.split(os.path.realpath(__file__))[
                       0] + os.sep + "image"
        if not os.path.isdir(image_dir):
            os.mkdir(image_dir)

        index = -1
        year_list=[]
        month_list=[]
        number_list=[]
        sum_number_list=[]
        contentlist = f.readlines()
        lens=len(contentlist)
        i=0
        while i<lens-1:
            if i==0 or contentlist[i]=='\n':
                if i!=0:
                    i=i+1
                year_list.append(contentlist[i][:-1])  # 年份
                # 月份和发布数
                month_list.append([])
                number_list.append([])
                index=index+1
            else:
                temp_list=contentlist[i].split(": ")
                if temp_list[0]!="总计":
                    month_list[index].append(temp_list[0])
                    number_list[index].append(temp_list[1][:-1])
                else:
                    sum_number_list.append(temp_list[1][:-1])
            i=i+1
        year_lens=len(year_list)
        bar_list=[]
        page = Page(page_title=(self.username+"的微博数统计"))
        for j in range(0,year_lens):
            bar=Bar(year_list[j])
            bar.add("年发布数",month_list[j],number_list[j],mark_point=["max","min"],mark_line=["average"])
            bar_list.append(bar)
        bar = Bar(year_list[year_lens-1]+"-"+year_list[0])
        re_year_list=year_list[::-1]
        re_sum_number_list=sum_number_list[::-1]
        bar.add("总发布数",re_year_list,re_sum_number_list,mark_line=["average"],mark_point=["max","min"])
        bar_list.append(bar)
        bar_lens=len(bar_list)
        for k in range(0,bar_lens):
            page.add(bar_list[k])
        html_path = image_dir + os.sep + "%d.html" % self.user_id
        page.render(html_path)
        
def main():
    # locale.getdefaultlocale()   #系统默认编码
    # sys.getdefaultencoding()    #python代码中的编码
    # sys.getfilesystemencoding()  #文件编码
    # sys.stdin.encoding   #终端输入编码
    # sys.stdout.encoding  # 终端输出编码
    # locale.getpreferredencoding()
    # locale.getlocale()
    try:
        # 使用实例,输入一个用户id，所有信息都会存储在wb实例中
        user_id=1239246050 #薛之谦
        wb = Weibo(user_id)  # 调用Weibo类，创建微博实例wb
        wb.start()  # 爬取微博信息
        print(u"用户名: " + wb.username)
        print(u"全部微博数: " + str(wb.weibo_num))
        print(u"关注数: " + str(wb.following))
        print(u"粉丝数: " + str(wb.followers))
        if wb.weibo_content:
            print(u"最新/置顶 微博为: " + wb.weibo_content[0])
            print(u"最新/置顶 微博位置: " + wb.weibo_place[0])
            print(u"最新/置顶 微博发布时间: " + wb.publish_time[0])
            print(u"最新/置顶 微博获得赞数: " + str(wb.up_num[0]))
            print(u"最新/置顶 微博获得转发数: " + str(wb.retweet_num[0]))
            print(u"最新/置顶 微博获得评论数: " + str(wb.comment_num[0]))
            print(u"最新/置顶 微博发布工具: " + wb.publish_tool[0])
    except Exception as e:
        print("Error: ", e)
        traceback.print_exc()


if __name__ == "__main__":
    main()
