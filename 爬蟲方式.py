#https://istudy.ntut.edu.tw/mooc/login.php
#使用post方式
'''
"reurl"        : ""     ,
"login_key"   : html hidden項目 ,    
"encrypt_pwd"   : 使用密碼用DES加密 ,  
"username"   : 學號 ,  
"password"   : 密碼長度 * '*' ,  
"password1"   : "cm9iZXJ0MTM1Nzk=" ,
'''
#登入加密方式 使用DES zeropadding
"""
var md5key  = MD5(node.password.value);
var cypkey  = md5key.substr(0,4) + node.login_key.value.substr(0,4);
node.encrypt_pwd.value = stringToBase64(des(cypkey, node.password.value, 1));
	/*** CUSTOM by Yea ***/
node.password1.value   = stringToBase64(node.password.value);
node.password.value    = pwdmask.substr(0,node.password.value.length);
"""


#https://istudy.ntut.edu.tw/learn/mooc_sysbar.php  取得課程名稱
#可以取得課程名稱與course_id用於使用goto_course切換選擇課程

#https://istudy.ntut.edu.tw/learn/mooc_header.php  
#取得登入學生名字

#https://istudy.ntut.edu.tw/mooc/controllers/forum_ajax.php  
#取得公告

#https://istudy.ntut.edu.tw/learn/goto_course.php?<manifest><ticket/><course_id>10057895</course_id><env/></manifest>: 
#去到指定課程

#https://istudy.ntut.edu.tw/learn/path/launch.php 
#取得課程cid，用使用pathtree.php取得下載回傳參數

#https://istudy.ntut.edu.tw/learn/path/pathtree.php?cid=hx6y5E6Kqkw,  
#取得SCORM_fetchResource POST回傳參數

#https://istudy.ntut.edu.tw/learn/path/SCORM_loadCA.php  
#取得下載檔案XML 取得下載檔案名稱與下載href(由base與href組成)
'''
href產生方式
var base = resource.getAttribute('xml:base') == null ? ' ' : resource.getAttribute('xml:base');
var href = base + '@' + resource.getAttribute('href');
objForm.href.value = href;
'''
#https://istudy.ntut.edu.tw/learn/path/SCORM_fetchResource.php  
#取得下載檔案真實下載連接 使用POST方式
#發生例外302 跑到檔案預覽畫面
'''
https://istudy.ntut.edu.tw/learn/path/download_preview.php?path=z1AeXRPiVW2u5IpLTt2_3cp60q8xE1L4KpmAf_3uPVOuUEIAGUlvAgPTjsraf1rFK1TZjkxTDGLK8O1pjunXigCgJGIJhjHW

https://istudy.ntut.edu.tw/learn/path/download.php?path=z1AeXRPiVW2u5IpLTt2_3cp60q8xE1L4KpmAf_3uPVOuUEIAGUlvAgPTjsraf1rFK1TZjkxTDGLK8O1pjunXigCgJGIJhjHW
'''

'''
is_player: false
href: z1AeXRPiVW2u5IpLTt2_3RidAguU9RbKC0UTIQLGYFX_lL_zzS67Ag,,@YPLoX79HAQxYhdCzJ3qQuVhsyaT4Cjz2
prev_href: 
prev_node_id: 
prev_node_title: 
is_download: 
begin_time: 2020-02-21 11:11:21
course_id: hx6y5E6Kqkw,
read_key: b1c2954c8e14434d3038ac6e6ea2652e
'''

#下載檔案兩種可能的 Content-Disposition
'''
inline;filename='ebook.pdf'

attachment; filename="20190920121358wk2_Matlab%E7%B0%A1%E4%BB%8B%E5%8F%8A%E4%B8%80%E7%B6%AD%E8%A8%8A%E8%99%9F%E5%90%91%E9%87%8F.ppt";
'''


