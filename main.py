# 验证功能
# 登录 -> 扫码登录 : app扫码无效  白色背景√  黑色背景 ×
# 		  密码登录 : 成功
# 登录Cookie用于免验证码功能 √
#   检测京东商品库存,实现有货自动购入 √
#   获取商品库存 √
#   购入模拟 √
# 
# 预期功能:
#  模拟提交订单
#
"""
JD online shopping helper tool
-----------------------------------------------------

only support to login by QR code, 
username / password is not working now.

"""
import os

#python3 默认utf-8编码
# sys.setdefaultencoding('utf-8')

# get function name 调试用
# sys._getframe(paras)
# paras 可选参数 深度:depth 默认为0 即返回动态链头函数名
# 0 : xxx 含义不明

def main():
    pass

os.chdir(r'C:\Users\goldfish\PycharmProjects\python\JD_simulator')
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