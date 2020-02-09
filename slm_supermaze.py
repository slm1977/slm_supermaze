# installare la seguente libreria col comando
# sudo python3.7 -m pip install -U numpy
# (specifica la versione di python installata sul proprio pc se necessario)
import numpy
from numpy.random import randint as rand
import random
import pygame
from pygame.locals import *
from supermaze_levels import levels
import time
import sys

# importo tutte le classi che
# servono per gestire i personaggi di gioco,
# compreso il giocatore (Player)
from characters import *

pygame.init()
pygame.mixer.init()




class Wall(pygame.sprite.Sprite):
    """
    Classe che rappresenta ciascuna delle porzioni
    di muro del labirinto
    """
    def __init__(self, w, h, filename, *args):
        pygame.sprite.Sprite.__init__(self, *args)
        self.image =  pygame.image.load(filename).convert()
        self.image = pygame.transform.scale(self.image, (w,h))
        self.rect = self.image.get_rect()
        self.rect.width = w
        self.rect.height = h


class Coin(pygame.sprite.Sprite):
    """
    Classe che rappresenta le monete da raccogliere,
    operazione necessaria per il completamento di
    ciascun livello di gioco
    """

    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self, color, width, height, *args):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self, *args)

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface([width, height]).convert()
        self.image.fill(color)

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()






class GameState:
    SETUP = 0
    PLAYING = 1
    PAUSED = 2
    LEVEL_COMPLETED = 3
    PLAYER_WON = 4
    PLAYER_LOOSE = 5
    HELP = 6




class Score:
    """
    Indica i vari punteggi in caso di raccolta monete,
    eliminazione nemici, etc
    """
    COIN = 10
    ENEMY = 100

class Game:

    MAZE_DENSITY = .2
    MAZE_COMPLEXITY = .75

    WHITE = (255,255,255)
    BLACK = (0,0,0)
    RED = (255, 0, 0)
    ORANGE = (255,127,80)
    YELLOW = (255,255,0)

    def __init__(self, win_size, fullscreen=False):

        self.pause = False
        self.done = False
        self.win_size = win_size
        self.state = GameState.SETUP
        self.score = 0
        self.levelIndex = 0
        self.numLives = 30

        # creo la finestra di gioco
        if (fullscreen):
            self.screen = pygame.display.set_mode(win_size, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(win_size)

        pygame.display.set_caption("Super Maze")
        self.clock = pygame.time.Clock()

        # abilito l'uso del joystick

        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()
        if joystick_count > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            self.joystick = None


        # costruisco il primo livello
        self.setupLevel()


    def setupLevel(self):
        """
        Qui leggo dal file di configurazione
        tutte le informazioni per impostare correttamente
        il livello di gioco,
        Nel caso di assenza di informazioni verranno caricate
        le impostazioni di default.
        :return:
        """

        self.state = GameState.SETUP

        # vado a leggere il dizionario corrispondente
        # al numero di livello corrente facendo in modo
        # che se il numero di livello richiesto non esiste
        # carico quello più vicino a quello richiesto
        if self.levelIndex>= len(levels):
            self.levelIndex = len(levels) -1
        elif self.levelIndex <0:
            self.levelIndex = 0

        level = levels[self.levelIndex]

        # dimensione del labirinto (numero di righe e di colonne)
        self.nrows = level.get("nrows", 20)
        self.ncols = level.get("ncols", 20)

        # l'algoritmo di generazione del labirinto supporta solo un numero di
        # righe e di colonne dispari, quindi approssimiamo le dimensioni ai
        # valori dispari più vicini
        if self.nrows % 2 == 0:
            self.nrows+=1
        if self.ncols % 2 == 0:
            self.ncols+=1


        # fattore di scala del labirinto
        # attenzione che, fattori di scala molto
        # grandi, rallentano le prestazioni di gioco
        self.scale = level.get("scale", 30)

        background_image_filename = level.get("background_image", None)
        if background_image_filename!=None:
            self.background_image = pygame.image.load(background_image_filename).convert()
        else:
            self.background_image = None

        # parametri usati dall'algoritmo di generazione del labirinto
        # si veda https://en.wikipedia.org/wiki/Maze_generation_algorithm
        self.maze_density = level.get("maze_density", Game.MAZE_DENSITY)
        self.maze_complexity = level.get("maze_complexity", Game.MAZE_COMPLEXITY)

        # colore delle monete
        self.coin_color = level.get("coin_color", Game.YELLOW)

        # tempo a disposizione per completare il livello
        self.time = level.get("time", 240)
        self.clockTime = level.get("clock", 80)

        # numero di nemici
        self.numEnemies =  level.get("num_enemies", 0)

        # numero di ricaricatori temporali
        self.numTimeReloaders = level.get("time_reloaders", 0)

        # numero di bombe "distruggi monete"
        self.bonus_bombs = level.get("bombs", [])
        # numero di bombe "distruggi muri"
        self.bonus_wall_bombs = level.get("wall_bombs", [])
        # numero di bombe "distruggi nemici"
        self.bonus_enemy_killers = level.get("enemy_killers", [])
        # numero di pizze che rendono i nemici golosi di monete
        self.bonus_greedy_enemies = level.get("greedy_enemies", 0)
        # numero di portali (teletrasporto del giocatore)
        self.bonus_portals = level.get("portals", 0)

        # proiettili a disposizione del giocatore per un certo periodo di tempo
        self.bonus_player_bullets = level.get("player_bullets", [])

        #numero di bonus che rendono il giocatore invisibile per un certo periodo di tempo
        self.bonus_invisibility_players = level.get("invisibility_players", [])

        # numero di shooters (nemici che sparano contro il giocatore)
        self.numShooters = level.get("num_shooters" , [])


        # suoni di collisione
        self.sound_explosion = pygame.mixer.Sound("Effects/smc-wwvi/big_explosion.ogg")
        self.sound_bomb_explosion = pygame.mixer.Sound("Effects/smc-wwvi/bombexplosion.ogg")


        # suono della moneta raccolta
        #self.sound_coin = pygame.mixer.Sound("Effects/SFX/beep_7.wav")
        self.sound_coin = pygame.mixer.Sound("Effects/jute-dh/gold.wav")

        # suono del timeReloader
        self.sound_time_reloader = pygame.mixer.Sound("Effects/SFX/echo_5.wav")

        # suono di collisione con enemy killer
        self.sound_enemy_killer =  pygame.mixer.Sound("Effects/smc-wwvi/big_explosion.ogg")

        # suono dell'invisibility player
        self.sound_invisibility_player =  pygame.mixer.Sound("Effects/sound_effects/trekscan.wav")

        # suono del teletrasporto
        self.sound_portal = pygame.mixer.Sound("Effects/sound_effects/trekscan.wav")

        # suono dell'arma presa e del proiettile sparato
        self.sound_weapon = pygame.mixer.Sound("Effects/jute-dh/hit_2m.wav")

        # suono dei greedy enemies
        self.sound_greedy_enemies = pygame.mixer.Sound("Effects/sound_effects/squeak2.wav")

        # suono del levello completato
        self.sound_completed_level = pygame.mixer.Sound("Effects/sound_effects/level_completed.wav")

        #
        # IMMAGINI DEGLI SPRITE DI GIOCO: CONFIGURABILE DA FILE DI CONFIGURAZIONE!!
        #

        # immagine delle pareti del labirinto
        self.wall_filename = level.get("wall", "Backgrounds/Dim/Boards.jpg")

        # immagine dei nemici del labirinto
        self.enemies_filename = level.get("enemies", "Sprites/Animals/duck.png")

        # immagine dei nemici del labirinto che possono anche sparare
        # di default gli shooters hanno lo stesso aspetto dei nemici normali
        self.shooters_filename = level.get("shooters", self.enemies_filename)

        # immagine della bomba distruggi monete
        self.bomb_filename = level.get("bomb", "Sprites/bomb_bonus.png")
        # immagine della bomba distruggi muri
        self.wall_bomb_filename = level.get("wall_bomb", "Sprites/bomb_wall_bonus.png")

        self.time_reloaders_filename = level.get("time_reloader", "Sprites/clessidra.png")
        self.enemy_killers_filename = level.get("enemy_killer", "Sprites/skull2.png")
        self.greedy_enemies_filename = level.get("greedy_enemy", "Sprites/pizza.png")
        self.portals_filename = level.get("portal", "Sprites/CrawlStone/portal.png")
        self.invisibility_players_filename = level.get("invisibility_player", "Sprites/CrawlStone/wizard_hat_2.png")

        # lo sprite che fornisce i proiettili ha la stessa immagine dei proiettili
        self.player_bullets_filename = level.get("player_bullet", "Sprites/CrawlStone/apple.png")
        self.bonus_player_bullets_filename = self.player_bullets_filename

        self.shooters_bullets_filename = level.get("shooter_bullet", "Sprites/CrawlStone/apple.png")

        #
        #  GRUPPI DI SPRITES
        #

        # i muri del mio labirinto
        self.walls = pygame.sprite.Group()

        # i nemici
        self.enemies = pygame.sprite.Group()

        # i nemici che sparano fanno parte dello stesso gruppo dei nemici!
        #self.shooters = pygame.sprite.Group()

        # le bombe
        self.bombs = pygame.sprite.Group()

        # gli attivatori/disattivatori di nemici golosi
        self.greedyEnemies = pygame.sprite.Group()

        # le bombe che spaccano i muri
        self.wallBombs = pygame.sprite.Group()

        # i ricaritori temporali
        self.timeReloaders = pygame.sprite.Group()

        # le monete da raccogliere
        self.coins = pygame.sprite.Group()

        # i killer dei nemici
        self.enemyKillers = pygame.sprite.Group()

        # i portali per spostarsi in nuove aree
        self.portals = pygame.sprite.Group()

        # i nemici che rendono invisibile il giocatore
        self.invisibilityPlayers = pygame.sprite.Group()

        # i proiettili sparati dal giocatore
        self.playerBullets = pygame.sprite.Group()

        # i proiettili sparati dagli shooters
        self.shooterBullets = pygame.sprite.Group()

        # il bonus che fornisce proiettili sparati dal giocatore
        self.bonusPlayerBullets = pygame.sprite.Group()


        self.free_locations = []

        # genero il labirinto che prescinde dai fattori di scala
        self.maze = self.generate_maze()
        #print(self.maze)

        # il giocatore e i nemici hanno una dimensione che dipende dal fattore di scala
        self.player = pygame.sprite.GroupSingle(Player(int(self.scale * 0.8), int(self.scale * 0.8),
                                                       self.scale, 1,
                                                       "Sprites/pac-classic/ghost-red-front.png",
                                                      )
                                                     )
        self.player.sprite.setWalls(self.walls)
        # imposto le immagini del giocatore sulla base della posizione
        # l'ordine è UP, DOWN , RIGHT, LEFT

        self.player.sprite.setImages([
                                      ["Sprites/pac-classic/ghost-red-rear.png",
                                      "Sprites/pac-classic/ghost-red-front.png",
                                      "Sprites/pac-classic/ghost-red-right.png",
                                      "Sprites/pac-classic/ghost-red-left.png",
                                      ],

                                        ["Sprites/pac-classic/ghost-orange-rear.png",
                                         "Sprites/pac-classic/ghost-orange-front.png",
                                         "Sprites/pac-classic/ghost-orange-right.png",
                                         "Sprites/pac-classic/ghost-orange-left.png",
                                         ],

                                        ["Sprites/pac-classic/ghost-lblue-rear.png",
                                         "Sprites/pac-classic/ghost-lblue-front.png",
                                         "Sprites/pac-classic/ghost-lblue-right.png",
                                         "Sprites/pac-classic/ghost-lblue-left.png",
                                         ],

                                    ]
        )




        #
        # CREAZIONE DEGLI SPRITES
        #

        # CREO I MIEI NEMICI
        self.createEnemies(self.numEnemies,self.enemies_filename,self.enemies)

        # CREO I MIEI NEMICI CHE SPARANO che aggiungo allo stesso gruppo dei nemici!
        self.createShooters(self.numShooters, self.shooters_filename, self.shooters_bullets_filename,self.shooterBullets,
                            self.sound_weapon, self.enemies)

        # CREO LE BOMBE che sono ObjectDestroyer che distruggono le monete
        self.createObjectDestroyers(self.bonus_bombs,self.bomb_filename,self.bombs, self.coins)


        # CREO LE WALL BOMBS che sono WallDestroyer che consentono di distruggere i muri
        # interni del labirinto
        self.createInnerObjectDestroyers(self.ncols, self.nrows,self.bonus_wall_bombs,
                                         self.wall_bomb_filename,self.wallBombs,self.walls)
        # CREO GLI ENEMY KILLERS che sono ObjectDestroyer che consentono di eliminare i nemici
        self.createObjectDestroyers(self.bonus_enemy_killers, self.enemy_killers_filename, self.enemyKillers, self.enemies)

        # Creo GREEDY_ENEMIES come ENEMY che consentono di rendere, alternativamente, i nemici golosi di monete oppure no
        self.createEnemies(self.bonus_greedy_enemies, self.greedy_enemies_filename, self.greedyEnemies)

        # Alternativamente potrei creare GREED ENEMIES come ObjectDestroyer che in realtà non distruggono niente, ma rendono "golosi"
        # i nemici che stanno intorno a loro in modo che inizino a mangiare monete. Se stanno già mangiando
        # monete, al contrario, dovrebbero smettere. CHIEDERLO COME ESERCIZIO

        # CREO I TIME RELOADERS che consentono di ripristinare il tempo
        self.createEnemies(self.numTimeReloaders, self.time_reloaders_filename,  self.timeReloaders)

        # CREO I PORTALI che consentono di trasferirsi in una nuova locazione random
        self.createEnemies(self.bonus_portals, self.portals_filename, self.portals)

        # CREO I TIME LIMITED POWERS, come quello che rende invisibile il giocatore
        self.createTimeLimitedPowers(self.bonus_invisibility_players, self.invisibility_players_filename, self.invisibilityPlayers)
        # e come il ricaricatore di proiettili
        self.createTimeLimitedPowers(self.bonus_player_bullets, self.bonus_player_bullets_filename, self.bonusPlayerBullets)

        self.mazeSurf = pygame.Surface((self.ncols * self.scale, self.nrows * self.scale))
        # disegno il labirinto coi suoi muri
        self.drawMaze()

        self.scrollSurface = self.mazeSurf.copy()
        #self.scrollSurface.fill((0, 0, 0))

        pos = random.choice(self.free_locations)
        print("Loc Player:%s" % str(pos))

        self.player.sprite.setPosition(pos)

        # imposto posizione e movimento iniziale
        # ai vari gruppi di sprites

        self.setInitialPosition(self.enemies.sprites())
        self.setInitialPosition(self.bombs.sprites())
        self.setInitialPosition(self.wallBombs.sprites())
        self.setInitialPosition(self.timeReloaders.sprites())
        self.setInitialPosition(self.enemyKillers.sprites())
        self.setInitialPosition(self.greedyEnemies.sprites())
        self.setInitialPosition(self.portals.sprites())
        self.setInitialPosition(self.invisibilityPlayers.sprites())
        self.setInitialPosition(self.bonusPlayerBullets.sprites())

        #self.setInitialPosition(self.shooters.sprites())

        # normalmente i nemici non mangiano monete...
        self.enemies_eater = False


        # a inizio livello si dà tempo di 5 secondi al Giocatore per divincolarsi
        # da eventuali nemici che compaiono negli immediati dintorni
        # della posizione (casuale) in cui si viene a trovare
        # il giocatore a inizio livello
        self.player.sprite.addPower(PlayerPowers.INVISIBILITY, (self.time,5))

        # imposto la musica del livello e la mando in esecuzione
        self.music = level.get("music", "./Music/Soundimage/Techno-Gameplay_Looping.ogg")
        pygame.mixer.music.load(self.music)
        # mando in esecuzione in modalità loop (valore -1)
        pygame.mixer.music.play(-1)

        # barra di stato del gioco con informazioni sul punteggio
        self.setupGamebarSurface()


    def createEnemies(self, num_enemies, obj_filename, group):
        for i in range(num_enemies):
            enemy = Enemy(int(self.scale * 0.8), int(self.scale * 0.8),
                          self.scale, 1,obj_filename, group)
            enemy.setWalls(self.walls)


    def createShooters(self, shooters_info, shooter_filename, bullet_filename, shooterBulletsGroup, soundBullet, group):
        for tlpo in shooters_info:
            for i in range(tlpo[0]):

                shooter = Shooter(int(self.scale * 0.8), int(self.scale * 0.8),
                                  self.scale, 1, shooter_filename, tlpo[1],
                                  bullet_filename, shooterBulletsGroup, soundBullet, group)

                shooter.setWalls(self.walls)


    def createTimeLimitedPowers(self, power_info, obj_filename,  group):
        for tlpo in power_info:
            for i in range(tlpo[0]):
                tlp = TimeLimitedPower(tlpo[1], int(self.scale * 0.8), int(self.scale * 0.8),
                          self.scale, 1,obj_filename, group)
                tlp.setWalls(self.walls)

    def createObjectDestroyers(self, obj_list, obj_filename, group, objects):
        for binfo in obj_list:
            for i in range(binfo[0]):
                #print("INFO %s" % str(binfo))
                o = ObjectDestroyer(int(self.scale * 0.8), int(self.scale * 0.8),
                              self.scale, 1, obj_filename, binfo[1], group)
                o.setWalls(self.walls)
                o.setObjects(objects)

    def createInnerObjectDestroyers(self,ncols, nrows, obj_list, obj_filename, group, objects):
        for binfo in obj_list:
            for i in range(binfo[0]):
                #print("INFO %s" % str(binfo))
                o = InnerObjectDestroyer(ncols,nrows, int(self.scale * 0.8), int(self.scale * 0.8),
                              self.scale, 1, obj_filename, binfo[1], group)
                o.setWalls(self.walls)
                o.setObjects(objects)


    def setInitialPosition(self, group):
        for o in group:
            pos = random.choice(self.free_locations)
            o.setPosition(pos)
            o.randomMove()

    def get_remaining_time(self):
        res = self.time - (time.time() - self.start)
        if res < 0:
            return 0
        else:
            return res

    def drawGamebarSurface(self):
        # draw text
        font = pygame.font.Font(None, 30)
        msg = "Tempo: %0.f   Vite: %s   Livello: %s   Monete mancanti: %s   Punteggio: %s" % \
              (self.remaining_time, self.numLives, self.levelIndex + 1, len(self.coins.sprites()), self.score)

        text = font.render(msg, True, Game.WHITE, Game.BLACK)
        text_rect = text.get_rect(center=(self.win_size[0] / 2, 25))
        self.gamebarSurface.fill(Game.BLACK)
        self.gamebarSurface.blit(text, text_rect)

        self.screen.blit(self.gamebarSurface, self.gamebarSurface.get_rect())

    def setupGamebarSurface(self):
        self.gamebarSurface = pygame.Surface((self.win_size[0], 80))
        self.font_gamebar = pygame.font.Font(None, 36)

        # pannello delle vite
        self.life_gamebar = pygame.transform.scale(pygame.image.load("Sprites/heart.png").convert(), (40, 40))
        self.life_gamebar_info_rect = Rect(10, 0, self.life_gamebar.get_rect().width, self.life_gamebar.get_rect().height)

        # pannello del tempo rimasto
        self.rem_time_gamebar = pygame.transform.scale(pygame.image.load("Sprites/clessidra.png").convert_alpha(), (40, 40))
        self.rem_time_gamebar_info_rect = Rect(self.rem_time_gamebar.get_rect().right + 2, self.rem_time_gamebar.get_rect().y + 10,
                                               self.rem_time_gamebar.get_rect().width, self.rem_time_gamebar.get_rect().height)

        # pannello delle monete mancanti
        self.coin_gamebar = pygame.transform.scale(pygame.image.load("Sprites/coin.png").convert_alpha(), (40, 30))
        self.coin_gamebar_info_rect = Rect(self.coin_gamebar.get_rect().right + 2, self.coin_gamebar.get_rect().y + 5, self.coin_gamebar.get_rect().width,
                                           self.coin_gamebar.get_rect().height)

        # pannello del punteggio
        self.score_gamebar = pygame.transform.scale(pygame.image.load("Sprites/score.png").convert_alpha(), (50, 50))
        self.score_gamebar_info_rect = Rect(self.score_gamebar.get_rect().right + 2, self.score_gamebar.get_rect().y + 15,
                                            80,
                                            self.score_gamebar.get_rect().height)

        # pannello del bonus invisibilità
        self.invisibility_bonus_gamebar = pygame.transform.scale(pygame.image.load(self.invisibility_players_filename).convert_alpha(), (40, 40))
        self.invisibility_bonus_gamebar_info_rect = Rect(self.invisibility_bonus_gamebar.get_rect().right + 2,
                                                         self.invisibility_bonus_gamebar.get_rect().y +  10,
                                                         40,
                                                         self.invisibility_bonus_gamebar.get_rect().height)

        # pannello del bonus dell'arma
        self.weapon_bonus_gamebar = pygame.transform.scale(pygame.image.load(self.player_bullets_filename).convert_alpha(),
                                                                 (50, 50))
        self.weapon_bonus_gamebar_info_rect = Rect(self.weapon_bonus_gamebar.get_rect().right + 2,
                                                         self.weapon_bonus_gamebar.get_rect().y + 15,
                                                         40,
                                                         self.weapon_bonus_gamebar.get_rect().height)

        # pannello dei greedy enemies (on/off)
        self.greedy_enemies_bonus_gamebar = pygame.transform.scale(pygame.image.load(self.greedy_enemies_filename).convert_alpha(),(40, 40))

    def drawNewGamebarSurface(self):

        self.gamebarSurface.fill(Game.BLACK)

        # pannello delle vite

        info_life = self.font_gamebar.render("%s" % self.numLives, True, Game.WHITE, Game.BLACK)
        info_life_rect = Rect(self.life_gamebar_info_rect.right - 2, self.life_gamebar_info_rect.y + 10, self.life_gamebar_info_rect.width, self.life_gamebar_info_rect.height)

        life_panel = pygame.Surface((self.life_gamebar_info_rect.width + info_life_rect.width, self.life_gamebar_info_rect.height + info_life_rect.height))
        life_panel.blit(self.life_gamebar, self.life_gamebar.get_rect())
        life_panel.blit(info_life, info_life_rect)
        #####################################

        # Pannello del tempo
        color = Game.WHITE
        if self.remaining_time<10:
            color = Game.ORANGE
        info_time = self.font_gamebar.render(" %.0f " % self.remaining_time, True, color, Game.BLACK)

        time_panel = pygame.Surface((self.rem_time_gamebar.get_rect().width + self.rem_time_gamebar_info_rect.width + 20, self.rem_time_gamebar.get_rect().height + self.rem_time_gamebar_info_rect.height))
        time_panel.blit(self.rem_time_gamebar, self.rem_time_gamebar.get_rect())
        time_panel.blit(info_time, self.rem_time_gamebar_info_rect)
        ############################################

        # Pannello delle monete mancanti
        info_coin = self.font_gamebar.render(" %s" % len(self.coins.sprites()), True, Game.WHITE, Game.BLACK)

        coin_panel = pygame.Surface(
            (self.coin_gamebar.get_rect().width + self.coin_gamebar_info_rect.width + 20, self.coin_gamebar.get_rect().height + self.coin_gamebar_info_rect.height))
        coin_panel.blit(self.coin_gamebar, self.coin_gamebar.get_rect())
        coin_panel.blit(info_coin, self.coin_gamebar_info_rect)
        ############################################

        # pannello del livello
        font_level = pygame.font.Font(None, 40)
        panel_level = font_level.render("Livello %s" % (self.levelIndex+1), True, Game.WHITE, Game.BLACK)

        # pannello del punteggio
        info_score = self.font_gamebar.render(" %s" % self.score, True, Game.WHITE, Game.BLACK)

        panel_score = pygame.Surface(
            (self.score_gamebar.get_rect().width + self.score_gamebar_info_rect.width + 20,
             self.score_gamebar.get_rect().height + self.score_gamebar_info_rect.height))
        panel_score.blit(self.score_gamebar, self.score_gamebar.get_rect())
        panel_score.blit(info_score, self.score_gamebar_info_rect)
        ###########################################

        # pannello del bonus di invisibilità
        if self.player.sprite.hasPower(PlayerPowers.INVISIBILITY):
            powerStart, powerDuration = self.player.sprite.getPower(PlayerPowers.INVISIBILITY)
            remTime = self.remaining_time - (powerStart - powerDuration)
            color = Game.WHITE
            if remTime < 10:
                color = Game.ORANGE
            info_invisibility = self.font_gamebar.render(" %.0f" % max(0, remTime), True,color, Game.BLACK)
            panel_invisibility = pygame.Surface((self.invisibility_bonus_gamebar.get_rect().width+
                                                self.invisibility_bonus_gamebar_info_rect.width,
                                                self.invisibility_bonus_gamebar_info_rect.height)

                                                )
            panel_invisibility.blit(self.invisibility_bonus_gamebar, self.invisibility_bonus_gamebar.get_rect())
            panel_invisibility.blit(info_invisibility, self.invisibility_bonus_gamebar_info_rect)

        # pannello del bonus dell'arma
        if self.player.sprite.hasPower(PlayerPowers.WEAPON):
            powerStart, powerDuration = self.player.sprite.getPower(PlayerPowers.WEAPON)
            remTime = self.remaining_time - (powerStart - powerDuration)
            color = Game.WHITE
            if remTime < 10:
                color = Game.ORANGE
            info_weapon = self.font_gamebar.render(" %.0f" % max(0, remTime), True, color, Game.BLACK)
            panel_weapon = pygame.Surface((self.weapon_bonus_gamebar.get_rect().width +
                                                 self.weapon_bonus_gamebar_info_rect.width,
                                                 self.weapon_bonus_gamebar_info_rect.height)


                                                )
            panel_weapon.blit(self.weapon_bonus_gamebar, self.weapon_bonus_gamebar.get_rect())
            panel_weapon.blit(info_weapon, self.weapon_bonus_gamebar_info_rect)

        # disposizione dei pannelli

        panels_distance = 5

        nextRect =  life_panel.get_rect()
        nextRect.centery = self.gamebarSurface.get_rect().centery + 20
        self.gamebarSurface.blit(life_panel, nextRect)

        nextRect.x = nextRect.right + panels_distance
        nextRect.width = time_panel.get_rect().width
        self.gamebarSurface.blit(time_panel, nextRect)

        nextRect.x = nextRect.right + panels_distance
        nextRect.width = coin_panel.get_rect().width
        nextRect.y += 5
        self.gamebarSurface.blit(coin_panel, nextRect)

        #il pannello del livello lo voglio centrato sulla barra
        panel_level_rect = Rect(0,0,panel_level.get_rect().width,panel_level.get_rect().height)
        panel_level_rect.center = self.gamebarSurface.get_rect().center
        self.gamebarSurface.blit(panel_level, panel_level_rect)

        # il pannello del punteggio lo voglio allineato sulla destra sulla barra
        panel_score_rect = Rect(0, 0, panel_score.get_rect().width, panel_score.get_rect().height)
        panel_score_rect.right = self.gamebarSurface.get_rect().right
        panel_score_rect.centery = self.gamebarSurface.get_rect().centery + 20
        self.gamebarSurface.blit(panel_score, panel_score_rect)

        # i pannelli dei bonus li mostriamo allineati sulla destra, ma a sinistra del pannello
        # del punteggio

        last_pos = panel_score_rect.left - panels_distance
        if self.player.sprite.hasPower(PlayerPowers.INVISIBILITY):
            panel_invisibility_rect = panel_invisibility.get_rect()
            panel_invisibility_rect.right = last_pos
            last_pos = panel_invisibility_rect.left - panels_distance
            panel_invisibility_rect.centery = self.gamebarSurface.get_rect().centery - 5
            #panel_invisibility.fill(pygame.Color('white'))
            self.gamebarSurface.blit(panel_invisibility, panel_invisibility_rect)

        if self.player.sprite.hasPower(PlayerPowers.WEAPON):
            panel_weapon_rect = panel_weapon.get_rect()
            panel_weapon_rect.right = last_pos  # - 130
            last_pos = panel_weapon_rect.left - panels_distance
            panel_weapon_rect.centery = self.gamebarSurface.get_rect().centery - 5
            self.gamebarSurface.blit(panel_weapon, panel_weapon_rect)

        # pannello dei greedy enemies
        if self.enemies_eater == True:
            panel_greedy_enemies_rect = self.greedy_enemies_bonus_gamebar.get_rect()
            panel_greedy_enemies_rect.right = last_pos - panels_distance # - 280
            last_pos = panel_greedy_enemies_rect.left
            panel_greedy_enemies_rect.centery = self.gamebarSurface.get_rect().centery - 5
            self.gamebarSurface.blit(self.greedy_enemies_bonus_gamebar, panel_greedy_enemies_rect)

        self.screen.blit(self.gamebarSurface, self.gamebarSurface.get_rect())


    def drawMessage(self,message, delay=0, clear=True):
        # draw text
        font = pygame.font.Font(None, 52)
        text = font.render(" %s " % message, True, Game.WHITE, Game.BLACK)
        text_rect = text.get_rect(center=(self.win_size[0] / 2, self.win_size[1] / 2))
        if clear==True:
            self.screen.fill(Game.BLACK)
        self.screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(delay)


    #https://stackoverflow.com/questions/42014195/rendering-text-with-multiple-lines-in-pygame
    def drawMultilineText(self, surface, text, pos, font, color=pygame.Color('white')):
        words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
        space = font.size(' ')[0]  # The width of a space.
        max_width, max_height = surface.get_size()
        x, y = pos
        for line in words:
            for word in line:
                word_surface = font.render(word, 1, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.

        # restituiamo posizione [x,y] per successive scritture
        return [x,y]

    def drawHelpText(self, clear=False):
        """
        Mostra a video le istruzioni di gioco
        :param clear: se pari a True, cancella lo scchermo, altrimenti si sovrappone a quanto presente
        :return:
        """
        if clear==True:
            self.screen.fill(Game.BLACK)

        helpSurface = pygame.Surface((self.win_size[0]-10,self.win_size[1]))
        msgIntro = "Lo scopo del gioco è quello di raccogliere tutte le monete del labirinto " + \
        "entro il tempo limite riuscendo a evitare il contatto con i vari nemici.\n" + \
        "Oltre ai nemici veri e propri, nel labirinto possono comparire altri personaggi " + \
        "con dei poteri che possono venirti in aiuto. \nEcco l'elenco completo:\n"
        pos = (10,10)
        font = pygame.font.Font(None, 26)


        pos = self.drawMultilineText(helpSurface, msgIntro, pos, font)

        elementsInfo = [
                        (self.enemies_filename,
                         "Nemici: evitate ogni contatto con loro e coi loro proiettili per non perdere una vita!"),

                        (self.time_reloaders_filename,
                         "Clessidra: ripristina il tempo a disposizione"),

                        (self.enemy_killers_filename,
                         "Bomba distruggi nemici: rimuove i nemici che si trovano nel suo intorno. A seconda del potere della bomba, il raggio di azione puo' variare"),

                        (self.bomb_filename,
                         "Bomba distruggi monete: rimuove le monete che si trovano nel suo intorno. A seconda del potere della bomba, il raggio di azione puo' variare"),

                        (self.wall_bomb_filename,
                         "Bomba distruggi muri: distrugge i muri che si trovano nel suo intorno. A seconda del potere della bomba, il raggio di azione puo' variare"),

                        (self.greedy_enemies_filename, "Pizza: rende i nemici golosi di monete, aiutandovi così a concludere il livello. Attenzione che una nuova pizza rende i nemici indigesti e smetteranno di mangiarle!"),

            (self.portals_filename, "Portale: consente di essere teletrasportati in una nuova posizione!"),

            (self.invisibility_players_filename,
             "Invisibilità: rende il giocatore invisibile ai nemici, per un lasso di tempo che puo' variare"),

            (self.bonus_player_bullets_filename,
             "Arma: consente al giocatore di sparare ai nemici, per un lasso di tempo che puo' variare"),

        ]


        for e in elementsInfo:
            pos[1] += 30
            image = pygame.image.load(e[0]).convert_alpha()
            image = pygame.transform.scale(image, (30, 30))
            er = image.get_rect()
            er[0] = 10
            er[1] = pos[1]
            helpSurface.blit(image, er)
            # la descrizione va a destra della immagine
            pos[0] = image.get_rect().right + 20
            pos = self.drawMultilineText(helpSurface, e[1], pos, font)

        help_rect = helpSurface.get_rect(center=(self.win_size[0] / 2, self.win_size[1] / 2 + self.gamebarSurface.get_rect().height))
        self.screen.blit(helpSurface, help_rect)
        pygame.display.flip()
        #pygame.time.wait(delay)


    def drawMaze(self):
        """
        Crea i muri del labirinto, sulla base delle informazioni
        presenti nella matrice booleana self.maze
        I corridoi vengono automaticamente riempiti di monete
        La dimensione del labirinto dipende dal fattore di scala self.scale
        Da notare che, per semplicità di implementazione, lo spessore
        dei muri è sempre uguale alla larghezza dei corridoi
        :return:
        """
        self.free_locations = []
        #print("Righe: %s Colonne:%s" % (len(self.maze) , len(self.maze[0])) )
        for y in range(len(self.maze)):
            for x in range(len(self.maze[y])):
                #print(self.maze[y][x])
                if (self.maze[y][x]):
                    #print("Disegno in posizione (%s,%s)" % (x,y))
                    wall = Wall(self.scale, self.scale, self.wall_filename, self.walls)
                    wall.rect.topleft = (x*self.scale,y*self.scale)
                else:
                    self.free_locations.append((x,y))

                    # se si desidera, si puo' ridurre il numero
                    # di monete da raccogliere in modo random
                    #pr = random.randint(1, 100)
                    #if pr < 50: # 50% delle monete circa
                    #    continue

                    coin = Coin(self.coin_color,self.scale/4, self.scale/4, self.coins)
                    coin.rect.topleft = ( (x  * self.scale) + self.scale/2 - coin.rect.width/2,
                                          (y * self.scale) + self.scale/2 - coin.rect.height/2 )

    def removeLife(self):
        self.numLives -= 1
        if self.numLives <= 0:
            self.state = GameState.PLAYER_LOOSE
            self.done = True
        else:
            msg = "Vita persa!!! Ne hai ancora %s! " % self.numLives
            self.drawMessage(msg, 3000)
            self.setupLevel()
            self.run()


    def run(self):
        """
        Metodo che consente di far partire un livello di gioco
        :return:
        """

        # avviso l'utente sul livello che sta per partire il livello di
        # gioco corrente
        #self.drawMessage(" Livello %s " % (self.levelIndex + 1), 2000)
        self.state = GameState.PLAYING

        # variabili per la gestione del tempo
        # del corrente livello di gioco
        self.start = time.time()
        self.remaining_time = self.time
        pause_time = 0

        # incremento della velocita del giocatore
        # che aumento se si tiene premuta la barra spaziatrice
        vel_inc = 0

        # memorizzo il tipo di movimento da far eseguire al player
        player_move_action = self.player.sprite.stop


        # ciclo principale del gioco
        while not self.done:

            # gestione degli eventi
            for ev in pygame.event.get():

                if ev.type == QUIT:
                    self.done = True
                elif ev.type == KEYDOWN:
                    if ev.key == K_q:
                        self.done = True

                    # verifico per lo sparo
                    elif ev.key == K_LCTRL:
                        self.player.sprite.shot(self.player_bullets_filename, self.playerBullets, self.sound_weapon)
                    elif ev.key == K_SPACE:
                            vel_inc = 1
                    elif ev.key == K_LEFT:
                        player_move_action = self.player.sprite.moveLeft
                    elif ev.key == K_RIGHT:
                        player_move_action = self.player.sprite.moveRight
                    elif ev.key == K_UP:
                        player_move_action = self.player.sprite.moveUp
                    elif ev.key == K_DOWN:
                        player_move_action = self.player.sprite.moveDown
                    elif ev.key == K_r:
                        self.setupLevel()
                        self.run()
                    elif ev.key == K_n:
                        self.levelIndex += 1
                        self.setupLevel()
                        self.run()
                    elif ev.key == K_b:
                        self.levelIndex -= 1
                        self.setupLevel()
                        self.run()
                    elif ev.key == K_p or ev.key==K_h:
                        if self.state == GameState.PLAYING:
                            # registro l'istante in cui è avvenuta la pausa
                            pause_time = time.time()
                            if ev.key==K_p:
                                self.state = GameState.PAUSED
                            else:
                                self.state = GameState.HELP
                        else:
                            # ricavo il tempo passato da quando sono in pausa
                            dtime = time.time() - pause_time
                            # aumento il numero di secondi del tempo iniziale
                            # con quelli trascorsi durante la pausa
                            self.start += dtime
                            self.state = GameState.PLAYING
                        print("Stato:%s" % self.state)
                elif ev.type == KEYUP:
                    if ev.key == K_SPACE:
                        vel_inc = 0
                    elif ev.key != K_LCTRL:
                        player_move_action =self.player.sprite.stop

                # se ho un joystick collegato lo uso per gli spostamenti
                if self.joystick!=None:
                    velx = self.joystick.get_axis(0)
                    vely = self.joystick.get_axis(1)
                    #print("%s %s" % (velx,vely))
                    self.player.sprite.move(velx,vely)
                    # controllo se ho premuto un pulsante per lo sparo
                    if ev.type == pygame.JOYBUTTONDOWN:
                        self.player.sprite.shot(self.player_bullets_filename, self.playerBullets, self.sound_weapon)
                # altrimenti uso le informazioni ricevute dalla tastiera
                else:
                    # aziono il movimento del giocatore sulla base
                    # della combinazione dei tasti premuti
                    player_move_action(vel_inc)

            # aggiorno la posizione del giocatore e
            # dei nemici, verifico collisioni e poteri
            # solo se sono in fase di gioco

            if self.state == GameState.PLAYING:
                self.remaining_time = self.get_remaining_time()
                if self.remaining_time <= 0:
                    self.removeLife()

                # aggiorno le posizioni di tutti gli sprite
                self.updateAllSpritesPositions()

                # gestisco le collisioni di tutti gli sprite
                self.handleAllSpritesCollisions()

                # gestisco i vari poteri del player
                self.handlePowers()


                # verifico se ho, in un modo o nell'altro.
                # rimosso tutte le monete..in tal caso
                # dichiaro il livello completato
                if len(self.coins.sprites()) ==0:
                    if self.levelIndex>=len(levels)-1:
                        self.state = GameState.PLAYER_WON
                        self.done = True
                    else:
                        self.state = GameState.LEVEL_COMPLETED

            #
            # Aggiornamento dello schermo
            #

            #cancello lo schermo
            self.screen.fill((0, 0, 0))


            # il labirinto lo inserisco nella superficie scrollabile
            self.scrollSurface.blit(self.mazeSurf,self.mazeSurf.get_rect())

            # disegno tutti gli sprite di gioco
            self.drawAllSprites()


            # centro la superficie del labirinto rispetto al centro del giocatore
            sc_x = self.screen.get_rect().center[0] - self.player.sprite.rect.center[0]
            sc_y = self.screen.get_rect().center[1] - self.player.sprite.rect.center[1]
            scrollSurfaceRect = Rect((sc_x,sc_y+self.gamebarSurface.get_rect().height),(self.scrollSurface.get_rect().width, self.scrollSurface.get_rect().height))

            if (self.background_image!=None):
                self.screen.blit(self.background_image,(0,0))
            self.screen.blit(self.scrollSurface, scrollSurfaceRect)

            # disegno la barra di informazioni di gioco
            self.drawNewGamebarSurface()

            #  gestisco la logica di gioco sulla base dello stato corrente
            self.handleGameState()

            # riporto tutto a video
            # n.b: se ometto la seguente istruzione non vedo nulla!
            pygame.display.flip()

            # scandisco la velocità del gioco
            self.clock.tick(self.clockTime)


        # --- Uscita dal gioco
        pygame.mixer.music.stop()
        while pygame.mixer.get_busy():
            self.clock.tick(30)

        print("Uscita")
        pygame.quit()
        sys.exit()


    def updateAllSpritesPositions(self):
        """
        Qui aggiorno le posizioni di tutti gli sprite del gioco!
        :return:
        """

        # aggiorno posizione del player
        self.player.update()

        # aggiorno posizione dei nemici
        self.enemies.update()

        # aggiorno posizione delle bombe
        self.bombs.update()

        # aggiorno posizione delle wall bombs
        self.wallBombs.update()

        # aggiorno posizione dei ricaricatori del tempo
        self.timeReloaders.update()

        # aggiorno posizione dei killer dei nemici
        self.enemyKillers.update()

        # aggiorno la posizione dei greedy enemies
        self.greedyEnemies.update()

        # aggiorno la posizione di tutti i portali
        self.portals.update()

        # aggiorno la posizione di tutti gli invisible players
        self.invisibilityPlayers.update()

        # aggiorno la posizione di tutti i proiettili insieme al bonus
        self.playerBullets.update()
        self.bonusPlayerBullets.update()

        # aggiorno la posizione dei proiettili degli nemici che sparano
        #self.shooters.update()
        self.shooterBullets.update()


    def handleAllSpritesCollisions(self):
        """
        Qui gestisco tutte le collisioni di gioco!
        :return:
        """
        # verifico le collisioni coi nemici
        # purchè il giocatore sia per loro visibile
        if self.player.sprite.getState() == PlayerState.VISIBILE:
            if pygame.sprite.groupcollide(self.player, self.enemies, False, False):
                print("COLLISIONE CON NEMICO")
                self.sound_explosion.play()
                self.removeLife()


        # verifico le collisioni coi proiettili sparati dai nemici che sparano
        # purchè il giocatore sia per loro visibile
        if self.player.sprite.getState() == PlayerState.VISIBILE:
            if pygame.sprite.groupcollide(self.player, self.shooterBullets, False, False):
                print("COLLISIONE CON NEMICO")
                self.sound_explosion.play()
                self.removeLife()

        # verifico le collisioni con le bombe che rimuovon le monete nel loro intorno
        bombCollisions = pygame.sprite.groupcollide(self.player, self.bombs, False, True)
        if bombCollisions:
            self.sound_bomb_explosion.play()
            bombs = bombCollisions[self.player.sprite]
            for b in bombs:
                self.score += Score.COIN * b.getRemovedObjects()

        # verifico le collisioni con le wall bombs
        if pygame.sprite.groupcollide(self.player, self.wallBombs, False, True):
            self.sound_explosion.play()

        # verifico le collisioni con gli enemyKillers
        enemyKillersCollisions = pygame.sprite.groupcollide(self.player, self.enemyKillers, False, True)
        if enemyKillersCollisions:
            self.sound_enemy_killer.play()
            enemies = enemyKillersCollisions[self.player.sprite]
            for e in enemies:
                self.score += Score.ENEMY * e.getRemovedObjects()

        # verifico le collisioni coi timerReloaders
        if pygame.sprite.groupcollide(self.player, self.timeReloaders, False, True):
            self.sound_time_reloader.play()
            self.start = time.time()

        # verifico le collisioni con le monete
        if pygame.sprite.groupcollide(self.player, self.coins, False, True):
            self.sound_coin.play()
            self.score += Score.COIN

        # verifico le collisioni con i greedy enemies
        if pygame.sprite.groupcollide(self.player, self.greedyEnemies, False, True):
            self.sound_greedy_enemies.play()
            self.enemies_eater = not self.enemies_eater

        # verifico le collisioni tra proiettili e nemici
        if pygame.sprite.groupcollide(self.playerBullets, self.enemies, True, True):
            self.sound_explosion.play()
            self.score += Score.ENEMY

        # le collisioni tra proiettili e muri
        # sono gestite internamente alla classe Bullet

        # verifico le collisioni tra bonus dei proiettili e giocatore
        weaponPlayersCollisions = pygame.sprite.groupcollide(self.player, self.bonusPlayerBullets, False, True)
        if weaponPlayersCollisions:

            weapon_players = weaponPlayersCollisions[self.player.sprite]
            print("Collisione con bonusPlayersBullet: %s" % len(weapon_players))
            for p in  weapon_players:
                # riassegno le armi del mio giocatore
                # da notare che se il potere in questione esiste gia'
                # esso viene sovrascritto dal nuovo valore di potere
                self.sound_weapon.play()
                print("Aggiungo il potere dell'arma per %s secondi" % p.get_duration())
                self.player.sprite.addPower(PlayerPowers.WEAPON,
                                                (self.get_remaining_time(), p.get_duration()))

        # nel caso il valore di enemies_eater sia attivo
        # verifico la collosione con le monete anche per i nemici
        if self.enemies_eater:
            if pygame.sprite.groupcollide(self.enemies, self.coins, False, True):
                self.sound_coin.play()
                self.score += Score.COIN

        # nel caso il giocatore collida con un portale, viene
        # catapultato su una nuova posizione a caso!
        if pygame.sprite.groupcollide(self.player, self.portals, False, True):
            self.sound_portal.play()
            # nel caso al momento il player non abbia il potere della invisibilita
            # gliene do' un po'...
            if not self.player.sprite.hasPower(PlayerPowers.INVISIBILITY):
                # do' il tempo al giocatore di schivare eventuali avversari
                # attorno alla sua nuova posizione...
                self.player.sprite.addPower(PlayerPowers.INVISIBILITY, (self.get_remaining_time(),5))
            # scelgo una nuova posizione a caso tra quelle libere da muri
            self.player.sprite.setPosition(random.choice(self.free_locations))

        # verifico le collisioni con gli invisibilityPlayers
        invisiblePlayersCollisions = pygame.sprite.groupcollide(self.player, self.invisibilityPlayers, False, True)
        if invisiblePlayersCollisions:
            inv_players = invisiblePlayersCollisions[self.player.sprite]
            for p in inv_players:
                # riassegno il potere di invisibilità del mio giocatore
                # da notare che se il potere in questione esiste gia'
                # esso viene sovrascritto dal nuovo valore di potere
                self.sound_invisibility_player.play()
                self.player.sprite.addPower(PlayerPowers.INVISIBILITY,(self.get_remaining_time(), p.get_duration()))


    def handlePowers(self):
        """
        Qui gestisco i poteri dei giocatori e/o dei nemici
        :return:
        """
        self.player.sprite.handlePowers(self.get_remaining_time())



    def handleGameState(self):
        """
        Qui decido le azioni da intraprendere sulla base
        dello stato corrente del gioco
        :return:
        """
        if self.state == GameState.PLAYER_LOOSE:
            self.drawMessage(" Hai perso! ", 3000)
        elif self.state == GameState.LEVEL_COMPLETED:
            self.sound_completed_level.play()
            code = self.get_code(self.levelIndex+1)
            code_msg = ""
            if code:
                code_msg = "[Codice Bonus:%s]" % code
            self.drawMessage(" Livello %s completato! %s" % ((self.levelIndex + 1), code_msg), 3000)
            self.levelIndex += 1
            self.screen.fill(Game.BLACK)
            self.setupLevel()
            self.run()
        elif self.state == GameState.PLAYER_WON:
            self.drawMessage("Hai vinto!", 5000)
            # esco dal gioco poiche' ho terminato
            # valutare se chiedere di rincominciare la partita...
            pygame.quit()
        elif self.state == GameState.PAUSED:
            self.drawMessage("Pausa", 0, False)
        elif self.state == GameState.HELP:
            self.drawHelpText()


    def drawAllSprites(self):
        """
        Disegno tutti gli sprite
        :return:
        """

        # disegno il labirinto
        self.walls.draw(self.scrollSurface)

        # disegno le monete
        self.coins.draw(self.scrollSurface)

        # disegno il giocatore
        self.player.draw(self.scrollSurface)

        # disegno i nemici
        self.enemies.draw(self.scrollSurface)

        # disegno le bombe
        self.bombs.draw(self.scrollSurface)

        # disegno le wall bombs
        self.wallBombs.draw(self.scrollSurface)

        # disegno i killer enemies
        self.enemyKillers.draw(self.scrollSurface)

        # disegno i ricaricatori del tempo
        self.timeReloaders.draw(self.scrollSurface)

        # disegno i greedy enemies
        self.greedyEnemies.draw(self.scrollSurface)

        # disegno i portali
        self.portals.draw(self.scrollSurface)

        # disegno i nemici che rendono invisibile il giocatore
        self.invisibilityPlayers.draw(self.scrollSurface)

        # disegno i proiettili del giocatore insieme allo sprite del bonus
        self.playerBullets.draw(self.scrollSurface)
        self.bonusPlayerBullets.draw(self.scrollSurface)

        # disegno i proiettili sparatu dai nemici
        self.shooterBullets.draw(self.scrollSurface)


    def get_code(self, level):
        code_levels= { 1 : [77,65,71,79] }
        return self.get_magic(code_levels.get(level, []))

    def get_magic(self, codes):
        code = ""
        for c in codes:
            code+= chr(c)
        return code

    def generate_maze(self):
        """
        Genero il labirinto, sulla base del valore dei parametri
        di configurazione
        https://en.wikipedia.org/wiki/Maze_generation_algorithm
        This algorithm works by creating n (density) islands of length p (complexity).
        With a low complexity,islands are very small and the maze is easy to solve.
        With low density, the maze has more "big empty rooms".
        :return:
        """
        complexity = self.maze_complexity
        density = self.maze_density
        width = self.ncols-1
        height = self.nrows-1

        """Generate a maze using a maze generation algorithm."""
        # Only odd shapes
        shape = ((height // 2) * 2 + 1, (width // 2) * 2 + 1)
        # Adjust complexity and density relative to maze size
        complexity = int(complexity * (5 * (shape[0] + shape[1])))  # Number of components
        density    = int(density * ((shape[0] // 2) * (shape[1] // 2)))  # Size of components
        # Build actual maze
        Z = numpy.zeros(shape, dtype=bool)
        # Fill borders
        Z[0, :] = Z[-1, :] = 1
        Z[:, 0] = Z[:, -1] = 1
        # Make aisles
        for i in range(density):
            x, y = rand(0, shape[1] // 2) * 2, rand(0, shape[0] // 2) * 2  # Pick a random position
            Z[y, x] = 1
            for j in range(complexity):
                neighbours = []
                if x > 1:             neighbours.append((y, x - 2))
                if x < shape[1] - 2:  neighbours.append((y, x + 2))
                if y > 1:             neighbours.append((y - 2, x))
                if y < shape[0] - 2:  neighbours.append((y + 2, x))
                if len(neighbours):
                    y_, x_ = neighbours[rand(0, len(neighbours) - 1)]
                    if Z[y_, x_] == 0:
                        Z[y_, x_] = 1
                        Z[y_ + (y - y_) // 2, x_ + (x - x_) // 2] = 1
                        x, y = x_, y_
        return Z


if __name__ == '__main__':
    # creo un nuovo gioco
    # (che include la configurazione del primo livello)
    #game = Game((1200,800), False)
    game = Game((1200, 800), True)
    # faccio partire il nuovo livello di gioco
    game.run()