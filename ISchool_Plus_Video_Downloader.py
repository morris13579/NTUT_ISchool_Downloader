from cmath import log
from ftplib import ftpcp
from tkinter import E
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
from download import downloadMain #引入download.py
import urllib.parse

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

print("登入校園入口網站...")
post_data = {
		"muid"        : inputuserid     ,
		"mpassword"   : inputpassword   
	}

url     = "https://nportal.ntut.edu.tw/login.do"  #登入網址

login = res.post(url , data = post_data )
url 

if "myPortal.do" in login.text:
	loginpass = True
	url_start = login.text.find('"')
	url_start += 1
	url_end   = login.text.find('"' , url_start)
	url_jump = login.text[url_start:url_end]
	print ("登入成功") 
	
elif "帳號或密碼錯誤" in login.text:
	input ("帳號或密碼錯誤")
	exit()
else:
	pass
	# login_fail_time += 1
	# input ("失敗{0}次嘗試重新登入" .format(login_fail_time) )
	# exit()

print("登入IShool Plus系統")
url = "https://nportal.ntut.edu.tw/ssoIndex.do?apUrl=https://istudy.ntut.edu.tw/login.php&apOu=ischool_plus_&sso=true&datetime1=1582549002044"
result = res.get(url)
soup = BeautifulSoup(result.text, 'html.parser')
url = str()

post_data = {}

getsessionId = soup.find_all('form')
for item in getsessionId:
	if item.get("name") == "ssoForm":
		url = item.get("action")  #取得跳轉網址
		break

getsessionId = soup.find_all('input')
for item in getsessionId:
	post_data[item.get("name")] = item.get("value")

result = res.post(url  , data = post_data )

print("登入成功")

#-------------------------取得課程名稱-------------------------#
url = "https://istudy.ntut.edu.tw/learn/mooc_sysbar.php"

result = res.get(url)

soup = BeautifulSoup(result.text, 'html.parser')
soup = soup.find( id = "selcourse" )
soup = soup.find_all( "option" )[1:]

course_name_list = []
for index,s in enumerate(soup):
	course = {}
	course['name'] = s.text
	course['value'] = s.get("value")
	course_name_list.append(course)

os.system("cls") # windows

#-------------------------顯示課程名稱-------------------------#

#course_name_list.reverse()

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

file_list = []
for item in items:
	iref = item.get("identifierref");
	if iref == None : 
		continue
	resource = soup.find( "resource" , attrs={"identifier": iref } )
	file = {}
	base = resource.get("xml:base")
	file['href'] = (base if base != None else '') + '@' + resource.get("href")
	file['name'] = item.text.split("\t")[0].replace("\n" , "")
	if '[錄]' not in file['name']:
		continue
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


error_file_char = [ "/" , "|" ,'\\',"?",'"' ,'*' ,":" ,"<" ,">" , \
					"/" , "："]
file_extension = str()
file_url       = str()
video_list = []
videoName = []

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
	
	re_sreach = r"[\"|'](?P<url>https?:\/\/[\w|\:|\/|\.|\+|\s|\?|%|#|&|=|-]+)[\"|']"  #檢測http或https開頭網址
	re_result = re.search(re_sreach, result.text)
	if re_result != None:
		file_url = re_result.groupdict()['url']
		print(file_url)
		if 'istream.ntut.edu.tw' in file_url:
			print( "\n" + filename , end = '\n')
			query = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(file_url).query))
			result = res.get(file_url)
			soup = BeautifulSoup(result.text, 'html.parser')
			sourse_list = soup.find_all("source")
			
			for n in sourse_list:
				name = n.get('id')
				if name != None:
					print( '{}'.format(name) )
					savename = filename +  "_" + name + ".mp4"
					#-------------------------等待用戶選擇-------------------------#
					select = input('按Enter下載 or 輸入(Y/N):')
					if 'n' in select.lower():
						continue
					else:
						video_list.append("https://istream.ntut.edu.tw/videoplayer/" + n.get('src'))
						videoName.append(savename)
						
os.system('cls')
downloadMain(video_list,videoName,store_location) #呼叫download.py 裡面的函數


input("按任意建結束");
