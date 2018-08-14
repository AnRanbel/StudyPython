import itchat
import json
import requests
from itchat.content import *

def getResponse(_info):
	#print(_info)
	apiUrl = "http://openapi.tuling123.com/openapi/api/v2"
	data = {
		"reqType": 0,
		"perception": {
			"inputText": {
				"text": _info
			},
			"inputImage": {
				"url": _info
			},
			"selfInfo": {
				"location": {
					"city": "重庆",
					"province": "重庆",
					"street": "学府大道"
				}
			}
		},
		"userInfo": {
			"apiKey": "ab2bc8ca07fe46b79842d01418e2d21e",
			"userId": "wyjason1220"
		}
	}
	data = json.dumps(data).encode("utf-8") #将字典格式的data(request)编码为utf-8
	r = requests.post(apiUrl, data=data).json()
	return r

#自动回复
# 文字
@itchat.msg_register(TEXT)
def auto_reply(msg):
	# NickName = msg['User']['NickName']
	# user = itchat.search_friends(name=NickName)[0]
	# user.send(u"山风大哥家的baozi：" + getResponse(msg['Text'])['results'][0]['values']['text'])
	userid = msg['FromUserName']  # 每个用户和群聊都会使用很长的ID来区分
	temp=getResponse(msg['Text'])
	#回复新闻
	#判断是否是新闻标志类
	if temp['intent']['code']==10003:   #是
		if temp['results'][1]['resultType']=='news':
			buff1=temp['results'][0]['values']['text']
			news=temp['results'][1]['values']['news']
			buff2=""
			for new in news:
				buff2=buff2+"\n标题：（"+new['info']+"）"+new['name']+"\n链接："+new['detailurl']
			itchat.send(u"山风大哥家的baozi：" + buff1 + buff2,userid)
		else:
			buff1=temp['results'][1]['values']['text']
			buff2=temp['results'][0]['values']['url']
			itchat.send(u"山风大哥家的baozi："+buff1+"\n链接："+buff2,userid)
	else:   #普通回复
		itchat.send(u"山风大哥家的baozi：" + temp['results'][0]['values']['text'],userid)

# 图片
@itchat.msg_register(PICTURE)
def auto_reply(msg):
	NickName = msg['User']['NickName']
	user = itchat.search_friends(name=NickName)[0]
	user.send_image('../images/cute_pig.gif')
	download_files(msg,user)  # 下载图片

#语音
# @itchat.msg_register(VOICE)
# def auto_reply(msg):
# 	NickName = msg['User']['NickName']
# 	user = itchat.search_friends(name=NickName)[0]
# 	user.send_image('../images/cute_pig.gif')

#处理多媒体类消息（图片、录音、文件、视频）
@itchat.msg_register([RECORDING,ATTACHMENT,VIDEO])
def download_files(msg,user):
	msg['Text'](msg['FileName'])    #msg['Text']是一个文件下载函数

	#向发送者发回去
	"""
		send(msg,toUserName)
		msg:文本消息内容
		@fil@path_to_file:发送文件
		@img@path_to_img:发送图片
		@vid@path_to_video:发送视频
		
		ithcat.send("@fil@%s" % '/tmp/test.text')
		ithcat.send("@img@%s" % '/tmp/test.png')
		ithcat.send("@vid@%s" % '/tmp/test.mkv')
	"""
	user.send("I have received this %s." %msg['Type'])
	#return '@%s@%s' % ({'Picture': 'img', 'Video': 'vid'}.get(msg['Type'], 'fil'), msg['FileName'])

#处理好友添加请求
@itchat.msg_register(FRIENDS)
def add_friend(msg):
	#该操作会自动将新好友的消息录入，不需要重载通讯录
	itchat.add_friend(**msg['Text'])    #**kwargs表示关键字参数，为dict
	#加完好友后，打招呼
	itchat.send_msg('Nice to meet you!',msg['RecommendInfo']['UserName'])


if __name__ == '__main__':
	itchat.auto_login(hotReload=True)
	user = itchat.search_friends(name=u'上官延叶')[0]
	user.send(u"How Are You?")
	itchat.run()
