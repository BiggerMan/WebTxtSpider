# -*- coding: utf-8 -*- 
#---------------------------------------------------
#   程序：糗百小爬虫
#   版本：0.1
#   作者：修改：flytiger,来自网友why，地址:http://blog.csdn.net/pleasecallmewhy/article/details/8932310
#   语言：python 2.7
#   功能：浏览糗百新消息
#   历史：
#       版本0.1初步实现了功能
#---------------------------------------------------

import urllib2
import urllib
import re
import thread
import time


#----------处理页面上的各种标签----------
class Html_Tool:
    # 用非贪婪模式匹配 \t 或者 \n 或者 空格 或者 超链接 或者 图片
    bgnCharToNoneRex = re.compile("(\t|\n| |<a.*?>|<img.*?>)")
    # 用非贪婪模式匹配任意标签
    endCharToNoneRex = re.compile("(<.*?>)")
    # 用非 贪婪模式 匹配 任意<p>标签
    bgnPartRex = re.compile("<p.*?>")
    charToNewLineRex = re.compile("(<br/>|</p>|<tr>|<div>|</div>)")
    charToNextTabRex = re.compile("<td>")
    # 将一些html的符号实体转变为原始符号
    replaceTab = [("<","<"),(">",">"),("&","&"),("&","\""),(" "," ")]
    
    #
    def ReplaceChar(self, x):
        x = self.bgnCharToNoneRex.sub("", x)#sub方法执行替换工作
        x = self.bgnPartRex.sub("\n     ", x)
        x = self.charToNewLineRex.sub("\n", x)
        x = self.charToNextTabRex.sub("\t", x)
        x = self.endCharToNoneRex.sub("", x)
        
        for t in self.replaceTab:
            x = x.replace(t[0], t[1])#replace
        return x

#----------加载处理糗事百科----------
class Html_Model: 
    #构造函数
    def __init__(self):
        self.page = 1 #当前到达的页面计数
        self.pages =[] #后台线程pages缓存
        self.myTool = Html_Tool()#新建Html_Tool对象
        self.enable = False
    def GetPage(self, page):
        myUrl = "http://www.qiushibaike.com/hot/page/" + page
        myResponse = urllib2.urlopen(myUrl)
        myPage = myResponse.read()
        #encode的作用是将unicode编码转换成其他编码的字符串  
        #decode的作用是将其他编码的字符串转换成unicode编码  
        unicodePage = myPage.decode("utf-8") 
        # 找出所有class="content"的div标记  
        #re.S是任意匹配模式，也就是.可以匹配换行符
        #myItems是二维数组？？对，对正则表达式要正确理解，用到正则表达式的用括号（）括起来的地方就是被提取出来的字符串
        #例如下面的语句每次都得到两个"（.*?）"位置的内容，这里有两个位置，结果为两个，组成数组则为二维
        myItems = re.findall('<div.*?class="content".*?title="(.*?)">(.*?)</div>', unicodePage, re.S)
        items = []
        for item in myItems:
            # item 中第一个是div的标题，也就是时间  item[0]
            # item 中第二个是div的内容，也就是内容  item[1]
            items.append([item[0].replace("\n", ""), item[1].replace("\n", "")])
        return items
    #用于加载新的段子
    def LoadPage(self):
        #用户未输入quit一直运行
        while self.enable:
            if len(self.pages) < 2:
                try:
                    #获取新页面的段子
                    myPage = self.GetPage(str(self.page))
                    self.page += 1
                    self.pages.append(myPage)
                except:
                    print "无法连接糗事百科 -_-!"
            else:
                time.sleep(1)
    
    def ShowPage(self, page, page_count):
        for items in page:
            print u'第%d页'%page_count, items[0]
            print self.myTool.ReplaceChar(items[1])
            myInput = raw_input('退出输入quit，回车继续：')
            if myInput == 'quit':
                self.enable = False
                break
            
    
    def Start(self):
        self.enable = True
        page = self.page
        print u'正在加载中...'
        
        #启动新线程在后台加载新页面
        thread.start_new_thread(self.LoadPage, ())
        
        while self.enable:
            if self.pages:
                curPage = self.pages[0]
                del self.pages[0]
                self.ShowPage(curPage, page)
                page += 1

#一定要紧贴左边栏，不然就是在class范围里了
#----------程序入口----------
raw_input('糗百小爬虫已经启动,按任意键开始浏览段子')
myModel =Html_Model()
myModel.Start()
