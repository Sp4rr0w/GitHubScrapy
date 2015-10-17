#coding:utf-8
#!/usr/bin/env python
#author:Z0fr3y
#update:2015-10-11
#version:1.0--1.2--2.2--2.3--3.0--------4.0 !
#name:GitHubSpider
#运行：scrapy crawl github 或者加上 -s LOG_FILE=scrapy.log
#暂停：ctrl+c
#再运行：scrapy crawl github -s JOBDIR=crawl/github_stop
import urllib
from scrapy import Request
from scrapy.spider import Spider
from scrapy.selector import Selector
#from scrapy.spiders import CrawlSpider, Rule
from GitHub.items import Github_Item
import pymongo

import sys
import os
reload (sys)
sys.setdefaultencoding("utf-8")#这3句话让爬到的内容是utf-8的
#PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))#返回绝对路径（#返回文件路径）

host="https://github.com"
a=1
b=0#限制爬取深度
c=30#爬取深度为30
f_newlist=[]#文件名（不包含后缀），避免重复爬取。
filecount = 0#文件数量
followers_urls=["https://github.com/1st1/followers",]#存储所有followers不为零的用户followers页面，以便进一步爬取
followers_urls_test=[]#用于测试 如果和followers_urls相等  
counter=0#多少followers
followers_url_people=51#每个follwers页面最多为51位
class GithubSpider(Spider):
    """
    爬取GitHub网站中用户信息
    """
    name = 'github'
    allowed_domains = ['github.com']
    headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip,deflate",
    "Accept-Language": "zh-CN,zh;q=0.8",
    "Connection": "keep-alive",
    "Content-Type":" application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
    }
    start_urls = ["https://github.com/1st1",]
    #def __init__(self,category=None,*args,**kwargs):
        #super(GithubSpider,self).__init__(*args,**kwargs)
        
    def parse(self,response):
        print "~"*60+"start"
    	print response.url
    	people_mainpage=Selector(response)
        
        self.getfile()
        self.filesnum()
        print "saved "+str(filecount)+" people.OK-Continue~~~"
        global f_newlist
    	people=Github_Item()#以下是爬取用户的详细信息
        people['home_page']=response.url
        people_profile=people_mainpage.xpath('//div[@class="column one-fourth vcard"]')
        people['image_urls'] = people_profile.xpath('a[1]/img/@src').extract()
        x1=people_profile.xpath('h1/span[@class="vcard-fullname"]/text()').extract()
        if x1==[]:#没有if/else 会出现超越边界错误。
            people['fullname']="None"
        else:
            people['fullname']=x1[0]    
        for i in range(len(f_newlist)):
            if (people['fullname']==f_newlist[i]):
                if followers_urls==followers_urls_test:
                    break#如果和followers_urls相等  则跳出
                else:
                    yield Request(url=followers_urls[0],callback=self.parse_two,dont_filter=True)
        
        x2=people_profile.xpath('h1/span[@class="vcard-username"]/text()').extract()
        if x2==[]:
            people['username']="None"
        else:
            people['username']=x2[0]
        x3=people_profile.xpath('//li/@title').extract()
        if x3==[]:
            people['organization']="None"
        else:
            people['organization']=x3[0] 
        x4=people_profile.xpath('//a[@class="email"]/text()').extract()
        if x4==[]:
            people['mail']="None"
        else:
            people['mail']=x4[0]
        
        x5=people_profile.xpath('//time[@class="join-date"]/text()').extract()
        if x5==[]:
            people['joined']="None"
        else:
            people['joined']=x5[0]
        x6=people_profile.xpath('div[@class="vcard-stats"]/a[1]/strong[@class="vcard-stat-count"]/text()').extract()
        if x6==[]:
            people['followers']="None"
        else:
            people['followers']=x6[0]
        x7=people_profile.xpath('div[@class="vcard-stats"]/a[2]/strong[@class="vcard-stat-count"]/text()').extract()
        if x7==[]:
            people['starred']="None"
        else:
            people['starred']=x7[0]
        x8=people_profile.xpath('div[@class="vcard-stats"]/a[3]/strong[@class="vcard-stat-count"]/text()').extract()
        if x8==[]:
            people['following']="None"
        else:
            people['following']=x8[0]
        popular_repo=people_mainpage.xpath('//div[@class="columns popular-repos"]/div[@class="column one-half"][1]')
        people['popular_repos']=" "
        for i in range(1,6):#这是popular_repos数据
            people['popular_repos']=people['popular_repos']+" "+' '.join(popular_repo.xpath('div/ul[@class="boxed-group-inner mini-repo-list"]/li['+str(i)+']/a/span[2]/span/text()').extract())
        repo_contribution=people_mainpage.xpath('//div[@class="columns popular-repos"]/div[@class="column one-half"][2]')
        people['repo_contributions']=" "
        for i in range(1,6):#这是repo_contributions数据
            people['repo_contributions']=people['repo_contributions']+" "+' '.join(repo_contribution.xpath('div/ul[@class="boxed-group-inner mini-repo-list"]/li['+str(i)+']/a/span[2]/span[1]/text()').extract())+"/"+' '.join(repo_contribution.xpath('div/ul[@class="boxed-group-inner mini-repo-list"]/li['+str(i)+']/a/span[2]/span[2]/text()').extract())
        
        followers_page=host+''.join(people_mainpage.xpath('//a[@class="vcard-stat"][1]/@href').extract())
        xxxx=people
        #'../media.people/'GitHub\media\people
        fh=open('GitHub/media/people/'+people['fullname']+'.txt','w')
        fh.write(str(xxxx))
        fh.close()
        global b
        global c
        if b<c:
            b+=1
            print str(b)+" "+ "people Detail information"
            print people
            yield Request(url=followers_page,callback=self.parse_followers,dont_filter=True)
        if b:
            yield people


    def parse_followers(self,response):
        print "~"*60+"parse_followers"
        print response.url#followers页面
        global followers_urls
        followers_urls.append(response.url)#存储followers页面
        followers_urls_2=[]#去重
        for m in range(len(followers_urls)):
            if followers_urls[m] not in followers_urls_2:
                followers_urls_2.append(followers_urls[m])

        followers_urls=followers_urls_2

        people_parse_one=Selector(response)
        
        followers_parse_one_link=host+''.join(people_parse_one.xpath('//ol[@class="follow-list clearfix"]/li[1]/a/@href').extract())
        print followers_parse_one_link
        return Request(url=followers_parse_one_link,callback=self.parse_one,dont_filter=True)

    def parse_one(self,response):
        print "~"*60+"parse_one_start"
        print response.url
        people_parse_one=Selector(response)
        x=people_parse_one.xpath('//div[@class="vcard-stats"]/a[1]/strong[@class="vcard-stat-count"]/text()').extract()
        followers_page=host+''.join(people_parse_one.xpath('//a[@class="vcard-stat"][1]/@href').extract())
        #print "x=:"+x[0]
        #y=int(''.join([str(t) for t in x]))
        #print "y=:"+y
        print "x=:"
        print x
        if x!= ["0"]:
            followers_urls.append(followers_page)
            print "followers is not 0 ....Go to--->"
            yield Request(url=response.url,callback=self.parse,dont_filter=True)
        else:
            #当x=['0']时 不再返回前一页面（难搞），而是重新爬取followers_urls里面链接。
            print "followers_urls第一个参数:"
            print followers_urls[0]
            yield Request(url=followers_urls[0],callback=self.parse_two,dont_filter=True)
    def parse_two(self,response):
        print "~"*60+"parse_two_start"#当上一级的followers为零时或者重复爬取了某个人跳到这。也是用户的followers页
        print response.url
        global counter
        global followers_urls
        people_parse_two=Selector(response)
        x1=people_parse_two.xpath('//span[@class="counter"]/text()').extract()
        counter=int(x1[0])#计算多少followers
        if counter>followers_url_people:
            counter1=counter/followers_url_people+1#一个页面有51个人，counter1指有多少页面
            for o in range(2,counter1):
                followers_urls.append(response.url+"?page="+o)
        global a
        global c
        a+=1
        print "find : "+str(a)+" followers is 0."
        #print "so hava"+str(c)+"people information"
        if (a<counter):
            followers_parse_two_link=host+''.join(people_parse_two.xpath('//ol[@class="follow-list clearfix"]/li['+str(a)+']/a/@href').extract())
            yield Request(url=followers_parse_two_link,callback=self.parse,dont_filter=True)
        if(a>=counter):
            a=0#重置a
            print "~"*60+"over"
            print "start crawl followers_urls~~~~~~~~~~~~~~~~~"
            #若一个人的fllowers的某个人的followers的.....爬完了（即最后一个人的followers为0）,就执行这个。
            #因为之前有保存每个人的follower页面，则爬取时从第二个人出发爬取（第一个已爬了），over。
            #for v in range(len(followers_urls)):
            followers_1=followers_urls[0]#先把要取的一个保存为followers_1  然后再删掉  再爬取followers_1。
            followers_urls.remove(followers_urls[0])
            yield Request(url=followers_1,callback=self.parse_followers,dont_filter=True)

    def getfile(self):#获取文件名（不包含后缀)
        path1 = r'GitHub\media\people'
        f_list = os.listdir(path1)
        global f_newlist
        for i in range(len(f_list)):
            l,b=os.path.splitext(f_list[i])
            f_newlist.append(l)
        return f_newlist
    def filesnum(self):#获取已下载用户的txt文件数量
        global filecount 
        filecount = 0
        path2 = r'e://scrapy/GitHub/GitHub/media/people'
        for root, dirs, files in os.walk(path2):
            #print files
            fileLength = len(files)
            if fileLength != 0:
                filecount = filecount + fileLength
        return filecount
        #print "The number of files under <%s> is: %d" %(path,count)


#通过scrapy进行大数据采集时，默认的scrpay crawl spider 是不能暂停的
#但是在settings.py文件里加入下面的代码： 
#JOBDIR='github.com'
#crawl/github_stop是目录  按ctrl+c时会把暂停的数据存放到那里面
#scrapy提供了相关的方法保存采集的作业状态:
#ctrl+c之后再启动时输入
#scrapy crawl github -s JOBDIR=crawl/github_stop









# yield：生成器
# 任何使用yield的函数都称之为生成器
# def count(n):  
#     while n > 0:  
#         yield n   #生成值：n  
#         n -= 1
# 使用yield，可以让函数生成一个序列
# 该函数返回的对象类型是"generator"，通过该对象连续调用next()方法返回序列值。

# c = count(5)  
# c.next()  
# >>> 5  
# c.next()  
# >>>4  