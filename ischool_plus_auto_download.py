from bs4 import BeautifulSoup
from contextlib import closing
import requests
import getpass
import urllib3
import time
import sys
import os
import re
import hashlib
from PrettyPrint import *
from MyEncrypt import *
from ProgressBar import *

define_verify = False

dirname = "北科i學園資料"
#-------------------------創建資料夾-------------------------#
try:
	os.mkdir(dirname)
except FileExistsError:
	pass


inputuserid   = str()
inputpassword = str()

urllib3.disable_warnings() 
#-------------------------取得登入資料-------------------------#

try:
	f = open('login.txt', 'r')
	inputuserid = f.readline().replace("\n","")
	inputpassword = f.readline().replace("\n","")	
	encrypt_key = inputuserid[:7]
	pc = prpcrypt( encrypt_key )  # 初始化金鑰
	decrypt_inputpassword = pc.decrypt(inputpassword)
	inputpassword = decrypt_inputpassword
	print(inputuserid)
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
	
#-------------------------創建一個session-------------------------#

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



#-------------------------登入-------------------------#
print("登入IShool Plus系統")

url = "https://istudy.ntut.edu.tw/mooc/login.php"
#取得登入資料
title = res.get(url,verify = define_verify)
soup = BeautifulSoup(title.text, 'html.parser')

form = soup.find_all('form')

items = form[2].find_all("input")
for item in items:
	if item.get("name") == "login_key":
		login_key = item.get("value")

data = inputpassword
md5 = hashlib.md5()
md5.update(data.encode("utf-8"))
md5key = md5.hexdigest()
cypkey  = md5key[0:4] + login_key[0:4];



encrypt_pwd = DesEncrypt(inputpassword, cypkey)
encrypt_pwd = encrypt_pwd.decode("utf-8")

url = "https://istudy.ntut.edu.tw/login.php";

post_data = {
		"reurl"        : ""     ,
		"login_key"   : login_key ,    
		"encrypt_pwd"   : encrypt_pwd ,  
		"username"   : inputuserid ,  
		"password"   : len(inputpassword) * '*' ,  
		"password1"   : "cm9iZXJ0MTM1Nzk=" ,  
	}

result = res.post(url , data = post_data ,verify = define_verify )

print("登入成功")

#-------------------------取得課程名稱-------------------------#
url = "https://istudy.ntut.edu.tw/learn/mooc_sysbar.php"

result = res.get(url,verify = define_verify)

soup = BeautifulSoup(result.text, 'html.parser')
soup = soup.find( id = "selcourse" );
soup = soup.find_all( "option" )[1:]

course_name_list = []
for index,s in enumerate(soup):
	course = {}
	course['name'] = s.text
	course['value'] = s.get("value")
	course_name_list.append(course)

os.system("cls") # windows

#-------------------------顯示課程名稱-------------------------#

last_year = 0
count = 0
for index,s in enumerate(course_name_list):
	name = s["name"].split('_')
	s["realname"] = name[1]
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

#-------------------------等待用戶選擇-------------------------#
while True:
	course_number = input("\n輸入下載號碼:")
	try:
		course_number = int(course_number)
		course_select = course_name_list[course_number]
		break
	except:
		print("輸入號碼有誤")

course_id = course_select["value"]
couesename = course_select["realname"]

os.system("cls") # windows

print( couesename )

store_location = str()
try:
	store_location = os.path.join(dirname , couesename)
	os.mkdir(store_location)
except FileExistsError:
	pass
	#print("資料夾已存在")



#-------------------------選擇選中的課程-------------------------#
url = "https://istudy.ntut.edu.tw/learn/goto_course.php"
xml = "<manifest><ticket/><course_id>{}</course_id><env/></manifest>".format( course_id )
result = res.post(url , data = xml)


#-------------------------取得課程頁面cid-------------------------#
url = "https://istudy.ntut.edu.tw/learn/path/launch.php"  
result = res.get(url)

re_sreach= r"'(?P<url>/.+)'"
course_url = re.search(re_sreach, result.text).groupdict()['url']

re_sreach= r"cid=(?P<cid>(\w)+)"
cid = re.search(re_sreach, result.text).groupdict()['cid']

#-------------------------取得下載檔案參數-------------------------#
url = "https://istudy.ntut.edu.tw/learn/path/pathtree.php?cid={}".format(cid)

result = res.get(url)
download_data = {
		'is_player'			: '',
		'href'				: '',
		'prev_href'			: '',
		'prev_node_id'		: '',
		'prev_node_title'	: '',
		'is_download'		: '',
		'begin_time'		: '',
		'course_id'			: '',
		'read_key'			: ''
	}

soup = BeautifulSoup(result.text, 'html.parser')
form  = soup.find( id = "fetchResourceForm" )

for i in form.find_all("input"):
	key = i.get("name")
	if key in download_data.keys():
		download_data[key] = i.get("value")

#-------------------------取得下載檔案真實名稱與下載連結-------------------------#


url = "https://istudy.ntut.edu.tw/learn/path/SCORM_loadCA.php"
result = res.get(url)

soup = BeautifulSoup(result.text, 'lxml')
items = soup.find_all( "item" )
resources = soup.find_all( "resource" )

file_list = []
for item,resource in zip(items,resources):
	file = {}
	base = resource.get("xml:base")
	file['href'] = (base if base != None else '') + '@' + resource.get("href")
	file['name'] = item.text.split("\t")[0].replace("\n" , "")
	file_list.append(file)


for index,s in enumerate(file_list):
	name = s["name"]
	print("{:2d}.{:s}".format(index , name))

#-------------------------等待用戶選擇-------------------------#
download_index_list = [ i for i in range(0,len(file_list)) ]
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


error_file_char = [ "/" , "|" ,'\\',"?",'"' ,'*' ,":" ,"<" ,">" ,"." , \
					"/" , "："]
file_extension = str()
file_url       = str()


exist_file = os.listdir(store_location)
for index,file_item in enumerate(file_list):
	if index not in download_index_list:  #只下載有選擇的
		continue
		
	filename = file_item['name']
	file_href = file_item['href']
	
	download_data['href'] = file_href
	
	#-------------------------取得下載檔案真實下載連結-------------------------#
	url = "https://istudy.ntut.edu.tw/learn/path/SCORM_fetchResource.php"

	result = res.post(url , data = download_data , allow_redirects=False)

	if result.is_redirect:  #發生需要重新導向 代表出現檔案預覽畫面
		rsps = res.resolve_redirects(result, result.request)
		for rsp in rsps:
			url = rsp.url.replace("download_preview" , "download")
			break
	else:
		try:
			re_sreach= r"\"(?P<url>/.+)\""
			file_url = re.search(re_sreach, result.text).groupdict()['url']
			url = "https://istudy.ntut.edu.tw" + file_url;
		except AttributeError:  #可能是PDF預覽
			re_sreach= r"\"(?P<url>.+)\""
			file_url = re.search(re_sreach, result.text).groupdict()['url']
			url = "https://istudy.ntut.edu.tw/learn/path/" + file_url;
			result = res.get( url );
			re_sreach= r"DEFAULT_URL.+'(?P<url>.+)'"
			file_url = re.search(re_sreach, result.text).groupdict()['url']
			url = "https://istudy.ntut.edu.tw/learn/path/" + file_url;
			
	
	file_url = url
	#-------------------------處理下載檔名並開使下載-------------------------#

	for char in error_file_char: #去除檔名違法字元
		filename = filename.replace(char," ")
	
	with closing(res.get(file_url, verify = define_verify , stream=True)) as response:
		file_net_name = response.headers['Content-Disposition']
		re_sreach= r"('|\")(?P<name>.+)('|\")"
		file_net_name = re.search(re_sreach, file_net_name ).groupdict()['name']
		file_extension = file_net_name.split('.')[-1]
		if response.headers.__contains__('content-length'):
			file_size = response.headers['content-length']  
		else:
			file_size = 0;
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
		progress.endPrint()
		file.close()



input("按任意建結束");



