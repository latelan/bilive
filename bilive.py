#coding=UTF-8
#
# from lwl12 https://blog.lwl12.com/read/bilibili-live-upgrade.html
#
import urllib
import urllib2
import cookielib
import json
import sys
import os
import re
import datetime
import time
reload(sys)
sys.setdefaultencoding('utf-8')
COOKIE_FILE = 'BILIVE_COOKIES_DATA'
def login(COOKIE_FILE):
	cookie = cookielib.MozillaCookieJar(COOKIE_FILE)
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))  
	response = opener.open('https://passport.bilibili.com/ajax/miniLogin/minilogin')
	print'Please input your bilibili Username:'
	userid = raw_input()
	print'Please input your bilibili Password:'
	pwd = raw_input()
	postdata = urllib.urlencode({
            	'keep':'0',  
            	'captcha':'',
            	'userid':userid,
            	'pwd':pwd
        	})    
	loginUrl = 'https://passport.bilibili.com/ajax/miniLogin/login' 
	response = opener.open(loginUrl,postdata)
	liveUrl = 'http://live.bilibili.com/User/getUserInfo' 
	result = opener.open(liveUrl)
	cookie.save(ignore_discard=True, ignore_expires=True)
	return opener
def check_login(opener):
	liveUrl = 'http://live.bilibili.com/User/getUserInfo' 
	result = opener.open(liveUrl)
	result = result.read()
	s = json.loads(result)
	if s["code"] == "REPONSE_OK":
		return s
	else:
		print'Login Failed: ' + result.decode('unicode_escape')
		os.remove(COOKIE_FILE)
		time.sleep(3)
		exit()
def heart(opener):
	postdata = ''
	heartUrl = 'http://live.bilibili.com/User/userOnlineHeart'
	roomId = get_room_id(opener)
	print'RoomId: ' + roomId
	refererHeader = 'http://live.bilibili.com/' + roomId
	opener.addheaders = [('Referer', refererHeader)]
	result = opener.open(heartUrl,postdata)
	result = result.read()
	return result

def get_room_id(opener):
	liveUrl = 'http://live.bilibili.com/'
	result = opener.open(liveUrl)
	result = result.read()
	res = re.search(r'data-room-id="(\d+)"', result)
	if res:
		return res.group(1)
	else:
		print'Get RoomId Failed'
		exit()
			
cookie = cookielib.MozillaCookieJar(COOKIE_FILE)   
if not os.path.exists(COOKIE_FILE):
	opener = login(COOKIE_FILE)
else:
	cookie.load(COOKIE_FILE, ignore_discard=True, ignore_expires=True)
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))

s = check_login(opener)
print'Hello, '+s["data"]["uname"]+'!'
upr = str(s["data"]['user_next_intimacy'] - s["data"]['user_intimacy'])
result = heart(opener)
h = json.loads(result)
if h["code"] != 0:
	for x in xrange(1,6):
		print "Heart Status: Error, Retrying......("+ str(x) +")"
		if x != 5:
			time.sleep(2)
		else:
			time.sleep(10)
		result = heart(opener)
		h = json.loads(result)
		if h["code"] != 0:
			continue
		else:
			print 'Live Level: '+ str(s["data"]['user_level']) +'\nUpgrade requires: '+ upr +'\nLevel Rank: '+ str(s["data"]['user_level_rank']) +'\nHeart Status: Successful\nHeart Time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\nDebug:'+ result.decode('unicode_escape')
			time.sleep(3)
			exit()
	print 'Live Level: '+ str(s["data"]['user_level']) +'\nUpgrade requires: '+ upr +'\nLevel Rank: '+ str(s["data"]['user_level_rank']) +'\nHeart Status: Error\nHeart Time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\nDebug:'+ result.decode('unicode_escape')
else:
	print 'Live Level: '+ str(s["data"]['user_level']) +'\nUpgrade requires: '+ upr +'\nLevel Rank: '+ str(s["data"]['user_level_rank']) +'\nHeart Status: Successful\nHeart Time: ' + time.strftime("%Y-%m-%d %H:%M:%S") + '\nDebug:'+ result.decode('unicode_escape')
