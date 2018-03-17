import requests
import bs4

class down():
    def __inti__(self,url):
        self.url = url
        self.head = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}

    def urlink(self):
        #请求处理
        req = requests.get(self.url,self.head)
        #获取charset
        code = req.encoding
        #读取链接数据与解码utf-8
        return req.text
    
    def _wma(self,p,pp):
        downdata = self.urlink()
        return re.findall(p,downdata),re.findall(pp,downdata)

    def download(self,path):
        one,two = self._wma()
        for f,s in zip(one,two):
            wdata = requests.get(r"https://%s/%s" %(whost,f)).content
            with open(path+s,mode='wb') as f:
                f.write(wdata)




