import string
from collections import namedtuple

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