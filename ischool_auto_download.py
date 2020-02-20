from binascii import b2a_hex, a2b_hex
from Cryptodome.Cipher import AES
from collections import namedtuple
from contextlib import closing
from bs4 import BeautifulSoup
import requests
import getpass
import urllib3
import string
import time
import sys
import os



AES_LENGTH = 16

class prpcrypt():
	def __init__(self, key):
		self.key = key
		self.mode = AES.MODE_ECB
		self.cryptor = AES.new(self.pad_key(self.key).encode(), self.mode)

	# 加密函式，如果text不是16的倍數【加密文字text必須為16的倍數！】，那就補足為16的倍數
	# 加密內容需要長達16位字元，所以進行空格拼接
	def pad(self,text):
		while len(text) % AES_LENGTH != 0:
			text += ' '
		return text

	# 加密金鑰需要長達16位字元，所以進行空格拼接
	def pad_key(self,key):
		while len(key) % AES_LENGTH != 0:
			key += ' '
		return key

	def encrypt(self, text):

		# 這裡金鑰key 長度必須為16（AES-128）、24（AES-192）、或32（AES-256）Bytes 長度.目前AES-128足夠用
		# 加密的字元需要轉換為bytes
		# print(self.pad(text))
		self.ciphertext = self.cryptor.encrypt(self.pad(text).encode())
		# 因為AES加密時候得到的字串不一定是ascii字符集的，輸出到終端或者儲存時候可能存在問題
		# 所以這裡統一把加密後的字串轉化為16進位制字串
		return b2a_hex(self.ciphertext)

		# 解密後，去掉補足的空格用strip() 去掉

	def decrypt(self, text):
		plain_text = self.cryptor.decrypt(a2b_hex(text)).decode()
		return plain_text.rstrip(' ')




define_verify = False

inputuserid   = str()
inputpassword = str()

urllib3.disable_warnings() 

try:
	f = open('login.txt', 'r')
	inputuserid = f.readline().replace("\n","")
	inputpassword = f.readline().replace("\n","")	
	encrypt_key = inputuserid[:7]
	pc = prpcrypt( encrypt_key )  # 初始化金鑰
	decrypt_inputpassword = pc.decrypt(inputpassword)
	inputpassword = decrypt_inputpassword
	print(inputuserid)
	print("登入校園入口網站...")
except:
	print("檔案不存在")
	f = open('login.txt', 'w')
	inputuserid = input("輸入學號:")
	inputpassword = getpass.getpass("輸入密碼:")
	encrypt_key = inputuserid[:7]
	pc = prpcrypt( encrypt_key )  # 初始化金鑰
	encrypt_inputpassword = pc.encrypt(inputpassword)
	f.write(inputuserid + "\n")
	f.write(encrypt_inputpassword.decode())
	f.close()
	

ntut_host     = "https://nportal.ntut.edu.tw"                   
loginout_ulr  = "https://nportal.ntut.edu.tw/logout.do" #登出網址
login_ulr     = "https://nportal.ntut.edu.tw/login.do"  #登入網址
ischool_url   = "https://ischool.ntut.edu.tw"
get_course_file_url = "https://ischool.ntut.edu.tw/learning/document/document.php\
?cidReset=true&cidReq="
#北科i學園檔案下載
dirname = "北科i學園資料"


res = requests.session()

user_header = {
	"Accept"           : "text/html,application/xhtml+xml,application/xml;\
q=0.9,*/*;q=0.8",
	"Accept-Encoding"  : "gzip, deflate, br" ,
	"Accept-Language"  : "zh-TW" ,
'User-Agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4)\
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
	"Cache-Control": "max-age=0",
	"Upgrade-Insecure-Requests": "1",
	"Referer": "https://nportal.ntut.edu.tw/index.do?thetime=1556366755131"
}

res.headers = user_header   #放入自定義header

res.get(loginout_ulr,verify = define_verify)  #先進行登出

post_data = {
		"muid"        : inputuserid     ,
		"mpassword"   : inputpassword   
	}

login = res.post(login_ulr , data = post_data )

if "myPortal.do" in login.text:
	loginpass = True
	url_start = login.text.find('"')
	url_start += 1
	url_end   = login.text.find('"' , url_start)
	url_jump = login.text[url_start:url_end]
	print ("登入成功")
	url_jump = ntut_host + '/' + url_jump
	#print("跳轉網址:"+url_jump)
	print("登入北科i學園...")
	url_jump = res.get(url_jump,verify = define_verify)
elif "帳號或密碼錯誤" in login.text:
	input ("帳號或密碼錯誤")
	exit()
else:
	login_fail_time += 1;
	input ("失敗{0}次嘗試重新登入" .format(login_fail_time) )
	exit()



url = "https://nportal.ntut.edu.tw/ssoIndex.do?apUrl=\
https://ischool.ntut.edu.tw/learning/auth/login.php&\
apOu=ischool"
#取得登入資料
title = res.get(url,verify = define_verify)
soup = BeautifulSoup(title.text, 'html.parser')
url = str()

getsessionId = soup.find_all('form')
for item in getsessionId:
	if item.get("name") == "ssoForm":
		url = item.get("action") + "?"
		break

getsessionId = soup.find_all('input')
for item in getsessionId:
	url += ( item.get("name") + "=" + item.get("value") + "&" )
	
title = res.post(url,verify = define_verify)
print("登入成功\n")


url = ischool_url
title = res.get(url,verify = define_verify)



try:
	os.mkdir(dirname)
except FileExistsError:
	pass



course = {}
soup = BeautifulSoup(title.text, 'html.parser')
soup = soup.find_all("option")
del soup[0]  #刪除課程選擇

def strQ2B(ustring):
	ss = []
	for s in ustring:
		rstring = ""
		for uchar in s:
			inside_code = ord(uchar)
			if inside_code == 12288:  # 全形空格直接轉換
				inside_code = 32
			elif (inside_code >= 65281 and inside_code <= 65374):  # 全形字元（除空格）根據關係轉化
				inside_code -= 65248
			rstring += chr(inside_code)
		ss.append(rstring)
	return ''.join(ss)


def str_count(s):
	count_en = count_dg = count_sp = count_zh = count_pu = 0
	s_len = len(s)
	for c in s:
		# 英文
		if c in string.ascii_letters:
			count_en += 1
		# 數字
		elif c.isdigit():
			count_dg += 1
		# 空格
		elif c.isspace():
			count_sp += 1
		# 中文
		elif c.isalpha():
			count_zh += 1
		# 特殊字符
		else:
			count_pu += 1
	total_chars = count_zh + count_en + count_sp + count_dg + count_pu
	if total_chars == s_len:
		return namedtuple('Count', ['total', 'zh', 'en', 'space', 'digit', 'punc'])(s_len, count_zh, count_en,count_sp, count_dg, count_pu)
	else:
		print('Something is wrong!')
		return None
		
		
def get_display(showlen , name ):
	name = strQ2B(name)
	name_info = str_count(name)
	name_len = name_info.zh * 2 +  (len(name) - name_info.zh)
	spacenum = showlen - name_len
	display = name + spacenum * ' '
	return display
		
		
os.system("cls") # windows

last_year = 0
count = 0
for index,s in enumerate(soup):
	name = s.string.split('_')
	if name[0] != last_year:
		last_year = name[0]
		if index != 0:
			print("\n")
		print("{:3s}學年度第{:1s}學期".format(last_year[:3],last_year[3]) )
		count = 0
	if count >= 4:
		count = 0
		print()
	count = count + 1
	display = get_display( 24 , name[1])
	print("{:2d}.{:s}".format(index , display) , end="")

while True:
	course_number = input("\n輸入下載號碼:")
	try:
		course_number = int(course_number)
		course = soup[course_number]
		break
	except:
		print("輸入號碼有誤")

os.system("cls") # windows

coursecid  = course.get("value")
course_name_start = course.string.find("_")
course_name_end = course.string.find("_",course_name_start+1)
couesename = course.string[course_name_start+1:course_name_end]
coursecid = coursecid[coursecid.find("cid")+4:]
url = coursecid = get_course_file_url + coursecid
print(couesename)
store_location = str()
try:
	store_location = os.path.join(dirname , couesename)
	os.mkdir(store_location)
except FileExistsError:
	pass
	#print("資料夾已存在")


title = res.get(url,verify = define_verify)
soup = BeautifulSoup(title.text, 'html.parser')

soup = soup.find_all("tr" , attrs = {"align" :"center"} )
del soup[0] #刪除標題


extension_list = ["","pdf","docx","pptx","xlsx","rar","link"]
for index,onefile in enumerate(soup):
	filedetail = onefile.find_all("td")
	filename   = filedetail[0].string                        #第一個放檔名
	filetime   = filedetail[len(filedetail)-1].small.string  #最後一個是時間
	for i in range(1,len(filedetail)-1):
		item = filedetail[i]
		try:
			file_url = ischool_url + item.a.get("href")
			file_extension = extension_list[i]
		except:
			continue
	print('{:2d}.{}'.format(index,filename) )

download_index_list = [ i for i in range(0,len(soup)) ]
input_index = input("請輸入要下載編號( ex: 1,2,3,4 如果要下載全部請直接按Enter):\n")
input_index = input_index.replace(' ','')
if input_index != '':
	try:
		index_list = []
		for i in input_index.split(','): 
			index_list.append(int(i))
		download_index_list = index_list
	except:
		print("輸入格式錯誤")


os.system("cls") # windows


class ProgressBar(object):
	def __init__(self, title,
				 count=0.0,
				 run_status=None,
				 fin_status=None,
				 total=100.0,
				 unit='', sep='/',
				 chunk_size=1.0):
		super(ProgressBar, self).__init__()
		self.info = "%s %s %.2f %s %s %.2f %s"
		self.title = get_display( 80 , title)
		self.total = total
		self.count = count
		self.chunk_size = chunk_size
		self.status = run_status or ""
		self.fin_status = fin_status or " " * len(self.status)
		self.unit = unit
		self.seq = sep

	def __get_info(self):
		# 【名稱】狀態 進度 單位 分割線 總數 單位
		_info = self.info % (self.title, self.status,
							 self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)
		return _info

	def refresh(self, count=1, status=None):
		self.count += count
		# if status is not None:
		self.status = status or self.status
		end_str = "\r"
		if self.count >= self.total:
			end_str = '\n'
			self.status = status or self.fin_status
		print(self.__get_info(), end=end_str)


error_file_char = [ "/" , "|" ,'\\',"?",'"' ,'*' ,":" ,"<" ,">" ,"." , \
					"/" , "："]
file_extension = str()
file_url       = str()


exist_file = os.listdir(store_location)
for index,onefile in enumerate(soup):
	if index not in download_index_list:
		continue
		
	filedetail = onefile.find_all("td")
	filename   = filedetail[0].string                        #第一個放檔名
	filetime   = filedetail[len(filedetail)-1].small.string  #最後一個是時間
	
	
	for i in range(1,len(filedetail)-1):
		item = filedetail[i]
		try:
			file_url = ischool_url + item.a.get("href")
		except:
			continue
	for char in error_file_char: #去除檔名違法字元
		filename = filename.replace(char," ")
	
	with closing(res.get(file_url, verify = define_verify , stream=True)) as response:
		file_extension = response.headers['Content-Disposition']
		file_extension = str(file_extension)
		file_extension = file_extension.split('"')[1]
		file_extension = file_extension.split('.')[-1]
		file_size = response.headers['content-length']  
		filename = filename + "." + file_extension
		
		if filename in exist_file:
			display = get_display( 80 , filename)
			print("{:s} 已存在".format(display))
			continue
		
		new_exist_file = os.listdir(store_location)
		
		repeat_file_name = filename
		time = 1
		while repeat_file_name in new_exist_file:
			repeat_file_name = filename.split('.')[0] + '_' + str(time) + '.' + filename.split('.')[1]
		filename = repeat_file_name
		
		
		chunk_size = 1024 # 單次請求最大值
		content_size = int(file_size) # 內容體總大小
		progress = ProgressBar(filename, total=content_size,
										 unit="KB", chunk_size=chunk_size, run_status="正在下載", fin_status="下載完成")
		with open(store_location + "\\" + filename,'wb') as file:
			for data in response.iter_content(chunk_size=chunk_size):
				file.write(data)
				progress.refresh(count=len(data))
		file.close()
	


input("按任意建結束")



