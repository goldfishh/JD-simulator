import requests
import time
import json
import sys
from bs4 import BeautifulSoup

s = requests.session()

FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

def tag_val(tag, key=''):
    '''
    return html tag attribute @key
    if @key is empty, return tag content
    '''
    if tag is None:
        return ''
    elif key:
        txt = tag.get(key)
        return txt.strip(' \t\r\n') if txt else ''
    else:
        txt = tag.text
        return txt.strip(' \t\r\n') if txt else ''

def tags_val(tag, key='', index=0):
    '''
    return html tag list attribute @key @index
    if @key is empty, return tag content
    '''
    if len(tag) == 0 or len(tag) <= index:
        return ''
    elif key:
        txt = tag[index].get(key)
        return txt.strip(' \t\r\n') if txt else ''
    else:
        txt = tag[index].text
        return txt.strip(' \t\r\n') if txt else ''

class Purchase:
    def __init__(self,options,cookies):
        s.cookies = cookies

        self.areaid = options.area
        self.goodid = str(options.good)
        self.count = options.count
        self.interval = options.interval

        self.flushflag = options.flush
        self.submitflag = options.submit

        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
            'ContentType': 'text/html; charset=utf-8',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Connection' : 'keep-alive',
            'Referer': 'https://www.jd.com/',
        }

    def good_stock(self):
        '''
        33 : on sale, 
        34 : out of stock
        '''
        # http://ss.jd.com/ss/areaStockState/mget?app=cart_pc&ch=1&skuNum=3180350,1&area=1,72,2799,0
        #   response: {"3180350":{"a":"34","b":"1","c":"-1"}}
        #stock_url = 'http://ss.jd.com/ss/areaStockState/mget'

        # http://c0.3.cn/stocks?callback=jQuery2289454&type=getstocks&skuIds=3133811&area=1_72_2799_0&_=1490694504044
        #   jQuery2289454({"3133811":{"StockState":33,"freshEdi":null,"skuState":1,"PopType":0,"sidDely":"40","channel":1,"StockStateName":"现货","rid":null,"rfg":0,"ArrivalDate":"","IsPurchase":true,"rn":-1}})
        # jsonp or json both work
        stock_url = 'https://c0.3.cn/stocks'
        # area_id = "8_573_5909_52451"
        area_id = "7_538_543_39636"
        data = {
            'type' : 'getstocks',
            'skuIds' : str(self.goodid),
            'area' : self.areaid, # area change as needed
        }

        # get stock data
        # example:
        # {'920115': {'ArrivalDate': '',
        #   'IsPurchase': False,
        #   'PopType': 0,
        #   'StockState': 33,
        #   'StockStateName': '现货',
        #   'ac': '-1',
        #   'ad': '-1',
        #   'ae': '-1',
        #   'af': '-1',
        #   'channel': 1,
        #   'freshEdi': None,
        #   'rfg': 0,
        #   'rid': None,
        #   'rn': 2,
        #   'sidDely': '0',
        #   'skuState': 1}}
        try:
            resp = s.get(stock_url, params=data)
            if(resp.status_code != 200):
                raise ValueError
        except:
            print ('获取商品库存失败')
            return (0, '')

        # return json
        resp.encoding = 'gbk'  # 解决名字乱码
        stock_info = json.loads(resp.text)
        stock_stat = int(stock_info[self.goodid]['StockState'])
        stock_stat_name = stock_info[self.goodid]['StockStateName']

        # 33 : on sale, 34 : out of stock, 36: presell
        # example: (33, '现货')
        return (stock_stat, stock_stat_name)

    def good_price(self):
        # get good price
        url = 'http://p.3.cn/prices/mgets'
        payload = {
            'type'   : 1,
            'pduid'  : int(time.time() * 1000),
            'skuIds' : 'J_' + self.goodid,
        }

        price = '?'
        try:
            resp = s.get(url, params=payload)
            #example:
            #resp.text:
            #'[{"op":"79.00","m":"102.00","id":"J_920115","p":"69.00"}]\n'
            resp_txt = resp.text.strip() # 去尾部\n
            #example:
            #resp.txt:
            #'[{"op":"79.00","m":"102.00","id":"J_920115","p":"69.00"}]'
            js = json.loads(resp_txt[1:-1])
            #example:
            #js:
            #{'id': 'J_920115', 'm': '102.00', 'op': '79.00', 'p': '69.00'}
            price = js.get('p')

        except Exception as e:
            print(str(e))

        return price

    def good_detail(self):
        # return good detail
        good_data = {
            'id' : self.goodid,
            'name' : '',
            'link' : '',
            'price' : '',
            'stock' : 0,
            'stockName': '',
        }

        try:
            # shop page
            stock_link = 'https://item.jd.com/{}.html'.format(self.goodid)
            resp = s.get(stock_link,headers = self.headers)

            # good page
            soup = BeautifulSoup(resp.text, "html.parser")

            # good name
            # 'div#name h1' 待确认有效性
            tags = soup.select('div#name h1')
            if not tags:
                tags = soup.select('div.sku-name')

            good_data['name'] = tags[0].text.strip()

            # cart link 购物车链接
            tags = soup.select('a#InitCartUrl')

            link = tags[0].attrs['href']
            if (link[:2] == '//'):
            	link = 'http:' + link

            good_data['link'] = link

        except Exception as e:
            print ('Exp {0} : {1}'.format(FuncName(), e))

        # good price
        good_data['price'] = self.good_price()

        # good stock
        good_data['stock'], good_data['stockName'] = self.good_stock()
        #stock_str = u'有货' if good_data['stock'] == 33 else u'无货'

        print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print (u'{0} > 商品详情'.format(time.ctime()))
        print (u'编号：{0}'.format(good_data['id']))
        print (u'库存：{0}'.format(good_data['stockName']))
        print (u'价格：{0}'.format(good_data['price']))
        print (u'名称：{0}'.format(good_data['name']))

        return good_data



    def tocart(self):
        # stock detail
        good_data = self.good_detail()
        '''
        33 : on sale, 
        34 : out of stock
        '''

        tocart_url = "http://cart.jd.com/gate.action"
        params = {
            "pid" : self.goodid,
            "pcount" : self.count,
            "ptype" : '1',
        }

        # 未获取到购物车链接或无货状态
        if (good_data['stock'] != 33 or tocart_url == ''):
            print("tocart(): 运行中断")
            return False

        try:
            # add to cart
            headers = {
                "Host": "cart.jd.com",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Referer": "https://item.jd.com/{}.html".format(self.goodid),
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
            }
            resp = s.get(tocart_url, headers = headers,params=params)
            soup = BeautifulSoup(resp.text, "html.parser")

            # tag if add to cart succeed
            # example:
            # tag = [<h3 class="ftx-02">商品已成功加入购物车！</h3>]
            tag = soup.select('h3.ftx-02')
            if not tag:
                tag = soup.select('div.p-name a')

            if not tag:
                print ('添加到购物车失败')
                return False

            print ('{0} > 购买详情'.format(time.ctime()))
            print ('链接：{0}'.format(headers["Referer"]))
            print ('结果：{0}'.format(tag[0].text))

            # change count after add to shopping cart
            #self.buy_good_count(options.good, options.count)

        except Exception as e:
            print ('Exp {0} : {1}'.format(FuncName(), e))
        else:
            # self.cart_detail()
            return self.order_info(self.submitflag)

        return False


    def cart_detail(self):
        # list all goods detail in cart
        cart_url = 'https://cart.jd.com/cart.action'
        th = '序号  选中  数量  单价    优惠  商品名'
        sformat = '{:<6}{:<6}{:<6}{:<8}{:<6}{:<}'

        try:
            resp = s.get(cart_url, headers = self.headers)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, "html.parser")

            print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
            print ('{} > 购物车明细'.format(time.ctime()))
            # print (sformat.format('序号','选中','数量','单价','优惠','商品名'))
            print(th)
            start = 0
            items = soup.select('div.item-form')
            for item in items:
                start += 1
                chunk = item.select('div.cart-checkbox input[checked="checked"]')
                select = '√' if chunk else '○'
                count = item.select('div.quantity-form input[value]')[0].get("value")
                price = item.select('div.p-price strong')[0].text.strip()
                promos  = item.select('div.promotion-cont ul li input')
                # promos_list = []
                # for p in promos:
                #     promos_list.append(p.get("title").strip())
                select_promo = '√' if promos else '×'
                name = item.select('div.p-name a')[0].text.strip()
                #: ￥字符解析出错, 输出忽略￥
                print (sformat.format(str(start), str(select), str(count), str(price), str(select_promo), str(name), chr(12288)))

            t_count = soup.select('div.amount-sum  em')[0].text.strip()
            t_value = soup.select('span.sumPrice em')[0].text.strip()
            print ('总件数: {0}'.format(t_count))
            print ('总价: {0}'.format(t_value[1:]))

        except Exception as e:
            print ('Exp {0} : {1}'.format(FuncName(), e))

    def cart_panel(self):
        修改数量 + -
        修改选中 + -
        选择优惠
        删除商品

    def change_cart_detail(self):
        url = 'http://cart.jd.com/changeNum.action'

        payload = {
            'venderId': '8888',
            'pid': self.goodid,
            'pcount': self.count,
            'ptype': '1',
            'targetId': '0',
            'promoID':'0',
            'outSkus': '',
            'random': random.random(),
            'locationId':self.areaid,  # need changed to your area location id
        }

        try:
            rs = s.post(url, params = payload, headers = self.headers)
            if rs.status_code == 200:
                js = json.loads(rs.text)
                if js.get('pcount'):
                    print (u'数量：%s @ %s' % (js['pcount'], js['pid']))
                    return True
            else:
                print (u'购买 %d 失败' % count)

        except Exception as e:
            print ('Exp {0} : {1}'.format(FuncName(), e))

        return False

    def order_info(self, submit=False):
        # get order info detail, and submit order
        print ('+++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print (u'{0} > 订单详情'.format(time.ctime()))

        try:
            order_url = 'http://trade.jd.com/shopping/order/getOrderInfo.action'
            payload = {
                'rid' : str(int(time.time() * 1000)),
            }

            # get preorder page
            rs = s.get(order_url, params=payload)
            soup = BeautifulSoup(rs.text, "html.parser")

            # order summary
            payment = tag_val(soup.find(id='sumPayPriceId'))
            detail = soup.find(class_='fc-consignee-info')

            if detail:
                snd_usr = tag_val(detail.find(id='sendMobile'))
                snd_add = tag_val(detail.find(id='sendAddr'))

                print (u'应付款：{0}'.format(payment))
                print (snd_usr)
                print (snd_add)

            # just test, not real order
            if not submit:
                return False

            # order info
            payload = {
                'overseaPurchaseCookies': '',
                'submitOrderParam.btSupport': '1',
                'submitOrderParam.ignorePriceChange': '0',
                'submitOrderParam.sopNotPutInvoice': 'false',
                # 'submitOrderParam.trackID': self.trackid,
                # 'submitOrderParam.eid': self.eid,
                # 'submitOrderParam.fp': self.fp,
            }

            order_url = 'http://trade.jd.com/shopping/order/submitOrder.action'
            rp = s.post(order_url, params=payload,headers = self.headers)

            if rp.status_code == 200:
                js = json.loads(rp.text)
                if js['success'] == True:
                    print (u'下单成功！订单号：{0}'.format(js['orderId']))
                    print (u'请前往东京官方商城付款')
                    return True
                else:
                    print (u'下单失败！<{0}: {1}>'.format(js['resultCode'], js['message']))
                    if js['resultCode'] == '60017':
                        # 60017: 您多次提交过快，请稍后再试
                        time.sleep(1)
            else:
                print (u'请求失败. StatusCode:', rp.status_code)

        except Exception as e:
            print ('Exp {0} : {1}'.format(FuncName(), e))

        return False

    def main(self):
        pass