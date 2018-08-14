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
					"street": "解放碑"
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
	#回复图片
	elif temp['intent']['code']==10014:
		buff1 = temp['results'][1]['values']['text']
		buff2 = temp['results'][0]['values']['url']
		itchat.send(u"山风大哥家的baozi：" + buff1 + "\n链接：" + buff2, userid)
	#回复关键词
	elif ('秦岚' in msg['Text']) or ('秦嵐'in msg['Text']):
		return '秦岚（Qin Lan），1981年7月17日出生于辽宁省沈阳市，毕业于沈阳工业大学会计系，中国内地女演员、歌手。\
		2001年，出演个人首部电视剧《大唐情史》，从而正式进入演艺圈；2002年，因在古装爱情剧《还珠格格3》中饰演陈知画而崭露头角；\
		2003年，出演古装武侠剧《风云2》；2004年，主演古装爱情剧《护花奇缘》；2006年，出演古装励志剧《绣娘兰馨》；\
		2007年，因在青春爱情剧《又见一帘幽梦》中饰演汪绿萍而获得更多关注；2009年，出演剧情片《南京！南京！》；\
		2011年，凭借家庭伦理片《母语》荣获第三届英国万像国际华语电影节“最具潜力女演员奖”；2012年，凭借古装传奇片\
		《王的盛宴》荣获第七届亚洲电影节“最佳女配角”；同年，在古装传奇剧《楚汉传奇》中饰演吕雉；2013年，秦岚推\
		出首张个人EP《一肩之隔》；2014年，出演古装武侠剧《神雕侠侣》；2015年，在都市爱情剧《咱们相爱吧》中饰演蔡春妮；\
		2017年5月，秦岚担当出品人的网络电影《超级APP》在广州开机；2018年7月，在古装剧《延禧攻略》中饰演富察容音。'
	elif ('山风大哥' in msg['Text']) or ('山風大哥' in msg['Text']):
		itchat.send(u"山风大哥家的baozi：喏，就是下面这位小姐姐咯~", userid)
		itchat.send_image(fileDir='../images/shanfeng.gif', toUserName=userid)
	# 普通回复
	else:
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
	user.send(u"山风大哥家的baozi：I have received this %s." %msg['Type'])
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
	#向好友发消息
	#user = itchat.search_friends(name=u'xxx')[0] #将xxx换成任一好友的昵称
	#user.send(u"很高兴认识你~~")
	
	#向文件传输助手发消息
	itchat.send('Hello,filehelper',toUserName='filehelper')
	itchat.run()
