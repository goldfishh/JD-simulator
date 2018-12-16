账密登录已失效
20个星的话试一试继续开发这个项目?
> A [JD.COM(京东) market](https://www.jd.com/) simulator tool based on Python 3  

[![Python](https://img.shields.io/badge/Python-3.6%2B-red.svg)](https://www.python.org)

## Environment
- Python 3.6.1
- Third-party library:  
  - Python HTTP [Requests](https://github.com/requests/requests) for Humans
  - [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
  - [lxml](http://lxml.de/)
  - [pickle](https://docs.python.org/3/library/pickle.html)

## Setup
1. Downloading zip file
2. unzip
3. cd JD-simulator*
2. pip install -r requirements.txt    

## Run
1. editing main.main() function
2. python main.py

## How to simulate  
1. Searching for helping   
   - `python main.py -h`    
   - `python main.py --help` 
2. Logging in
   - Scanning  
     `python main.py -t 1`  (注: 二维码背景需为白色!)
   - Normal means  
     `python -t 2 -u yourusername -p yourpassword`    
3. Other  
   - editting main.main()  
   
## How to edit the main.main()  
1. 购物车模拟
``` 
def main(options, cookies):  
    # build a object for purchasing.  
    pc = Purchase(options, cookies)  
    pc.cart_detail()  
    pass  
    
python main.py ......
```
2. 

------  
## 目前已实现功能
#大部分功能已有思路, 但是搬砖太累,接下来可能会只更新自己用到的功能  
> 2.9 添加Plus专享价格信息  
> 2.9 全球购、普通商品隐藏bug发现  
> 2.9   
### class Login
> △验证码扫码登录 2018.2.6  
> △密码登录 2018.2.7 #bug : 无法无验证码登录   
>   保存cookies 2018.2.6  
> ※验证cookies是否过期 2018.2.8  
### class Purchase  
>   查看商品库存 2018.2.6  
>   查看商品价格 2018.2.6  
>   添加商品进入购物车 2018.2.7  
>   显示购物车信息 2018.2.6  
> ※修改购物车功能 2018.2.8  
>>  修改数量 + -   
>>  修改选中 + -  
>>※选择优惠  
>>  删除商品  

>   代码模块化 2018.2.7  
## 程序入口  
## API解析 类 函数  
## 计划实现功能  
> 提交订单  
>>  优惠券选择  
>>  地址选择  
>>  支付密码、验证码输入  
>>  
>   模拟 预售 抢购 等商品的定时购买  
>   更友好的助手函数  
> 
>   模拟获取优惠券功能   
