import requests
import time
import json
import random
import re
import sys
from bs4 import BeautifulSoup
from lxml import etree

#取消SSL验证
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

s = requests.session()

FuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name

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

        self.promos_dict = {

        }
    def good_stock(self):
        # get good stock
        '''
        33 : on sale, 
        34 : out of stock
        '''
        stock_url = 'https://c0.3.cn/stocks'
        data = {
            'type' : 'getstocks',
            'skuIds' : str(self.goodid),
            'area' : self.areaid,
        }
        try:
            resp = s.get(stock_url, params=data, headers = self.headers)
            # return json:
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
            resp.encoding = 'gbk'  # 解决名字乱码
            stock_info = json.loads(resp.text)
            stock_stat = int(stock_info[self.goodid]['StockState'])
            stock_stat_name = stock_info[self.goodid]['StockStateName']

            # 33 : on sale, 34 : out of stock, 36: presell
            # example: (33, '现货')
            print('{} > 获取库存信息成功!'.format(time.ctime()))
            return (stock_stat, stock_stat_name)
        except Exception as e:
            print('ERROR{} > good_stock():'.format(time.ctime()) + str(e))
            return (0, 'Unknown')

    def good_price(self):
        # get good price
        price_url = 'http://p.3.cn/prices/mgets'
        params = {
            'type'   : 1,
            'pduid'  : int(time.time() * 1000),
            'skuIds' : 'J_' + self.goodid,
        }

        price = '?'
        try:
            resp = s.get(price_url, params=params, headers = self.headers)
            #example:
            #resp.text:
            #'[{"op":"79.00","m":"102.00","id":"J_920115","p":"69.00"}]\n'
            resp_txt = resp.text.strip() # 去尾部\n
            js = json.loads(resp_txt[1:-1]) # 去'['、']',json解析
            #example:
            #js:
            #{'id': 'J_920115', 'm': '102.00', 'op': '79.00', 'p': '69.00'}
            if(js.get('tpp')):
                price = 'Ordinary: ' + js.get('p') + ' | Plus: ' + js.get('tpp')
            else:
                price = js.get('p')
            print('{} > 获取价格信息成功!'.format(time.ctime()))
        except Exception as e:
            print('ERROR{} > good_price():'.format(time.ctime()) + str(e))
        return price

    def good_detail(self):
        # get good detail
        good_data = {
            'id' : self.goodid,
            'name' : '',
            'link' : '',
            'price' : '',
            'stock' : 0,
            'stock_state': '',
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

            # link 商品链接
            tags = soup.select('a#InitCartUrl')
            link = tags[0].attrs['href']
            if (link[:2] == '//'):
                link = 'http:' + link
            good_data['link'] = link

        except Exception as e:
            print('ERROR{} > good_detail():'.format(time.ctime()) + str(e))

        # good price
        good_data['price'] = self.good_price()

        # good stock
        good_data['stock'], good_data['stock_state'] = self.good_stock()
        '''
        0  : fail to access
        33 : on sale, 
        34 : out of stock
        36 : presell
        '''
        print('{} > 获取商品主要信息成功!'.format(time.ctime()))
        print ('{} > 商品详情'.format(time.ctime()))
        print ('编号：{}'.format(good_data['id']))
        print ('状态：{}'.format(good_data['stock_state']))
        print ('价格：{}'.format(good_data['price']))
        print ('名称：{}'.format(good_data['name']))

        return good_data


    def tocart(self):
        # stock detail
        good_data = self.good_detail()
        '''
        0  : fail to access
        33 : on sale, 
        34 : out of stock
        36 : presell
        '''
        tocart_url = "http://cart.jd.com/gate.action"
        params = {
            "pid" : self.goodid,
            "pcount" : self.count,
            "ptype" : '1',
        }
        # 无货状态 或其他状态
        # 未debug 预售或者 秒杀 等其他动态变化情况
        if (good_data['stock'] != 33):
            print('ERROR{} > tocart():不是现货状态!'.format(time.ctime()))
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

            # tag if succeed in adding to cart
            # example:
            # tag = [<h3 class="ftx-02">商品已成功加入购物车！</h3>]
            tag = soup.select('h3.ftx-02')
            if not tag:
                tag = soup.select('div.p-name a')

            if not tag:
                raise ValueError

            print ('{} > 购买详情'.format(time.ctime()))
            print ('链接：{0}'.format(resp.url))
            print ('结果：{0}'.format(tag[0].text.strip()))
            return True
        # get_error
        # bs4_parser error
        except ValueError:
            print('ERROR{} > tocart():tag_API失效'.format(time.ctime()))
            return False
        except Exception as e:
            print('ERROR{} > tocart():解析错误!'.format(time.ctime()) + str(e))
            return False

    def cart_detail(self):
        # list all goods detail in cart
        # □ ■ 第三方卖家 京东自营 △ ▲  是 否 全球购
        cart_url = 'https://cart.jd.com/cart.action'
        th = '序号  选中  数量   单价    ID         优惠   商品名'
        sformat = '{:<6}{:<6}{:<6}{:<8}{:<11}{:<6}{:<}'

        try:
            resp = s.get(cart_url, headers = self.headers)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.text, "html.parser")

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
                gname = item.select('div.p-name a')[0].text.strip()
                tgid = item.select('div.p-name a')[0].get("href")
                gid = re.search(r'\d+',tgid).group(0)
                promos  = item.select('div.promotion-cont ul li input')
                promos_list = []
                for p in promos:
                    pselect = p.get("checked")
                    pselect = '×' if not pselect else '√'
                    ptitle = p.get("title")
                    pvalue = p.get("value")
                    promos_list.append((pselect,ptitle,pvalue))
                self.promos_dict[gid] = promos_list
                select_promo = '√' if promos else '×'
                print (sformat.format(str(start), str(select), str(count), str(price), str(gid), str(select_promo), str(gname)))
            t_count = soup.select('div.amount-sum  em')[0].text.strip()
            t_value = soup.select('span.sumPrice em')[0].text.strip()
            print('{} > 购物车总计'.format(time.ctime()))
            print ('总件: {}'.format(t_count))
            print ('总价: {}'.format(t_value[1:]))
            time.sleep(0.5)
            self.cart_panel()
        except Exception as e:
            print('ERROR{} > cart_detail():'.format(time.ctime()) + str(e))

    def cart_panel(self):
        print('{} > 购物车操作页面'.format(time.ctime()))
        print("请选择下一步需要进行操作代码")
        while True:
            option = input("\t1: 修改购物车商品数量\n\t2: 选中某商品\n\t3: 取消选中某商品\n\t4: 修改商品优惠信息\n\t5: 删除某商品\n\t0: 退出\n我选择: ")
            if(option == '1'):
                option2 = input("\t请输入商品ID,输入0退出\n我选择: ")
                if(option2 != '0'):
                    option3 = input("\t请输入该商品新数量,输入0退出\n我选择: ")
                    if(option3 != '0'):
                        self.change_cart_detail((option,option2,option3))
                # break
            elif(option == '2'):
                option2 = input("\t请输入商品ID,输入0退出\n我选择: ")
                if (option2 != '0'):
                    self.change_cart_detail((option, option2))
                # break
            elif(option == '3'):
                option2 = input("\t请输入商品ID,输入0退出\n我选择: ")
                if (option2 != '0'):
                    self.change_cart_detail((option, option2))
                # break
            elif(option == '4'):
                option2 = input("\t请输入商品ID,输入0退出\n我选择: ")
                if (option2 != '0'):
                    now_promo_id = self.cart_promos_detail(option2)
                    if(not now_promo_id):
                        print('{} > 该商品无优惠信息!'.format(time.ctime()))
                        continue
                    option3 = input("\t请输入新优惠ID,输入0退出\n我选择: ")
                    if(option3 != '0'):
                        self.change_cart_detail((option, option2, now_promo_id, option3))
                        print('{} > 重新获取购物车信息中...'.format(time.ctime()))
                        time.sleep(0.5)
                        self.cart_detail()
                break
            elif(option == '5'):
                option2 = input("\t请输入商品ID,输入0退出\n我选择: ")
                if (option2 != '0'):
                    self.change_cart_detail((option, option2))
                # break
            elif(option == '0'):
                break
            else:
                print("识别失败,请重新输入!")
        pass
    def cart_promos_detail(self, goodid, option = None):
        # 单参: 打印信息                  输出当前优惠ID
        # 双参: change_cart_detail()调用 输出(当前优惠ID, post参数)
        # goodid = str , option = tuple
        # return None if 无优惠
        #               or 当前优惠ID
        pheader = "序号  选中  ID        名称"
        pformat = "{:<6}{:<6}{:<10}{}"
        if(not option):
            print('{} > 优惠信息: '.format(time.ctime()))
            print(pheader)
        if(self.promos_dict.get(goodid)):
            promos = self.promos_dict[goodid]
            start = 0
            prtn = ''
            for promo in promos:
                start += 1
                nselect = promo[0]
                nname = promo[1]
                nid = promo[2].split('_')[1]
                if(nselect == '√'):
                    prtn = nid
                    if(option):
                        ntail = promo[2].split('_')[3]
                        return (prtn,ntail)
                if(not option):
                    print(pformat.format(str(start),str(nselect),str(nid),str(nname)))

            if (not option):
                print('{} > 获取优惠信息成功!'.format(time.ctime()))
            return prtn
        else:
            return None
    def change_cart_detail(self,option):
        headers = {
            "Host": "cart.jd.com",
            "Connection": "keep-alive",
            "Origin": "https://cart.jd.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
            "Referer": "https://cart.jd.com/cart.action",
            "Accept-Encoding": "gzip, deflate, br",
        }
        if(option[0] == '1'):
            #option = (1, goodid, new_count)
            num_url = 'http://cart.jd.com/changeNum.action'
            num_data = {
                't': '0',
                'venderId': '8888',
                'pid': option[1],
                'pcount': option[2],
                # 有优惠商品 '11' + targetId
                # 无优惠商品 '1'
                # targetId 成功请求必要条件!
                'outSkus': '',
                'random': random.random(),
                'locationId':"-".join(self.areaid.split('_')),
            }
            if(self.promos_dict.get(option[1])):
                num_data['targetId'], num_data['ptype']  = self.cart_promos_detail(option[1], True)
                num_data['promoID'] = num_data['targetId']
            else:
                num_data['ptype'] = '1'
                num_data['targetId'] = '0'
                num_data['promoID'] = '0'
            try:
                resp = s.post(num_url, data = num_data, headers = headers)
                if (resp.status_code == 200):
                    js = json.loads(resp.text)
                    if js.get('pcount'):
                        print('{} > 已成功更改id:{}商品数量到:{}'.format(time.ctime(),js['pid'],js['pcount']))
                        return True
                else:
                    raise ValueError("post error or json_parse error!")
            except Exception as e:
                print('ERROR{} > change_cart_detail():'.format(time.ctime()) + str(e))
                return False
        elif(option[0] == '2'):
            # option = (2, goodid)
            select_url = "https://cart.jd.com/selectItem.action?rd" + str(random.random())
            select_data = {
                't': '0',
                'venderId': '8888',
                'pid': option[1],
                'packId': '0',
                'outSkus': '',
                'locationId':"-".join(self.areaid.split('_')),
            }
            if(self.promos_dict.get(option[1])):
                select_data['targetId'], select_data['ptype'] = self.cart_promos_detail(option[1], True)
                select_data['promoID'] = select_data['targetId']
            else:
                select_data['ptype'] = '1'
                select_data['targetId'] = '0'
                select_data['promoID'] = '0'
            try:
                resp = s.post(select_url, data = select_data, headers = headers)
                if (resp.status_code == 200):
                    js = json.loads(resp.text)
                    if (js.get('sortedWebCartResult').get('ids') and option[1] in js['sortedWebCartResult']['ids']):
                        print('{} > 已成功选中id:{}商品!'.format(time.ctime(),js['pid']))
                        return True
                else:
                    raise ValueError("post error or json_parse error!")
            except Exception as e:
                print('ERROR{} > change_cart_detail():'.format(time.ctime()) + str(e))
                return False
        elif(option[0] == '3'):
            # option = (3, goodid)
            cancel_url = "https://cart.jd.com/cancelItem.action?rd" + str(random.random())
            cancel_data = {
                't': '0',
                'venderId': '8888',
                'pid': option[1],
                'packId': '0',
                'outSkus': '',
                'locationId': "-".join(self.areaid.split('_')),
            }
            if (self.promos_dict.get(option[1])):
                cancel_data['targetId'], cancel_data['ptype'] = self.cart_promos_detail(option[1], True)
                cancel_data['promoID'] = cancel_data['targetId']
            else:
                cancel_data['ptype'] = '1'
                cancel_data['targetId'] = '0'
                cancel_data['promoID'] = '0'
            try:
                resp = s.post(cancel_url, data = cancel_data, headers = headers)
                if (resp.status_code == 200):
                    js = json.loads(resp.text)
                    if (option[1] not in js['sortedWebCartResult']['ids']):
                        print('{} > 已成功取消选中id:{}商品!'.format(time.ctime(),js['pid']))
                        return True
                else:
                    raise ValueError("post error or json_parse error!")
            except Exception as e:
                print('ERROR{} > change_cart_detail():'.format(time.ctime()) + str(e))
                return False
        elif(option[0] == '4'):
            # option = (4, goodid, now_promo_id, modify_promo_id)
            now_promo_id, modify_promo_id = option[2], option[3]
            promo_url = "https://cart.jd.com/changePromotion.action"
            promo_data = {
                'venderId': '8888',
                'pid': option[1],
                'promoID': option[2],
                'modifyPromoID': option[3],
                't': '0',
                'outSkus': '',
                'random': random.random(),
                'locationId': "-".join(self.areaid.split('_')),
            }
            promo_data['targetId'], promo_data['ptype'] = self.cart_promos_detail(option[1], True)
            try:
                # 有优惠信息商品更新优惠需要再次调用cart_detail()!
                resp = s.post(promo_url, data = promo_data, headers = headers)
                if (resp.status_code == 200):
                    js = json.loads(resp.text)
                    # ----------  debug -----------
                    if ( True ):
                        print('{} > 已成功更新选中id:{}商品优惠信息!'.format(time.ctime(), js['pid']))
                        return True
                else:
                    raise ValueError("post error or json_parse error!")
            except Exception as e:
                print('ERROR{} > change_cart_detail():'.format(time.ctime()) + str(e))
                return False
        elif(option[0] == '5'):
            # option = (5, goodid)
            delete_url = "https://cart.jd.com/removeSkuFromCart.action"
            delete_params = {
                'rd': random.random(),
            }
            delete_data = {
                'venderId': '8888',
                'pid': option[1],
                'packId': '0',
                't': '0',
                'outSkus': '',
                'random': random.random(),
                'locationId': "-".join(self.areaid.split('_')),
            }
            if (self.promos_dict.get(option[1])):
                delete_data['targetId'], delete_data['ptype'] = self.cart_promos_detail(option[1], True)
                delete_data['promoID'] = delete_data['targetId']
            else:
                delete_data['ptype'] = '1'
                delete_data['targetId'] = '0'
                delete_data['promoID'] = '0'
            try:
                resp = s.post(delete_url, params = delete_params, data = delete_data, headers = headers)
                if (resp.status_code == 200):
                    js = json.loads(resp.text)
                    if (str(option[1]) not in js['sortedWebCartResult']['allSkuIds']):
                        print('{} > 已成功删除选中id:{}商品!'.format(time.ctime(), js['pid']))
                        return True
                else:
                    raise ValueError("post error or json_parse error!")
            except Exception as e:
                print('ERROR{} > change_cart_detail():'.format(time.ctime()) + str(e))
                return False
    def order_panel(self):
        #修改地址  -> 可能修改后无法提交地址
        change_address_url = "https://trade.jd.com/shopping/dynamic/consignee/saveConsignee.action"
        reference = 'https://trade.jd.com/shopping/order/getOrderInfo.action?rid=1518184846987'

        # consigneeParam.id
        # 138504070
        # consigneeParam.type
        # null
        # consigneeParam.commonConsigneeSize
        # 2
        # consigneeParam.isUpdateCommonAddress
        # 0
        # consigneeParam.giftSenderConsigneeName
        # consigneeParam.giftSendeConsigneeMobile
        # consigneeParam.noteGiftSender
        # false
        # consigneeParam.isSelfPick
        # 0
        # consigneeParam.selfPickOptimize
        # 1
        # consigneeParam.pickType
        # 0
        #快递  货到付款 / 在线支付
        pay_way_url = 'https://trade.jd.com/shopping/dynamic/payAndShip/getVenderInfo.action'
        # shipParam.payId
        # 4 在线支付  1 货到付款
        # shipParam.pickShipmentItemCurr
        # false
        # shipParam.onlinePayType
        # 0
        #打印当前购买信息 (库存状态)
        # 静态信息 直接解析!
        #优惠选择 优惠券  京东卡 京豆
        # 可用优惠券信息打印
        # 静态解析
        use_coupon_url = "https://trade.jd.com/shopping/dynamic/coupon/useCoupon.action"
        # couponParam.couponKey
        # 0000-0300-0744-9933
        # couponParam.pageNum
        # 1
        cancel_coupon_url = "https://trade.jd.com/shopping/dynamic/coupon/cancelCoupon.action"
        # couponParam.couponId
        # 30007449933
        # couponParam.pageNum
        # 1
        #提交
        # 是否需要支付密码
        check_pwd_url = "https://trade.jd.com/shopping/dynamic/coupon/checkFundsPwdResult.action"
        #返回
        pass

    def toorder(self, issubmit = False):
        # get order info detail, and submit order
        print (u'{0} > 订单详情'.format(time.ctime()))

        try:
            order_url = 'http://trade.jd.com/shopping/order/getOrderInfo.action'
            hk_order_url = "http://trade.jd.hk/shopping/order/getOrderInfo.action"
            params = {
                'rid' : str(int(time.time() * 1000)),
            }
            hk_params = {
                'flowId': 10,
                'rid': int(time.time() * 1000),
            }
            # get preorder page
            resp = s.get(order_url, params=params, headers = self.headers)
            # soup = BeautifulSoup(rs.text, "html.parser")
            selector = etree.HTML(resp.text)
            # order summary
            # total_cost = soup.find(id='sumPayPriceId').text.strip()
            # detail = soup.find(class_='fc-consignee-info').text.strip()
            total_cost = selector.xpath("//span[@id='sumPayPriceId']/text()")[0]
            # if detail:
                # receiver = detail.find(id='sendMobile').text.strip()
                # re_address = detail.find(id='sendAddr').text.strip()
            receiver = selector.xpath("//span[@id='sendMobile']/text()")[0].strip()
            re_address = selector.xpath("//span[@id='sendAddr']/text()")[0].strip()
            print (u'应付款：{0}'.format(total_cost))
            print (receiver)
            print (re_address)
            self.order_panel()
            # --------------- debug --------------------
            if (issubmit or self.submitflag):
                self.submit_order()
        except Exception as e:
            print('ERROR{} > tocart(): '.format(time.ctime()) + str(e))

    def submit_order(self):
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
        rp = s.post(order_url, params=payload, headers=self.headers)

        if rp.status_code == 200:
            js = json.loads(rp.text)
            if js['success'] == True:
                print('下单成功！订单号：{0}'.format(js['orderId']))
                print('请前往东京官方商城付款')
                return True
            else:
                print('下单失败！<{0}: {1}>'.format(js['resultCode'], js['message']))
                if js['resultCode'] == '60017':
                    # 60017: 您多次提交过快，请稍后再试
                    time.sleep(1)
        else:
            print('请求失败. StatusCode:', rp.status_code)
            order_url = 'http://trade.jd.com/shopping/order/submitOrder.action'
        rp = s.post(order_url, params=payload, headers=self.headers)

        if rp.status_code == 200:
            js = json.loads(rp.text)
            if js['success'] == True:
                print('下单成功！订单号：{0}'.format(js['orderId']))
                print('请前往东京官方商城付款')
                return True
            else:
                print('下单失败！<{0}: {1}>'.format(js['resultCode'], js['message']))
                if js['resultCode'] == '60017':
                    # 60017: 您多次提交过快，请稍后再试
                    time.sleep(1)
        else:
            print('请求失败. StatusCode:', rp.status_code)

    def main(self):
        pass