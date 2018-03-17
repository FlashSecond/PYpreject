import urllib.request
import re

class down():
    def __inti__(self,url):
        self.url = url
        self.head = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

    def urlink(self):
        #请求处理
        req = urllib.request.Request(self.url,self.head)
        whost = req.host
        #链接网站
        response = urllib.request.urlopen(req)
        #获取charset
        code = response.getheaders()[1][1].split('=')[1]
        #读取链接数据与解码utf-8
        return response.read().decode(code,"ignore")
    
    def _wma(self,p,pp):
        downdata = self.urlink()
        return re.findall(p,downdata),re.findall(pp,downdata)

    def download(self,path):
        one,two = self._wma()
        for f,s in zip(one,two):
            wdata = urllib.request.urlopen(r"https://%s/%s" %(whost,f)).read()
            with open(path+s,mode='wb') as f:
                f.write(wdata)




