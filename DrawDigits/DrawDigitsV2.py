# DrawDigitsV2.py
import turtle
import time
import DrawDigitsV1 as drawv1  # 引用同一文件路径下另一.py文件函数


# def drawGap():      #设置字符间隔(相当于实现空格效果)
#     turtle.penup()
#     turtle.forward(20)

def drawDate(date):  # 获得要输出的数字
    for i in date:
        if i == '-':
            turtle.write('年', font=("Arial", 18, "normal"))  # 输出字符串
            turtle.pencolor("green")
            turtle.fd(20)
        elif i == '=':
            turtle.write('月', font=("Arial", 18, "normal"))
            turtle.pencolor("blue")
            turtle.fd(20)
        elif i == '+':
            turtle.write('日', font=("Arial", 18, "normal"))
            turtle.pencolor("pink")
            turtle.fd(20)
        elif i == ':':
            turtle.write(':', font=("Arial", 18, "bold"))
            turtle.fd(20)
        else:
            drawv1.drawDigit(eval(i))
        drawv1.drawGap(20)


def main():
    turtle.setup(1300, 400, 200, 200)
    turtle.penup()
    turtle.fd(-620)
    turtle.pensize(5)
    turtle.pencolor("red")
    str = time.strftime("%Y-%m=%d+%H:%M:%S")
    drawDate(str)
    turtle.hideturtle()  # “海龟”隐身
    turtle.done()


main()
