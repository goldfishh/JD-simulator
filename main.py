"""
-----------------------
JD.COM simulation tool.
            2018.2.16
-----------------------
"""
import os

from Helper import help_message
from login import Login
from purchase import Purchase

def main(options, cookies):
    # build a object for purchasing.
    pc = Purchase(options, cookies)
    # print (pc.good_stock())
    # print (pc.good_price())
    # pc.good_detail()
    pc.cart_detail()
    pass

# os.chdir(r'C:\Users\goldfish\PycharmProjects\python\JD_simulator')

if __name__ == '__main__':
    parser = help_message()
    options = parser.parse_args()
    print (options)
    # 提高options鲁棒
    if (options.logintype == 2 and \
            (options.password == '' or options.username == '')):
        print ('用户名密码必须不为空!')
        exit(0)
    if(options.logintype != 1 and options.logintype != 2):
        options.logintype = 1

    jd = Login(options)
    cookies = jd.login()

    main(options, cookies)