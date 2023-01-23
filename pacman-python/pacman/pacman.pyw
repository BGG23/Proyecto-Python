#Proyecto Pacman

import pygame, sys, os, random
from pygame.locals import *

# WIN???
SCRIPT_PATH=sys.path[0]

# Numero de casillas que no corresponden a un gift
# Actualmente solo "23" para la lista de puntajes más altos
NO_GIF_TILES=[23]

NO_WX=0 # Si se establece, el código de puntuación más alta no intentará preguntarle al usuario su nombre
USER_NAME="User" # USER_NAME=os.getlogin() # Nombre prederterminado

# Joystick por defecto
JS_DEVNUM=0 # device 0 (En pygame los joysticks siempre empiezan por 0).
JS_XAXIS=0 # axis 0 para derecha/izquierda.
JS_YAXIS=1 # axis 1 para arriba/abajo
JS_STARTBUTTON=0 # Número de botón para iniciar el juego.

# Debe ir antes de pygame.init()
pygame.mixer.pre_init(22050,16,2,512)
JS_STARTBUTTON=0 # Número de botón para iniciar el juego.
pygame.mixer.init()

clock = pygame.time.Clock()
pygame.init()

window = pygame.display.set_mode((1, 1))
pygame.display.set_caption("Pacman")

screen = pygame.display.get_surface()

img_Background = pygame.image.load(os.path.join(SCRIPT_PATH,"res","fondo","1.gif")).convert()

snd_pellet = {}
snd_pellet[0] = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sonido","pellet1.wav"))
snd_pellet[1] = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sonido","pellet2.wav"))
snd_powerpellet = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sonido","powerpellet.wav"))
snd_eatgh = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sonido","eatgh2.wav"))
snd_fruitbounce = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sonido","fruitbounce.wav"))
snd_eatfruit = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sonido","eatfruit.wav"))
snd_extralife = pygame.mixer.Sound(os.path.join(SCRIPT_PATH,"res","sonido","extralife.wav"))

ghostcolor = {}
ghostcolor[0] = (255, 0, 0, 255)
ghostcolor[1] = (255, 128, 255, 255)
ghostcolor[2] = (128, 255, 255, 255)
ghostcolor[3] = (255, 128, 0, 255)
ghostcolor[4] = (50, 50, 255, 255) # azul, vulnerable
ghostcolor[5] = (255, 255, 255, 255) # blanco, fantasma parpadeando

#      _______________________
# ___/  Definiciones de clases  \_______________________________________________

class game ():


    def gethiscores(self):
            """Si res/record.txt exists, leelo. Si no, devuelve el record predeterminado.
               Output is [ (score,name) , (score,name) , .. ]."""
            try:
              f=open(os.path.join(SCRIPT_PATH,"res","record.txt"))
              hs=[]
              for line in f:
                while len(line)>0 and (line[0]=="\n" or line[0]=="\r"): line=line[1:]
                while len(line)>0 and (line[-1]=="\n" or line[-1]=="\r"): line=line[:-1]
                score=int(line.split(" ")[0])
                name=line.partition(" ")[2]
                if score>99999999: score=99999999
                if len(name)>22: name=name[:22]
                hs.append((score,name))
              f.close()
              if len(hs)>6: hs=hs[:6]
              while len(hs)<6: hs.append((0,""))
              return hs
            except IOError:
              return self.defaulthiscorelist()
              
    def writehiscores(self,hs):
            """Da una nueva lista, escribe dentro del documento por defecto."""
            fname=os.path.join(SCRIPT_PATH,"res","record.txt")
            f=open(fname,"w")
            for line in hs:
              f.write(str(line[0])+" "+line[1]+"\n")
            f.close()
            
    def getplayername(self):
            """Pregunta al jugador su nombre, para colocarlo en la lista de records."""
            if NO_WX: return USER_NAME
            try:
              import wx
            except:
              print("Pacman Error: No tienes wx instalado. No puedo preguntarte tu nombre!")
              print( "     :(       Descarga wx en http://www.wxpython.org/")
              print( "     :(       Para evitar volver a ver este error, configure NO_WX en el archivo pacman.pyw.")
              return USER_NAME
            app=wx.App(None)
            dlog=wx.TextEntryDialog(None,"Estas en la lista de records! Name:")
            dlog.ShowModal()
            name=dlog.GetValue()
            dlog.Destroy()
            app.Destroy()
            return name
              
    def updatehiscores(self,newscore):
            """Añade una nueva puntuacion a la lista de recods."""
            hs=self.gethiscores()
            for line in hs:
              if newscore>=line[0]:
                hs.insert(hs.index(line),(newscore,self.getplayername()))
                hs.pop(-1)
                break
            self.writehiscores(hs)

    def makehiscorelist(self):
            "Lee el archivo de puntuación más alta y conviértalo en una superficie utilizable."

            f=pygame.font.Font(os.path.join(SCRIPT_PATH,"res","VeraMoBd.ttf"),10)
            scoresurf=pygame.Surface((276,86),pygame.SRCALPHA)
            scoresurf.set_alpha(200)
            linesurf=f.render(" "*18+"HIGH SCORES",1,(255,255,0))
            scoresurf.blit(linesurf,(0,0))
            hs=self.gethiscores()
            vpos=0
            for line in hs:
              vpos+=12
              linesurf=f.render(line[1].rjust(22)+str(line[0]).rjust(9),1,(255,255,255))
              scoresurf.blit(linesurf,(0,vpos))
            return scoresurf
            
    def drawmidgamehiscores(self):
            """Vuelve a dibujar la imagen de la lista de puntajes más altos después de que pacman muera."""
            self.imHiscores=self.makehiscorelist()

    def __init__ (self):
        self.levelNum = 0
        self.score = 0
        self.lives = 3
        
        # 1 = normal
        # 2 = golpea al fantasma
        # 3 = juego terminado
        # 4 = espera para ganar
        # 5 = esperar despues de comerte un fantasma
        # 6 = esperar despues de acabar rl nivel
        self.mode = 0
        self.modeTimer = 0
        self.ghostTimer = 0
        self.ghostValue = 0
        self.fruitTimer = 0
        self.fruitScoreTimer = 0
        self.fruitScorePos = (0, 0)
        
        self.SetMode( 3 )
        
        # variables de camara
        self.screenPixelPos = (0, 0) # posición x,y absoluta de la pantalla desde la esquina superior izquierda del nivel
        self.screenNearestTilePos = (0, 0) # posición de la casilla más cercana de la pantalla desde la esquina UL
        self.screenPixelOffset = (0, 0) # desplazamiento en píxeles de la pantalla desde su posición de mosaico más cercana
        
        self.screenTileSize = (23, 21)
        self.screenSize = (self.screenTileSize[1] * 16, self.screenTileSize[0] * 16)

        # dígitos numéricos de visualización
        self.digit = {}
        for i in range(0, 10, 1):
            self.digit[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text",str(i) + ".gif")).convert()
        self.imLife = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","life.gif")).convert()
        self.imGameOver = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","gameover.gif")).convert()
        self.imReady = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","ready.gif")).convert()
        self.imLogo = pygame.image.load(os.path.join(SCRIPT_PATH,"res","text","logo.gif")).convert()
        self.imHiscores = self.makehiscorelist()
        
    def StartNewGame (self):
        self.levelNum = 1
        self.score = 0
        self.lives = 3
        
        self.SetMode( 4 )
        thisLevel.LoadLevel( thisGame.GetLevelNum() )
            
    def AddToScore (self, amount):
        
        extraLifeSet = [25000, 50000, 100000, 150000]
        
        for specialScore in extraLifeSet:
            if self.score < specialScore and self.score + amount >= specialScore:
                snd_extralife.play()
                thisGame.lives += 1
        
        self.score += amount
        
    
    def DrawScore (self):
        self.DrawNumber (self.score, 24 + 16, self.screenSize[1] - 24 )
            
        for i in range(0, self.lives, 1):
            screen.blit (self.imLife, (24 + i * 10 + 16, self.screenSize[1] - 12) )
            
        screen.blit (thisFruit.imFruit[ thisFruit.fruitType ], (4 + 16, self.screenSize[1] - 20) )
            
        if self.mode == 3:
            screen.blit (self.imGameOver, (self.screenSize[0] / 2 - 32, self.screenSize[1] / 2 - 10) )
        elif self.mode == 4:
            screen.blit (self.imReady, (self.screenSize[0] / 2 - 20, self.screenSize[1] / 2 + 12) )
            
        self.DrawNumber (self.levelNum, 0, self.screenSize[1] - 12 )
            
    def DrawNumber (self, number, x, y):
        strNumber = str(int(number))
        for i in range(0, len(strNumber), 1):
            iDigit = int(strNumber[i])
            screen.blit (self.digit[ iDigit ], (x + i * 9, y) )
        
    def SmartMoveScreen (self):
            
        possibleScreenX = player.x - self.screenTileSize[1] / 2 * 16
        possibleScreenY = player.y - self.screenTileSize[0] / 2 * 16
        
        if possibleScreenX < 0:
            possibleScreenX = 0
        elif possibleScreenX > thisLevel.lvlWidth * 16 - self.screenSize[0]:
            possibleScreenX = thisLevel.lvlWidth * 16 - self.screenSize[0]
            
        if possibleScreenY < 0:
            possibleScreenY = 0
        elif possibleScreenY > thisLevel.lvlHeight * 16 - self.screenSize[1]:
            possibleScreenY = thisLevel.lvlHeight * 16 - self.screenSize[1]
        
        thisGame.MoveScreen( possibleScreenX, possibleScreenY )
        
    def MoveScreen (self, newX, newY ):
        self.screenPixelPos = (newX, newY)
        self.screenNearestTilePos = (int(newY / 16), int(newX / 16)) # nearest-tile position of the screen from the UL corner
        self.screenPixelOffset = (newX - self.screenNearestTilePos[1]*16, newY - self.screenNearestTilePos[0]*16)
        
    def GetScreenPos (self):
        return self.screenPixelPos
        
    def GetLevelNum (self):
        return self.levelNum
    
    def SetNextLevel (self):
        self.levelNum += 1
        
        self.SetMode( 4 )
        thisLevel.LoadLevel( thisGame.GetLevelNum() )
        
        player.velX = 0
        player.velY = 0
        player.anim_pacmanCurrent = player.anim_pacmanS
        
        
    def SetMode (self, newMode):
        self.mode = newMode
        self.modeTimer = 0
        
class node ():
    
    def __init__ (self):
        self.g = -1 # coste de movimiento para pasar del nodo anterior a este (generalmente +10)
        self.h = -1 # coste de movimiento estimado para pasar de este nodo al nodo final (pasos horizontales y verticales restantes * 10)
        self.f = -1 # coste total de movimiento de este nodo (= g + h)
        # nodo principal: se usa para rastrear la ruta de regreso al nodo inicial al final
        self.parent = (-1, -1)
        # tipo de nodo: 0 para espacio vacío, 1 para pared (opcionalmente, 2 para el nodo inicial y 3 para el final)
        self.type = -1
        
class path_finder ():
    
    def __init__ (self):
        # map es una matriz 1-DIMENSIONAL.
        # use la función Unfold( (row, col) ) para convertir un par de coordenadas 2D
        # en un índice 1D para usar con esta matriz.
        self.map = {}
        self.size = (-1, -1) # rows by columns
        
        self.pathChainRev = ""
        self.pathChain = ""
                
        # nodos inicial y final
        self.start = (-1, -1)
        self.end = (-1, -1)
        
        # nodo actual
        self.current = (-1, -1)
        
        # listas abiertas y cerradas de nodos a considerar
        self.openList = []
        self.closedList = []
        
        # utilizado en el algoritmo
        self.neighborSet = [ (0, -1), (0, 1), (-1, 0), (1, 0) ]
        
    def ResizeMap (self, numRows, numCols):
        self.map = {}
        self.size = (numRows, numCols)

        # inicializa el mapa path_finder a una matriz 2D de nodos vacíos
        for row in range(0, self.size[0], 1):
            for col in range(0, self.size[1], 1):
                self.Set( row, col, node() )
                self.SetType( row, col, 0 )
        
    def CleanUpTemp (self):
        
        # esto restablece las variables necesarias para una búsqueda
    
        self.pathChainRev = ""
        self.pathChain = ""
        self.current = (-1, -1)
        self.openList = []
        self.closedList = []
        
    def FindPath (self, startPos, endPos ):
        
        self.CleanUpTemp()
    
        self.start = startPos
        self.end = endPos
        
        # agregar nodo de inicio a la lista abierta
        self.AddToOpenList( self.start )
        self.SetG ( self.start, 0 )
        self.SetH ( self.start, 0 )
        self.SetF ( self.start, 0 )
        
        doContinue = True
        
        while (doContinue == True):
        
            thisLowestFNode = self.GetLowestFNode()

            if not thisLowestFNode == self.end and not thisLowestFNode == False:
                self.current = thisLowestFNode
                self.RemoveFromOpenList( self.current )
                self.AddToClosedList( self.current )
                
                for offset in self.neighborSet:
                    thisNeighbor = (self.current[0] + offset[0], self.current[1] + offset[1])
                    
                    if not thisNeighbor[0] < 0 and not thisNeighbor[1] < 0 and not thisNeighbor[0] > self.size[0] - 1 and not thisNeighbor[1] > self.size[1] - 1 and not self.GetType( thisNeighbor ) == 1:
                        cost = self.GetG( self.current ) + 10
                        
                        if self.IsInOpenList( thisNeighbor ) and cost < self.GetG( thisNeighbor ):
                            self.RemoveFromOpenList( thisNeighbor )
                            
                            
                        if not self.IsInOpenList( thisNeighbor ) and not self.IsInClosedList( thisNeighbor ):
                            self.AddToOpenList( thisNeighbor )
                            self.SetG( thisNeighbor, cost )
                            self.CalcH( thisNeighbor )
                            self.CalcF( thisNeighbor )
                            self.SetParent( thisNeighbor, self.current )
            else:
                doContinue = False
                        
        if thisLowestFNode == False:
            return False
                        
        # reconstructor de camino
        self.current = self.end
        while not self.current == self.start:
            # crea una representacion del camino usando R, L, D, U
            if self.current[1] > self.GetParent(self.current)[1]:
                self.pathChainRev += 'R' 
            elif self.current[1] < self.GetParent(self.current)[1]:
                self.pathChainRev += 'L'
            elif self.current[0] > self.GetParent(self.current)[0]:
                self.pathChainRev += 'D'
            elif self.current[0] < self.GetParent(self.current)[0]:
                self.pathChainRev += 'U'
            self.current = self.GetParent(self.current)
            self.SetType( self.current[0],self.current[1], 4)

        for i in range(len(self.pathChainRev) - 1, -1, -1):
            self.pathChain += self.pathChainRev[i]
        
        # establecer las posiciones de inicio y final para futuras referencias
        self.SetType( self.start[0],self.start[1], 2)
        self.SetType( self.end[0],self.start[1], 3)
        
        return self.pathChain

    def Unfold (self, row,col):
        # esta función convierte un par de coordenadas de matriz 2D
        # a un índice de matriz 1D, para la matriz de mapa 1D del objeto.
        return (row * self.size[1]) + col
    
    def Set (self, row,col, newNode):
        # establece el valor de una celda de mapa en particular
        self.map[ self.Unfold(row, col) ] = newNode
        
    def GetType (self,val):
        row,col = val
        return self.map[ self.Unfold(row, col) ].type
        
    def SetType (self,row,col, newValue):
        self.map[ self.Unfold(row, col) ].type = newValue

    def GetF (self, val):
        row,col = val
        return self.map[ self.Unfold(row, col) ].f

    def GetG (self, val):
        row,col = val
        return self.map[ self.Unfold(row, col) ].g
    
    def GetH (self, val):
        row,col = val
        return self.map[ self.Unfold(row, col) ].h
        
    def SetG (self, val, newValue ):
        row,col = val
        self.map[ self.Unfold(row, col) ].g = newValue

    def SetH (self, val, newValue ):
        row,col = val
        self.map[ self.Unfold(row, col) ].h = newValue
        
    def SetF (self, val, newValue ):
        row,col = val
        self.map[ self.Unfold(row, col) ].f = newValue
        
    def CalcH (self, val):
        row,col = val
        self.map[ self.Unfold(row, col) ].h = abs(row - self.end[0]) + abs(col - self.end[0])
        
    def CalcF (self, val):
        row,col = val
        unfoldIndex = self.Unfold(row, col)
        self.map[unfoldIndex].f = self.map[unfoldIndex].g + self.map[unfoldIndex].h
    
    def AddToOpenList (self, val):
        row,col = val
        self.openList.append( (row, col) )
        
    def RemoveFromOpenList (self, val ):
        row,col = val
        self.openList.remove( (row, col) )
        
    def IsInOpenList (self, val ):
        row,col = val
        if self.openList.count( (row, col) ) > 0:
            return True
        else:
            return False
        
    def GetLowestFNode (self):
        lowestValue = 1000 
        lowestPair = (-1, -1)
        
        for iOrderedPair in self.openList:
            if self.GetF( iOrderedPair ) < lowestValue:
                lowestValue = self.GetF( iOrderedPair )
                lowestPair = iOrderedPair
        
        if not lowestPair == (-1, -1):
            return lowestPair
        else:
            return False
        
    def AddToClosedList (self, val ):
        row,col = val
        self.closedList.append( (row, col) )
        
    def IsInClosedList (self, val ):
        row,col = val
        if self.closedList.count( (row, col) ) > 0:
            return True
        else:
            return False

    def SetParent (self, val, val2 ):
        row,col = val
        parentRow,parentCol = val2
        self.map[ self.Unfold(row, col) ].parent = (parentRow, parentCol)

    def GetParent (self, val ):
        row,col = val
        return self.map[ self.Unfold(row, col) ].parent
        
    def draw (self):
        for row in range(0, self.size[0], 1):
            for col in range(0, self.size[1], 1):
            
                thisTile = self.GetType((row, col))
                screen.blit (tileIDImage[ thisTile ], (col * 32, row * 32))
        
class ghost ():
    def __init__ (self, ghostID):
        self.x = 0
        self.y = 0
        self.velX = 0
        self.velY = 0
        self.speed = 1
        
        self.nearestRow = 0
        self.nearestCol = 0
        
        self.id = ghostID
        
        # 1 = normal
        # 2 = vulnerable
        self.state = 1
        
        self.homeX = 0
        self.homeY = 0
        
        self.currentPath = ""
        
        self.anim = {}
        for i in range(1, 7, 1):
            self.anim[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","ghost " + str(i) + ".gif")).convert()
            
            # frame cambio de color de los fantasmas
            for y in range(0, 16, 1):
                for x in range(0, 16, 1):
                
                    if self.anim[i].get_at( (x, y) ) == (255, 0, 0, 255):
                        # color fantasma rojo por defecto
                        self.anim[i].set_at( (x, y), ghostcolor[ self.id ] )
            
        self.animFrame = 1
        self.animDelay = 0
        
    def Draw (self):
        
        if thisGame.mode == 3:
            return False
        
        
        # ojos de fantasma --
        for y in range(4, 8, 1):
            for x in range(3, 7, 1):
                self.anim[ self.animFrame ].set_at( (x, y), (255, 255, 255, 255) )  
                self.anim[ self.animFrame ].set_at( (x+6, y), (255, 255, 255, 255) )
                
                if player.x > self.x and player.y > self.y:
                    #player is to lower-right
                    pupilSet = (5, 6)
                elif player.x < self.x and player.y > self.y:
                    #player is to lower-left
                    pupilSet = (3, 6)
                elif player.x > self.x and player.y < self.y:
                    #player is to upper-right
                    pupilSet = (5, 4)
                elif player.x < self.x and player.y < self.y:
                    #player is to upper-left
                    pupilSet = (3, 4)
                else:
                    pupilSet = (4, 6)
                    
        for y in range(pupilSet[1], pupilSet[1] + 2, 1):
            for x in range(pupilSet[0], pupilSet[0] + 2, 1):
                self.anim[ self.animFrame ].set_at( (x, y), (0, 0, 255, 255) )  
                self.anim[ self.animFrame ].set_at( (x+6, y), (0, 0, 255, 255) )    
        # -- final ojos fantasma
        
        if self.state == 1:
            
            screen.blit (self.anim[ self.animFrame ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
        elif self.state == 2:
            
            
            if thisGame.ghostTimer > 100:
                # azul
                screen.blit (ghosts[4].anim[ self.animFrame ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
            else:
                # parpadeo blanco y azul
                tempTimerI = int(thisGame.ghostTimer / 10)
                if tempTimerI == 1 or tempTimerI == 3 or tempTimerI == 5 or tempTimerI == 7 or tempTimerI == 9:
                    screen.blit (ghosts[5].anim[ self.animFrame ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
                else:
                    screen.blit (ghosts[4].anim[ self.animFrame ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
            
        elif self.state == 3:

            screen.blit (tileIDImage[ tileID[ 'glasses' ] ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
        
        if thisGame.mode == 6 or thisGame.mode == 7:
            
            return False
        
        self.animDelay += 1
        
        if self.animDelay == 2:
            self.animFrame += 1 
        
            if self.animFrame == 7:
                # wrap to beginning
                self.animFrame = 1
                
            self.animDelay = 0
            
    def Move (self):
        

        self.x += self.velX
        self.y += self.velY
        
        self.nearestRow = int(((self.y + 8) / 16))
        self.nearestCol = int(((self.x + 8) / 16))

        if (self.x % 16) == 0 and (self.y % 16) == 0:
            # si el fantasma vuelve a estar alineado con la cuadrícula
            # es decir, es hora de ir al siguiente elemento de la ruta
            
            if (self.currentPath):
                self.currentPath = self.currentPath[1:]
                self.FollowNextPathWay()
        
            else:
                self.x = self.nearestCol * 16
                self.y = self.nearestRow * 16
            
                self.currentPath = path.FindPath( (self.nearestRow, self.nearestCol), (player.nearestRow, player.nearestCol) )
                self.FollowNextPathWay()
            
    def FollowNextPathWay (self):
        
        
        if not self.currentPath == False:
        
            if len(self.currentPath) > 0:
                if self.currentPath[0] == "L":
                    (self.velX, self.velY) = (-self.speed, 0)
                elif self.currentPath[0] == "R":
                    (self.velX, self.velY) = (self.speed, 0)
                elif self.currentPath[0] == "U":
                    (self.velX, self.velY) = (0, -self.speed)
                elif self.currentPath[0] == "D":
                    (self.velX, self.velY) = (0, self.speed)
                    
            else:
                
                if not self.state == 3:

                    self.currentPath = path.FindPath( (self.nearestRow, self.nearestCol), (player.nearestRow, player.nearestCol) )
                    self.FollowNextPathWay()
                
                else:

                    self.state = 1
                    self.speed = self.speed / 4
                    
                    (randRow, randCol) = (0, 0)

                    while not thisLevel.GetMapTile(randRow, randCol) == tileID[ 'pellet' ] or (randRow, randCol) == (0, 0):
                        randRow = random.randint(1, thisLevel.lvlHeight - 2)
                        randCol = random.randint(1, thisLevel.lvlWidth - 2)

                    self.currentPath = path.FindPath( (self.nearestRow, self.nearestCol), (randRow, randCol) )
                    self.FollowNextPathWay()

class fruit ():
    def __init__ (self):
        # cuando la fruta no está en uso, está en la posición (-1, -1) fuera de la pantalla.
        self.slowTimer = 0
        self.x = -16
        self.y = -16
        self.velX = 0
        self.velY = 0
        self.speed = 1
        self.active = False
        
        self.bouncei = 0
        self.bounceY = 0
        
        self.nearestRow = (-1, -1)
        self.nearestCol = (-1, -1)
        
        self.imFruit = {}
        for i in range(0, 5, 1):
            self.imFruit[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","fruit " + str(i) + ".gif")).convert()
        
        self.currentPath = ""
        self.fruitType = 1
        
    def Draw (self):
        
        if thisGame.mode == 3 or self.active == False:
            return False
        
        screen.blit (self.imFruit[ self.fruitType ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1] - self.bounceY))

            
    def Move (self):
        
        if self.active == False:
            return False
        
        self.bouncei += 1
        if self.bouncei == 1:
            self.bounceY = 2
        elif self.bouncei == 2:
            self.bounceY = 4
        elif self.bouncei == 3:
            self.bounceY = 5
        elif self.bouncei == 4:
            self.bounceY = 5
        elif self.bouncei == 5:
            self.bounceY = 6
        elif self.bouncei == 6:
            self.bounceY = 6
        elif self.bouncei == 9:
            self.bounceY = 6
        elif self.bouncei == 10:
            self.bounceY = 5
        elif self.bouncei == 11:
            self.bounceY = 5
        elif self.bouncei == 12:
            self.bounceY = 4
        elif self.bouncei == 13:
            self.bounceY = 3
        elif self.bouncei == 14:
            self.bounceY = 2
        elif self.bouncei == 15:
            self.bounceY = 1
        elif self.bouncei == 16:
            self.bounceY = 0
            self.bouncei = 0
            snd_fruitbounce.play()
        
        self.slowTimer += 1
        if self.slowTimer == 2:
            self.slowTimer = 0
            
            self.x += self.velX
            self.y += self.velY
            
            self.nearestRow = int(((self.y + 8) / 16))
            self.nearestCol = int(((self.x + 8) / 16))

            if (self.x % 16) == 0 and (self.y % 16) == 0:
                # si la fruta vuelve a estar alineada con la rejilla
                # es decir, es hora de ir al siguiente elemento de la ruta
                
                if len(self.currentPath) > 0:
                    self.currentPath = self.currentPath[1:]
                    self.FollowNextPathWay()
            
                else:
                    self.x = self.nearestCol * 16
                    self.y = self.nearestRow * 16
                    
                    self.active = False
                    thisGame.fruitTimer = 0
            
    def FollowNextPathWay (self):
        

        # Solo sige este camino si se encuentra un camino posible!
        if not self.currentPath == False:
        
            if len(self.currentPath) > 0:
                if self.currentPath[0] == "L":
                    (self.velX, self.velY) = (-self.speed, 0)
                elif self.currentPath[0] == "R":
                    (self.velX, self.velY) = (self.speed, 0)
                elif self.currentPath[0] == "U":
                    (self.velX, self.velY) = (0, -self.speed)
                elif self.currentPath[0] == "D":
                    (self.velX, self.velY) = (0, self.speed)

class pacman ():
    
    def __init__ (self):
        self.x = 0
        self.y = 0
        self.velX = 0
        self.velY = 0
        self.speed = 2
        
        self.nearestRow = 0
        self.nearestCol = 0
        
        self.homeX = 0
        self.homeY = 0
        
        self.anim_pacmanL = {}
        self.anim_pacmanR = {}
        self.anim_pacmanU = {}
        self.anim_pacmanD = {}
        self.anim_pacmanS = {}
        self.anim_pacmanCurrent = {}
        
        for i in range(1, 9, 1):
            self.anim_pacmanL[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman-l " + str(i) + ".gif")).convert()
            self.anim_pacmanR[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman-r " + str(i) + ".gif")).convert()
            self.anim_pacmanU[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman-u " + str(i) + ".gif")).convert()
            self.anim_pacmanD[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman-d " + str(i) + ".gif")).convert()
            self.anim_pacmanS[i] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","sprite","pacman.gif")).convert()

        self.pelletSndNum = 0
        
    def Move (self):
        
        self.nearestRow = int(((self.y + 8) / 16))
        self.nearestCol = int(((self.x + 8) / 16))

        if not thisLevel.CheckIfHitWall(self.x + self.velX, self.y + self.velY, self.nearestRow, self.nearestCol):
            
            self.x += self.velX
            self.y += self.velY
            
            # revision de colisiones
            thisLevel.CheckIfHitSomething(self.x, self.y, self.nearestRow, self.nearestCol)
            
            # revision de colisiones con los fantasmas
            for i in range(0, 4, 1):
                if thisLevel.CheckIfHit( self.x, self.y, ghosts[i].x, ghosts[i].y, 8):
                    # hit a ghost
                    
                    if ghosts[i].state == 1:
                        # fantasma es normal
                        thisGame.SetMode( 2 )
                        
                    elif ghosts[i].state == 2:
                        # fantasma es vulnerable
                        thisGame.AddToScore(thisGame.ghostValue)
                        thisGame.ghostValue = thisGame.ghostValue * 2
                        snd_eatgh.play()
                        
                        ghosts[i].state = 3
                        ghosts[i].speed = ghosts[i].speed * 4
                        # mandar ojos a la caja
                        ghosts[i].x = ghosts[i].nearestCol * 16
                        ghosts[i].y = ghosts[i].nearestRow * 16
                        ghosts[i].currentPath = path.FindPath( (ghosts[i].nearestRow, ghosts[i].nearestCol), (thisLevel.GetGhostBoxPos()[0]+1, thisLevel.GetGhostBoxPos()[1]) )
                        ghosts[i].FollowNextPathWay()

                        thisGame.SetMode( 5 )
                        
            # revision de colisiones con frutas
            if thisFruit.active == True:
                if thisLevel.CheckIfHit( self.x, self.y, thisFruit.x, thisFruit.y, 8):
                    thisGame.AddToScore(2500)
                    thisFruit.active = False
                    thisGame.fruitTimer = 0
                    thisGame.fruitScoreTimer = 120
                    snd_eatfruit.play()
        
        else:
            self.velX = 0
            self.velY = 0
            
        if thisGame.ghostTimer > 0:
            thisGame.ghostTimer -= 1
            
            if thisGame.ghostTimer == 0:
                for i in range(0, 4, 1):
                    if ghosts[i].state == 2:
                        ghosts[i].state = 1
                self.ghostValue = 0
                
        thisGame.fruitTimer += 1
        if thisGame.fruitTimer == 500:
            pathwayPair = thisLevel.GetPathwayPairPos()
            
            if not pathwayPair == False:
            
                pathwayEntrance = pathwayPair[0]
                pathwayExit = pathwayPair[1]
                
                thisFruit.active = True
                
                thisFruit.nearestRow = pathwayEntrance[0]
                thisFruit.nearestCol = pathwayEntrance[1]
                
                thisFruit.x = thisFruit.nearestCol * 16
                thisFruit.y = thisFruit.nearestRow * 16
                
                thisFruit.currentPath = path.FindPath( (thisFruit.nearestRow, thisFruit.nearestCol), pathwayExit )
                thisFruit.FollowNextPathWay()
            
        if thisGame.fruitScoreTimer > 0:
            thisGame.fruitScoreTimer -= 1
            
        
    def Draw (self):
        
        if thisGame.mode == 3:
            return False
        
        # cambio de cara pacman
        if self.velX > 0:
            self.anim_pacmanCurrent = self.anim_pacmanR
        elif self.velX < 0:
            self.anim_pacmanCurrent = self.anim_pacmanL
        elif self.velY > 0:
            self.anim_pacmanCurrent = self.anim_pacmanD
        elif self.velY < 0:
            self.anim_pacmanCurrent = self.anim_pacmanU
            
        screen.blit (self.anim_pacmanCurrent[ self.animFrame ], (self.x - thisGame.screenPixelPos[0], self.y - thisGame.screenPixelPos[1]))
        
        if thisGame.mode == 1:
            if not self.velX == 0 or not self.velY == 0:
                self.animFrame += 1 
            
            if self.animFrame == 9:
                self.animFrame = 1
            
class level ():
    
    def __init__ (self):
        self.lvlWidth = 0
        self.lvlHeight = 0
        self.edgeLightColor = (255, 255, 0, 255)
        self.edgeShadowColor = (255, 150, 0, 255)
        self.fillColor = (0, 255, 255, 255)
        self.pelletColor = (255, 255, 255, 255)
        
        self.map = {}
        
        self.pellets = 0
        self.powerPelletBlinkTimer = 0
        
    def SetMapTile (self, row, col, newValue):
        self.map[ (row * self.lvlWidth) + col ] = newValue
        
    def GetMapTile (self, row, col):
        if row >= 0 and row < self.lvlHeight and col >= 0 and col < self.lvlWidth:
            return self.map[ (row * self.lvlWidth) + col ]
        else:
            return 0
    
    def IsWall (self, row, col):
    
        if row > thisLevel.lvlHeight - 1 or row < 0:
            return True
        
        if col > thisLevel.lvlWidth - 1 or col < 0:
            return True
    
        result = thisLevel.GetMapTile(row, col)

        if result >= 100 and result <= 199:
            return True
        else:
            return False
    
                    
    def CheckIfHitWall (self, possiblePlayerX, possiblePlayerY, row, col):
    
        numCollisions = 0
        
        for iRow in range(row - 1, row + 2, 1):
            for iCol in range(col - 1, col + 2, 1):
            
                if  (possiblePlayerX - (iCol * 16) < 16) and (possiblePlayerX - (iCol * 16) > -16) and (possiblePlayerY - (iRow * 16) < 16) and (possiblePlayerY - (iRow * 16) > -16):
                    
                    if self.IsWall(iRow, iCol):
                        numCollisions += 1
                        
        if numCollisions > 0:
            return True
        else:
            return False
        
        
    def CheckIfHit (self, playerX, playerY, x, y, cushion):
    
        if (playerX - x < cushion) and (playerX - x > -cushion) and (playerY - y < cushion) and (playerY - y > -cushion):
            return True
        else:
            return False


    def CheckIfHitSomething (self, playerX, playerY, row, col):
    
        for iRow in range(row - 1, row + 2, 1):
            for iCol in range(col - 1, col + 2, 1):
            
                if  (playerX - (iCol * 16) < 16) and (playerX - (iCol * 16) > -16) and (playerY - (iRow * 16) < 16) and (playerY - (iRow * 16) > -16):
                    
                    result = thisLevel.GetMapTile(iRow, iCol)
        
                    if result == tileID[ 'pellet' ]:
                        
                        thisLevel.SetMapTile(iRow, iCol, 0)
                        snd_pellet[player.pelletSndNum].play()
                        player.pelletSndNum = 1 - player.pelletSndNum
                        
                        thisLevel.pellets -= 1
                        
                        thisGame.AddToScore(10)
                        
                        if thisLevel.pellets == 0:
                            # Gana nivel
                            thisGame.SetMode( 6 )
                            
                        
                    elif result == tileID[ 'pellet-power' ]:
                        # tiene una bola de poder
                        thisLevel.SetMapTile(iRow, iCol, 0)
                        snd_powerpellet.play()
                        
                        thisGame.AddToScore(100)
                        thisGame.ghostValue = 200
                        
                        thisGame.ghostTimer = 360
                        for i in range(0, 4, 1):
                            if ghosts[i].state == 1:
                                ghosts[i].state = 2
                        
                    elif result == tileID[ 'door-h' ]:
                        # atraviesa puerta horizontal
                        for i in range(0, thisLevel.lvlWidth, 1):
                            if not i == iCol:
                                if thisLevel.GetMapTile(iRow, i) == tileID[ 'door-h' ]:
                                    player.x = i * 16
                                    
                                    if player.velX > 0:
                                        player.x += 16
                                    else:
                                        player.x -= 16
                                        
                    elif result == tileID[ 'door-v' ]:
                        # atraviesa puerta vertical
                        for i in range(0, thisLevel.lvlHeight, 1):
                            if not i == iRow:
                                if thisLevel.GetMapTile(i, iCol) == tileID[ 'door-v' ]:
                                    player.y = i * 16
                                    
                                    if player.velY > 0:
                                        player.y += 16
                                    else:
                                        player.y -= 16
                                        
    def GetGhostBoxPos (self):
        
        for row in range(0, self.lvlHeight, 1):
            for col in range(0, self.lvlWidth, 1):
                if self.GetMapTile(row, col) == tileID[ 'ghost-door' ]:
                    return (row, col)
                
        return False
    
    def GetPathwayPairPos (self):
        
        doorArray = []
        
        for row in range(0, self.lvlHeight, 1):
            for col in range(0, self.lvlWidth, 1):
                if self.GetMapTile(row, col) == tileID[ 'door-h' ]:
                    # encuentra puerta horizontal
                    doorArray.append( (row, col) )
                elif self.GetMapTile(row, col) == tileID[ 'door-v' ]:
                    # encuentra puerta vertical
                    doorArray.append( (row, col) )
        
        if len(doorArray) == 0:
            return False
        
        chosenDoor = random.randint(0, len(doorArray) - 1)
        
        if self.GetMapTile( doorArray[chosenDoor][0],doorArray[chosenDoor][1] ) == tileID[ 'door-h' ]:
            # pasa la puerta horizontal
            # mirar la puerta horizontal contraria
            for i in range(0, thisLevel.lvlWidth, 1):
                if not i == doorArray[chosenDoor][1]:
                    if thisLevel.GetMapTile(doorArray[chosenDoor][0], i) == tileID[ 'door-h' ]:
                        return doorArray[chosenDoor], (doorArray[chosenDoor][0], i)
        else:
            # pasa por la puerta vertical
            # mirar la puerta vertical contraria
            for i in range(0, thisLevel.lvlHeight, 1):
                if not i == doorArray[chosenDoor][0]:
                    if thisLevel.GetMapTile(i, doorArray[chosenDoor][1]) == tileID[ 'door-v' ]:
                        return doorArray[chosenDoor], (i, doorArray[chosenDoor][1])
                    
        return False
        
    def PrintMap (self):
        
        for row in range(0, self.lvlHeight, 1):
            outputLine = ""
            for col in range(0, self.lvlWidth, 1):
            
                outputLine += str( self.GetMapTile(row, col) ) + ", "
                
            # print outputLine
            
    def DrawMap (self):
        
        self.powerPelletBlinkTimer += 1
        if self.powerPelletBlinkTimer == 60:
            self.powerPelletBlinkTimer = 0
        
        for row in range(-1, thisGame.screenTileSize[0] +1, 1):
            outputLine = ""
            for col in range(-1, thisGame.screenTileSize[1] +1, 1):

                actualRow = thisGame.screenNearestTilePos[0] + row
                actualCol = thisGame.screenNearestTilePos[1] + col

                useTile = self.GetMapTile(actualRow, actualCol)
                if not useTile == 0 and not useTile == tileID['door-h'] and not useTile == tileID['door-v']:

                    if useTile == tileID['pellet-power']:
                        if self.powerPelletBlinkTimer < 30:
                            screen.blit (tileIDImage[ useTile ], (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]) )

                    elif useTile == tileID['showlogo']:
                        screen.blit (thisGame.imLogo, (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]) )
                    
                    elif useTile == tileID['hiscores']:
                            screen.blit(thisGame.imHiscores,(col*16-thisGame.screenPixelOffset[0],row*16-thisGame.screenPixelOffset[1]))
                    
                    else:
                        screen.blit (tileIDImage[ useTile ], (col * 16 - thisGame.screenPixelOffset[0], row * 16 - thisGame.screenPixelOffset[1]) )
        
    def LoadLevel (self, levelNum):
        
        self.map = {}
        
        self.pellets = 0
        
        f = open(os.path.join(SCRIPT_PATH,"res","levels",str(levelNum) + ".txt"), 'r')

        lineNum=-1
        rowNum = 0
        useLine = False
        isReadingLevelData = False
          
        for line in f:

          lineNum += 1
        
          while len(line)>0 and (line[-1]=="\n" or line[-1]=="\r"): line=line[:-1]
          while len(line)>0 and (line[0]=="\n" or line[0]=="\r"): line=line[1:]
          str_splitBySpace = line.split(' ')
            
            
          j = str_splitBySpace[0]
                
          if (j == "'" or j == ""):
                useLine = False
          elif j == "#":
                useLine = False
                
                firstWord = str_splitBySpace[1]
                
                if firstWord == "lvlwidth":
                    self.lvlWidth = int( str_splitBySpace[2] )
                    
                elif firstWord == "lvlheight":
                    self.lvlHeight = int( str_splitBySpace[2] )
                    
                elif firstWord == "edgecolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.edgeLightColor = (red, green, blue, 255)
                    self.edgeShadowColor = (red, green, blue, 255)
                    
                elif firstWord == "edgelightcolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.edgeLightColor = (red, green, blue, 255)
                    
                elif firstWord == "edgeshadowcolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.edgeShadowColor = (red, green, blue, 255)
                
                elif firstWord == "fillcolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.fillColor = (red, green, blue, 255)
                    
                elif firstWord == "pelletcolor":
                    red = int( str_splitBySpace[2] )
                    green = int( str_splitBySpace[3] )
                    blue = int( str_splitBySpace[4] )
                    self.pelletColor = (red, green, blue, 255)
                    
                elif firstWord == "fruittype":
                    thisFruit.fruitType = int( str_splitBySpace[2] )
                    
                elif firstWord == "startleveldata":
                    isReadingLevelData = True
                    rowNum = 0
                    
                elif firstWord == "endleveldata":
                    isReadingLevelData = False
                    
          else:
                useLine = True
                
                
            # lineado del mapa   
          if useLine == True:
                
                if isReadingLevelData == True:
                    
                    for k in range(0, self.lvlWidth, 1):
                        self.SetMapTile(rowNum, k, int(str_splitBySpace[k]) )
                        
                        thisID = int(str_splitBySpace[k])
                        if thisID == 4: 
                            # posicion inicial del pacman
                            
                            player.homeX = k * 16
                            player.homeY = rowNum * 16
                            self.SetMapTile(rowNum, k, 0 )
                            
                        elif thisID >= 10 and thisID <= 13:
                            # salida uno de los fantasmas
                            
                            ghosts[thisID - 10].homeX = k * 16
                            ghosts[thisID - 10].homeY = rowNum * 16
                            self.SetMapTile(rowNum, k, 0 )
                        
                        elif thisID == 2:
                            
                            self.pellets += 1
                            
                    rowNum += 1
                    
                
        # recargar todos los casillas y establecer los colores apropiados
        GetCrossRef()

        # cargar el mapa en el objeto del buscador
        path.ResizeMap( self.lvlHeight, self.lvlWidth )
        
        for row in range(0, path.size[0], 1):
            for col in range(0, path.size[1], 1):
                if self.IsWall( row, col ):
                    path.SetType( row, col, 1 )
                else:
                    path.SetType( row, col, 0 )
        
        self.Restart()
        
    def Restart (self):
        
        for i in range(0, 4, 1):
            # mover de vuelta a los fantasmas

            ghosts[i].x = ghosts[i].homeX
            ghosts[i].y = ghosts[i].homeY
            ghosts[i].velX = 0
            ghosts[i].velY = 0
            ghosts[i].state = 1
            ghosts[i].speed = 1
            ghosts[i].Move()
            
            # dale a cada fantasma un camino a un lugar aleatorio
            (randRow, randCol) = (0, 0)

            while not self.GetMapTile(randRow, randCol) == tileID[ 'pellet' ] or (randRow, randCol) == (0, 0):
                randRow = random.randint(1, self.lvlHeight - 2)
                randCol = random.randint(1, self.lvlWidth - 2)
            
            ghosts[i].currentPath = path.FindPath( (ghosts[i].nearestRow, ghosts[i].nearestCol), (randRow, randCol) )
            ghosts[i].FollowNextPathWay()
            
        thisFruit.active = False
            
        thisGame.fruitTimer = 0

        player.x = player.homeX
        player.y = player.homeY
        player.velX = 0
        player.velY = 0
        
        player.anim_pacmanCurrent = player.anim_pacmanS
        player.animFrame = 3


def CheckIfCloseButton(events):
    for event in events: 
        if event.type == pygame.QUIT: 
            sys.exit(0)


def CheckInputs(): 
    
    if thisGame.mode == 1:
        if pygame.key.get_pressed()[ pygame.K_RIGHT ] or (js!=None and js.get_axis(JS_XAXIS)>0):
            if not thisLevel.CheckIfHitWall(player.x + player.speed, player.y, player.nearestRow, player.nearestCol): 
                player.velX = player.speed
                player.velY = 0
                
        elif pygame.key.get_pressed()[ pygame.K_LEFT ] or (js!=None and js.get_axis(JS_XAXIS)<0):
            if not thisLevel.CheckIfHitWall(player.x - player.speed, player.y, player.nearestRow, player.nearestCol): 
                player.velX = -player.speed
                player.velY = 0
            
        elif pygame.key.get_pressed()[ pygame.K_DOWN ] or (js!=None and js.get_axis(JS_YAXIS)>0):
            if not thisLevel.CheckIfHitWall(player.x, player.y + player.speed, player.nearestRow, player.nearestCol): 
                player.velX = 0
                player.velY = player.speed
            
        elif pygame.key.get_pressed()[ pygame.K_UP ] or (js!=None and js.get_axis(JS_YAXIS)<0):
            if not thisLevel.CheckIfHitWall(player.x, player.y - player.speed, player.nearestRow, player.nearestCol):
                player.velX = 0
                player.velY = -player.speed
                
    if pygame.key.get_pressed()[ pygame.K_ESCAPE ]:
        sys.exit(0)
            
    elif thisGame.mode == 3:
        if pygame.key.get_pressed()[ pygame.K_RETURN ] or (js!=None and js.get_button(JS_STARTBUTTON)):
            thisGame.StartNewGame()
            

    
#      ____________________________________________
# ___/  funcion: get ID-Tilename Cross References  \______________________________________ 
    
def GetCrossRef ():

    f = open(os.path.join(SCRIPT_PATH,"res","crossref.txt"), 'r')

    lineNum = 0
    useLine = False

    for i in f.readlines():
        while len(i)>0 and (i[-1]=='\n' or i[-1]=='\r'): i=i[:-1]
        while len(i)>0 and (i[0]=='\n' or i[0]=='\r'): i=i[1:]
        str_splitBySpace = i.split(' ')
        
        j = str_splitBySpace[0]
            
        if (j == "'" or j == "" or j == "#"):
            useLine = False
        else:
            useLine = True
        
        if useLine == True:
            tileIDName[ int(str_splitBySpace[0]) ] = str_splitBySpace[1]
            tileID[ str_splitBySpace[1] ] = int(str_splitBySpace[0])
            
            thisID = int(str_splitBySpace[0])
            if not thisID in NO_GIF_TILES:
                tileIDImage[ thisID ] = pygame.image.load(os.path.join(SCRIPT_PATH,"res","tiles",str_splitBySpace[1] + ".gif")).convert()
            else:
                    tileIDImage[ thisID ] = pygame.Surface((16,16))
            
            # cambia los colores en tileIDImage para que coincidan con los colores del laberinto
            for y in range(0, 16, 1):
                for x in range(0, 16, 1):
                
                    if tileIDImage[ thisID ].get_at( (x, y) ) == (255, 206, 255, 255):
                        # borde de la pared
                        tileIDImage[ thisID ].set_at( (x, y), thisLevel.edgeLightColor )
                        
                    elif tileIDImage[ thisID ].get_at( (x, y) ) == (132, 0, 132, 255):
                        # relleno de pared
                        tileIDImage[ thisID ].set_at( (x, y), thisLevel.fillColor ) 
                        
                    elif tileIDImage[ thisID ].get_at( (x, y) ) == (255, 0, 255, 255):
                        # color de la pelotilla
                        tileIDImage[ thisID ].set_at( (x, y), thisLevel.edgeShadowColor )   
                        
                    elif tileIDImage[ thisID ].get_at( (x, y) ) == (128, 0, 128, 255):
                        tileIDImage[ thisID ].set_at( (x, y), thisLevel.pelletColor )   
        lineNum += 1


#      ____________________________
# ___/  bloque de código principal  \_____________________________________________________

# crea el pacman
player = pacman()

# crear un objeto path_finder
path = path_finder()

# crea objetos fantasma
ghosts = {}
for i in range(0, 6, 1):
    # recuerda, ghost[4] es el fantasma azul y vulnerable
    ghosts[i] = ghost(i)
    
# crea una pieza de fruta
thisFruit = fruit()

tileIDName = {} 
tileID = {} 
tileIDImage = {} 

# crear juegos y objetos de nivel y cargar el primer nivel
thisGame = game()
thisLevel = level()
thisLevel.LoadLevel( thisGame.GetLevelNum() )

window = pygame.display.set_mode( thisGame.screenSize, pygame.DOUBLEBUF | pygame.HWSURFACE )

# inicializa el joystick
if pygame.joystick.get_count()>0:
  if JS_DEVNUM<pygame.joystick.get_count(): js=pygame.joystick.Joystick(JS_DEVNUM)
  else: js=pygame.joystick.Joystick(0)
  js.init()
else: js=None

while True: 

    CheckIfCloseButton( pygame.event.get() )
    
    if thisGame.mode == 1:
        # modo de juego normal
        CheckInputs()
        
        thisGame.modeTimer += 1
        player.Move()
        for i in range(0, 4, 1):
            ghosts[i].Move()
        thisFruit.Move()
            
    elif thisGame.mode == 2:
        # esperando después de ser golpeado por un fantasma
        thisGame.modeTimer += 1
        
        if thisGame.modeTimer == 90:
            thisLevel.Restart()
            
            thisGame.lives -= 1
            if thisGame.lives == -1:
                thisGame.updatehiscores(thisGame.score)
                thisGame.SetMode( 3 )
                thisGame.drawmidgamehiscores()
            else:
                thisGame.SetMode( 4 )
                
    elif thisGame.mode == 3:
        # juego terminado
        CheckInputs()
            
    elif thisGame.mode == 4:
        # espera para jugar
        thisGame.modeTimer += 1
        
        if thisGame.modeTimer == 90:
            thisGame.SetMode( 1 )
            player.velX = player.speed
            
    elif thisGame.mode == 5:
        # breve pausa después de masticar un fantasma vulnerable
        thisGame.modeTimer += 1
        
        if thisGame.modeTimer == 30:
            thisGame.SetMode( 1 )
            
    elif thisGame.mode == 6:
        # pausa después de comer todos los gránulos
        thisGame.modeTimer += 1
        
        if thisGame.modeTimer == 60:
            thisGame.SetMode( 7 )
            oldEdgeLightColor = thisLevel.edgeLightColor
            oldEdgeShadowColor = thisLevel.edgeShadowColor
            oldFillColor = thisLevel.fillColor
            
    elif thisGame.mode == 7:
        # laberinto intermitente después de terminar el nivel
        thisGame.modeTimer += 1
        
        whiteSet = [10, 30, 50, 70]
        normalSet = [20, 40, 60, 80]
        
        if not whiteSet.count(thisGame.modeTimer) == 0:
            # miembro del conjunto blanco
            thisLevel.edgeLightColor = (255, 255, 255, 255)
            thisLevel.edgeShadowColor = (255, 255, 255, 255)
            thisLevel.fillColor = (0, 0, 0, 255)
            GetCrossRef()
        elif not normalSet.count(thisGame.modeTimer) == 0:
            # miembro del conjunto normal
            thisLevel.edgeLightColor = oldEdgeLightColor
            thisLevel.edgeShadowColor = oldEdgeShadowColor
            thisLevel.fillColor = oldFillColor
            GetCrossRef()
        elif thisGame.modeTimer == 150:
            thisGame.SetMode ( 8 )
            
    elif thisGame.mode == 8:
        # pantalla en blanco antes de cambiar de nivel
        thisGame.modeTimer += 1
        if thisGame.modeTimer == 10:
            thisGame.SetNextLevel()

    thisGame.SmartMoveScreen()
    
    screen.blit(img_Background, (0, 0))
    
    if not thisGame.mode == 8:
        thisLevel.DrawMap()
        
        if thisGame.fruitScoreTimer > 0:
            if thisGame.modeTimer % 2 == 0:
                thisGame.DrawNumber (2500, thisFruit.x - thisGame.screenPixelPos[0] - 16, thisFruit.y - thisGame.screenPixelPos[1] + 4)

        for i in range(0, 4, 1):
            ghosts[i].Draw()
        thisFruit.Draw()
        player.Draw()
        
        if thisGame.mode == 3:
                screen.blit(thisGame.imHiscores,(32,256))
        
    if thisGame.mode == 5:
        thisGame.DrawNumber (thisGame.ghostValue / 2, player.x - thisGame.screenPixelPos[0] - 4, player.y - thisGame.screenPixelPos[1] + 6)
    
    
    
    thisGame.DrawScore()
    
    pygame.display.flip()
    
    clock.tick (60)
