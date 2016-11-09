'''
Create on 2016-11-8
@author: latelan
'''
import json
import time
import requests

class YunDaMa(object):
	'''
	docstring for YunDaMa
	'''
	def __init__(self, username, password, appid=None, appkey=None):
		self.base_url = "http://api.yundama.com/api.php"
		self.username = username
		self.password = password
		self.appid = "2859" if not appid else appid
		self.appkey = "550644178743dfe5cf36aa7032b3c1d3" if not appkey else appkey
		self.req = requests.Session()

	def get_captcha(self, filebytes, filename, filetype, codetype='1000', repeat=15):
		'''
		default timeout is 30s
		'''
		cid = self.upload(filebytes, filename, filetype, codetype)
		if not cid:
			return None
		while repeat > 0:
			code = self.result(cid)
			if code:
				return code
			repeat -= 1
			time.sleep(2)
		return None

	def upload(self, filebytes, filename, filetype, codetype):
		data = {
			'method': 'upload',
			'username': self.username,
			'password': self.password,
			'codetype': codetype,
			'appid': self.appid,
			'appkey': self.appkey,
			'timeout': 60
		}
		file = {
			'file': (filename, filebytes, filetype)
		}
		try:
			result = self.req.post(self.base_url, data=data, files=file).json()
		except Exception as e:
			raise
		return result['cid']

	def result(self, cid):
		data = {
			'method': 'result',
			'cid': cid
		}
		try:
			result = self.req.post(self.base_url, data=data).json()
		except Exception as e:
			raise

		if result['text']:
			return result['text']

if __name__ == '__main__':
	ydm = YunDaMa(username, password)
	code = ydm.get_captcha(requests.get('https://passport.bilibili.com/captcha').content, 'captcha.jpg', 'image/jpeg')
	print code
