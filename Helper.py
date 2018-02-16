#for command-parsing
import argparse
    
def help_message():
	parser = argparse.ArgumentParser(description='This is a open-source python script for simulating login activity of JD.COM market(https://www.jd.com)  \
										, and simulating others thing like detecting good stock, buying, etc')
	parser.add_argument('-t', '--logintype', 
	                   help='the way you want to login JD:\n\t \
	                   		 1: qrcode\n\t 2: password',
					   type=int, 	                   
	                   default=1)
	parser.add_argument('-u', '--username', 
	                   help='if you login by password, you should type in your username',
	                   default='')
	parser.add_argument('-p', '--password', 
	                   help='if you login by password, you should type in your password',
	                   default='')
	parser.add_argument('-a', '--area', 
	                    help='Area code, like: province_id_city_id_district_id_street_id\n\t \
							  Example: 1_222_3333_44444',
	                    default='')
	parser.add_argument('-g', '--good',
						type=int, 
	                    help='Jingdong good ID\n\t \
							  Example: if the good_url is: https://item.jd.com/2047126.html,\n\t\
							  then you should type in 2047126,which is the good_id.',
	                    default=920115)
	parser.add_argument('-c', '--count', 
						type=int, 
	                    help='The count of to buy', 
	                    default=1)
	parser.add_argument('-i', '--interval',
	                    type=int, 
	                    default=1000,
	                    help='Detecting good interval, unitted by Millisecond')
	parser.add_argument('-f', '--flush', 
	                    action='store_true',
	                    default=False, 
	                    help='Whether detecting the stock if out of stock')
	parser.add_argument('-s', '--submit', 
	                    action='store_true',
	                    default=False, 
	                    help='Whether submit the selected order')
	return parser