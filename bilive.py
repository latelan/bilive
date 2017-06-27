'''
Create at 2016-11-08
@author latelan
'''

import sys
import os
import time
import requests
import json
import re
import rsa
from base64 import b64encode

from yundama import YunDaMa
import config

reload(sys)
sys.setdefaultencoding('utf-8')

COOKIE_FILE = 'BILIVE_COOKIE_FILE'

def login(requester):
	'''
	login bilibili and save cookie to file
	'''
	userid = config.B_USER
	pwd = config.B_PWD

	# get key, use rsa encrypt pwd
	getkey_url = 'https://passport.bilibili.com/login'  
	param_data = {
			'act': 'getkey',
			'_': str(int(time.time()*1000))
			}
	res = requester.get(getkey_url, params=param_data)
	hashkey = res.json()
	pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(hashkey['key'])
	enpwd = b64encode(rsa.encrypt((hashkey['hash'] + pwd).encode(), pub_key)).decode()	

	# get captcha
	captcha_url = 'https://passport.bilibili.com/captcha'
	res = requester.get(captcha_url)
	captcha_content = res.content
	vdcode = get_captcha(captcha_content)

	# login
	login_url = 'https://passport.bilibili.com/login/dologin'
	post_data = {
			'act': 'login',
			'gourl': 'http://www.bilibili.com/',
			'keeptime':2592000,
			'vdcode': vdcode,
			'userid': userid,
			'pwd': enpwd
			}
	res = requester.post(login_url, data=post_data)
	cookie = res.request.headers['Cookie']
	save_cookie(COOKIE_FILE, cookie)

def get_captcha(captcha):
	'''
	get result of the captcha, user can implement, here using YunDaMa
	@param captcha - capthcha content,
	@return the result of captcha
	'''
	username = config.YDM_USER
	password = config.YDM_PWD
	ydm = YunDaMa(username, password)
	captcha = ydm.get_captcha(captcha, 'capthcha.jpg', 'image/jpeg')
	if not captcha:
		print'Get captcha failed'
		exit()

	return captcha

def check_login(requester):
	'''
	check login status
	'''
	user_url = 'http://live.bilibili.com/User/getUserInfo'
	res = requester.get(user_url)
	user = res.json()
	if user['code'] == 'REPONSE_OK':
		return user
	else:
		print'Login Failed: ' + res.text.decode('unicode_escape')
		os.remove(COOKIE_FILE)
		time.sleep(3)
		exit()

def heart(requester):
	'''
	heartbeat
	'''
	heart_url = 'http://live.bilibili.com/User/userOnlineHeart'
	room_id = get_room_id(requester)
	print'RoomId: ' + room_id
	referer_header = 'http://live.bilibili.com/' + room_id
	headers = {'Referer': referer_header}
	res = requester.get(heart_url, headers=headers)
	return res.text

def get_room_id(requester):
	'''
	get live room id
	'''
	live_url = 'http://live.bilibili.com/'
	res = requester.get(live_url)
	room_id = re.search(r'data-roomid="(\d+)"', res.text)
	if room_id:
		return room_id.group(1)
	else:
		roomid_url = 'http://api.live.bilibili.com/area/newRecom?area=all'
		res = requests.get(roomid_url)
		data = res.json()                                                                
		if 'roomid' in data['data'][0]:                                                  
			return str(data['data'][0]['roomid'])                                        
		else:                                                                            
			print'Get roomid failed'                                                     
			exit()                     
			
def save_cookie(filepath, cookie):
	'''
	save cookies as json formt
	"k1=v1; k2=v2" -> "{k1:v1, k2:v2}"
	'''
	matcher = re.findall(r'(\S+)=(\S[^;]+)', cookie)	
	cookies = {}
	for (k,v) in matcher:
		cookies[k] = v
	cookies = json.dumps(cookies)
	file = open(filepath, 'w')	
	file.write(cookies)
	file.close()

def get_cookie(filepath):
	file = open(filepath, 'r')
	cookie = file.read()
	file.close()
	return json.loads(cookie)


s = requests.Session()
if not os.path.exists(COOKIE_FILE):
	login(s)
else:
	cookie_dict = get_cookie(COOKIE_FILE)
	cookies = requests.utils.cookiejar_from_dict(cookie_dict, cookiejar=None, overwrite=True)
	s.cookies = cookies

d = check_login(s)
print'Hello, '+d["data"]["uname"]+'!'
upr = str(d["data"]['user_next_intimacy'] - d["data"]['user_intimacy'])
result = heart(s)
h = json.loads(result)
if h["code"] != 0:
	for x in xrange(1,6):
		print "Heart Status: Error, Retrying......("+ str(x) +")"
		if x != 5:
			time.sleep(2)
		else:
			time.sleep(10)
		result = heart(s)
		h = json.loads(result)
		if h ["code"] != 0:
			continue
		else:
			print 'Live Level: '+ str(d["data"]["user_level"]) +'\nUpgrade requires: '+ upr +'\nLevel Rank: '+ str(d["data"]["user_level_rank"]) +'\nHeart Status: Successful\nHeart Time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\nDebug:'+ result.decode('unicode_escape')
			time.sleep(3)
	print 'Live Level: '+ str(d["data"]["user_level"]) +'\nUpgrade requires: '+ upr +'\nLevel Rank: '+ str(d["data"]["user_level_rank"]) +'\nHeart Status: Error\nHeart Time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\nDebug:'+ result.decode('unicode_escape')
else:
	print 'Live Level: '+ str(d["data"]["user_level"]) +'\nUpgrade requires: '+ upr +'\nLevel Rank: '+ str(d["data"]["user_level_rank"]) +'\nHeart Status: Successful\nHeart Time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\nDebug:'+ result.decode('unicode_escape')
