import base64
import pyDes
from binascii import b2a_hex, a2b_hex
from Cryptodome.Cipher import AES


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


def DesEncrypt(str,key):
	# str 明文password
	# key uid
	Des_Key = (key+"0000")[0:8]
	#k = des(Des_Key, CBC, Des_IV, pad=None, padmode=PAD_PKCS5)
	k = pyDes.des(Des_Key  ,padmode=pyDes.PAD_PKCS5)
	EncryptStr = k.encrypt(str)
	return base64.b64encode(EncryptStr) #转base64编码返回

def DesDecrypt(str,key):
	# str 密文password
	# key uid
	Des_Key = (key+"0000")[0:8]
	EncryptStr = base64.b64decode(str)
	#k = pyDes.des(Des_Key, pyDes.CBC, Des_IV, pad=None, padmode=pyDes.PAD_PKCS5)
	k = pyDes.des(Des_Key, padmode=pyDes.PAD_PKCS5)
	DecryptStr = k.decrypt(EncryptStr)
	return DecryptStr 