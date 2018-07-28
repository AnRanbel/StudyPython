# CalSportCompeV1.py

#排球运动

import random

#打印提示信息
def printInfo():
	print("这个程序模拟两个选手A和B的某种竞技比赛：")
	print("程序运行需要A和B的能力值（以0到1之间的小数表示）：")


#获取输入信息
def getInputs():
	proA = eval(input("请输入选手A的能力值（0-1）："))
	proB = eval(input("请输入选手B的能力值（0-1）："))
	n = eval(input("模拟比赛的场次："))
	return proA, proB, n


def simNGames(proA, proB, n):
	countA, countB = 0, 0
	for i in range(n):          #n场模拟依次进行
		if SimOneGame(proA, proB) == 1:     #A方赢
			countA += 1
		else:       #B方赢
			countB += 1
	return countA, countB


def SimOneGame(proA, proB):
	#随机决定发球方（正式排球比赛中，通常以抛硬币的方式决定）
	temp=0.5
	while temp == 0.5:
		temp = random.random()
	if temp<0.5:
		serve = "A"  # 发球方
	else:
		serve="B"

	setA,setB=0,0       #赢的回合数
	while not gameOver(setA,setB):
		scoreA, scoreB = 0, 0       #每回合的分数
		while not setOver(scoreA, scoreB,setA+setB+1):      #每回合的最后一分肯定是此回合胜方所发，所以不需要再手动设定发球方
			if serve == "A":
				if random.random() < proA:      #A方赢
					scoreA += 1
				else:
					scoreB+=1
					serve = "B"
			else:
				if random.random() < proB:      #B方赢
					scoreB += 1
				else:
					scoreA+=1
					serve = "A"

		if scoreA>scoreB:
			setA+=1
		else:
			setB+=1

	return (1 if (setA > setB) else 0)

#判断回合是否结束
def setOver(scoreA, scoreB,sets):
	if sets==5:         #若比赛进行到第5回合
		if scoreA >= 15 or scoreB >= 15:
			if(abs(scoreA-scoreB)>=2):      #满15分相差2分及以上才算结束
				return True
			else:       #未满15分
				False
		else:
			return False
	else:           #第1-4回合
		if scoreA >= 25 or scoreB >= 25:
			if(abs(scoreA-scoreB)>=2):       #满25分相差2分及以上才算结束
				return True
			else:
				return False
		else:       #未满25分
			return False

#判断比赛是否结束
def gameOver(setA,setB):
	if setA==3 or setB==3:      #先赢三局者获胜
		return True
	else:
		return False

#输出最终结果
def printSummary(countA, countB):
	print("选手A获胜{0}场比赛，占比{1:.2f}%".format(countA, countA / (countA + countB) * 100))
	print("选手B获胜{0}场比赛，占比{1:.2f}%".format(countB, countB / (countA + countB) * 100))


#主函数
#main()
if __name__ == "__main__":
	printInfo()
	proA, proB, n = getInputs()
	print("竞技分析开始，共模拟{}场比赛".format(n))
	countA, countB = simNGames(proA, proB, n)
	printSummary(countA, countB)
