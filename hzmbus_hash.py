from seleniumwire import webdriver
from seleniumwire.thirdparty.mitmproxy.net.http.encoding import encode
from seleniumwire.thirdparty.mitmproxy.net.http.encoding import decode
import zlib
import brotli
import base64
import acw_sc_v2
import os
import json
import requests
from pyvirtualdisplay import Display
import re

def split(delimiters, string, maxsplit=0):
    regex_pattern = '|'.join(map(re.escape, delimiters))
    return re.split(regex_pattern, string, maxsplit)
class HZMHash():
    def __init__(self, activate=False, url="https://i.hzmbus.com/webhtml/index.html", myJSURL=None, jsScript=None, disable_redirects=False):
        self.activated = activate
        self.browser = None
        if activate:
            self.activate_browser(url=url, myJSURL=myJSURL, jsScript=jsScript, disable_redirects=disable_redirects)
    def activate_browser(self, url="https://i.hzmbus.com/webhtml/index.html", myJsURL=None, jsScript=None, disable_redirects=False):
        stealthminjs = None
        with open('stealth.min.js', 'r') as f:
            stealthminjs = f.read()
        if self.browser != None:
            self.browser.quit()
        try:
            if os.name == "posix":
                display = Display(visible=0, size=(1024, 768))
                display.start()
            myRandomChromeUA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
            print("Your useragent is", myRandomChromeUA, ".")
            options = webdriver.ChromeOptions()
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("user-agent="+myRandomChromeUA)
            options.add_argument("--headless")
            if os.name == "posix":
                options.add_argument("--no-sandbox")
            self.browser = webdriver.Chrome(options=options)
            # 调用函数在页面加载前执行脚本
            self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': stealthminjs})
            self.browser.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': 'window.fakelocation=new Proxy(Object.create(window.location),{get:function(e,o,n){return"replace"===o||"reload"===o||"assign"===o?()=>void 0:window.location[o]},set:function(e,o,n,t){}}),window.donothing=()=>void 0,window.onbeforeunload=()=>"Redirect intercepted";Object.defineProperty(window, "fakelocation",{writable: false})'})
            if disable_redirects:
                def interceptor_js(request, response):
                    if request.path.endswith(('.js', '.html', '.htm', '.mht', '.mhtm', '.mhtml', '.xht', '.xhtm', '.xhtml', '.dht', '.dhtm', '.dhtml', '.htm', '.html')):
                        myResText = response.body
                        print("我捕获到了 js / HTML 请求。")
                        print("路径: ", request.path)
                        enc = response.headers.get('Content-Encoding', 'identity')
                        print("文件编码：", enc)
                        print("首5字节：", myResText[0:5])
                        myResText = decode(myResText, enc)
                        print("首5字节 （已解压缩）：", myResText[0:5])
                        # print(myResText)
                        myResText = myResText.replace(b"document.location", b"window.fakelocation")
                        myResText = myResText.replace(b"window.location", b"window.fakelocation")
                        # print(myResText)
                        myResText = encode(myResText, enc)
                        print("首5字节（已重新压缩）:", myResText[0:5])
                        response.body = myResText
                        del response.headers['Content-Length']
                        response.headers['Content-Length'] = str(len(response.body))
                    print("=====响应=====")
                    print(response)
                    print(response.headers)
                    print("首5字节：", response.body[0:5])
                self.browser.response_interceptor = interceptor_js
        except Exception as e:
            print(e)
            print("失败")
        self.browser.get(url)
        print("The site is loaded.")
        myJS = None
        jsURL = None
        if jsScript != None:
            myJS = jsScript
        else:
            if myJsURL != None:
                jsURL = myJsURL
            else:
                jsURL = self.browser.execute_script("return Array.prototype.slice.call(document.getElementsByTagName(\"script\")).reverse()[0].src;")
            headers = {
                "accept": "application/json, text/plain, */*",
                "accept-language": "zh-CN,zh;q=0.9",
                "authorization": "",
                "content-type": "application/json;charset=UTF-8",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "Referer": "https://i.hzmbus.com/webhtml/register",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
            }
            jsScrape = requests.Session()
            acw = jsScrape.get("https://i.hzmbus.com/webhtml", headers=headers)
            if str(acw.content, encoding="UTF-8").startswith("<html><script>"):
                arg1 = acw_sc_v2.getArg1FromHTML(str(acw.content, encoding="UTF-8"))
                print("arg1="+arg1)
                ACWSCV2 = acw_sc_v2.getAcwScV2(arg1)
                print("acw_sc__v2="+ACWSCV2)
                acw = requests.cookies.RequestsCookieJar()
                acw.set("acw_sc__v2", ACWSCV2)
                jsScrape.cookies.update(acw)
            headers["accept"] = "text/javascript, text/plain, */*"
            myJS = str(jsScrape.get(jsURL, headers=headers).content, encoding="UTF-8")
            myJS = myJS.split("var e=t.data.sessionId")[1]
            myJS = split(["}else t.data={", "}return Q(t)}"], myJS)[0]
            myJS+="return t.data;}"
            myJS="window.setTokenWeb = function (j){let t={\"data\":JSON.parse(j)};var e=t.data.sessionId"+myJS
            print(myJS)
        self.browser.execute_script(myJS)
        self.activated = True
    def msk6(self, data):
        if self.activated and self.browser != None:
            return self.browser.execute_script("return window.msk6(" + json.dumps(data, ensure_ascii=False) + ");")
    def cs(self, data):
        if self.activated and self.browser != None:
            return self.browser.execute_script("return window.cs(" + json.dumps(data, ensure_ascii=False) + ");")
    def ft(self, data):
        if self.activated and self.browser != None:
            return self.browser.execute_script("return window.ft(" + json.dumps(data, ensure_ascii=False) + ");")
    def set_token_web(self, data):
        if self.activated and self.browser != None:
            return self.browser.execute_script("return window.setTokenWeb('" + json.dumps(data, ensure_ascii=False) + "');")
        return data