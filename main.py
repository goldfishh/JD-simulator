# -*- coding: utf-8 -*-



# 验证功能
# 登录 -> 扫码登录 : app扫码无效
# 		  密码登录 : 成功
# 登录Cookie用于免验证码功能 √
# 
# 预期功能:
#   检测京东商品库存,实现有货自动购入
#   获取商品库存
#   购入模拟
"""
JD online shopping helper tool
-----------------------------------------------------

only support to login by QR code, 
username / password is not working now.

"""


from bs4 import BeautifulSoup
import requests, requests.utils, pickle
import requests.packages.urllib3

#取消SSL验证
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import os
import time
import json

import sys
from importlib import reload
reload(sys)
#python3 默认utf-8编码
# sys.setdefaultencoding('utf-8')

# get function name 调试用
# sys._getframe(paras)
# paras 可选参数 深度:depth 默认为0 即返回动态链头函数名
# 0 : xxx 含义不明
FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name



class JDWrapper():
    '''
    This class used to simulate JD activity
    '''
    
    def __init__(self, options):
        # cookie info
        # self.trackid = ''
        # self.uuid = ''
        # self.eid = ''
        # self.fp = ''

        self.username = options.username
        self.password = options.password

        self.area = options.area
        self.goodid = options.good
        self.count = options.count
        self.interval = 0

        self.flushflag = options.flush
        self.submitflag = options.submit

        # init url related
        # login html:
        self.home = 'https://passport.jd.com/new/login.aspx'
        # try to post
        self.login = 'https://passport.jd.com/uc/loginService'
        # tuling testing:
        self.imag = 'http://authcode.jd.com/verify/image'
        # whether or not to verify you
        self.auth = 'https://passport.jd.com/uc/showAuthCode'
        
        self.sess = requests.Session()

        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'ContentType': 'text/html; charset=utf-8',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Connection' : 'keep-alive',
            'Referer': 'https://www.jd.com/',
        }
        
        self.cookies = {

        }
        
    @staticmethod
    def print_json(resp_text):
        '''
        format the response content
        '''
        if (resp_text[0] == '('):
            resp_text = resp_text[1:-1]
        
        for k,v in json.loads(resp_text).items():
            print (u'%s : %s' % (k, v))

    @staticmethod
    def response_status(resp):
        if (resp.status_code != requests.codes.OK):
            print ('Status: %u, Url: %s' % (resp.status_code, resp.url))
            return False
        return True


    #保证成功
    def get_auth_code(self, url):
        qr_url = 'http:' + url
        # image save path
        image_file = os.path.join(os.getcwd(), 'auth.jpg')                        
        # get auth code
        while True:
            try:
                # 必须有 referer! 否则返回主页html
                r = self.sess.get(qr_url, headers=self.headers,timeout = 1.5)
                break
            except:
                print ('获取验证码失败,休眠一秒')
                time.sleep(1)       

        with open(image_file, 'wb') as f:
            f.write(r.content)
        
        os.system('start ' + image_file)
        return input('Auth Code: ')

    # def _login_once(self, login_data):
    #     # url parameter
    #     payload = {
    #         'r': random.random(),
    #         'uuid' : login_data['uuid'],
    #         'version' : 2015,
    #     }
        
    #     resp = self.sess.post(self.login, data=login_data, params=payload)
    #     if self.response_status(resp):
    #         js = json.loads(resp.text[1:-1])
    #         #self.print_json(resp.text)
            
    #         if not js.get('success') :
    #             print  (js.get('emptyAuthcode'))
    #             return False
    #         else:
    #             return True

    #     return False
  

    


    def loginbypassword(self):
        # 无cookies文件 -> 验证码登录
        # 有cookies -> 判断是否失效 
        #                   失效  ->  重新登陆
        #                   有效  ->  直接使用
        # 成功登录即保存cookies文件
        html = self.sess.get(self.home, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        auth_code = ''
        self.uuid = soup.select('#uuid')[0].get('value')
        if (self.need_auth_code()):
            print('需要验证码。。。')
            auth_code_url = soup.select('#JD_Verification1')[0].get('src2')
            auth_code = self.get_auth_code(auth_code_url)
        
        # eid = soup.select('#eid')[0].get('value')
        # fp = soup.select('input[name="fp"]')[0].get('value')  # session id
        eid = ""
        fp = ""
        _t = soup.select('input[name="_t"]')[0].get('value')  # token
        login_type = soup.select('input[name="loginType"]')[0].get('value')
        pub_key = soup.select('input[name="pubKey"]')[0].get('value')
        sa_token = soup.select('input[name="sa_token"]')[0].get('value')

        data = {
            'uuid': self.uuid,
            'eid': eid,
            'fp': fp,
            '_t': _t,
            'loginType': login_type,
            'loginname': self.username,
            'nloginpwd': self.password,
            'chkRememberMe': True,
            'authcode': auth_code,
            'pubKey': pub_key,
            'sa_token': sa_token,
            # 'authCode': auth_code,
        }

        headers = {
            'Referer': 'https://passport.jd.com/uc/login?ltype=logout',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'X-Requested-With': 'XMLHttpRequest'
        }
        content = self.sess.post(self.login, data=data, headers=headers).text
        result = json.loads(content[1: -1])        
        if result.get('success'):
            print('登录成功')
            with open("cookie","wb") as f:
                pickle.dump(self.sess.cookies,f)
                print("保存cookies文件成功!")
            return True
        else:
            print('登录失败')      
            print(result)     	
            return False
    # dalian address code : 8_573_5909_52451



def main(options):
    # 
    jd = JDWrapper(options)
    # 如果旧有cookie文件过期,并且未成功登录 则返回
    if(not jd.checkLogin()):
        if(options.logintype == 2):
            if(not jd.loginbypassword()):
                print ('账密登录异常!')
                return None
            # exit(1)
        elif(options.logintyoe == 1):
            if(not jd.login_by_QR()):
                print ('账密登录异常!')
                return None
                
    # 未成功购买 并且刷新flag为false 则返回
    while (not jd.buy() and options.flush):
        time.sleep(options.wait / 1000.0)

    print("结束")

from Helper import help_message
from login import Login
from purchase import Purchase
if __name__ == '__main__':
    parser = help_message()
    options = parser.parse_args()
    print (options)
    # 提高options鲁棒
    if (options.logintype == 2 and \
            options.password == '' or options.username == ''):
        print ('用户名密码必须不为空!')
        exit(0)
    if(options.logintype != 1 and options.logintype != 2):
        options.logintype = 1

    jd = Login(options)
    cookies = jd.login()



    main(options)