# 获取cookie
import time
import json
import requests
import random
from lxml import etree
import os
import pickle
from bs4 import BeautifulSoup

#取消SSL验证
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

s = requests.Session()

FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

class Login:
    def __init__(self, options):
        # to login by password
        self.logintype = options.logintype
        if(self.logintype == 2):
            self.username = options.username
            self.password = options.password
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'Referer': 'https://www.jd.com/'
        }

    '''
        only used by type 2
    '''
    def need_auth_code(self):
        # check if need auth code
        authurl = 'https://passport.jd.com/uc/showAuthCode'
        data = {
            'loginName': self.username,
        }
        params = {
            'r': random.random(),
            'version': 2015,
        }
        try:
            resp = s.post(authurl, data=data, params=params)
            if resp.status_code == 200: 
                js = json.loads(resp.text[1:-1])
                return js['verifycode']
        except Exception as e:
            print('ERROR{} > need_auth_code():'.format(time.ctime()) + str(e))
            time.sleep(1)
            self.need_auth_code()
    '''
        only used by type 2
    '''            
    def get_auth_img(self, url):
        auth_code_url = 'http:' + url
        auth_img = s.get(auth_code_url, headers=self.headers)
        with open('auth.jpg', 'wb') as f:
            f.write(auth_img.content)
        os.system("start auth.jpg")
        '''
            注意有效期
        '''
        code = input('请输入验证码：  ')
        return code
    '''
        only used by type 2
    '''
    def get_login_data(self):
        url = 'https://passport.jd.com/new/login.aspx'
        html = s.get(url, headers=self.headers).content
        soup = BeautifulSoup(html, 'lxml')
        # display = soup.select('#o-authcode')[0].get('style')
        auth_code = ''
        if(self.need_auth_code()):
            print('{} > 需要验证码...'.format(time.ctime()))
            auth_code_url = soup.select('#JD_Verification1')[0].get('src2')
            auth_code = self.get_auth_img(auth_code_url)

        uuid = soup.select('#uuid')[0].get('value')
        # eid = soup.select('#eid')[0].get('value')
        # fp = soup.select('input[name="fp"]')[0].get('value')  # session id
        eid = ""
        fp = ""
        _t = soup.select('input[name="_t"]')[0].get('value')  # token
        login_type = soup.select('input[name="loginType"]')[0].get('value')
        pub_key = soup.select('input[name="pubKey"]')[0].get('value')
        sa_token = soup.select('input[name="sa_token"]')[0].get('value')

        data = {
            'uuid': uuid,
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
            # 'authCode': auth_code
        }
        return data

    def login(self):
        if(self.check_cookies()):
            return s.cookies

        if(self.logintype == 1):
            if(self.loginbyQR()):
                print('{} > 登录成功！'.format(time.ctime()))
                self.save_cookies(s.cookies)
                return s.cookies
            else:
                print('{} > 登录失败！'.format(time.ctime()))
                while True:
                    choice = input("是否继续 y/n")
                    if(choice == 'y' or choice == 'Y'):
                        return self.login()
                    elif(choice == 'n' or choice == 'N'):
                        return None
                    else:
                        pass

        elif(self.logintype == 2):
            if(self.loginbyPWD()):
                print('{} > 登录成功！'.format(time.ctime()))
                self.save_cookies(s.cookies)
                return s.cookies
            else:
                print('{} > 登录失败！'.format(time.ctime()))
                while True:
                    choice = input("是否继续 y/n")
                    if(choice == 'y' or choice == 'Y'):
                        return self.login()
                    elif(choice == 'n' or choice == 'N'):
                        return None
                    else:
                        pass

    '''
        only used by type 2
    '''
    def loginbyPWD(self):
        """
        登录
        :return:
        """
        url = 'https://passport.jd.com/uc/loginService'
        data = self.get_login_data()
        headers = {
            'Referer': 'https://passport.jd.com/uc/login?ltype=logout',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'X-Requested-With': 'XMLHttpRequest'
        }
        try:
            r = s.post(url, data=data, headers=headers)
            content = r.text
            if 'success' in content:
                return True
            else:
                return False
        except Exception as e:
            print("ERROR{} > loginbyPWD():".format(time.ctime()) + str(e))
            return False
    '''
        only used by type 1
    '''
    def loginbyQR(self):
        # jd login by QR code
        try:
            print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print (u'{0} > 请打开京东手机客户端，准备扫码登陆:'.format(time.ctime()))

            urls = (
                'https://passport.jd.com/new/login.aspx',
                'https://qr.m.jd.com/show',
                'https://qr.m.jd.com/check',
                'https://passport.jd.com/uc/qrCodeTicketValidation'
            )

            # step 1: open login page
            resp = self.sess.get(
                urls[0], 
                headers = self.headers
            )
            if resp.status_code != requests.codes.OK:
                print (u'获取登录页失败: %u' % resp.status_code)
                return False

            ## save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v
            

            # step 2: get QR image
            resp = self.sess.get(
                urls[1], 
                headers = self.headers,
                cookies = self.cookies,
                params = {
                    'appid': 133,
                    'size': 147,
                    't': int(time.time() * 1000)
                }
            )
            if resp.status_code != requests.codes.OK:
                print (u'获取二维码失败: %u' % resp.status_code)
                return False

            ## save cookies
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            ## save QR code
            image_file = 'qr.png'
            with open (image_file, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=1024):
                    f.write(chunk)
            
            ## scan QR code with phone
            if os.name == "nt": 
                # for windows
                os.system('start ' + image_file)
            else:
                if os.uname()[0] == "Linux":
                    # for linux platform
                    os.system("eog " + image_file)
                else:
                    # for Mac platform
                    os.system("open " + image_file)

            # step 3: check scan result
            ## mush have
            self.headers['Host'] = 'qr.m.jd.com' 
            self.headers['Referer'] = 'https://passport.jd.com/new/login.aspx'

            # check if QR code scanned
            qr_ticket = None
            retry_times = 100
            while retry_times:
                retry_times -= 1
                resp = self.sess.get(
                    urls[2],
                    headers = self.headers,
                    cookies = self.cookies,
                    params = {
                        'callback': 'jQuery%u' % random.randint(100000, 999999),
                        'appid': 133,
                        'token': self.cookies['wlfstk_smdl'],
                        '_': int(time.time() * 1000)
                    }
                )

                if resp.status_code != requests.codes.OK:
                    continue

                n1 = resp.text.find('(')
                n2 = resp.text.find(')')
                rs = json.loads(resp.text[n1+1:n2])

                if rs['code'] == 200:
                    print (u'{} : {}'.format(rs['code'], rs['ticket']))
                    qr_ticket = rs['ticket']
                    break
                else:
                    print (u'{} : {}'.format(rs['code'], rs['msg']))
                    time.sleep(3)
            
            if not qr_ticket:
                print (u'二维码登陆失败')
                return False
            
            # step 4: validate scan result
            ## must have
            self.headers['Host'] = 'passport.jd.com'
            self.headers['Referer'] = 'https://passport.jd.com/uc/login?ltype=logout'
            resp = self.sess.get(
                urls[3], 
                headers = self.headers,
                cookies = self.cookies,
                params = {'t' : qr_ticket },
            )
            if resp.status_code != requests.codes.OK:
                print (u'二维码登陆校验失败: %u' % resp.status_code)
                return False
            
            ## 京东有时候会认为当前登录有危险，需要手动验证
            ## url: https://safe.jd.com/dangerousVerify/index.action?username=...
            res = json.loads(resp.text)
            if not resp.headers.get('P3P'):
                if res.has_key('url'):
                    print (u'需要手动安全验证: {0}'.format(res['url']))
                    return False
                else:
                    print_json(res)
                    print (u'登陆失败!!')
                    return False
            
            ## login succeed
            self.headers['P3P'] = resp.headers.get('P3P')
            for k, v in resp.cookies.items():
                self.cookies[k] = v

            with open('cookie', 'wb') as f:
                pickle.dump(self.cookies, f)

            print (u'登陆成功')
            return True
        
        except Exception as e:
            print ('Exp:', e)
            raise

        return False

            
    def save_cookies(self,cookies):
        with open("cookies","wb") as f:
            pickle.dump(cookies, f)
            print("{} > 保存cookies文件成功!".format(time.ctime()))

    def check_cookies(self):
        checkUrl = 'https://cart.jd.com/cart.action'
        # debugging 如果有
        try:
            print (u'{0} > 检查cookies是否过期...'.format(time.ctime()))
            with open('cookies', 'rb') as f:
                cookies = pickle.load(f)

            s.cookies = cookies
            resp = s.get(checkUrl,headers=self.headers)
            selector = etree.HTML(resp.text)
            feature = selector.xpath("//li[@id='ttbar-login']/a[@class='nickname']")
            if not feature:
                print('{} > 登录过期，将重新登录！'.format(time.ctime()))
                return False
            else:
                print('{} > cookies未失效！'.format(time.ctime()))
                print("{} > {}, 欢迎登录!".format(time.ctime(), feature[0].text.strip()))
                return True
        # 无cookies 文件
        # get error
        # etree 解析错误
        except Exception as e:
            print('ERROR{} > check_cookies():'.format(time.ctime()) + str(e))
            return False
            
# username = input('请输入京东账号：')
# password = input('请输入京东密码：')
# jd = JD(username, password)
# result = jd.login()
