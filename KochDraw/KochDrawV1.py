#KochDrawV1.py
#科赫曲线小包裹

import turtle
def koch(size,n):  #size->源曲线长度,n->阶数
     if n==0:
         turtle.fd(size)    #直接绘制一条直线
     else:
         for angle in [0,60,-120,60]:   #left为“海龟”方向(相对)
             turtle.left(angle)
             koch(size/3,n-1)

def main():
    turtle.setup(600,600)
    turtle.penup()
    turtle.goto(-200,100)
    turtle.pendown()
    turtle.pensize(2)
    # 科赫曲线的绘制
    # koch(400,3)     #3阶科赫曲线

    #科赫雪花的绘制
    level=3     #三阶科赫雪花
    turtle.color("red")
    koch(400,level)
    turtle.right(120)
    turtle.color("green")
    koch(400,level)
    turtle.right(120)
    turtle.color("blue")
    koch(400,level)
    turtle.hideturtle()
    turtle.done()

main()