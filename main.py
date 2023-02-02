"""Pacman"""

from random import choice
from turtle import *

from freegames import floor, vector

puntos = {'puntuacion': 0} #Puntuación del usuario.
camino = Turtle(visible=False) #Caminos del mapa.
movimiento = Turtle(visible=False) #Movimientos del pacman y de los fantasmas
aim = vector(5, 0) #Apuntado
pacman = vector(-40, -80) #Posicion inicial del pacman

#Posicion inicial fantasmas
ghosts = [
    [vector(-180, 160), vector(5, 0)],
    [vector(-180, -160), vector(0, 5)],
    [vector(100, 160), vector(0, -5)],
    [vector(100, -160), vector(-5, 0)],
]
#Mapa
casillas = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0,
    0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
    0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
]


def cuadado(x, y):
    """Dibuja un cuadrado usando la ruta (x, y)."""
    camino.up()
    camino.goto(x, y)
    camino.down()
    camino.begin_fill()

    for count in range(4):
        camino.forward(20)
        camino.left(90)

    camino.end_fill()


def desplazamiento(point):
    """Devuelve el desplazamiento del punto."""
    x = (floor(point.x, 20) + 200) / 20
    y = (180 - floor(point.y, 20)) / 20
    index = int(x + y * 20)
    return index


def validador(point):
    """Devuelve True si el punto es válido."""
    index = desplazamiento(point)

    if casillas[index] == 0:
        return False

    index = desplazamiento(point + 19)

    if casillas[index] == 0:
        return False

    return point.x % 20 == 0 or point.y % 20 == 0


def mapeado():
    """Dibuja el mapa usando la ruta."""
    bgcolor('black')
    camino.color('blue')

    for index in range(len(casillas)):
        tile = casillas[index]

        if tile > 0:
            x = (index % 20) * 20 - 200
            y = 180 - (index // 20) * 20
            cuadado(x, y)

            if tile == 1:
                camino.up()
                camino.goto(x + 10, y + 10)
                camino.dot(2, 'white')


def move():
    """Mueve pacman y todos los fantasmas."""
    movimiento.undo()
    movimiento.write(puntos['puntuacion'])

    clear()

    if validador(pacman + aim):
        pacman.move(aim)

    index = desplazamiento(pacman)

    if casillas[index] == 1:
        casillas[index] = 2
        puntos['puntuacion'] += 1
        x = (index % 20) * 20 - 200
        y = 180 - (index // 20) * 20
        cuadado(x, y)

    up()
    goto(pacman.x + 10, pacman.y + 10)
    dot(20, 'yellow')

    for point, course in ghosts:
        if validador(point + course):
            point.move(course)
        else:
            options = [
                vector(5, 0),
                vector(-5, 0),
                vector(0, 5),
                vector(0, -5),
            ]
            plan = choice(options)
            course.x = plan.x
            course.y = plan.y

        up()
        goto(point.x + 10, point.y + 10)
        dot(20, 'red')

    update()

    for point, course in ghosts:
        if abs(pacman - point) < 20:
            return

    ontimer(move, 100)


def cambiar(x, y):
    """Cambia el aim del pacman pacman si se puede."""
    if validador(pacman + vector(x, y)):
        aim.x = x
        aim.y = y


setup(420, 420, 370, 0)
hideturtle()
tracer(False)
movimiento.goto(160, 160)
movimiento.color('white')
movimiento.write(puntos['puntuacion'])
listen()
onkey(lambda: cambiar(5, 0), 'd')
onkey(lambda: cambiar(-5, 0), 'a')
onkey(lambda: cambiar(0, 5), 'w')
onkey(lambda: cambiar(0, -5), 's')
mapeado()
move()
done()
