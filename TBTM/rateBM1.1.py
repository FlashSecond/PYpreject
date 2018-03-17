import os
import os.path
import json
import re
import urllib.request
import urllib.parse
import glob
import time
import threading

#连接网络获取资源信息 
def urlink(url,headinfo):
      #请求处理
      req = urllib.request.Request(url,headers=headinfo)
      #链接网站
      response = urllib.request.urlopen(req)
      #读取链接数据与解码utf-8
      return response.read().decode('GBK',"ignore")

#获取初始信息
def loginfo(path):
      with open(path) as link:
            return link.read()
#写入内容
def infowrite(pathf,m,data):
      with open(pathf,mode = m) as info:
            info.write(data)
      return pathf
#下载评论图片
def BMratepic(picname,path):
      #匹配原始图片
      try:
            picp = re.compile(r".*?(.jpg|.png|.jpeg|.gif)")
            picname = picp.search(picname).group()
            picpath = picname
            picn = os.path.basename(picname)
            third = os.path.join(path,picn)
            if os.path.exists(third):
                  print("已有")
            else:
                  picinf = urllib.request.urlopen("https:" + picpath).read()
                  infowrite(third,'wb',picinf)
                  print("完成：%s" % third)
      except:
            print("有问题")
            print(picname)
            
class TBTM():
      def __init__(self,weblink,ratenum):
            self._weblink,self._ratenum = weblink,ratenum
            self._head = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
            self._TaoBao , self._TianMao = [],[]
            self._BMre = [re.compile(r"(?<=\.).*(?=\.com)"),re.compile(r"(?<=id=)\d*(?=&|$)")]
            self._BMinfo = {"taobao":{'cookie':r"cookie\TaoBao.txt",\
                                     'ratepath':r"ratelink\TaoBao.txt",\
                                     'name':"淘宝"},\
                           "tmall":{'cookie':r"cookie\TianMao.txt",\
                                    'ratepath':r"ratelink\TianMao.txt",\
                                    'name':"天猫"}}
            self._rskuinfo = {'reskuf': r'\[.*?\]|[\/*?"<>→]',\
                             'repf': '',\
                             'reskus': r'([ ;]|^)(.*?[:])',\
                             'reps': '',\
                             'untext': "unknow"}
            self._BMDetails = [r"(?<=https://img).*?(?=\" align|\">)"]
            self._TBlist = [r"(?<=g_config = {).*?(?=};)",r" |\s",r"\'",r"(?<={|,)(\w+)(?=:)",r'(\+newDate)|(!true)',r'(location.protocol==="http:"?).+?(":)']
            self._TMlist = [r"(?<=TShop.Setup\().*?(?=\);)"]
            self._rid = self._BMre[1].findall(weblink)[0]
            self._linkname = self._BMre[0].search(self._weblink).group()
            self._zero = os.path.join(os.getcwd(),self._BMinfo[self._linkname]['name'])
            self._TBpage = urlink(self._weblink,self._head)

      #获取店铺信息
      def _BMlistinfo(self):
            if "taobao" in self._linkname:
                  tblist1 = "{%s}" % re.search(self._TBlist[0],self._TBpage,re.DOTALL).group()
                  tblist2 = re.sub(self._TBlist[1],"",tblist1)
                  tblist3 = re.sub(self._TBlist[2],"\"",tblist2)
                  tblist4 = re.sub(self._TBlist[3],r'"\1"',tblist3)
                  tblist5 = re.sub(self._TBlist[4],'""',tblist4)
                  tblist6 = re.sub(self._TBlist[5],"",tblist5)
                  return json.loads(tblist6)
            elif "tmall" in self._linkname:
                  tmlist1 = re.search(self._TMlist[0],self._TBpage,re.DOTALL).group()
                  return json.loads(tmlist1)
      #提取店铺信息
      def _shopinfo(self):
            if "taobao" in self._linkname:
                  TB = self._BMlistinfo()
                  return TB['shopName'],TB['idata']['item']['auctionImages'],TB['descUrl']
            elif "tmall" in self._linkname:
                  TM = self._BMlistinfo()
                  return urllib.parse.unquote(TM['itemDO']['sellerNickName']),TM['propertyPics']['default'],TM['api']['descUrl']

      #创建目录
      def  _crpath(self,name):
            path = os.path.join(self._zero,self._shopinfo()[0])
            if not(os.path.exists(path)):
                  os.makedirs(path)
            path = os.path.join(self._zero,self._shopinfo()[0],name)
            if not(os.path.exists(path)):
                  os.mkdir(path)
            return path
      
      #提取店铺sku信息
      def _ratesku(self,skuinf,reskuf,repf,reskus,reps,untext):
            if skuinf:
                  sku = re.sub(reskuf,repf,skuinf)
                  sku = re.sub(reskus,reps,sku)
            else:
                  sku = untext
            first = self._crpath("买家评论")
            firstsku = os.path.join(first,sku)
            if not(os.path.exists(firstsku)):
                  os.makedirs(firstsku)
            fifth = os.path.join(first,sku,str(len(os.listdir(firstsku))))
            os.makedirs(fifth)
            return fifth
      
      #淘宝评论
      def _TBrun(self,i,ratelink):
            #获取淘宝店铺评论信息
            rinfo = json.loads(urlink(ratelink.format(self._rid,str(i)),self._head)[5:-2])
            self._TBPrate(rinfo["comments"])

      #淘宝店铺评论处理
      def _TBPrate(self,comments):
            for item in comments:
                if int(item['rate']) != -1 and item['photos']:
                        fifth = self._ratesku(item['auction']['sku'],**self._rskuinfo)
                        #每一条淘宝评论文字
                        if item['append']:
                              content = item['content'] + "\n\n追评： " + item['append']['content']
                        else:
                              content = item['content'] + "\n\n"
                        infowrite(os.path.join(fifth,"content.txt"),'w',content)
                        #每一条淘宝评论的图片
                        for itemf in item['photos']:
                              BMratepic(itemf['url'],fifth)
                        #每一条淘宝评论的追评图片
                        if item['append'] and item['append']['photos']:
                              for items in item['append']['photos']:
                                    BMratepic(items['url'],fifth)
     
      #天猫评论
      def _TMrun(self,i,ratelink):
            #获取淘宝店铺评论信息                
            rinfo = json.loads('{%s}' % (urlink(ratelink.format(self._rid,str(i)),self._head)))
            self._TMPrate(rinfo['rateDetail']['rateList'])
            
      #天猫店铺评论处理             
      def _TMPrate(self,comments):
            for item in comments:
                if item['pics']:
                        fifth = self._ratesku(item['auctionSku'],**self._rskuinfo)
                        
                        if item['appendComment']:
                              content = item['rateContent'] + "\n\n追评： " + item['appendComment']['content']
                        else:
                              content = item['rateContent'] + "\n\n"
                        infowrite(os.path.join(fifth,"content.txt"),'w',content)
                        #每一条天猫评论的图片
                        for itemf in item['pics']:
                                    BMratepic(itemf,fifth)
                        #每一条淘宝评论的追评图片
                        if item['appendComment'] and item['appendComment']['pics']:
                              for items in item['appendComment']['pics']:
                                  BMratepic(items,fifth)

      #存放与处理获取评论资源信息
      def ratephoto(self):
            if "taobao" in self._linkname:
                  #获取淘宝店铺登录cookie
                  self._head['cookie'] = loginfo(os.path.join(os.getcwd(),self._BMinfo[self._linkname]['cookie']))
                  #获取淘宝店铺评论网址
                  ratelink = loginfo(os.path.join(os.getcwd(),self._BMinfo[self._linkname]['ratepath']))
                  rate = json.loads(urlink(ratelink.format(self._rid,str(1)),self._head)[5:-2])
                  if rate['comments']:
                        self._ratenum = (self._ratenum > rate['maxPage']) and rate['maxPage'] or self._ratenum
                        self._TaoBao = [threading.Thread(target=self._TBrun,args=(i,ratelink),name=str(i)) for i in range(1,int(self._ratenum)+1)]
                        for t in self._TaoBao:
                              t.start()
                              t.join()
                  else:
                        print("没有评论信息")                    
            elif "tmall" in self._linkname:
                  #获取淘宝店铺登录cookie
                  self._head['cookie'] = loginfo(os.path.join(os.getcwd(),self._BMinfo[self._linkname]['cookie']))
                  #获取淘宝店铺评论网址
                  ratelink = loginfo(os.path.join(os.getcwd(),self._BMinfo[self._linkname]['ratepath']))
                  rate = json.loads('{%s}' % (urlink(ratelink.format(self._rid,str(1)),self._head)))
                  if rate['rateDetail']['rateList']:
                        self._ratenum = (self._ratenum > rate['rateDetail']['paginator']['lastPage']) and rate['rateDetail']['paginator']['lastPage'] or self._ratenum
                        self._TianMao = [threading.Thread(target=self._TMrun,args=(i,ratelink),name=str(i))for i in range(1,int(self._ratenum)+1)]
                        for t in self._TianMao:
                             t.start()
                             t.join()
                  else:
                        print("没有评论信息")
                        
      #存放与获取详情图
      def _BMpic(self):
            Depic = re.findall(self._BMDetails[0],urlink("http:" + self._shopinfo()[2],self._head))
            return Depic
      def DownDepic(self):
            for i in self._BMpic():
                  BMratepic("//img" + i,self._crpath("详情图"))
                  time.sleep(1)
      def DownTepic(self):
            for i in self._shopinfo()[1]:
                  BMratepic(i,self._crpath("主图"))
                  time.sleep(1)

if __name__=="__main__":
      a = input("网址: ")
      b = int(input("评论页数: "))
      c = TBTM(a,b)
      while True:
            d = input("请输入需要的操作('1'-获取评论;'2'-获取主图;'3'-获取详情图;'q'-退出): ")
            if '1' == d:
                  c.ratephoto()
            if '2' == d:
                  c.DownTepic()
            if '3' == d:
                  c.DownDepic()
            if 'q' == d:
                  break
            
      
