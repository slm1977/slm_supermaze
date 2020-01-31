"""
Modulo che contiene tutte le classi
che gestiscono i diversi personaggi animati
del gioco
"""

import pygame
from pygame.locals import *
import random


class PlayerState:
    VISIBILE = 0
    ALMOST_VISIBILE = 1
    INVISIBILE = 2


class PlayerPowers:
    INVISIBILITY = "invisibility"
    WEAPON = "weapon"


class Player(pygame.sprite.Sprite):
    """
    Un giocatore che è in grado di muoversi nel labirinto,
    purchè guidat dall'utente
    """

    def __init__(self, w, h, scale, speed, filename, *args):
        """
        Crea un nuovo Player che consiste in uno sprite in grado
        di essere mosso nel labirinto e di autogestire la collisione
        con le pareti
        :param w: larghezza dello sprite
        :param h: altezza dello sprite
        :param scale: scala di gioco (usata per collocare correttamente il player nel labirinto)
        :param speed: velocità di spostamento del player
        :param filename: nome del file di immagine del player
        :param args: altri argomenti passati alla classe sprite (tra cui il gruppo di appartenenza)
        """
        super().__init__(*args)

        self.w = w
        self.h = h
        self.image = pygame.transform.scale(pygame.image.load(filename).convert_alpha(), (w,h)).convert_alpha()

        self.scale=scale
        self.rect = self.image.get_rect()
        self.rect.width = w
        self.rect.height = h
        self.vel = [0,0]
        self.speed = speed
        self.walls = []
        self.state = PlayerState.VISIBILE
        self.powers = {}


        # eventuali immagini legate alla direzione
        # del giocatore

        self.dirImages = []
        self.dirIndex = -1
        self.lastDirIndex = -1

        self.state = PlayerState.INVISIBILE


    # metodi che gestiscono i poteri del giocatore
    def hasPower(self,power):
        return power in self.powers

    def removePower(self,power):
        if self.hasPower(power):
            del self.powers[power]

    def addPower(self, power, value):
        if power == PlayerPowers.INVISIBILITY:
            self.setState(PlayerState.INVISIBILE)
            self.powers[power] = value
        else:
            self.powers[power] = value


    def getPower(self,power):
        return self.powers.get(power,None)

    def handlePowers(self, currentRemainingTime):
        # gestisco il potere della invisibilità
        if self.hasPower(PlayerPowers.INVISIBILITY):
            powerStart, powerDuration = self.getPower(PlayerPowers.INVISIBILITY)
            if currentRemainingTime < (powerStart - powerDuration):
                self.removePower(PlayerPowers.INVISIBILITY)
                self.setState(PlayerState.VISIBILE)
            # SE mancano solo 5 secondi cambio aspetto del giocatore per avvisarlo
            elif currentRemainingTime - 5 < (powerStart - powerDuration):
                self.setState(PlayerState.ALMOST_VISIBILE)

        # gestisco il potere dell'arma
        if self.hasPower(PlayerPowers.WEAPON):
            powerStart, powerDuration = self.getPower(PlayerPowers.WEAPON)
            if currentRemainingTime < (powerStart - powerDuration):
                self.removePower(PlayerPowers.WEAPON)

    def setPosition(self, pos):
        self.rect.x = pos[0]*self.scale
        self.rect.y = pos[1]*self.scale

    def setImages(self, images):
        self.dirImages = []

        for i in range(len(images)):
            self.dirImages.append([])
            for im in images[i]:
                image = pygame.image.load(im).convert_alpha()
                image = pygame.transform.scale(image, (self.w, self.h)).convert_alpha()
                self.dirImages[i].append(image)

        #print("Richiamato setImages: %s" % self.dirImages)

    def setWalls(self,walls):
        self.walls = walls

    def setState(self, state):
        if (state==self.state):
            return
        self.state = state
        # l'aggiornamento di stato
        # richiede l'aggiornamento della immagine
        print("STATO CAMBIATO IN %s" % self.state)
        self.updateImage(True)

    def getState(self):
        return self.state

    def checkCollisions(self):
        # Muovere il rettangolo
        dx = self.vel[0]
        dy = self.vel[1]
        self.rect.x += dx
        self.rect.y += dy

        # Collisione coi muri
        collision_found = False
        for wall in self.walls:
            if self.rect.colliderect(wall.rect):
                collision_found = True
                if dx > 0:
                    self.rect.right = wall.rect.left
                if dx < 0:
                    self.rect.left = wall.rect.right
                if dy > 0:
                    self.rect.bottom = wall.rect.top
                if dy < 0:
                    self.rect.top = wall.rect.bottom

        return collision_found

    def move(self,velx,vely):
        velx =  round(velx * 5)
        vely = round(vely * 5)
        if velx>0:
            self.moveRight(velx)
        elif velx<0:
            self.moveLeft(-velx)
        else:
            self.vel[0] = 0

        if vely>0:
            self.moveDown(vely)
        elif vely<0:
            self.moveUp(-vely)
        else:
            self.vel[1] = 0


    def updateImage(self, stateChanged=False):

        if len(self.dirImages) < 3:
            self.lastDirIndex = self.dirIndex
            return
        elif stateChanged or self.lastDirIndex!=self.dirIndex:
            #print("AGGIORNO IMMAGINE con player state:%s" % self.state)
            self.image = self.dirImages[self.state][self.dirIndex]
            self.lastDirIndex = self.dirIndex


    def moveUp(self, inc=0):
        self.vel[0] = 0
        self.vel[1] = -(self.speed + inc)
        self.dirIndex = 0

    def moveDown(self, inc=0):
        self.vel[0] = 0
        self.vel[1] = self.speed + inc
        self.dirIndex = 1

    def moveRight(self, inc=0):
        self.vel[1] = 0
        self.vel[0] = self.speed + inc
        self.dirIndex = 2

    def moveLeft(self, inc=0):
        self.vel[1] = 0
        self.vel[0] = -(self.speed+inc)
        self.dirIndex = 3

    def stop(self,inc=0):
        """
        :param inc: parametro inserito per uniformita con gli altri (usato nella lista di funzioni in Game).Ignorato nella pratica
        :return:
        """
        self.vel = [0,0]
        #self.dirIndex = -1

    def shot(self, bullet_filename, playerBulletsGroup, soundBullet):
        # se il giocatore possiede il potere dell'arma (WEAPON)
        # creo un nuovo proiettile e lo lancio nella stessa direzione
        # in cui è rivolto il player con una velocità doppia rispetto
        # a quella massima del player
        # la posizione iniziale del player corrisponde al centro
        # del rettangolo del giocatore
        # creo e faccio partire il proiettile purchè il giocatore sia rivolto in una posizione
        # valida

        if self.hasPower(PlayerPowers.WEAPON) and self.dirIndex >= 0:
            #print("ARMA PRESENTE!")
            bullet = Bullet(int(self.w/2), int(self.h/2), self.scale, self.speed*4, bullet_filename, playerBulletsGroup)
            bullet.setWalls(self.walls)
            # la posizione iniziale del proiettile è quella del centro del giocatore
            bullet.rect.center = self.rect.center
            moves = [bullet.moveUp, bullet.moveDown, bullet.moveRight, bullet.moveLeft]

            soundBullet.play()
            moves[self.dirIndex]()


    def update(self):
        self.updateImage()
        self.checkCollisions()




class Bullet(Player):
    def checkCollisions(self):
        collision = super().checkCollisions()
        if (collision):
            self.kill()

class Enemy(Player):
    """
    Un oggetto che, come il giocatore, ha la possibilità di muoversi
    nel labirinto ma che, in più, è in grado di muoversi all'interno
    di esso autonomamente.
    """
    def __init__(self, w, h, scale, speed, filename, *args):
        super().__init__(w,h,scale,speed, filename, *args)
        self.loopAfterCross = 0
        self.nextMove = random.randint(1, 10)

    def randomMove(self):
        moves = [self.moveLeft, self.moveRight, self.moveUp, self.moveDown]
        moves[random.randint(0,3)]()

        self.loopAfterCross = 0
        self.nextMove = random.randint(1,20)

    def isCross(self):
        dx = self.vel[0]
        dy = self.vel[1]

        cross_up = False
        cross_down = False
        cross_right = False
        cross_left = False

        # se mi muovo in orizzontale verifico incroci in alto e
        # in basso, escludendo quelli a destra o sinistra
        if dx!=0:
            cross_right = False
            cross_left = False
            # verifico incroci in alto e in basso
            rect_up = Rect(self.rect.x, self.rect.top-self.rect.height, self.rect.width, self.rect.height)
            rect_down =Rect(self.rect.x, self.rect.bottom, self.rect.width, self.rect.height)

            # parto dal presupposto che in alto e in basso ci sia strada libera,
            # Se incontro anche un solo muro evidentemente non c'e' incrocio
            cross_up = True
            cross_down = True
            for wall in self.walls:
                # verifico incrocio in alto
                if wall.rect.colliderect(rect_up):
                    cross_up = False
                # verifico incrocio in basso
                if wall.rect.colliderect(rect_down):
                    cross_down = False

        # se mi muovo in verticale verifico incroci a destra e
        # sinistra, escludendo quelli in alto e in basso
        if dy!=0:
            cross_up = False
            cross_down = False
            # verifico incroci a destra e a sinistra
            rect_right = Rect(self.rect.right, self.rect.y, self.rect.width, self.rect.height)
            rect_left =Rect(self.rect.x-self.rect.width, self.rect.y, self.rect.width, self.rect.height)

            # parto dal presupposto che a destra e a sinistra ci sia strada libera,
            # Se incontro anche un solo muro evidentemente non c'e' incrocio
            cross_right = True
            cross_left = True
            for wall in self.walls:
                # verifico incrocio a destra
                if wall.rect.colliderect(rect_right):
                    cross_right= False
                # verifico incrocio a sinistra
                if wall.rect.colliderect(rect_left):
                    cross_left = False

        return (cross_up or cross_down or cross_left or cross_right)

    def checkCollisions(self):
        collisionFound = super().checkCollisions()
        # se ho sbattuto su un muro o sono in corrispondenza
        # di un  incrocio, do' la possibilità di cambiare direzione
        if (collisionFound):
            self.randomMove()

        elif self.isCross():
            self.loopAfterCross = (self.loopAfterCross+1) % self.nextMove
            if self.loopAfterCross==0:
                self.randomMove()


class ObjectDestroyer(Enemy):
    """
    Una classe di oggetti che, come i nemici, si muovono
    autonomamente nello schermo, ma che in piu hanno
    intorno a se un potere di distruzione la cui estensione
    e' pari al rettangolo intorno alla loro posizione
    corrente con lato pari al parametro power.
    Per far agire l'oggetto occorre richiamare il metodo kill()
    """

    def __init__(self, w, h, scale, speed, filename, power, *args):
        super().__init__(w, h, scale, speed, filename, *args)
        self.power = power
        self.objects = []
        self.removedObjects = 0

    def setObjects(self, objects):
        self.objects = objects

    def getCollisionRect(self):
        # creo un quadrato di azione con lato pari al valore di 'power'
        r = Rect(0,0, self.scale*self.power, self.scale*self.power)
        # centro il rettangolo creato rispetto alla posizione corrente
        # della bomba
        r.center = self.rect.center
        return r


    def getRemovedObjects(self):
        return self.removedObjects

    def removeCollidingObjects(self):
        self.removedObjects = 0
        powerRect = self.getCollisionRect()
        for ob in self.objects:
            if ob.rect.colliderect(powerRect):
                ob.kill()
                self.removedObjects +=1

    def kill(self):
        self.removeCollidingObjects()
        # ricordarsi di richiamare il metodo kill della
        # suoerclasse, altrimenti l'oggetto rimane!
        pygame.sprite.Sprite.kill(self)


class InnerObjectDestroyer(ObjectDestroyer):
    """
    Come un ObjectDestroyer, consente di distruggere gli oggetti specificati intorno
    alla propria posizione, preservando pero' il
    perimetro esterno del labirinto (o gli eventuali oggetti che collidono con esso)
    """
    def __init__(self,ncols,nrows, w, h, scale, speed, filename, *args):
        super().__init__(w, h, scale, speed, filename, *args)

        self.upRect =   Rect(0,0,ncols*scale,scale)
        self.leftRect = Rect(0,0, scale, nrows * scale)

        self.downRect =  Rect(0, (nrows-2)*scale, ncols * scale, scale)
        self.rightRect = Rect((ncols-2)*scale, 0, scale, nrows*scale)

        self.perimeter = [self.upRect,self.downRect,self.leftRect,self.rightRect]

    def removeCollidingObjects(self):
        self.removedObjects = 0
        powerRect = self.getCollisionRect()
        for ob in self.objects:
            # se il mio muro collide con il perimetro
            # del labirinto, non lo rimuovo
            if ob.rect.collidelist(self.perimeter)!=-1:
                continue

            if ob.rect.colliderect(powerRect):
                ob.kill()
                self.removedObjects +=1


class TimeLimitedPower(Enemy):
    """
    Nemici il cui 'contatto' con il giocatore provoca una azione
    le cui conseguenze hanno una durata specificata dal parametro
    'duration'
    """
    def __init__(self,duration, w, h, scale, speed, filename, *args):
        super().__init__(w, h, scale, speed, filename, *args)
        self.duration = duration

    def get_duration(self):
        return self.duration


class Shooter(Enemy):
    """
    Classe che rappresenta un nemico in grado di sparare autonomamente,
    con una frequenza proporzionale al valore del parametro aggressivity
    """
    def __init__(self, w, h, scale, speed, filename, aggressivity, bullet_filename, shooterBulletsGroup, soundBullet, *args):
        #print("Shooter filename:%s" % shooter_filename)
        #print("Bullet filename:%s" % bullet_filename)
        super().__init__(w, h, scale, speed, filename, *args)
        self.aggressivity = aggressivity
        self.bullet_filename = bullet_filename
        self.shooterBulletsGroup = shooterBulletsGroup
        self.soundBullet = soundBullet

        # lo shooter ha il potere dell'arma da fuoco!
        self.addPower(PlayerPowers.WEAPON,1000)

    def autoshot(self):
        # genero un numero random
        val = random.randint(0, 500)
        if val < self.aggressivity:
            self.shot(self.bullet_filename, self.shooterBulletsGroup, self.soundBullet)

    def update(self):
        super().update()
        self.autoshot()

