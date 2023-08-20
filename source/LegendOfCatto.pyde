add_library('minim')
import os,random


SCRN_WIDTH = 1280
SCRN_HEIGHT = 720
GND = SCRN_HEIGHT-100
GAME_LAG_THRESHHOLD = 500

# CATTO STATS DISPLAY IN THE CORNER VARIABLES
STATS_POSX = 20
STATS_POSY = 40

PATH =os.getcwd()
minim=Minim(this)

# TO AVOID PYTHON APPROXIMATING ERROR (ESPECIALLY IN THE MOVING PLATFORM CASE)
ERROR_THRESHHOLD=0.00000001

# LIST OF THE GAINS WITH THEIR INDEX SET TO THE VOLUME NUMBERS
VOLUME_DICT = [-100]+list(range(-34,26,6)) #diff*11

# AN UNUSED LIST TO MAP THE DIFFERENT MODES OF THE GAME SO THAT IT IS EASY TO KNOW WHAT PAGE LEADS WHERE

MODES=['menu', # MAIN MENU
       'controls', # MAIN MENU - CONTROLS
       'settings', # MAIN MENU - SETTINGS
       'credits', # MAIN MENU - CREDITS
       'confirmationMessageMenu', # MAIN MENU - EXIT - CONFIRMATION
       'game', # MAIN MENU - GAME
       'pause', # MAIN MENU - GAME - PAUSE
       'pausedControlMenu', # MAIN MENU - GAME - PAUSE - CONTROLS
       'pausedSettingsMenu', # MAIN MENU - GAME - PAUSE - SETTINGS
       'confirmationMessageMainMenu', # MAIN MENU - GAME - PAUSE - RETURN TO MAIN MENU
       'confirmationMessage', # MAIN MENU - GAME - PAUSE - EXIT - CONFIRMATION
       'gameover', # MAIN MENU - GAME - GAME OVER
       'highscore', # MAIN MENU - GAME - GAME OVER - HIGH SCORES
       ]

# DICT OF SCORES
SCORES_DICT = {'BIRDO_KILL':200,'COIN':40,'STAMINA':50,'HEALTH':50,'CHECKPOINT':1000,'BOSS':2000,'WIN':10000}

# CHEAT CODES DICT
CHEAT_CODES = {'PURRFECT':'HEALTH','STAMEWNA':'STAMINA','LAZYBLOB':'STAGE CLEAR'}
CHEAT_CODE_MAX_LEN = 8


def setup():
    size(SCRN_WIDTH,SCRN_HEIGHT)
    # fullScreen()
    background(0)
    # CUSTOM FONT FOR ARCADE VIBES
    font = createFont(PATH+"/Resources/fonts/8-BIT WONDER.TTF",36)
    textFont(font)
    frameRate(60) # DO NOT MESS WITH THE FRAME RATE


############################################################################################################
############################################################################################################

# CLASSES BEGIN HERE

############################################################################################################
############################################################################################################


# PLATFORM CLASSES
############################################################################################################

class Platform():
    def __init__(self,posX,posY,w,h,img):
        self.posX = posX
        self.posY = posY
        self.w = w
        self.h = h
        self.img = img

        # ALL THE FOUR CORNERS ARE STORED IN THE COORDSX and CORRDSY ATTRIBUTE
        self.coordsX=[self.posX,self.posX+self.w]
        self.coordsY=[self.posY,self.posY+self.h]

        self.vX=0
        self.vY=0
        self.rangeX=0
        self.rangeY=0
        self.initX=posX
        self.initY=posY

        self.solid = True
        self.label = "platform"

    # WE'LL USE THE UPDATE FOR THE MOVING AND POPUP PLATFORMS
    def update(self):
        pass

    def display(self,update=True):
        if update:
            self.update()
        image(self.img,self.posX-game.gameX,self.posY-game.gameY,self.w,self.h)

class MovingPlatform(Platform):
    def __init__(self,posX,posY,w,h,img,vX,vY,rangeX,rangeY):
        Platform.__init__(self,posX,posY,w,h,img)

        self.speedX=vX # THE VALUE OF THE SPEED, WE DO NOT CHANGE IT
        self.speedY=vY
        self.vX=vX
        self.vY=vY
        self.rangeX=rangeX # THE EXTENT OF MOVEMENT IN X DIRECTON
        self.rangeY=rangeY # THE EXTENT OF MOVEMENT IN Y DIRECTON
        self.initX=posX
        self.initY=posY
        self.prevDt = 1/60
        self.label = "moving"

    def update(self):

        if self.initX+self.rangeX<self.posX:
            self.posX = self.initX+self.rangeX
            self.vX = -self.speedX
        elif self.initX>self.posX:
            self.posX = self.initX
            self.vX=self.speedX
        if self.initY+self.rangeY<self.posY:
            self.posY = self.initY+self.rangeY
            self.vY = -self.speedY
        elif self.initY>self.posY:
            self.posY = self.initY
            self.vY= self.speedY

        self.posX+=self.vX*game.dt
        self.posY+=self.vY*game.dt

        self.prevDt = game.dt

        self.coordsX=[self.posX,self.posX+self.w]
        self.coordsY=[self.posY,self.posY+self.h]


class PopUpPlatform(Platform):
    def __init__(self,posX,posY,w,h,img,timePeriod):
        Platform.__init__(self,posX,posY,w,h,img)
        self.solid = True
        self.timePeriod = timePeriod*1000
        self.t=0
        self.threshhold=0.1
        self.label = "popup"

    def update(self):
        self.t += (game.dt)

        if self.t > self.timePeriod:
            self.t=0
            self.solid = not (self.solid)

    def display(self,update=True):
        if update:
            self.update()
        if self.solid:
            opacity=map(self.t,self.timePeriod-self.threshhold,self.timePeriod,255,0)
            tint(255,opacity)

            image(self.img,self.posX-game.gameX,self.posY-game.gameY,self.w,self.h)
            tint(255,255)

# OBSTACLE CLASS
class Obstacle():
    def __init__(self,posX,displayW,displayH,type,img):
        self.posX = posX
        self.posY = GND
        self.displayW = displayW
        self.displayH = displayH

        self.coordsX = [self.posX,self.posX+self.displayW]
        self.coordsY = [self.posY,self.posY+self.displayH]
        self.gnd = GND + self.displayH - 10
        self.type = type
        self.img = img
    def displayBG(self):
        if self.type=='trap':
            noStroke()
            fill(84,76,72)
            rect(self.posX-game.gameX,self.posY,self.displayW,self.displayH)
        if self.type == 'water':
            image(self.img,self.posX-game.gameX,self.posY,self.displayW,self.displayH,0,0,self.displayW,self.displayH)
            image(self.img,self.posX+self.displayW-10-game.gameX,self.posY,10,self.displayH,0,0,10,self.displayH)
    def display(self):
        if self.type=='water':
            tint(255,100)
        image(self.img,self.posX-game.gameX,self.posY,self.displayW,self.displayH,0,0,self.displayW,self.displayH)
        image(self.img,self.posX+self.displayW-10-game.gameX,self.posY,10,self.displayH,0,0,10,self.displayH)
        tint(255,255)


# CREATURE CLASSES
############################################################################################################

class Creature:
    def __init__(self,posX,posY,collisionW,collisionH,speedX,topSpeedX,speedY,img,imgWidth,imgHeight,displayW,displayH,gnd,totalFrames,defaultStopFrame,defaultJumpFrame,defaultLandingFrame,displayXOffset,displayYOffset,leftDisplayXOffset):
        self.posX=posX
        self.posY=posY
        self.imgWidth=imgWidth
        self.imgHeight=imgHeight
        self.displayW=displayW
        self.displayH=displayH
        self.img=img

        self.collisionW=collisionW
        self.collisionH=collisionH


        self.gnd=gnd
        self.totalFrames=totalFrames
        self.speedX=speedX
        self.topSpeedX = topSpeedX

        self.speedY=speedY
        self.vX=0
        self.vY=0
        self.aY= 0.02*17/16
        self.dir=RIGHT
        self.defaultStopFrame=defaultStopFrame
        self.defaultJumpFrame=defaultJumpFrame
        self.defaultLandingFrame=defaultLandingFrame
        self.f=defaultStopFrame
        self.displayXOffset=displayXOffset
        self.displayYOffset=displayYOffset
        self.leftDisplayXOffset=leftDisplayXOffset

        self.touchingPlatform=False
        self.abovePlatform = False
        self.prevPlatform = None
        self.collisionVX = 0
        self.collisionDir = None
        self.prevDt = 0

        self.coordsX=[self.posX-self.collisionW//2,self.posX+self.collisionW//2]
        self.coordsY=[self.posY-self.collisionH//2,self.posY+self.collisionH//2]


        # PLATFORM COLLISION
        self.collisionVelocity = 0.2
        self.platformVX = 0 # X VELOCITY OF THE PLATFORM THEY ARE STANDING ON
        self.platformVY = 0 # Y VELOCITY OF THE PLATFORM THEY ARE STANDING ON

    # RETURNS THE CURRENT HIGHEST PLATFORM THAT IS BELOW THE CREATURE
    def return_platform(self):
        for platform in game.sort_platform_by_gnd(self.gnd):
            if self.coordsY[1]<=platform.posY and self.coordsX[1]>platform.coordsX[0] and self.coordsX[0]<platform.coordsX[1]:
                return platform

    # IMPLEMENTS GRAVITY ANYWHERE
    def gravity(self):


        edgeCase = False
        insideObstacle = False

        platformVY=0
        Platform = None
        # DETECTS THE PLATFORM BELOW IT AND SETS THE GROUND
        for platform in game.platforms:#sort_platform_by_gnd(self.gnd):

            if platform.solid and self.coordsY[1]<=platform.posY+ERROR_THRESHHOLD and self.coordsX[1]>platform.coordsX[0] and self.coordsX[0]<platform.coordsX[1]:

                self.gnd = platform.posY

                self.abovePlatform = True

                Platform = platform
                self.prevPlatform = Platform
                platformVY=platform.vY
                break
        else:
            if self.abovePlatform and not Platform and (self.coordsX[1]<self.prevPlatform.coordsX[0] or self.coordsX[0]>self.prevPlatform.coordsX[1]):
                self.abovePlatform = False

            if not self.abovePlatform:
                # DETECT IF CATTO IS OVER AN OBSTACLE

                for obstacle in game.obstacles:
                    if self.coordsX[0]>=obstacle.coordsX[0] and self.coordsX[1]<=obstacle.coordsX[1]:

                        self.gnd = obstacle.gnd
                        insideObstacle = True
                        break
                # THE CAT MUST HAVE NO PLATFORM OR OBSTACLE BELOW ITSELF
                else:
                    self.gnd = game.gnd



            elif not Platform:
                if self.prevPlatform.solid and self.prevPlatform.label!='popup':
                    self.gnd = self.prevPlatform.posY
                    edgeCase = True
                else:
                    # DETECT IF CATTO IS OVER AN OBSTACLE

                    for obstacle in game.obstacles:
                        if self.coordsX[0]>=obstacle.coordsX[0] and self.coordsX[1]<=obstacle.coordsX[1]:
                            self.gnd = obstacle.gnd
                            insideObstacle = True
                            break
                    else:
                        self.gnd = game.gnd

                    # self.gnd = game.gnd
                    edgeCase = False

        # CHANGE THE VALUE OF GRAVITATIONAL ACCELERATION WHEN CAT IS INSIDE AN OBSTACLE
        if insideObstacle and self.coordsY[1]>GND:
            if self.type!='birdo':
                self.aY = 0.001*float(game.dt)/float(16)

        # IF THIS IS A MOVING PLATFORM AND IS ABOUT TO SHIFT ITS DIRECTION
        if Platform and Platform.vY!=0 and self.touchingPlatform and (Platform.initY+Platform.rangeY<=Platform.posY+Platform.vY*game.dt or Platform.initY>=Platform.posY+Platform.vY*game.dt):

            if (Platform.initY+Platform.rangeY<=Platform.posY+Platform.vY*game.dt):
                #SET THE VELOCITY SO THAT IT STAYS ABOVE THE PLATFORM AND DOESN'T GO DOWN EVER SO SLIGHTLY
                self.vY = (Platform.initY + Platform.rangeY - self.coordsY[1] -Platform.vY*game.dt - ERROR_THRESHHOLD)/game.dt

                self.touchingPlatform = True
            else:
                #GIVE THE CREATURE A SLIGHT JUMP WHEN THE PLATFORM STARTS GOING DOWN FROM UP
                self.vY = (Platform.initY - self.coordsY[1] + 0.5*Platform.vY*game.dt)/game.dt
                self.touchingPlatform = True

        else: # ELSE APPLY GRAVITY KEEPING IN MIND THE MOTION OF THE PLATFORM

            if self.coordsY[1] <self.gnd:
                # USUAL GRAVITY UPDATES THE VY
                self.vY += self.aY
                self.touchingPlatform=False

                # FIND OUT IF THE UPDATE CAUSES THE CREATURE TO CROSS THE PLATFORM
                if self.vY*game.dt+self.coordsY[1]>self.gnd + platformVY*game.dt:
                    #SET THE VELOCITY SO THAT IT STAYS ABOVE THE PLATFORM AND DOESN'T GO DOWN EVER SO SLIGHTLY
                    self.vY = (self.gnd + platformVY*game.dt - self.coordsY[1])/game.dt
                    self.touchingPlatform=True
            else:
                # ELSE IT IS STANDING ON THE PLATFORM, SO GIVE IT THE VELOCITY OF THE PLATFORM ITSELF
                self.vY = platformVY
                self.touchingPlatform=True

        # JUST TO SOLVE AN EDGE CASE REGARDING THE DIRECTION SHIFT OF THE PLATFORM
        if edgeCase:
            if self.prevPlatform.posY > self.prevPlatform.initY:
                self.vY = -2*abs(self.prevPlatform.vY)

    # METHOD THAT CHECKS AN OVERLAP BETWEEN A LINE SEGMENT WITH ANOTHER. IF USED TWICE FOR X AND Y DIRECTION, CAN DETECT COLLISION BETWEEN TWO RECTANGLES
    def check_overlap(self,xa1,xa2,xb1,xb2):
        max_l = abs(xa1-xa2) + abs(xb1-xb2)
        mn= min(xa1,xa2,xb1,xb2)
        mx= max(xa1,xa2,xb1,xb2)
        effective_l = abs(mx-mn)
        if effective_l<max_l:
            return True
        else:
            return False

    # USED FOR UPDATING THE VELOCITY AND HENCE THE MOTION OF OTHER CREATURES
    def update_vX_vY(self):
        pass


    # USED FOR UPDATING THE POSITION OF THE CREATURE
    def update(self):

        if self.type == 'birdo': # NO GRAVITY FOR BIRDS
            self.aY = 0
        else: # ELSE SCALE THE ACCELERATION TO ADJUST FOR THE VARYING FRAME DURATION
            self.aY=0.02*float(game.dt)/float(16)

        # NO SHAME IN UPDATING THE COORDINATES OF THE FOUR CORNERS IS THERE?
        self.coordsX=[self.posX-self.collisionW,self.posX+self.collisionW]
        self.coordsY=[self.posY-self.collisionH,self.posY+self.collisionH]

        self.collisionDir = None
        # CHECK FOR TOP COLLISIONS
        for platform in game.platforms:
            if platform.solid and self.check_overlap(self.coordsX[0],self.coordsX[1],platform.coordsX[0],platform.coordsX[1]) and self.check_overlap(self.coordsY[0],self.coordsY[1],platform.coordsY[0],platform.coordsY[1]):

                if self.posY-self.collisionH/2 - self.vY*self.prevDt >= platform.coordsY[1]:
                    self.collisionDir = DOWN
                self.vY=self.collisionVelocity


        # STOPS COLLISION VX FROM PUSHING THE CREATURE AWAY FOR AGES
        if  self.collisionVX!=0 and self.coordsY[1] >= self.gnd-50:
            self.collisionVX=0



            platform = self.return_platform()

        # UPDATE VY BY GRAVITY
        self.gravity()

        # ADD PLATFORM VELOCITIES ACCORDING TO PLATFORMS
        if platform and (self.vY==0 or self.vY==(self.gnd + platform.vY*game.dt - self.coordsY[1])/game.dt or self.vY==platform.vY or self.touchingPlatform):  # IF IT IS INDEED A PLATFORM THEN FIND THE PLATFORM VELOCITY:
            self.platformVX=platform.vX
            self.platformVY=platform.vY
            self.vY=self.vY
        else:
            self.platformVX=0
            self.platformVY=0

        # UPDATE THE INHERENT VELOCTIES NOW
        self.update_vX_vY()

        # FINALLY ADD THE X VELOCITY
        self.posX += (self.vX + self.platformVX + self.collisionVX) * game.dt


        # NO SHAME IN UPDATING THE COORDINATES OF THE FOUR CORNERS IS THERE?
        self.coordsX=[self.posX-self.collisionW,self.posX+self.collisionW]
        self.coordsY=[self.posY-self.collisionH,self.posY+self.collisionH]

        # FIX POSX BY CHECKING IF THERE ARE PLATFORMS
        for platform in game.platforms:
            if platform.solid and self.check_overlap(self.coordsX[0],self.coordsX[1],platform.coordsX[0],platform.coordsX[1]) and self.check_overlap(self.coordsY[0],self.coordsY[1],platform.coordsY[0],platform.coordsY[1]):
                if self.collisionDir!= DOWN and (self.abovePlatform and self.prevPlatform!=platform) or not self.abovePlatform:
                    if (self.vX>0 or self.platformVX>0) and self.coordsX[0]<platform.coordsX[0]:
                        self.posX=platform.coordsX[0]-(self.coordsX[1]-self.coordsX[0])//2

                    elif (self.vX<0 or self.platformVX<0) and self.coordsX[1]>platform.coordsX[1]:
                        self.posX=platform.coordsX[1]+(self.coordsX[1]-self.coordsX[0])//2


                    break


        # FINALLY ADD THE Y VELOCITY
        self.posY += (self.vY) * game.dt


        # STORE THE CURRENT FRAME DURATION FOR THE NEXT FRAME TO USE AS PREVIOUS FRAME DT
        self.prevDt = game.dt





    def display(self,update=True):
        if update:
            self.update()

            if self.vX!=0:
                self.f=self.f+map(abs(self.vX),self.speedX,self.topSpeedX,4,5.5)/self.totalFrames*float(game.dt)/float(32)
                self.f=self.f%self.totalFrames
            else:
                self.f=self.defaultStopFrame




        if (not self.touchingPlatform) and ((self.gnd)-(self.coordsY[1]+self.platformVY*game.dt))<50:
            self.f=self.defaultLandingFrame
        elif (not self.touchingPlatform) and ((self.gnd)-(self.coordsY[1]+self.platformVY*game.dt))>50:
            self.f=self.defaultJumpFrame
        elif (not self.touchingPlatform):
            self.f=self.defaultJumpFrame


        if self.dir==RIGHT:
            image(self.img,self.coordsX[0]+self.displayXOffset-game.gameX,self.coordsY[0]+self.displayYOffset-game.gameY,self.displayW,self.displayH,self.imgWidth/self.totalFrames*int(self.f),0,self.imgWidth/self.totalFrames*int(self.f+1),self.imgHeight)
        elif self.dir==LEFT:
            image(self.img,self.coordsX[0]+self.leftDisplayXOffset-game.gameX,self.coordsY[0]+self.displayYOffset-game.gameY,self.displayW,self.displayH,self.imgWidth/self.totalFrames*int(self.f+1),0,self.imgWidth/self.totalFrames*int(self.f),self.imgHeight)




# FINAL BOSS
class Fatslob(Creature):
    def __init__(self,img):
        Creature.__init__(self,0,0,70,45,0.4,0.9,0.65,img,190*7,95,190,95,GND,7,5,2,4,-40,0,-10)

        self.topSpeedX = 0.8
        self.speedX = 0.45

        self.vX= self.speedX
        self.initPosX=21000

        self.leftPosX = 20800
        self.rightPosX = 21780

        self.initPosY=GND-150
        self.posX = self.initPosX
        self.posY = self.initPosY

        self.type='fatslob'

        self.stamina = 100
        self.f=0

        self.sound_angry = minim.loadFile(PATH+"/Resources/sounds/boss_angry.wav")
        self.sound_running = minim.loadFile(PATH+"/Resources/sounds/walking_on_pavement_x2.mp3")
        self.sound_angry.setGain(10)
        # self.sound_running.loop()

        self.dir = RIGHT

        self.mode = 'attack'

        self.lives = 9
        self.totalLives = 9

        self.birdTimer = 0
        self.numBirdos = 0

        self.respawning = False
        self.respawnTimer = 3000

        self.active = False



    # SET VOLUMES
    def set_volume(self):
        self.sound_angry.setGain(game.sfx_volume)
        self.sound_running.setGain(game.sfx_volume)
    def pause_sound(self):
        self.sound_angry.pause()
        self.sound_running.pause()


    def update_vX_vY(self):

        # SUMMON BIRDOS
        if self.birdTimer>0:
            self.birdTimer-=game.dt

        if self.birdTimer<=0 and self.numBirdos == 0:
            game.enemies.append(Birdo(self.leftPosX+600+0*(self.rightPosX-self.leftPosX)/2,GND-500,game.birdo_img,label='boss'))
            game.enemies.append(Birdo(self.rightPosX-600,GND-500,game.birdo_img,label='boss'))
            self.numBirdos=2
            if self.lives<=5:
                game.enemies.append(Birdo(self.rightPosX-200,GND-500,game.birdo_img,label='boss'))
                self.numBirdos+=1

            self.birdTimer = 0
        elif self.birdTimer<=0 and self.numBirdos == 1:
            game.enemies.append(Birdo(self.rightPosX-500,GND-500,game.birdo_img,label='boss'))
            self.numBirdos=2
            if self.lives<=5:
                game.enemies.append(Birdo(self.rightPosX-400,GND-500,game.birdo_img,label='boss'))
                self.numBirdos+=1
            self.birdTimer = 0
        elif self.birdTimer<=0 and self.numBirdos == 2:
            if self.lives<=5:
                game.enemies.append(Birdo(self.leftPosX+400,GND-500,game.birdo_img,label='boss'))
                self.numBirdos=3
                self.birdTimer = 0

        # IF BOSS IS ATTACKED AND IS RESPAWNING
        if self.respawning:
            self.respawnTimer-=game.dt
            if self.respawnTimer<=0:
                self.respawnTimer = 0
                self.respawning = False

        # ATTACK MODE
        if self.mode=='attack' and not self.respawning:
            self.stamina-=0.3*float(game.dt)/float(17)

            #SOUNDS:
            if not self.sound_running.isPlaying() and self.active:
                self.sound_running.rewind()
                self.sound_running.play()
                # self.sound_running.loop()

            if self.stamina<=0:
                self.stamina = 0
                self.mode = 'tired'
                self.tiredF = 0

            if self.coordsX[1]+self.vX*game.dt>self.rightPosX-100:
                self.posX = self.rightPosX-100-(self.coordsX[1]-self.coordsX[0])/2
                self.vX = -map(self.stamina,0,100,self.speedX,self.topSpeedX)
                self.dir = LEFT
            elif self.coordsX[0]+self.vX*game.dt<self.leftPosX+100:
                self.posX = self.leftPosX+100+(self.coordsX[1]-self.coordsX[0])/2
                self.vX = map(self.stamina,0,100,self.speedX,self.topSpeedX)
                self.dir = RIGHT
            else:
                if game.catto.coordsY[1]>=GND-100 and game.catto.coordsX[0]>self.leftPosX and game.catto.coordsX[1]<self.rightPosX :
                    if game.catto.posX<self.posX:
                        self.dir=LEFT
                    else:
                        self.dir=RIGHT

                if self.dir==LEFT:
                    self.vX = -map(self.stamina,0,100,self.speedX,self.topSpeedX)
                elif self.dir==RIGHT:
                    self.vX = +map(self.stamina,0,100,self.speedX,self.topSpeedX)
        # TIRED MODE
        if self.mode =='tired' and not self.respawning:
            #SOUNDS:
            if self.sound_running.isPlaying():
                self.sound_running.pause()

            self.vX = 0

            self.stamina+=0.9*float(game.dt)/float(17)*map(self.lives,9,1,1,1.5)
            if self.stamina>100*map(self.lives,9,1,1,2):
                self.stamina = 100*map(self.lives,9,1,1,2)
                self.mode='attack'

    def display(self,update=True):
        if update:
            self.update()

            if self.vX!=0:
                self.f=self.f+map(abs(self.vX),self.speedX,self.topSpeedX,4,5.5)/self.totalFrames*float(game.dt)/float(32)
                self.f=self.f%self.totalFrames
            else:
                self.tiredF=self.tiredF+1.1/self.totalFrames*float(game.dt)/float(32)
                self.tiredF=self.tiredF%self.totalFrames

                self.f=self.tiredF + 8

        if self.respawning:
            tint(255,128+128*sin(self.respawnTimer*2*PI/500))


        # BOSS WON'T JUMP,  BUT MAYBE IN A HARDER VERSION OF THE GAME?
        if (not self.touchingPlatform) and ((self.gnd)-(self.coordsY[1]+self.platformVY*game.dt))<50:
            self.f=self.defaultLandingFrame
        elif (not self.touchingPlatform) and ((self.gnd)-(self.coordsY[1]+self.platformVY*game.dt))>50:
            self.f=self.defaultJumpFrame
        elif (not self.touchingPlatform):
            self.f=self.defaultJumpFrame


        if self.dir==RIGHT:
            image(self.img,self.coordsX[0]+self.displayXOffset-game.gameX,self.coordsY[0]+self.displayYOffset-game.gameY,self.displayW,self.displayH,self.imgWidth/self.totalFrames*int(self.f),0,self.imgWidth/self.totalFrames*int(self.f+1),self.imgHeight)
        elif self.dir==LEFT:
            image(self.img,self.coordsX[0]+self.leftDisplayXOffset-game.gameX,self.coordsY[0]+self.displayYOffset-game.gameY,self.displayW,self.displayH,self.imgWidth/self.totalFrames*int(self.f+1),0,self.imgWidth/self.totalFrames*int(self.f),self.imgHeight)


        tint(255,255)


class Birdo(Creature):
    def __init__(self,posX,posY,img,label='normal'):
        Creature.__init__(self,posX,posY,50,20,0.23,0.46,0.5,img,1200,150,100,150,GND,10,0,0,0,0,-60,0)

        self.speedX = 0.23
        self.speedY = 0.46
        self.topSpeedX = 0.46
        self.vX = self.speedX
        self.vY = 0

        self.flyingRangeX=300
        self.initPosX=posX
        self.initPosY=posY
        self.posX = self.initPosX
        self.type='birdo'
        self.mode = 'guard'
        self.overstepX = 200

        self.stopChasing = True
        self.aY = 0

        self.divingSpeed = 0.7
        self.risingSpeed = 2
        self.diveHeight = 0
        self.diveTime = 0

        self.guardTimer = 0

        self.sound_attack = minim.loadFile(PATH+"/Resources/sounds/birdo_attack.mp3")

        self.defaultAttackFrameRight = 10
        self.defaultAttackFrameLeft = 10

        self.label = label
        self.active = False

        # IF LABEL IS BOSS THEN THIS IS THE BIRD OF THE BOSS LEVEL
        if self.label == 'boss':
            self.posY = GND-650

    # SOUND VOLUME CONTROL METHODS
    def pause_sound(self):
        self.sound_attack.pause()
    def unpause_sound(self):
        self.sound_attack.play()

    def set_volume(self):
        self.sound_attack.setGain(game.sfx_volume)
        #pass

    # UPDATE THE MOTION
    def update_vX_vY(self):

        # MAKE THE BIRDO DESCEND FROM A HEIGHT TO ENTER THE SCREEN WHEN SPAWNING
        if self.label=='boss' and not self.active:
            self.set_volume()
            if self.posY<self.initPosY:
                self.vY=0.05
            else:
                self.vY = 0
                self.active = True

        # GUARD MODE
        if self.mode == 'guard':
            # DETECT CATTO

            if self.guardTimer<=0 and 0<= self.posX - game.catto.posX <= self.flyingRangeX:#
                self.dir=LEFT
                self.vX = (game.catto.posX - self.posX)/(dist(self.posX,self.posY,game.catto.posX,game.catto.posY)/self.divingSpeed)
                self.vY = (game.catto.posY - self.posY)/(dist(self.posX,self.posY,game.catto.posX,game.catto.posY)/self.divingSpeed)#self.speedY
                self.mode = 'attack'
                self.sound_attack.rewind()
                self.sound_attack.play()

                self.guardTimer = 0
                self.diveTime = 0
                self.diveHeight = game.catto.posY
            elif self.guardTimer<=0 and  0<= game.catto.posX - self.posX <= self.flyingRangeX:
                self.dir=RIGHT
                self.vX = (game.catto.posX - self.posX)/(dist(self.posX,self.posY,game.catto.posX,game.catto.posY)/self.divingSpeed)
                self.vY = (game.catto.posY - self.posY)/(dist(self.posX,self.posY,game.catto.posX,game.catto.posY)/self.divingSpeed)#self.speedY
                self.mode = 'attack'
                self.sound_attack.rewind()
                self.sound_attack.play()

                self.guardTimer = 0
                self.diveTime = 0
                self.diveHeight = game.catto.posY

            else:
                # IF CATTO NOT DETECTED THEN DO THE USUAL CHECK
                self.guardTimer -= game.dt
                if self.vX<0 and self.posX< self.initPosX-self.flyingRangeX:# and self.posY<self.initPosY+self.flyingRangeX:
                    self.posX = self.initPosX - self.flyingRangeX
                    self.vX = self.speedX
                    self.dir = RIGHT
                elif self.vX>0 and self.posX> self.initPosX+self.flyingRangeX:
                    self.posX = self.initPosX + self.flyingRangeX
                    self.vX = -self.speedX
                    self.dir = LEFT
        # ATTACK MODE
        elif self.mode=='attack':
            # IF EXCEEDS DIVE HEIGHT
            if self.vY>=0 and self.posY+self.collisionH>=self.diveHeight:
                self.diveHeight = 0
                self.diveTime = 0
                self.vY = (self.initPosY - self.posY)/(dist(self.posX,self.posY,self.initPosX,self.initPosY)/self.divingSpeed)
                if self.dir==LEFT:
                    self.vX = (self.initPosX-self.flyingRangeX - self.posX)/(dist(self.posX,self.posY,self.initPosX-self.flyingRangeX,self.initPosY)/self.divingSpeed)
                    if self.vX>0:
                        self.dir=RIGHT
                elif self.dir==RIGHT:
                    self.vX = (self.initPosX+self.flyingRangeX - self.posX)/(dist(self.posX,self.posY,self.initPosX+self.flyingRangeX,self.initPosY)/self.divingSpeed)
                    if self.vX<0:
                        self.dir=LEFT

            # DID IT HIT A PLATFORM ?
            elif self.vY>=0 and self.posY+self.collisionH - self.vY*self.prevDt >= self.posY+self.collisionH - ERROR_THRESHHOLD:#self.posY+self.collisionH-self.vY
                if self.dir==LEFT:
                    self.vX = (self.initPosX-self.flyingRangeX - self.posX)/(dist(self.posX,self.posY,self.initPosX-self.flyingRangeX,self.initPosY)/self.divingSpeed)
                    if self.vX>0:
                        self.dir=RIGHT
                elif self.dir==RIGHT:
                    self.vX = (self.initPosX+self.flyingRangeX - self.posX)/(dist(self.posX,self.posY,self.initPosX+self.flyingRangeX,self.initPosY)/self.divingSpeed)
                    if self.vX<0:
                        self.dir=LEFT

                self.vY = (self.initPosY - self.posY)/(dist(self.posX,self.posY,self.initPosX,self.initPosY)/self.divingSpeed)
                # self.mode = 'recover'
                self.diveHeight = 0
                self.diveTime = 0

            # STOP RISING BEYOND THE INITIAL Y POSITION
            elif self.vY<=0 and self.posY<=self.initPosY:
                self.posY = self.initPosY
                self.vY = 0
                self.mode = 'guard'

                self.guardTimer = 2500

                if self.dir == LEFT:
                    self.vX = self.speedX # REVERSE THE DIRECTION
                    self.dir = RIGHT
                if self.dir == RIGHT:
                    self.vX = -self.speedX # REVERSE THE DIRECTION
                    self.dir=LEFT

            # STILL ANOTHER CONDITION TO NOT GET STUCK IN THE PLATFORM FOR TOO LONG, MORE THAN 5 SECONDS
            if self.diveTime > 5000 and self.vY > 0:
                self.vX = (self.initPosX - self.posX)/(dist(self.posX,self.posY,self.initPosX,self.initPosY)/self.divingSpeed)
                self.vY = (self.initPosY - self.posY)/(dist(self.posX,self.posY,self.initPosX,self.initPosY)/self.divingSpeed)

                self.diveHeight = 0
                self.diveTime = 0

            # CALCULATE HOW LONG IT IS TAKKING FOR THE ATTACK DIVE, SO THAT IF IT IS TOO LONG, IT PROBABLY MEANS THE BIRD ID STUCK
            self.diveTime += game.dt

        # KEEP FLYING UPWARD
        elif self.mode=='recover':
            if self.vY<=0 and self.posY<=self.initPosY:
                self.posY = self.initPosY
                self.vY = 0
                self.mode = 'guard'

                self.guardTimer = 1000

                if self.dir == LEFT:
                    self.vX = self.speedX # REVERSE THE DIRECTION
                    self.dir = RIGHT
                if self.dir == RIGHT:
                    self.vX = -self.speedX # REVERSE THE DIRECTION
                    self.dir=LEFT

    def display(self,update=True):
        if update:
            self.update()

            if self.mode=='guard':
                self.f=self.f+3.5/self.totalFrames*float(game.dt)/float(32) # GUARD FRAME
                self.f=self.f%self.totalFrames
            elif (self.mode=='attack' and self.vY<=0): # RECOVERY FRAME
                self.f=self.f+5.5/self.totalFrames*float(game.dt)/float(32)
                self.f=self.f%self.totalFrames
            else:
                if self.vX>0:
                    self.f=self.defaultAttackFrameRight # ATTACK FRAME
                else:
                    self.f=self.defaultAttackFrameLeft # ATTACK FRAME



        if self.dir==RIGHT:
            image(self.img,self.coordsX[0]+self.displayXOffset-game.gameX,self.coordsY[0]+self.displayYOffset-game.gameY,self.displayW,self.displayH,self.displayW*int(self.f),0,self.displayW*int(self.f+1),self.imgHeight)
        elif self.dir==LEFT:
            image(self.img,self.coordsX[0]+self.leftDisplayXOffset-game.gameX,self.coordsY[0]+self.displayYOffset-game.gameY,self.displayW,self.displayH,self.displayW*int(self.f+1),0,self.displayW*int(self.f),self.imgHeight)


class Doggo(Creature):
    def __init__(self,posX,posY,img):
        Creature.__init__(self,posX,posY,80.5,41.5,0.23,0.46,0,img,1218,115,1218/7,115,GND,7,5,2,4,0,-30,0)
        self.speedX = 0.23
        self.topSpeedX = 0.46
        self.vX= self.speedX
        self.visionRangeX=400
        self.runningRangeX=300
        self.initPosX=posX
        self.initPosY=posY
        self.posX = self.initPosX
        self.type='doggo'
        self.mode = 'guard'
        self.overstepX = 200


        self.bark = minim.loadFile(PATH+"/Resources/sounds/doggo2.mp3")
        self.bark.setGain(10)

        self.stopChasing = True

    # VOLUME CONTROL METHODS
    def set_volume(self):
        self.bark.setGain(game.sfx_volume-15) # ORIGINAL FILE IS TOO LOUD SO REDUCE IT EVEN MORE
    def pause_sound(self):
        self.bark.pause()
    def unpause_sound(self):
        self.bark.play()


    def update_vX_vY(self):

        # WHEN CATTO IS OUTSIDE RANGE

        if self.mode=='guard':

            if self.bark.isPlaying():
                self.bark.pause()
                # self.bark.rewind()

            if 0< self.posX - game.catto.posX <= self.visionRangeX and not game.catto.respawning:
                self.vX = -self.topSpeedX
                self.dir=LEFT

                self.mode='pursuit'
            elif 0< game.catto.posX - self.posX <= self.visionRangeX and not game.catto.respawning:
                self.vX = self.topSpeedX
                self.dir=RIGHT

                self.mode='pursuit'
            else:
                if self.posX>self.initPosX+self.runningRangeX: # RIGHT BOUND
                    self.vX = -self.speedX
                    self.dir=LEFT
                    #self.posX = 500

                elif self.posX<self.initPosX:  # LEFT BOUND
                    self.vX = self.speedX
                    self.dir=RIGHT
                    #self.posX = 100
                self.mode = 'guard'

        # WHEN CATTO IS INSIDE RANGE BUT DEAD, RETURN THE DOG TO ORIGINAL LOCATION
        elif self.mode == 'pursuit' and game.catto.respawning:

            self.mode='guard'
            self.posX = self.initPosX
            self.dir = RIGHT
            self.vX = self.speedX

        # WHEN CATTO IS INSIDE RANGE AND NOT DEAD
        elif self.mode == 'pursuit':

            # BARK PLEES
            if not self.bark.isPlaying():
                self.bark.rewind()
                self.bark.play()
                #self.bark.loop()

            if self.dir == LEFT:

                if self.posX - game.catto.posX < -self.overstepX:
                    self.vX = self.topSpeedX
                    self.dir=RIGHT
                    self.mode='pursuit'

                elif (self.stopChasing and self.posX - game.catto.posX > self.visionRangeX):
                    self.vX = self.speedX
                    self.dir=RIGHT
                    self.mode='guard'

            elif self.dir == RIGHT:
                if game.catto.posX - self.posX < -self.overstepX:
                    self.vX = -self.topSpeedX
                    self.dir=LEFT
                    self.mode='pursuit'
                elif (self.stopChasing and game.catto.posX - self.posX > self.visionRangeX):
                    self.vX = -self.speedX
                    self.dir=LEFT
                    self.mode='guard'







class Catto(Creature):
    def __init__(self,posX,posY,img):
        Creature.__init__(self,posX,posY,55,30,0.4,0.9,0.65,img,2267/2,100,2267/14,100,GND,7,5,2,4,-48,-30,0)

        self.keyHandler={RIGHT:False,LEFT:False,UP:False,DOWN:False,'X':False}
        self.aX=0

        self.type = 'catto'

        #Sounds
        self.sound_walking_grass = minim.loadFile(PATH+"/Resources/sounds/walking_on_grass_x2.mp3")
        self.sound_running_grass = minim.loadFile(PATH+"/Resources/sounds/walking_on_grass_x4.mp3")
        self.sound_walking_pavement = minim.loadFile(PATH+"/Resources/sounds/walking_on_pavement_x1.mp3")
        self.sound_running_pavement = minim.loadFile(PATH+"/Resources/sounds/walking_on_pavement_x1.6.mp3")
        self.sound_walking = self.sound_walking_pavement
        self.sound_running = self.sound_running_pavement
        self.sound_movement = self.sound_walking
        self.sound_jump = minim.loadFile(PATH+"/Resources/sounds/jumping.mp3")
        self.sound_land = minim.loadFile(PATH+"/Resources/sounds/landing.mp3")
        self.sound_mew_list = [minim.loadFile(PATH+"/Resources/sounds/annoyed.wav"),minim.loadFile(PATH+"/Resources/sounds/annoyed_2.wav"),minim.loadFile(PATH+"/Resources/sounds/angry_2.wav")]
        self.sound_mew=self.sound_mew_list[random.randint(0,len(self.sound_mew_list)-1)]
        self.sound_claw = minim.loadFile(PATH+"/Resources/sounds/claw_2.mp3")
        self.sound_coin = minim.loadFile(PATH+"/Resources/sounds/coin.mp3")
        self.sound_birdo_kill =minim.loadFile(PATH+"/Resources/sounds/birdo_kill.mp3")
        self.sound_health_lost = minim.loadFile(PATH+"/Resources/sounds/health_lost.mp3")
        self.sound_health_gained = minim.loadFile(PATH+"/Resources/sounds/health.mp3")
        self.sound_stamina_gained = minim.loadFile(PATH+"/Resources/sounds/stamina.mp3")
        self.health_lostX = 0


        for sound in self.sound_mew_list:
            sound.setGain(10)
        self.sound_walking.setGain(30)
        self.sound_running.setGain(30)
        self.sound_jump.setGain(30)
        self.sound_land.setGain(30)


        self.topSpeedX = 0.9

        # PLATFORM COLLISION
        self.collisionVelocity = 0.4
        self.platformVX = 0 # X VELOCITY OF THE PLATFORM THEY ARE STANDING ON
        self.platformVY = 0 # Y VELOCITY OF THE PLATFORM THEY ARE STANDING ON

        self.stamina = 100
        self.totalLives = 9
        self.lives=9
        self.respawning = False
        self.insideObstacle = False


        self.touchingPlatform=False
        self.collisionVX = 0
        self.collisionDir = None
        self.prevDt = 0


        self.attack = False
        self.attackKeyPressed = False

    # VOLUME CONTROL METHODS
    def set_volume(self):
        for sound in self.sound_mew_list:
            sound.setGain(game.sfx_volume)
        self.sound_walking.setGain(game.sfx_volume)
        self.sound_running.setGain(game.sfx_volume)
        self.sound_jump.setGain(game.sfx_volume)
        self.sound_land.setGain(game.sfx_volume)
        self.sound_health_lost.setGain(game.sfx_volume)
        self.sound_health_gained.setGain(game.sfx_volume)
        self.sound_stamina_gained.setGain(game.sfx_volume)
        self.sound_claw.setGain(game.sfx_volume)
        self.sound_coin.setGain(game.sfx_volume)
        self.sound_birdo_kill.setGain(game.sfx_volume)

    def update(self):

        # IF DEAD STOP TAKING INPUTS
        if self.insideObstacle or self.respawning:
            self.keyHandler[LEFT] = False
            self.keyHandler[RIGHT] = False
            self.keyHandler[UP] = False
            self.keyHandler[DOWN] = False
            self.keyHandler['X'] = False

        # RECALCULATE THE ACCELERATION TO ACCOUNT FOR THE VARYING FRAME DURATION
        self.aY=0.02*float(game.dt)/float(16)

        # NO SHAME IN UPDATING THE COORDINATES OF THE FOUR CORNERS IS THERE?
        self.coordsX=[self.posX-self.collisionW,self.posX+self.collisionW]
        self.coordsY=[self.posY-self.collisionH,self.posY+self.collisionH]


        # CHECK FOR ENEMY COLLISION:

        if not self.respawning:
            for enemy in game.enemies:
                if self.check_overlap(self.coordsX[0],self.coordsX[1],enemy.coordsX[0],enemy.coordsX[1]) and self.check_overlap(self.coordsY[0],self.coordsY[1],enemy.coordsY[0],enemy.coordsY[1]):
                    # DOG? NO WAY TO KILL IT SORRY. RIP.
                    if enemy.type == 'doggo':
                        self.lives-=1
                        # self.posX = game.safePointsList[game.safePointsIndex]

                        # PLAY THE OUCH SOUND
                        if self.lives>0 and not self.sound_health_lost.isPlaying():
                            self.sound_health_lost.rewind()
                            self.sound_health_lost.play()

                        self.respawning = True
                        self.health_lostX = self.posX


                        enemy.posX = enemy.initPosX
                        enemy.posY = GND-(enemy.coordsY[1]-enemy.coordsY[0])/2

                    elif enemy.type == 'birdo':
                        # KILL BIRD BY ATTACKING
                        if self.attack and not (enemy.mode=='attack' and enemy.vY>0) and self.check_overlap(self.coordsX[0],self.coordsX[1],enemy.coordsX[0],enemy.coordsX[1]) and self.check_overlap(self.coordsY[0],self.coordsY[1],enemy.coordsY[0],enemy.coordsY[1]):

                            if enemy.label == 'boss':
                                game.fatslob.numBirdos-=1
                                game.fatslob.birdTimer=5000

                            game.enemies.remove(enemy)
                            del enemy

                            game.score+=SCORES_DICT['BIRDO_KILL']
                            self.sound_birdo_kill.rewind()
                            self.sound_birdo_kill.play()
                        # GET KILLED HEHE
                        else:
                            self.lives-=1

                            # PLAY THE OUCH SOUND
                            if self.lives>0 and not self.sound_health_lost.isPlaying():
                                self.sound_health_lost.rewind()
                                self.sound_health_lost.play()
                            self.respawning = True
                            self.health_lostX = self.posX
                    # IS IT THE BOSS? SEE IF HE IS TIRED TO INJURE HIM
                    elif enemy.type=='fatslob':
                        if self.attack and (enemy.mode=='tired' and not enemy.respawning) and self.check_overlap(self.coordsX[0],self.coordsX[1],enemy.coordsX[0],enemy.coordsX[1]) and self.check_overlap(self.coordsY[0],self.coordsY[1],enemy.coordsY[0],enemy.coordsY[1]):
                            game.fatslob.lives-=1
                            game.fatslob.posX = game.fatslob.rightPosX-game.fatslob.displayW/2
                            game.fatslob.dir = LEFT
                            game.fatslob.stamina = 100*map(game.fatslob.lives,9,1,1,2)
                            game.fatslob.respawning = True
                            game.fatslob.respawnTimer = 3000*map(game.fatslob.lives,9,1,1,0.5)

                            #BOSS ANGRY SOUND
                            game.fatslob.sound_angry.rewind()
                            game.fatslob.sound_angry.play()

                            game.score+=SCORES_DICT['BOSS'] # ADD SCORE OF INJURING THE BOSS

                            game.foods.append(Consumable(20600+random.randint(0,8)*160,GND-250,game.food_img,55*1.2,30*1.2,6,55*6,30))
                            if self.lives<6 and random.randint(0,1) == 1:
                                game.foods.append(Consumable(20600+random.randint(0,8)*160,GND-250,game.food_img,55*1.2,30*1.2,6,55*6,30))

                        # IF BOSS WASN'T TIRED, GET KILLED. RIP.
                        elif not enemy.respawning:
                            self.lives-=1

                            # PLAY THE OUCH SOUND
                            if self.lives>0 and not self.sound_health_lost.isPlaying():
                                self.sound_health_lost.rewind()
                                self.sound_health_lost.play()
                            self.respawning = True
                            self.health_lostX = self.posX


        # CHECK IF IN AN OBSTACLE, TRAP OR WATER
        if not self.insideObstacle:
            for obstacle in game.obstacles:
                if self.coordsX[0]>=obstacle.coordsX[0] and self.coordsX[1]<=obstacle.coordsX[1]:
                    if self.coordsY[1]>obstacle.coordsY[0]+10:
                        self.lives-=1

                        if self.lives>0 and not self.sound_health_lost.isPlaying():
                            self.sound_health_lost.rewind()
                            self.sound_health_lost.play()

                        self.respawning = True
                        self.vY = 0.05
                        self.insideObstacle = obstacle

                        self.health_lostX = self.posX
                        break

        # COLLECT COINS
        for coin in game.coins:
            if self.check_overlap(self.coordsX[0],self.coordsX[1],coin.coordsX[0],coin.coordsX[1]) and self.check_overlap(self.coordsY[0],self.coordsY[1],coin.coordsY[0],coin.coordsY[1]):
                game.coins.remove(coin)
                game.score+=SCORES_DICT['COIN']

                self.sound_coin.rewind()
                self.sound_coin.play()

        # YUMMY
        for food in game.foods:
            if self.check_overlap(self.coordsX[0],self.coordsX[1],food.coordsX[0],food.coordsX[1]) and self.check_overlap(self.coordsY[0],self.coordsY[1],food.coordsY[0],food.coordsY[1]):
                game.foods.remove(food)
                game.score+=SCORES_DICT['HEALTH']

                if self.lives<9:
                    self.lives+=1

                # HEALTH SOUND
                self.sound_health_gained.rewind()
                self.sound_health_gained.play()

        # STAMINA ++
        for stamina in game.staminas:
            if self.check_overlap(self.coordsX[0],self.coordsX[1],stamina.coordsX[0],stamina.coordsX[1]) and self.check_overlap(self.coordsY[0],self.coordsY[1],stamina.coordsY[0],stamina.coordsY[1]):
                game.staminas.remove(stamina)
                game.score+=SCORES_DICT['STAMINA']

                if self.stamina<100:
                    self.stamina+=50
                    if self.stamina>100:
                        self.stamina = 100

                # HEALTH SOUND
                self.sound_stamina_gained.rewind()
                self.sound_stamina_gained.play()

        self.collisionDir = None
        self.platform_above = None
        # CHECK FOR LEFT, RIGHT & TOP COLLISIONS
        for platform in game.platforms:
            if platform.solid and self.check_overlap(self.coordsX[0],self.coordsX[1],platform.coordsX[0],platform.coordsX[1]) and self.check_overlap(self.coordsY[0],self.coordsY[1],platform.coordsY[0],platform.coordsY[1]):


                if self.posY-self.collisionH/2 - self.vY*self.prevDt >= platform.coordsY[1]:
                    self.collisionDir = DOWN
                    self.platform_above = platform
                self.vY=self.collisionVelocity

                break




        # UPDATE VY BY GRAVITY
        platform = self.return_platform()

        self.gravity()
        if platform and (self.vY==0 or self.vY==(self.gnd + platform.vY*game.dt - self.coordsY[1])/game.dt or self.vY==platform.vY or self.touchingPlatform):  # IF IT IS INDEED A PLATFORM THEN FIND THE PLATFORM VELOCITY:
            self.platformVX=platform.vX
            self.platformVY=platform.vY
            self.vY=self.vY
        else:
            self.platformVX=0
            self.platformVY=0



        ## ONLY UPDATES X ACCELERATION WHEN PRESSED SPACE


        # CHECK IF SHE HAS STAMINA TO ACCELERATE


        if self.aX>0 and self.vX!=0:# and self.vY==0:
            self.stamina-=0.7*float(game.dt)/float(17)
            # NO NEGATIVE STAMINA
            if self.stamina<0:
                self.stamina=0


        if self.stamina<ERROR_THRESHHOLD:
            self.aX=0
            self.stamina=0





        if self.keyHandler[RIGHT]:
            if self.vX == 0 or (self.vX!=0 and self.dir==LEFT):
                self.vX = self.speedX
            elif self.vX>0:
                if self.stamina<ERROR_THRESHHOLD or (self.aX==0):
                    self.vX = self.speedX
                elif self.touchingPlatform:
                    self.vX += self.aX
            self.dir = RIGHT

        elif self.keyHandler[LEFT]:
            if self.vX == 0 or (self.vX!=0 and self.dir==RIGHT):
                self.vX = -self.speedX
            elif self.vX<0:
                if self.stamina<ERROR_THRESHHOLD or (self.aX==0):
                    self.vX = -self.speedX
                elif self.touchingPlatform:
                    self.vX -= self.aX
            self.dir = LEFT

        else:
            self.vX=0




        if self.collisionVX != 0:
            self.vX=0


        # TOP SPEED REGULATION
        if self.vX>self.topSpeedX:
            self.vX=self.topSpeedX
        elif self.vX<-self.topSpeedX:
            self.vX=-self.topSpeedX





        #WALKING OR RUNNING SOUND

        if abs(self.vX)>(self.speedX+self.topSpeedX)/2:
            if game.catto.sound_movement==game.catto.sound_walking:
                game.catto.sound_movement.pause()
                game.catto.sound_movement = game.catto.sound_running
        else:
            if game.catto.sound_movement==game.catto.sound_running:
                game.catto.sound_movement.pause()
                game.catto.sound_movement = game.catto.sound_walking


        #JUMP
        if self.keyHandler[UP] and (self.touchingPlatform): #self.vY==self.platformVY or
            self.vY=-self.speedY
            self.sound_jump.rewind()
            self.sound_jump.play()






        # FINALLY ADD THE X VELOCITY
        self.posX += (self.vX + self.platformVX + self.collisionVX) * game.dt


        # NO SHAME IN UPDATING THE COORDINATES OF THE FOUR CORNERS IS THERE?
        self.coordsX=[self.posX-self.collisionW,self.posX+self.collisionW]
        self.coordsY=[self.posY-self.collisionH,self.posY+self.collisionH]

        # CHANGE CAMERA WITH CATTO MOVEMENT OR NOT?
        shiftCam = True

        # IF X COLLISION, THEN DONOT SHIFT CAM, ELSE SHIFT CAM
        for platform in game.platforms:
            if platform.solid and self.check_overlap(self.coordsX[0],self.coordsX[1],platform.coordsX[0],platform.coordsX[1]) and self.check_overlap(self.coordsY[0],self.coordsY[1],platform.coordsY[0],platform.coordsY[1]):
                if self.collisionDir!= DOWN and (self.abovePlatform and self.prevPlatform!=platform) or not self.abovePlatform:
                    if (self.vX>0 or self.platformVX>0) and self.coordsX[0]<platform.coordsX[0]:
                        self.posX=platform.coordsX[0]-(self.coordsX[1]-self.coordsX[0])//2
                        shiftCam = False
                    elif (self.vX<0 or self.platformVX<0) and self.coordsX[1]>platform.coordsX[1]:
                        self.posX=platform.coordsX[1]+(self.coordsX[1]-self.coordsX[0])//2
                        shiftCam = False

                    break

        # IF INSIDE OBSTACLE DONOT SHIFT CAM
        if self.insideObstacle:
            if self.coordsX[0]<self.insideObstacle.coordsX[0]:
                self.posX=platform.coordsX[0]-(self.coordsX[1]-self.coordsX[0])//2
                shiftCam = False
            elif self.coordsX[1]>self.insideObstacle.coordsX[1]:
                self.posX=platform.coordsX[0]+(self.coordsX[1]-self.coordsX[0])//2
                shiftCam = False

        # FINALLY ADD THE Y VELOCITY
        self.posY += (self.vY                  ) * game.dt #  + self.platformVY

        self.coordsX=[self.posX-self.collisionW,self.posX+self.collisionW]
        self.coordsY=[self.posY-self.collisionH,self.posY+self.collisionH]


        # JUST CHECKING TO KEEP CATTO NOT CROSS THE GROUND
        if self.coordsY[1] > self.gnd:
            self.posY = self.gnd-self.collisionH

        # CHECK DOWN COLLISION
        for platform in game.platforms:
            if platform.solid and self.check_overlap(self.coordsX[0],self.coordsX[1],platform.coordsX[0],platform.coordsX[1]) and self.check_overlap(self.coordsY[0],self.coordsY[1],platform.coordsY[0],platform.coordsY[1]):


                if self.posY-self.collisionH/2 - self.vY*self.prevDt >= platform.coordsY[1]:
                    self.collisionDir = DOWN
                    self.platform_above = platform
                    self.posY = platform.coordsY[1]+self.collisionH
                    self.vY=0

                    break



        # STORE CURRENT DT FOR NEXT FRAME TO USE AS PREVIOUS DT
        self.prevDt = game.dt

        # WHEN LOSES HEALTH
        if self.respawning and self.sound_health_lost.isPlaying():
            self.posX = self.health_lostX

            shiftCam = False

        # RESPAWNING SUCCESSFUL, TURN BACK TO NORMAL
        elif self.respawning and not self.sound_health_lost.isPlaying():
            self.posX = game.safePointsList[game.safePointsIndex]+self.collisionW//2
            self.posY = GND - 400
            self.vY = 0
            game.gameX = self.posX-SCRN_WIDTH//2
            self.respawning = False
            self.stamina = 100
            shiftCam = True
        if self.insideObstacle:
            if not self.respawning:
                self.insideObstacle = None


        # SETTING NEW SAFE POINTS (CHECK POINTS THAT YOU SPAWN INTO)
        if game.safePointsIndex+1<len(game.safePointsList) and  self.posX - (self.coordsX[1]-self.coordsX[0])/2 >= game.safePointsList[game.safePointsIndex+1]:
            game.safePointsIndex+=1
            game.score+=SCORES_DICT['CHECKPOINT']

        # SETTING NEW LEFT CHECKPOINT (TO NOT MOVE THE CAMERA BEYOND THE LEFT CHECKPOINT!)
        if self.posX>game.checkPointsList[game.rightCheckPointIndex-1] + game.w//2 + (self.coordsX[1]-self.coordsX[0])/2:
            game.leftCheckPointIndex=game.rightCheckPointIndex-1

        # DONOT LET HIM CROSS THE LEFT CHECK POINT
        if self.posX<game.checkPointsList[game.leftCheckPointIndex]+(self.coordsX[1]-self.coordsX[0])/2:
            self.posX=game.checkPointsList[game.leftCheckPointIndex]+(self.coordsX[1]-self.coordsX[0])/2

        # DONOT LET HIM CROSS THE RIGHT CHECK POINT
        if self.posX>game.checkPointsList[game.rightCheckPointIndex]-(self.coordsX[1]-self.coordsX[0])/2:
            self.posX=game.checkPointsList[game.rightCheckPointIndex]-(self.coordsX[1]-self.coordsX[0])/2



        # SHIFT SCREEN X,Y
        if shiftCam and self.posX >= game.w//2+game.checkPointsList[game.leftCheckPointIndex]:
            game.gameX += (self.vX + self.platformVX  + self.collisionVX)*game.dt

        # DONOT SHIFT THE SCREEN IF BEYOND THE LEFT CHECKPOINT
        if self.posX < game.checkPointsList[game.leftCheckPointIndex] + game.w//2:
            game.gameX = game.checkPointsList[game.leftCheckPointIndex] + (game.gameX-game.checkPointsList[game.leftCheckPointIndex])/2

        # DONOT SHIFT THE SCREEN BEYOND THE RIGHT CHECKPONT
        if self.posX > game.checkPointsList[game.rightCheckPointIndex]-game.w//2:
            game.gameX = game.checkPointsList[game.rightCheckPointIndex]-game.w#-= (self.vX + self.platformVX  + self.collisionVX)*game.dt







        # INCREASE STAMINA BY USUAL RATE, ACCOUNT FOR THE VARIABLE FRAME DURATION
        if abs(self.vX)==self.speedX:
            self.stamina+=0.05*game.dt/float(17)
        elif self.vX==0:
            self.stamina+=0.08*game.dt/float(17)
        # STAMINA CANT BE GREATER THAN 100
        if self.stamina>100:
            self.stamina=100





        ## SOUNDS
        if (not self.touchingPlatform) and abs(self.posY-self.gnd)<self.collisionH+10:
            if not self.sound_land.isPlaying():
                self.sound_land.rewind()
                self.sound_land.play()

        if self.vX!=0 and self.vY==0 and not self.sound_movement.isPlaying():

            self.sound_movement.play()
        elif self.vX==0 or self.vY!=0:
            self.sound_movement.pause()
            self.sound_movement.rewind()

    # CATTO DISPLAY
    def display(self,update=True):
        if self.insideObstacle or self.respawning:
            self.keyHandler[LEFT] = False
            self.keyHandler[RIGHT] = False
            self.keyHandler[UP] = False
            self.keyHandler[DOWN] = False
            self.keyHandler['X'] = False
            self.attack = False

        if update:
            self.update()

            if not self.attack:
                if self.vX!=0:
                    self.f=self.f+map(abs(self.vX),self.speedX,self.topSpeedX,4,5.5)/self.totalFrames*float(game.dt)/float(32)
                    self.f=self.f%self.totalFrames
                else:
                    self.f=self.defaultStopFrame

                if (not self.touchingPlatform) and ((self.gnd)-(self.coordsY[1]+self.platformVY*game.dt))<50:
                    self.f=self.defaultLandingFrame
                elif (not self.touchingPlatform) and ((self.gnd)-(self.coordsY[1]+self.platformVY*game.dt))>50:
                    self.f=self.defaultJumpFrame
                elif (not self.touchingPlatform):
                    self.f=self.defaultJumpFrame

            # SCRATCH ANIMATION
            elif self.attack:
                self.f = self.f+6.1/self.totalFrames*float(game.dt)/float(32)
            if self.f>=13:
                self.attack = False




        if (not self.respawning or (self.insideObstacle)) and self.dir==RIGHT:
            image(self.img,self.coordsX[0]+self.displayXOffset-game.gameX,self.coordsY[0]+self.displayYOffset-game.gameY,self.displayW,self.displayH,self.displayW*int(self.f),0,self.displayW*int(self.f+1),self.imgHeight)
        elif (not self.respawning or (self.insideObstacle)) and self.dir==LEFT:
            image(self.img,self.coordsX[0]+self.leftDisplayXOffset-game.gameX,self.coordsY[0]+self.displayYOffset-game.gameY,self.displayW,self.displayH,self.displayW*int(self.f+1),0,self.displayW*int(self.f),self.imgHeight)


# COINS, FOOD AND STAMINA
class Consumable():
    def __init__(self, posX, posY, img, w, h, numFrames, imgWidth, imgHeight):
        self.posX = posX
        self.posY = posY
        self.w = w
        self.h = h
        self.coordsX = [self.posX,self.posX+self.w]
        self.coordsY = [self.posY,self.posY+self.h]
        self.numFrames = numFrames
        self.img = img
        self.imgWidth = imgWidth
        self.imgHeight = imgHeight
        self.curFrame = 0


    def display(self,update=True):

        if update:
            self.curFrame = (self.curFrame + 0.4*float(game.dt)/float(32))%self.numFrames
        image(self.img, self.posX-game.gameX, self.posY, self.w, self.h, int(self.curFrame)*self.imgWidth/self.numFrames, 0, (int(self.curFrame)+1)*self.imgWidth/self.numFrames, self.imgHeight)



############################################################################################################
# MENU CLASSES
############################################################################################################


# CONTROLS CLASS
# NOT BEAUTIFUL, BUT THE DEADINE AIN'T BEAUTIFUL AS WELL
class ControlMenu():
    def __init__(self,displayBG=True):
        self.img=loadImage(PATH+"/Resources/images/bg.png")
        self.texts=["LEFT ARROW            Move Left",
                    "RIGHT ARROW           Move Right",
                    "UP ARROW                Jump",
                    "SPACE BAR               Hold while moving to sprint",
                    "M                             Mew",
                    "X                              Scratch your opponent",
                    "ENTER                      Pause the game",
                    "ESC                          Back to Main Menu"]
        self.posX = 0-300
        self.posY = 0+50
        self.TEXT_SPACING=50
        self.displayBG = displayBG

    def display(self):

        if self.displayBG:
            image(self.img,0,0,SCRN_WIDTH,SCRN_HEIGHT)
        noStroke()
        rectMode(CENTER)
        fill(0,0,0,100)

        rect(SCRN_WIDTH//2,SCRN_HEIGHT//2,1100,600,100)

        rectMode(CORNER)

        fill(255,255,255)
        textAlign(CENTER)
        textSize(40)
        text("CONTROLS",SCRN_WIDTH//2,self.posY+SCRN_HEIGHT//2-1*self.TEXT_SPACING-len(self.texts)//2*self.TEXT_SPACING)
        textAlign(LEFT)
        textSize(20)
        for i,txt in enumerate(self.texts):
            text(txt,SCRN_WIDTH//2+self.posX,self.posY+SCRN_HEIGHT//2+i*self.TEXT_SPACING-len(self.texts)//2*self.TEXT_SPACING)

# CREDITS CLASS
class Credits():
    def __init__(self):
        self.img=loadImage(PATH+"/Resources/images/bg.png")
        self.texts=[["Team Member 1","Meher Md Saad"],
                    ["Team Member 2","Asif Tauhid"],
                    ["Supervisor","Prof Yasir Zaki"],
                    ["Inspiration","Scarlett"],
                    ["Lead Designer","Asif Tauhid"],
                    ["Co Designer","Meher Md Saad"],
                    ["Sound Design Inspiration","Pierre"],
                    ["Sound Design Inspiration","Fardin"],
                    ["Sound Design Inspiration","Mashrafi"],
                    ["Music Credit","Hundred Years of Harmony (YT)"],
                    ["Sound Effects","ZapSplat"],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    [" "," "],
                    ["The Legend of Catto","All rights reserved"]]

        self.posX = 0
        self.posY = SCRN_HEIGHT//2
        self.TEXT_SPACING=50
        self.distanceX = 50
        self.moveY= 200
        self.spd = 0
        self.acc = 0.01
        self.msg_img=loadImage(PATH+"/Resources/images/credits.jpg")

    # SET SCROLLING INITIAL POSITION5
    def set_start(self):
        self.moveY = 300
        self.spd = 0

    def display(self):

        self.acc = 0.01*game.dt/float(16)

        image(self.img,0,0,SCRN_WIDTH,SCRN_HEIGHT)

        rectMode(CENTER)
        fill(0,0,0,100)

        rect(SCRN_WIDTH//2,SCRN_HEIGHT//2,SCRN_WIDTH,SCRN_HEIGHT)

        rectMode(CORNER)


        fill(255,255,255)
        textAlign(CENTER)
        textSize(40)
        text("CREDITS",SCRN_WIDTH//2,self.moveY+self.posY+SCRN_HEIGHT//2-2*self.TEXT_SPACING-len(self.texts)//2*self.TEXT_SPACING)
        textSize(20)

        for i,txt in enumerate(self.texts):
            textAlign(RIGHT)
            text(txt[0],SCRN_WIDTH//2-self.distanceX,self.moveY+self.posY+SCRN_HEIGHT//2+i*self.TEXT_SPACING-len(self.texts)//2*self.TEXT_SPACING)
            textAlign(LEFT)
            text(txt[1],SCRN_WIDTH//2+self.distanceX,self.moveY+self.posY+SCRN_HEIGHT//2+i*self.TEXT_SPACING-len(self.texts)//2*self.TEXT_SPACING)

        textAlign(CENTER)
        text("MESSAGE TO THE PROFESSOR",SCRN_WIDTH//2-0*self.distanceX,self.moveY+self.posY+SCRN_HEIGHT//2+12.5*self.TEXT_SPACING-len(self.texts)//2*self.TEXT_SPACING)
        image(self.msg_img,SCRN_WIDTH//2-350/2,self.moveY+self.posY+SCRN_HEIGHT//2+13.5*self.TEXT_SPACING-len(self.texts)//2*self.TEXT_SPACING,350,335)

        self.moveY-=self.spd

        if self.spd<5:
            self.spd+=self.acc

        if self.moveY+self.posY+SCRN_HEIGHT//2+i*self.TEXT_SPACING-len(self.texts)//2*self.TEXT_SPACING <= SCRN_HEIGHT//2:
            self.spd=0


# MENU CLASS TO MAKE OPTIONS AND MOUSE TRACKING
class Menu():
    def __init__(self,options=["PLAY GAME","CONTROLS","SETTINGS","CREDITS","EXIT"],choice=0,posX=270,posY=100,TEXT_SPACING=50,textTitle = "Legend of Catto",textTitleAlign=RIGHT,textTitlePosX=SCRN_WIDTH-50,textTitlePosY=100+100,textTitleFontSize=50,optionsFontSize=36,displayBG=True,xOffset=0,yOffset=-16):
        self.options = options
        self.choice = choice
        self.sound_menu_hover = minim.loadFile(PATH+"/Resources/sounds/menu_hover_2.mp3")
        self.bg = loadImage(PATH+"/Resources/images/bg.png")
        self.displayBG = displayBG

        self.posX = posX
        self.posY = posY
        self.textTitle = textTitle
        self.TEXT_SPACING = TEXT_SPACING
        self.textTitleAlign = textTitleAlign
        self.textTitlePosX = textTitlePosX
        self.textTitlePosY = textTitlePosY
        self.textTitleFontSize = textTitleFontSize
        self.optionsFontSize=optionsFontSize

        self.select = None

        # DISPLAY STUFF:

        # TRIANGLE ICON
        self.l=13 # Triangle Side Length Kinda Variable
        self.xOffset=xOffset # How far left is the icon from the text
        self.yOffset=yOffset
        self.mouseMotion = False

    def set_volume(self):
        self.sound_menu_hover.setGain(game.sfx_volume)

    # METHOD TO UPDATE SELECTED OPTION BY MOUSE CLICK ORI MOUSE MOTION
    def updateOptionByMouse(self):
        if (game.mouseMotion or game.mouseClick) and (self.posY-self.l+SCRN_HEIGHT//2+0*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING+self.yOffset) <= mouseY <= (self.posY-self.l+SCRN_HEIGHT//2-len(self.options)//2*self.TEXT_SPACING+self.yOffset) +(len(self.options))*self.TEXT_SPACING:
            val=(mouseY-(self.posY-self.l+SCRN_HEIGHT//2+0*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING+self.yOffset))//(self.TEXT_SPACING)

            if val<0:
                val=0
            elif val>=len(self.options):
                val=len(self.options)-1

            if self.posX+SCRN_WIDTH//2-textWidth(self.options[val])//2-self.xOffset <= mouseX <= self.posX+SCRN_WIDTH//2+textWidth(self.options[val])//2+self.xOffset:
                # val=(mouseY-(self.posY-self.l+SCRN_HEIGHT//2+0*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING+self.yOffset))//(self.TEXT_SPACING)

                if val != self.choice and not self.sound_menu_hover.isPlaying():
                    self.sound_menu_hover.rewind()
                    self.sound_menu_hover.play()
                self.choice = val
                return True
        return False

    def display(self):

        self.updateOptionByMouse()


        if self.displayBG:
            image(self.bg,0,0,SCRN_WIDTH,SCRN_HEIGHT)
        fill(255,255,255)
        textAlign(CENTER)
        textSize(self.optionsFontSize)
        for i,option_txt in enumerate(self.options):
            text(option_txt,SCRN_WIDTH//2+self.posX,self.posY+SCRN_HEIGHT//2+i*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING)

        textSize(self.textTitleFontSize)
        textAlign(self.textTitleAlign)
        text(self.textTitle,self.textTitlePosX,self.textTitlePosY)

        noStroke()
        triangle(self.posX+SCRN_WIDTH//2-textWidth(self.options[self.choice])//2-self.xOffset,self.posY+self.l+SCRN_HEIGHT//2+self.choice*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING+self.yOffset,
                 self.posX+SCRN_WIDTH//2-textWidth(self.options[self.choice])//2-self.xOffset,self.posY-self.l+SCRN_HEIGHT//2+self.choice*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING+self.yOffset,
                 self.l+self.posX+SCRN_WIDTH//2-textWidth(self.options[self.choice])//2-self.xOffset,self.posY+SCRN_HEIGHT//2+self.choice*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING+self.yOffset)



class PauseMenu(Menu):
    def __init__(self):
        Menu.__init__(self,options=["RESUME","SETTINGS","CONTROLS","RETURN TO MAIN MENU","EXIT GAME"],choice=0,posX=0,posY=50,TEXT_SPACING=50,textTitle = "GAME PAUSED",textTitleAlign=CENTER,textTitlePosX=SCRN_WIDTH//2,textTitlePosY=200,displayBG=False)

class ConfirmationMessage(Menu):
    def __init__(self,displayBG=False):
        Menu.__init__(self,options=["YES","NO"],choice=1,posX=0,posY=50,TEXT_SPACING=50,textTitle = "ARE YOU SURE YOU WANT TO EXIT",textTitleAlign=CENTER,textTitlePosX=SCRN_WIDTH//2,textTitlePosY=270,textTitleFontSize=36,optionsFontSize=36,displayBG=displayBG,xOffset=30)

class ConfirmationMessageMainMenu(Menu):
    def __init__(self):
        Menu.__init__(self,options=["YES","NO"],choice=1,posX=0,posY=50,TEXT_SPACING=50,textTitle = "ARE YOU SURE YOU WANT TO RETURN TO MAIN MENU",textTitleAlign=CENTER,textTitlePosX=SCRN_WIDTH//2,textTitlePosY=270,textTitleFontSize=28,optionsFontSize=28,displayBG=False,xOffset=30)

# MAINLY VOLUME SETTINGS
class Settings(Menu):
    def __init__(self,displayBG=True):
        Menu.__init__(self,options=["8","8"],choice=0,posX=200,posY=50,TEXT_SPACING=80,textTitle = "SETTINGS",textTitleAlign=CENTER,textTitlePosX=SCRN_WIDTH//2,textTitlePosY=200,displayBG=displayBG,xOffset=50)
        self.settings_text = ["MUSIC VOLUME","SFX VOLUME"]

    def updateOptionText(self,index,dx):
        self.options[index]=str(int(self.options[index])+dx)
        if int(self.options[index])<0:
            self.options[index]="0"
        elif int(self.options[index])>10:
            self.options[index]="10"
        return int(self.options[index])


    def display(self):
        self.updateOptionByMouse()


        if self.displayBG:
            image(self.bg,0,0,SCRN_WIDTH,SCRN_HEIGHT)
        fill(255,255,255)
        textAlign(CENTER)
        textSize(self.optionsFontSize)
        for i,option_txt in enumerate(self.options):
            text(option_txt,SCRN_WIDTH//2+self.posX,self.posY+SCRN_HEIGHT//2+i*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING)

        for i,option_txt in enumerate(self.settings_text):
            text(option_txt,SCRN_WIDTH//2-self.posX,self.posY+SCRN_HEIGHT//2+i*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING)

        textSize(self.textTitleFontSize)
        textAlign(self.textTitleAlign)
        text(self.textTitle,self.textTitlePosX,self.textTitlePosY)

        noStroke()
        triangle(self.posX+SCRN_WIDTH//2-textWidth(self.options[self.choice])//2-self.xOffset,self.posY+self.l+SCRN_HEIGHT//2+self.choice*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING+self.yOffset,
                 self.posX+SCRN_WIDTH//2-textWidth(self.options[self.choice])//2-self.xOffset,self.posY-self.l+SCRN_HEIGHT//2+self.choice*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING+self.yOffset,
                 -self.l+self.posX+SCRN_WIDTH//2-textWidth(self.options[self.choice])//2-self.xOffset,self.posY+SCRN_HEIGHT//2+self.choice*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING+self.yOffset)

        triangle(self.posX+SCRN_WIDTH//2+textWidth(self.options[self.choice])//2+self.xOffset,self.posY+self.l+SCRN_HEIGHT//2+self.choice*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING+self.yOffset,
                 self.posX+SCRN_WIDTH//2+textWidth(self.options[self.choice])//2+self.xOffset,self.posY-self.l+SCRN_HEIGHT//2+self.choice*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING+self.yOffset,
                 self.l+self.posX+SCRN_WIDTH//2+textWidth(self.options[self.choice])//2+self.xOffset,self.posY+SCRN_HEIGHT//2+self.choice*self.TEXT_SPACING-len(self.options)//2*self.TEXT_SPACING+self.yOffset)

# CLASS TO SHOW GAMEOVER SCREEN WITH NAME TEXT
class GameOver():
    def __init__(self):
        self.img_lost=loadImage(PATH+"/Resources/images/game_over_lost_1.png")
        self.img_lost_highscore=loadImage(PATH+"/Resources/images/game_over_lost_highscore_1.png")
        self.img_won=loadImage(PATH+"/Resources/images/game_won_1.png")
        self.img_won_highscore=loadImage(PATH+"/Resources/images/game_won_highscore_1.png")

        self.vid_win_path = PATH+"/Resources/videos/win_000"
        self.vid_win_frame = 0
        self.vid_win_current_frame = loadImage(self.vid_win_path+str(int(self.vid_win_frame))+".png")

        self.name_txt_posX = 450
        self.name_txt_posY = 590
        self.name_txt_font = 30

        self.name_txt = ""

        self.character_offset = 44

    def display(self,win=False,highscore=False):
        if win:
            if highscore:
                image(self.img_won_highscore,0,0)
            else:
                image(self.img_won,0,0)
        else:
            if highscore:
                image(self.img_lost_highscore,0,0)
            else:
                image(self.img_lost,0,0)

        if win:
            self.vid_win_frame += float(8)/(float(1000)/float(game.dt))#float(60)
            self.vid_win_frame = self.vid_win_frame % 71
            self.vid_win_current_frame = loadImage(self.vid_win_path+str(int(self.vid_win_frame))+".png")
            image(self.vid_win_current_frame,0,0)
            del self.vid_win_current_frame
            self.vid_win_current_frame = ""

        textAlign(CENTER)
        xOffset = 0
        yOffset = 0
        if game.win:
            xOffset=365
            yOffset=-70
        fill(255)
        text(str(game.score),SCRN_WIDTH//2+xOffset,455+yOffset)

        textAlign(LEFT)
        textSize(self.name_txt_font)

        for i,character in enumerate(list(self.name_txt)):
            text(character,self.name_txt_posX+self.character_offset*i+xOffset,self.name_txt_posY+yOffset)

# CLASS TO DISPLAY LEADER BOARD
class HighscoreMenu():
    def __init__(self):
        self.img=loadImage(PATH+"/Resources/images/highscore.png")
        self.posX = -400
        self.posY = 100
        self.TEXT_SPACING=40

    def display(self):

        image(self.img,0,0,SCRN_WIDTH,SCRN_HEIGHT)
        noStroke()
        rectMode(CENTER)
        fill(0,0,0,100)

        rect(SCRN_WIDTH//2,SCRN_HEIGHT//2+50,1100,520,50)

        rectMode(CORNER)
        #tint(0,255)

        fill(255,255,255)
        textAlign(CENTER)

        textAlign(LEFT)
        textSize(25)


        text("Rank",SCRN_WIDTH//2+self.posX,self.posY+SCRN_HEIGHT//2+-1.5*self.TEXT_SPACING-5*self.TEXT_SPACING)
        text("Name",SCRN_WIDTH//2+self.posX + 200,self.posY+SCRN_HEIGHT//2+-1.5*self.TEXT_SPACING-5*self.TEXT_SPACING)
        textAlign(RIGHT)
        text("Score",SCRN_WIDTH//2+self.posX + 700,self.posY+SCRN_HEIGHT//2+-1.5*self.TEXT_SPACING-5*self.TEXT_SPACING)

        textSize(20)
        for i,entry in enumerate(game.highscore_list):
            textAlign(LEFT)
            text(str(i+1),SCRN_WIDTH//2+self.posX,self.posY+SCRN_HEIGHT//2+i*self.TEXT_SPACING-5*self.TEXT_SPACING)
            text(entry[0],SCRN_WIDTH//2+self.posX + 200,self.posY+SCRN_HEIGHT//2+i*self.TEXT_SPACING-5*self.TEXT_SPACING)
            textAlign(RIGHT)
            text(str(entry[1]),SCRN_WIDTH//2+self.posX + 700,self.posY+SCRN_HEIGHT//2+i*self.TEXT_SPACING-5*self.TEXT_SPACING)

# CLASS TO DISPLAY VITAL INSTRUCTIONS DURING GAMEPLAY
class Information():
    def __init__(self,posX,txt_list,img,title = "Information"):
        self.title = title
        self.txts = txt_list
        self.TEXT_SPACING = 40
        self.xPadding = 60
        self.yPadding = 40
        self.w = 650
        self.h = (len(self.txts)+1)*20 + (len(self.txts))*self.TEXT_SPACING
        self.img = img
        self.sound_active=minim.loadFile(PATH+"/Resources/sounds/info.mp3")

        self.posX = posX
        self.rangeX = 300
        self.active = False

    def set_volume(self):
        self.sound_active.setGain(game.sfx_volume)

    def display_img(self):
        imageMode(CENTER)
        image(self.img,self.posX-game.gameX+self.rangeX/2,GND-80)
        imageMode(CORNER)

    def display(self):

        if game.catto.check_overlap(self.posX,self.posX+self.rangeX,game.catto.coordsX[0],game.catto.coordsX[1]):
        # if game.catto.posX
            if not self.active:
                self.sound_active.play()
            self.active = True
            # game.mode = 'information'
            for txt in self.txts:
                if self.w<textWidth(txt):
                    self.w = textWidth(txt)

            # tint(255,100)
            rectMode(CENTER)
            fill(0,150)
            noStroke()
            # rect(SCRN_WIDTH//2,SCRN_HEIGHT//2,self.w+self.xPadding,self.h+self.yPadding,50)
            rect(SCRN_WIDTH//2,SCRN_HEIGHT//2,SCRN_WIDTH,self.h+self.yPadding)
            # tint(255,255)
            rectMode(CORNER)


            fill(255)
            textAlign(CENTER)
            textSize(30)
            text(self.title,SCRN_WIDTH//2,SCRN_HEIGHT//2+((-1+1)-len(self.txts)//2)*self.TEXT_SPACING)
            textSize(16)
            for i,txt in enumerate(self.txts):
                text(txt,SCRN_WIDTH//2,SCRN_HEIGHT//2+((i+1)-len(self.txts)//2)*self.TEXT_SPACING)
        else:
            self.active = False
            if not self.sound_active.isPlaying():
                self.sound_active.rewind()

# THE GAME RUNS HERE
class Game():
    def __init__(self):
        self.w = SCRN_WIDTH
        self.h = SCRN_HEIGHT
        self.gnd=GND

        self.score = 0
        self.game_over = False



        self.prevTime=millis()
        self.dt=17

        self.dummy_img = loadImage(PATH+"/Resources/images/dummy.png")

        self.catto_img=loadImage(PATH+"/Resources/images/catto_scratch.png")
        self.doggo_img=loadImage(PATH+"/Resources/images/doggo_new.png")
        self.birdo_img=loadImage(PATH+"/Resources/images/birdo.png")

        self.catto = Catto(100,100,self.catto_img)



        self.gameX = 0
        self.gameY = 0
        self.leftCheckPointIndex = 0
        self.safePointsIndex = 0

        self.checkpoint_img = loadImage(PATH+"/Resources/images/checkpoint.png")
        self.checkPointsList=[]#[0,1280,1280*2,1280*3,1280*4]
        self.safePointsList = []#[0,1280,1280*2,1280*3,1280*4]

        self.coin_img = loadImage(PATH+"/Resources/images/coin.png")
        self.food_img = loadImage(PATH+"/Resources/images/food.png")
        self.stamina_img = loadImage(PATH+"/Resources/images/stamina.png")
        self.coins =[]
        self.foods =[]
        self.staminas =[]

        self.enemies = []

        self.obstacle_trap_img = loadImage(PATH+"/Resources/images/trap_obstacle.png")
        self.obstacle_water_img = loadImage(PATH+"/Resources/images/water_obstacle.png")
        self.obstacles = []

        self.info_img = loadImage(PATH+"/Resources/images/info.png")
        self.infos = []

        self.platform_img=loadImage(PATH+"/Resources/images/platform.png")
        self.platform_block_img=loadImage(PATH+"/Resources/images/platform_block.png")
        self.popup_platform_img=loadImage(PATH+"/Resources/images/cracked_platform.png")

        self.platforms=[]

        self.fatslob_img = loadImage(PATH+"/Resources/images/fatslob.png")
        self.fatslob = Fatslob(self.fatslob_img)


        # CONSTRUCT THE LEVEL FROM READING FROM THE CSV FILE
        self.levelsFile = open(PATH+"/Resources/data/levels.csv",'r')

        for dataLine in self.levelsFile:
            dataLine=dataLine.strip().split(',')

            if dataLine[0] and dataLine[0][0]=='#':
                continue
            elif dataLine[0]=='checkpoint':
                self.checkPointsList.append(int(dataLine[1]))
                self.safePointsList.append(int(dataLine[1]))

            elif dataLine[0]=='coin':
                self.coins.append(Consumable(int(dataLine[1]),int(eval(dataLine[2])),self.coin_img,55,55,7,55*7,55))

            # posX, posY, img, w, h, numFrames, imgWidth, imgHeight)
            elif dataLine[0]=='food':
                self.foods.append(Consumable(int(dataLine[1]),int(eval(dataLine[2])),self.food_img,55*1.2,30*1.2,6,55*6,30))
            elif dataLine[0]=='stamina':
                self.staminas.append(Consumable(int(dataLine[1]),int(eval(dataLine[2])),self.stamina_img,119.0/7*2,30*2,7,119,30))

            elif dataLine[0] == 'doggo':
                self.enemies.append(Doggo(int(dataLine[1]),int(eval(dataLine[2])),self.doggo_img))

            elif dataLine[0] == 'birdo':
                self.enemies.append(Birdo(int(dataLine[1]),int(eval(dataLine[2])),self.birdo_img))


            elif dataLine[0] == 'obstacle':
                if dataLine[1]=='trap':
                    self.obstacles.append(Obstacle(int(dataLine[2]),int(dataLine[3]),int(dataLine[4]),dataLine[1],self.obstacle_trap_img))
                else:
                    self.obstacles.append(Obstacle(int(dataLine[2]),int(dataLine[3]),int(dataLine[4]),dataLine[1],self.obstacle_water_img))

            elif dataLine[0] == 'info':
                info_msg = []
                for sentence in dataLine[2:]:
                    info_msg.append(sentence)
                self.infos.append(Information(int(dataLine[1]),info_msg,self.info_img))

            elif dataLine[0] == 'movingPlatform':
                if len(dataLine)==10 and dataLine[9]=='boulder':
                    self.platforms.append(MovingPlatform(int(dataLine[1]),int(eval(dataLine[2])),int(dataLine[3]),int(dataLine[4]),self.platform_block_img,float(dataLine[5]),float(dataLine[6]),int(dataLine[7]),int(dataLine[8])))

                else:
                    self.platforms.append(MovingPlatform(int(dataLine[1]),int(eval(dataLine[2])),int(dataLine[3]),int(dataLine[4]),self.platform_img,float(dataLine[5]),float(dataLine[6]),int(dataLine[7]),int(dataLine[8])))

            elif dataLine[0] == 'popupPlatform':
                self.platforms.append(PopUpPlatform(int(dataLine[1]),int(eval(dataLine[2])),int(dataLine[3]),int(dataLine[4]),self.popup_platform_img,float(dataLine[5])))

        self.enemies.append(self.fatslob)

        self.rightCheckPointIndex = len(self.checkPointsList)-1


        # CHECK POINT PLATFORMS
        for i in range(len(self.checkPointsList)):
            self.platforms.append(MovingPlatform(self.checkPointsList[i]-100+75,GND-10,200,10,self.platform_img,0,0,100,200))

        # SORT THE PLATFORMS
        self.platforms.sort(reverse=False,key=lambda x:x.coordsY[0])




        # LOADING BGS
        self.bgs = []

        for i in range(5):
            self.bgs.append(loadImage(PATH+"/Resources/images/m_bg_0{0}.png".format(5-i)))

        # self.constant_bg = []
        self.constant_bg=loadImage(PATH+"/Resources/images/o_bg_02.png")
        self.constant_bg_posX = 20600
        self.displayConstantBG = False



        # MENU AND MODES STUFF

        self.menu = Menu()
        self.mouseMotion = False
        self.mouseClick = False

        self.settingsMenu=Settings()
        self.confirmationMessageMenu=ConfirmationMessage(displayBG=True)

        self.pausedSettingsMenu=Settings(displayBG=False)
        self.pauseMenu=PauseMenu()
        self.pausedControlMenu=ControlMenu(displayBG=False)
        self.confirmationMessage=ConfirmationMessage()
        self.confirmationMessageMainMenu=ConfirmationMessageMainMenu()

        self.controlMenu=ControlMenu()
        self.creditsMenu=Credits()
        self.highscoreCredits=Credits()

        self.gameover=GameOver()
        self.win = False
        self.highscore = False
        self.highscoreMenu=HighscoreMenu()

        self.cheatCode = ""
        self.cheatCodeTimer = 0



        ##############################################################################
        # Read scores and determine highscore
        score_file = open(PATH+"/Resources/data/scores.csv",'r')
        scores_list = []
        for l in score_file:
            l=l.strip().split(',')
            scores_list.append([l[0],int(l[1]),int(l[2])]) # [name,score,time]
        score_file.close()

        scores_list.sort(reverse=True,key = lambda x: (x[1],x[2]))
        self.highscore_list=scores_list[:10]
        del scores_list

        ##############################################################################

        self.mode='menu'
        self.loading = False
        self.display_speed_bar = False


        # SOUNDS
        self.music_volume = VOLUME_DICT[8]
        self.sfx_volume = VOLUME_DICT[8]

        self.sound_intro_start=minim.loadFile(PATH+"/Resources/sounds/intro_start.mp3")
        self.sound_intro_loop=minim.loadFile(PATH+"/Resources/sounds/intro_loop.mp3")
        self.sound_intro_flag = "non-pause"
        self.sound_game_over=minim.loadFile(PATH+"/Resources/sounds/gameover.mp3")
        self.sound_win_start=minim.loadFile(PATH+"/Resources/sounds/win_start.mp3")
        self.sound_win_loop=minim.loadFile(PATH+"/Resources/sounds/win_loop.mp3")
        self.sound_boss_music=minim.loadFile(PATH+"/Resources/sounds/boss_music.mp3")

        self.sound_win_start_flag = False

        self.sound_intro_start.play()
        self.sound_intro_start.setGain(self.music_volume)
        self.sound_intro_loop.setGain(self.music_volume)
        self.sound_game_over.setGain(self.music_volume)
        self.sound_win_start.setGain(self.music_volume)
        self.sound_win_loop.setGain(self.music_volume)
        self.sound_boss_music.setGain(self.music_volume)




    # SET THE VOLUME OF EVERYTHING IN THE GAME
    def set_volume(self):

        self.catto.set_volume()

        for enemy in self.enemies:
            enemy.set_volume()


        for info in self.infos:
            info.set_volume()



        self.fatslob.set_volume()
        self.menu.set_volume()
        self.settingsMenu.set_volume()
        self.confirmationMessageMenu.set_volume()
        self.pausedSettingsMenu.set_volume()
        self.pauseMenu.set_volume()
        self.confirmationMessage.set_volume()
        self.confirmationMessageMainMenu.set_volume()

        self.sound_intro_start.setGain(self.music_volume-10)
        self.sound_intro_loop.setGain(self.music_volume-10)
        self.sound_game_over.setGain(self.music_volume)
        self.sound_win_start.setGain(self.music_volume)
        self.sound_win_loop.setGain(self.music_volume)
        self.sound_boss_music.setGain(self.music_volume-25)

    # SORT ALL THE PLATFORMS BY THEIR GND
    def sort_platform_by_gnd(self,gnd):
        self.platforms.sort(reverse=False,key=lambda x:x.coordsY[0])
        for i,platform in enumerate(self.platforms):
            if platform.coordsY[0]<=gnd:
                ind=i
                break
        else:
            return []
        return self.platforms[ind:]

    # SHOW SPEED BAR FOR THE CAT WHEN ACCELERATING
    def speed_bar(self):
        if self.mode=='game' and self.catto.aX>0 and self.catto.vX!=0:
            # DISPLAY STAMINA:

            noStroke()
            fill("#616161")
            rect(STATS_POSX,STATS_POSY+40,100,8,5)

            colorMode(HSB, 100)
            colH=map(abs(self.catto.vX),self.catto.speedX,self.catto.topSpeedX,0,20)
            fill(colH,100,100)
            rect(STATS_POSX,STATS_POSY+40,map(abs(self.catto.vX),self.catto.speedX,self.catto.topSpeedX,0,100),8,5)

            if abs(self.catto.vX) == self.catto.topSpeedX:
                textSize(11)
                textAlign(LEFT)
                text("FULL SPEED",STATS_POSX,STATS_POSY+70)


            colorMode(RGB, 255)

    # CHECK GAME OVER CONDITIONS
    def check_game_over(self):
        if self.catto.lives<=0:
            if self.mode=='game':
                for entry in self.highscore_list:
                    if self.score>=entry[1]:
                        self.highscore = True
                self.mode='gameover'

                for enemy in game.enemies:
                    if enemy.type=='doggo':
                        enemy.pause_sound()
                self.win = False
            return True
        elif self.fatslob.lives<=0:
            if self.mode=='game':
                for entry in self.highscore_list:
                    if self.score>=entry[1]:
                        self.highscore = True
                self.mode='gameover'
                self.win = True
                self.score+=SCORES_DICT['WIN']
            return True
        return False

    # WHEN GAME DT IS TOO BIG, DISPLAY THIS INSTEAD
    def display_loading(self):
        fill(0,100)
        rect(0,0,SCRN_WIDTH,SCRN_HEIGHT)
        tint(255,255)
        textAlign(CENTER)
        text("( LOADING )",SCRN_WIDTH//2,SCRN_HEIGHT//2)

    # DISPLAY THE GAME
    def display(self):

        self.dt=millis()-self.prevTime
        self.prevTime=millis()

        # CRUCIAL PRINTS FOR DEBUGGING
        # print("GAME DT",self.dt)
        # print(self.catto.posX, 'POS X')



        # BG MUSIC:


        if self.check_game_over():
            if self.sound_intro_start.isPlaying():
                self.sound_intro_start.pause()
            if self.sound_intro_loop.isPlaying():
                self.sound_intro_loop.pause()

            if self.sound_boss_music.isPlaying():
                self.sound_boss_music.pause()

            if self.win:
                if not self.sound_win_start_flag and not self.sound_win_start.isPlaying():
                    self.sound_win_start.play()
                    self.sound_win_start_flag = True
                elif self.sound_win_start_flag and not self.sound_win_start.isPlaying() and not self.sound_win_loop.isPlaying():
                    self.sound_win_loop.play()
                    self.sound_win_loop.loop()


            else:
                if not self.sound_game_over.isPlaying():
                    self.sound_game_over.play()
                    self.sound_game_over.loop()

        elif self.safePointsIndex==len(self.safePointsList)-2: # BOSS MODE
            if self.sound_intro_loop.isPlaying():
                self.sound_intro_loop.setGain(self.sound_intro_loop.getGain()-1)
                if self.sound_intro_loop.getGain()<-60:
                    self.sound_intro_loop.pause()
                self.sound_intro_loop.pause()
            if self.sound_intro_start.isPlaying():
                self.sound_intro_start.setGain(self.sound_intro_start.getGain()-1)
                if self.sound_intro_start.getGain()<-60:
                    self.sound_intro_start.pause()
            if not self.sound_boss_music.isPlaying():
                self.sound_boss_music.play()
                self.sound_boss_music.loop()
        elif not self.sound_intro_start.isPlaying() and not self.sound_intro_loop.isPlaying() and self.sound_intro_flag == "non-pause":
            self.sound_intro_loop.play()
            self.sound_intro_loop.loop()


        # MENU WISE DISPLAYS
        if self.mode == 'menu':
            self.menu.display()

        elif self.mode == 'settings':
            self.settingsMenu.display()

        elif self.mode=='confirmationMessageMenu':
            self.confirmationMessageMenu.display()



        elif self.mode == 'pause':
            #DISPLAY ALL THE GAME STUFF BUT DONOT UPDATE THEM

            for i,bg in enumerate(self.bgs):
                x = int((2*self.gameX) // (len(self.bgs)-i+1))
                image(bg,0-(x%self.w),0)

                image(bg,self.w-(x%self.w),0,(x%self.w),self.h,0,0,(x%self.w),self.h)

            stroke(0,255,0)
            line(0,self.gnd-game.gameY,self.w,self.gnd-game.gameY)
            noStroke()

            # DISPLAY LIVES:
            for i in range(self.catto.totalLives):
                fill(100,0,0)
                #ellipseMode(CORNER)
                circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
            for i in range(self.catto.lives):
                fill(230,0,0)
                #ellipseMode(CORNER)
                circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
            # DISPLAY STAMINA:
            fill("#616161")
            rect(STATS_POSX,STATS_POSY+15,100,5,5)
            fill("#ffffff")
            rect(STATS_POSX,STATS_POSY+15,self.catto.stamina,5,5)

            self.catto.display(update=False)

            for platform in self.platforms:
                platform.display(update=False)

            for coin in self.coins:
                coin.display(update=False)

            if self.display_speed_bar:
                self.speed_bar()
            #DISPLAY ALL THE GAME STUFF BUT DONOT UPDATE THEM
            #tint(255,100)
            fill(0,100)
            rect(0,0,SCRN_WIDTH,SCRN_HEIGHT)
            tint(255,255)

            # PAUSE THE SOUND OF WALKING OR RUNNING WHEN THE SCREEN IS PAUSED
            self.catto.sound_movement.pause()
            self.catto.sound_movement.rewind()


            self.pauseMenu.display()

        elif self.mode == 'pausedSettingsMenu':
            #DISPLAY ALL THE GAME STUFF BUT DONOT UPDATE THEM

            for i,bg in enumerate(self.bgs):
                x = int((2*self.gameX) // (len(self.bgs)-i+1))
                image(bg,0-(x%self.w),0)

                image(bg,self.w-(x%self.w),0,(x%self.w),self.h,0,0,(x%self.w),self.h)

            stroke(0,255,0)
            line(0,self.gnd-game.gameY,self.w,self.gnd-game.gameY)
            noStroke()

            # DISPLAY LIVES:
            for i in range(self.catto.totalLives):
                fill(100,0,0)
                #ellipseMode(CORNER)
                circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
            for i in range(self.catto.lives):
                fill(230,0,0)
                #ellipseMode(CORNER)
                circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
            # DISPLAY STAMINA:
            fill("#616161")
            rect(STATS_POSX,STATS_POSY+15,100,5,5)
            fill("#ffffff")
            rect(STATS_POSX,STATS_POSY+15,self.catto.stamina,5,5)

            self.catto.display(update=False)

            for platform in self.platforms:
                platform.display(update=False)

            for coin in self.coins:
                coin.display(update=False)

            if self.display_speed_bar:
                self.speed_bar()
            #DISPLAY ALL THE GAME STUFF BUT DONOT UPDATE THEM
            #tint(255,100)
            fill(0,100)
            rect(0,0,SCRN_WIDTH,SCRN_HEIGHT)
            tint(255,255)

            # PAUSE THE SOUND OF WALKING OR RUNNING WHEN THE SCREEN IS PAUSED
            self.catto.sound_movement.pause()
            self.catto.sound_movement.rewind()


            self.pausedSettingsMenu.display()

        elif self.mode == 'pausedControlMenu':
            #DISPLAY ALL THE GAME STUFF BUT DONOT UPDATE THEM

            for i,bg in enumerate(self.bgs):
                x = int((2*self.gameX) // (len(self.bgs)-i+1))
                image(bg,0-(x%self.w),0)

                image(bg,self.w-(x%self.w),0,(x%self.w),self.h,0,0,(x%self.w),self.h)

            stroke(0,255,0)
            line(0,self.gnd-game.gameY,self.w,self.gnd-game.gameY)
            noStroke()

            # DISPLAY LIVES:
            for i in range(self.catto.totalLives):
                fill(100,0,0)
                #ellipseMode(CORNER)
                circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
            for i in range(self.catto.lives):
                fill(230,0,0)
                #ellipseMode(CORNER)
                circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
            # DISPLAY STAMINA:
            fill("#616161")
            rect(STATS_POSX,STATS_POSY+15,100,5,5)
            fill("#ffffff")
            rect(STATS_POSX,STATS_POSY+15,self.catto.stamina,5,5)

            self.catto.display(update=False)

            for platform in self.platforms:
                platform.display(update=False)

            for coin in self.coins:
                coin.display(update=False)

            if self.display_speed_bar:
                self.speed_bar()
            #DISPLAY ALL THE GAME STUFF BUT DONOT UPDATE THEM
            #tint(255,100)
            fill(0,100)
            rect(0,0,SCRN_WIDTH,SCRN_HEIGHT)
            tint(255,255)
            self.pausedControlMenu.display()

        elif self.mode == 'confirmationMessage':
            #DISPLAY ALL THE GAME STUFF BUT DONOT UPDATE THEM

            for i,bg in enumerate(self.bgs):
                x = int((2*self.gameX) // (len(self.bgs)-i+1))
                image(bg,0-(x%self.w),0)

                image(bg,self.w-(x%self.w),0,(x%self.w),self.h,0,0,(x%self.w),self.h)

            stroke(0,255,0)
            line(0,self.gnd-game.gameY,self.w,self.gnd-game.gameY)
            noStroke()

            # DISPLAY LIVES:
            for i in range(self.catto.totalLives):
                fill(100,0,0)
                #ellipseMode(CORNER)
                circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
            for i in range(self.catto.lives):
                fill(230,0,0)
                #ellipseMode(CORNER)
                circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
            # DISPLAY STAMINA:
            fill("#616161")
            rect(STATS_POSX,STATS_POSY+15,100,5,5)
            fill("#ffffff")
            rect(STATS_POSX,STATS_POSY+15,self.catto.stamina,5,5)

            self.catto.display(update=False)

            for platform in self.platforms:
                platform.display(update=False)

            for coin in self.coins:
                coin.display(update=False)

            if self.display_speed_bar:
                self.speed_bar()
            #DISPLAY ALL THE GAME STUFF BUT DONOT UPDATE THEM
            #tint(255,100)
            fill(0,100)
            rect(0,0,SCRN_WIDTH,SCRN_HEIGHT)
            tint(255,255)
            self.confirmationMessage.display()

        elif self.mode == 'confirmationMessageMainMenu':
            #DISPLAY ALL THE GAME STUFF BUT DONOT UPDATE THEM

            for i,bg in enumerate(self.bgs):
                x = int((2*self.gameX) // (len(self.bgs)-i+1))
                image(bg,0-(x%self.w),0)

                image(bg,self.w-(x%self.w),0,(x%self.w),self.h,0,0,(x%self.w),self.h)

            stroke(0,255,0)
            line(0,self.gnd-game.gameY,self.w,self.gnd-game.gameY)
            noStroke()

            # DISPLAY LIVES:
            for i in range(self.catto.totalLives):
                fill(100,0,0)
                #ellipseMode(CORNER)
                circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
            for i in range(self.catto.lives):
                fill(230,0,0)
                #ellipseMode(CORNER)
                circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
            # DISPLAY STAMINA:
            fill("#616161")
            rect(STATS_POSX,STATS_POSY+15,100,5,5)
            fill("#ffffff")
            rect(STATS_POSX,STATS_POSY+15,self.catto.stamina,5,5)


            self.catto.display(update=False)

            for platform in self.platforms:
                platform.display(update=False)

            for coin in self.coins:
                coin.display(update=False)

            if self.display_speed_bar:
                self.speed_bar()
            #DISPLAY ALL THE GAME STUFF BUT DONOT UPDATE THEM
            #tint(255,100)
            fill(0,100)
            rect(0,0,SCRN_WIDTH,SCRN_HEIGHT)
            tint(255,255)
            self.confirmationMessageMainMenu.display()

        elif self.mode == 'controls':
            self.controlMenu.display()

        elif self.mode == 'credits':
            self.creditsMenu.display()

        elif self.mode=='game':

            # IF DT IS TOO MUCH THEN STOP THE GAME IF RUNNING
            if self.dt>GAME_LAG_THRESHHOLD:
                for i,bg in enumerate(self.bgs):
                    x = int((2*self.gameX) // (len(self.bgs)-i+1))
                    image(bg,0-(x%self.w),0)

                    image(bg,self.w-(x%self.w),0,(x%self.w),self.h,0,0,(x%self.w),self.h)

                stroke(0,255,0)
                line(0,self.gnd-game.gameY,self.w,self.gnd-game.gameY)
                noStroke()

                # DISPLAY LIVES:
                for i in range(self.catto.totalLives):
                    fill(100,0,0)
                    #ellipseMode(CORNER)
                    circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
                for i in range(self.catto.lives):
                    fill(230,0,0)
                    #ellipseMode(CORNER)
                    circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
                # DISPLAY STAMINA:
                fill("#616161")
                rect(STATS_POSX,STATS_POSY+15,100,5,5)
                fill("#ffffff")
                rect(STATS_POSX,STATS_POSY+15,self.catto.stamina,5,5)

                self.catto.display(update=False)

                for platform in self.platforms:
                    platform.display(update=False)

                if self.display_speed_bar:
                    self.speed_bar()
                #DISPLAY ALL THE GAME STUFF BUT DONOT UPDATE THEM
                #tint(255,100)
                fill(0,100)
                rect(0,0,SCRN_WIDTH,SCRN_HEIGHT)
                tint(255,255)
                textAlign(CENTER)
                text("( LOADING )",SCRN_WIDTH//2,SCRN_HEIGHT//2)

            else:

                # LOAD REPEATING BACKGROUND TILL A CERTAIN POSITION
                for i,bg in enumerate(self.bgs[:]):

                    x = int((2*self.gameX) // (len(self.bgs)-i+1))

                    if self.catto.posX<self.constant_bg_posX-800-1280:
                        image(bg,0-(x%bg.width),0)
                        image(bg,bg.width-(x%bg.width),0,(x%bg.width),bg.height,0,0,(x%bg.width),bg.height)
                    else:
                        if i==2:
                            image(bg,0-(x-int(2*7*bg.width)//(len(self.bgs)-2+1))-1280,0)
                            image(self.constant_bg,0-(x-int(2*7*bg.width)//(len(self.bgs)-2+1))+1480,0)

                        elif i==3:
                            image(bg,0-(x-int(2*14*bg.width)//(len(self.bgs)-3+1))+850-0*640,0)
                            image(bg,0-(x-int(2*14*bg.width)//(len(self.bgs)-3+1))+850-1280,0)
                        else:
                            image(bg,0-(x%bg.width),0)
                    if (i!=2 and i!=3):
                        image(bg,bg.width-(x%bg.width),0,(x%bg.width),bg.height,0,0,(x%bg.width),bg.height)

                # NON REPEATING BACKGROUNDS
                i=0
                x = int((1*self.gameX) // (len(self.bgs)-i+1))
                image(self.constant_bg,0-(x-int(1*7*bg.width)//(len(self.bgs)-i+1))-6000,0)


                # DISPLAY LIVES:
                for i in range(self.catto.totalLives):
                    fill(100,0,0)
                    #ellipseMode(CORNER)
                    circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
                for i in range(self.catto.lives):
                    fill(230,0,0)
                    #ellipseMode(CORNER)
                    circle(STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
                # DISPLAY STAMINA:
                fill("#616161")
                rect(STATS_POSX,STATS_POSY+15,100,5,5)
                fill("#ffffff")
                rect(STATS_POSX,STATS_POSY+15,self.catto.stamina,5,5)

                if self.safePointsIndex==len(self.safePointsList)-2:
                    game.fatslob.active = True
                    # DISPLAY FATSLOB LIVES:
                    for i in range(self.fatslob.totalLives):
                        fill("#874d1e")
                        #ellipseMode(CORNER)
                        circle(SCRN_WIDTH-100-STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,30+STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)
                    for i in range(self.fatslob.lives):
                        fill("#D87C30")
                        #ellipseMode(CORNER)
                        circle(SCRN_WIDTH-100-STATS_POSX+i*(100+2)/9+((100+2)/9-2)/2,30+STATS_POSY+((100+2)/9-2)/2,(100+2)/9-2)

                fill("#eeeeee")
                textSize(20)
                textAlign(RIGHT)
                text("SCORE "+str(self.score),SCRN_WIDTH-STATS_POSX,STATS_POSY)
                textAlign(LEFT)

                self.catto.display()

                imageMode(CENTER)
                for checkpointX in self.checkPointsList:

                    image(self.checkpoint_img,checkpointX-self.gameX+75,GND-80,150,150)
                imageMode(CORNER)

                for info in self.infos:
                    info.display_img()

                for enemy in self.enemies:
                    enemy.display()

                for platform in self.platforms:
                    platform.display()

                for obstacle in self.obstacles:
                    obstacle.displayBG()

                self.catto.display(update=False)

                for obstacle in self.obstacles:
                    obstacle.display()

                for coin in self.coins:
                    coin.display()
                for food in self.foods:
                    food.display()
                for stamina in self.staminas:
                    stamina.display()


                for info in self.infos:
                    info.display()


                if self.display_speed_bar:
                    self.speed_bar()

                # DISPLAY CHEATCODE ACTIVATED TEXT WHEN CHEATCODE IS TYPED
                if self.cheatCodeTimer>0:
                    fill(0,150)
                    noStroke()
                    textSize(20)
                    rect(SCRN_WIDTH-STATS_POSX-textWidth("CHEATCODE ACTIVATED")-10,STATS_POSY+30,textWidth("CHEATCODE ACTIVATED")+20,40+10,10)
                    fill(255)
                    textAlign(RIGHT)
                    text("CHEATCODE ACTIVATED",SCRN_WIDTH-STATS_POSX,STATS_POSY+60)
                    self.cheatCodeTimer -= self.dt


        elif self.mode == 'gameover':
            self.gameover.display(win=self.win,highscore=self.highscore)

        elif self.mode == 'highscore':
            self.highscoreMenu.display()

        elif self.mode == 'highscoreCredits':
            self.highscoreCredits.display()





game =Game()
game.set_volume()


# IMPORTANT CODE FOR DEBUGGING, SET P TO THE INDEX OF THE CHECKPOINT YOU WANT TO JUMP TO
# p=6
# game.catto.posX=game.safePointsList[p]
# game.gameX = game.catto.posX - game.w//2
# game.safePointsIndex=p


def draw():
    game.display()
    game.mouseMotion = False
    game.mouseClick = False

# CONSTANT TO NOT ESCAPE THE ESCAPE FUNCTION THAT CLOSES THE GAME WHEN PRESSED
NO_ESCAPE = '0'


def mouseMoved():
    game.mouseMotion = True

def mouseClicked():
    game.mouseClick = True
    if mouseButton == LEFT:
        if game.mode == 'menu':
            if game.menu.updateOptionByMouse():
                game.menu.select = game.menu.choice
                if game.menu.select == 0:
                    game.mode='game'
                elif game.menu.select == 1:
                    game.mode='controls'
                elif game.menu.select == 2:
                    game.mode='settings'
                elif game.menu.select == 3:
                    game.creditsMenu.set_start()
                    game.mode='credits'
                elif game.menu.select == 4:
                    game.mode='confirmationMessageMenu'
        elif game.mode == 'pause':
            if game.pauseMenu.updateOptionByMouse():
                game.pauseMenu.select = game.pauseMenu.choice
                if game.pauseMenu.select == 0:

                    # UNPAUSE
                    # RESUME BGM
                    if game.sound_intro_flag == 'start':
                        game.sound_intro_start.play()
                    elif game.sound_intro_flag == 'loop':
                        game.sound_intro_loop.play()
                    game.sound_intro_flag = "non-pause"


                    game.mode='game'
                elif game.pauseMenu.select == 1:
                    game.mode='settings'
                elif game.pauseMenu.select == 2:
                    game.mode='pausedControlMenu'
                elif game.pauseMenu.select == 3:
                    game.mode='confirmationMessageMainMenu'
                elif game.pauseMenu.select == 4:
                    game.mode='confirmationMessage'

        elif game.mode == 'confirmationMessage':
            if game.confirmationMessage.updateOptionByMouse():
                game.confirmationMessage.select = game.confirmationMessage.choice
                if game.confirmationMessage.select == 0:
                    exit()
                elif game.confirmationMessage.select == 1:
                    game.mode='pause'
        elif game.mode == 'confirmationMessageMenu':
            if game.confirmationMessage.updateOptionByMouse():
                game.confirmationMessage.select = game.confirmationMessage.choice
                if game.confirmationMessage.select == 0:
                    exit()
                elif game.confirmationMessage.select == 1:
                    game.mode='menu'

        elif game.mode=='controls':
            game.mode='menu'
        elif game.mode=='credits':
            game.mode='menu'
        elif game.mode=='pausedControlMenu':
            game.mode='pause'
        elif game.mode == 'confirmationMessageMainMenu':
            if game.confirmationMessageMainMenu.updateOptionByMouse():
                game.confirmationMessageMainMenu.select = game.confirmationMessageMainMenu.choice
                if game.confirmationMessageMainMenu.select == 0:
                    if game.sound_intro_loop.isPlaying():
                        game.sound_intro_loop.pause()
                        game.sound_intro_loop.rewind()
                    elif game.sound_intro_start.isPlaying():
                        game.sound_intro_start.pause()
                        game.sound_intro_start.rewind()
                    elif game.sound_boss_music.isPlaying():
                        game.sound_boss_music.pause()

                    for enemy in self.enemies:
                        if enemy.type=='doggo' and enemy.bark.isPlaying():
                            enemy.bark.pause()



                    game.__init__()


                    game.mode='menu'
                elif game.confirmationMessageMainMenu.select == 1:
                    game.mode='pause'

# FUNCTION TO RETURN THE TIMESTAMP FOR STORING SCORES
def date():
    yyyy=year()
    yyyy=str(yyyy)
    mm=month()
    if mm<10:
        mm="0"+str(mm)
    else:
        mm=str(mm)
    dd=day()
    if dd<10:
        dd="0"+str(dd)
    else:
        dd=str(dd)

    hh=hour()
    if hh<10:
        hh="0"+str(hh)
    else:
        hh=str(hh)
    mn=minute()
    if mn<10:
        mn="0"+str(mn)
    else:
        mn=str(mn)

    ss=second()
    if ss<10:
        ss="0"+str(ss)
    else:
        ss=str(ss)

    return yyyy+mm+dd+hh+mn+ss

def keyPressed():
    if key == ESC: # ESC
        if game.mode=='game':
            game.catto.keyHandler[LEFT] = False
            game.catto.keyHandler[RIGHT] = False
            game.catto.keyHandler[UP] = False
            game.catto.keyHandler[DOWN] = False

            # PAUSE THE SOUND WHILE PAUSED
            if game.sound_intro_start.isPlaying():
                game.sound_intro_flag = "start"
                game.sound_intro_start.pause()
            else:
                game.sound_intro_flag = "loop"
                game.sound_intro_loop.pause()

            for enemy in game.enemies:
                if enemy.type=='doggo':
                    enemy.pause_sound()

            game.mode='pause'
        elif game.mode=='pause':

            # RESUME BGM
            if game.sound_intro_flag == 'start':
                game.sound_intro_start.play()
            elif game.sound_intro_flag == 'loop':
                game.sound_intro_loop.play()
            game.sound_intro_flag = "non-pause"

            for enemy in game.enemies:
                enemy.pause_sound()

            game.mode='game'

        this.key = NO_ESCAPE

    # print(keyCode)

    if game.mode=='gameover':
        if 48<=keyCode<=57 or 65<=keyCode<=90:
            if len(game.gameover.name_txt)<9:
                game.gameover.name_txt+=chr(keyCode)
        elif keyCode == 8: # BACKSPACE
            if len(game.gameover.name_txt)>0:
                game.gameover.name_txt=game.gameover.name_txt[:-1]
        elif keyCode == 10 and len(game.gameover.name_txt)>0: # ENTER

            score_file = open(PATH+"/Resources/data/scores.csv",'a')
            timestamp = date()
            score_file.write(game.gameover.name_txt+","+str(game.score)+","+timestamp+"\n")
            score_file.close()

            # UPDATE HIGHSCORE:

            ##############################################################################
            # Read scores and determine highscore
            for i,entry in enumerate(game.highscore_list):
                if entry[1]<=game.score:
                    game.highscore_list.insert(i,[game.gameover.name_txt,game.score,int(timestamp)])
                    break
            game.highscore_list = game.highscore_list[:10]

            ##############################################################################

            game.gameover.name_txt=""

            game.mode = 'highscore'

            # SAVE NAME, SCORE


    elif game.mode == 'menu':
        if keyCode == UP and not game.menu.updateOptionByMouse():
            game.menu.choice -=1
            game.menu.choice = game.menu.choice%len(game.menu.options)

            if not game.menu.sound_menu_hover.isPlaying():
                game.menu.sound_menu_hover.rewind()
                game.menu.sound_menu_hover.play()
        if keyCode == DOWN and not game.menu.updateOptionByMouse():
            game.menu.choice +=1
            game.menu.choice = game.menu.choice%len(game.menu.options)

            if not game.menu.sound_menu_hover.isPlaying():
                game.menu.sound_menu_hover.rewind()
                game.menu.sound_menu_hover.play()
        if keyCode==10:
            game.menu.select = game.menu.choice
            if game.menu.select == 0:
                if game.sound_intro_start.isPlaying():
                    game.sound_intro_start.pause()
                    game.sound_intro_start.rewind()
                elif game.sound_intro_loop.isPlaying():
                    game.sound_intro_loop.pause()
                    game.sound_intro_loop.rewind()

                game.sound_intro_start.play()

                game.mode='game'
            elif game.menu.select == 1:
                game.mode='controls'
            elif game.menu.select == 2:
                game.mode='settings'
            elif game.menu.select == 3:
                game.creditsMenu.set_start()
                game.mode='credits'
            elif game.menu.select == 4:
                game.mode='confirmationMessageMenu'


    elif game.mode == 'settings':
        if keyCode == UP and not game.settingsMenu.updateOptionByMouse():
            game.settingsMenu.choice -=1
            game.settingsMenu.choice = game.settingsMenu.choice%len(game.settingsMenu.options)

            if not game.settingsMenu.sound_menu_hover.isPlaying():
                game.settingsMenu.sound_menu_hover.rewind()
                game.settingsMenu.sound_menu_hover.play()
        elif keyCode == DOWN and not game.settingsMenu.updateOptionByMouse():
            game.settingsMenu.choice +=1
            game.settingsMenu.choice = game.settingsMenu.choice%len(game.settingsMenu.options)

            if not game.settingsMenu.sound_menu_hover.isPlaying():
                game.settingsMenu.sound_menu_hover.rewind()
                game.settingsMenu.sound_menu_hover.play()
        elif keyCode==LEFT:


            game.settingsMenu.select = game.settingsMenu.choice

            if game.settingsMenu.select == 0:
                vol_option=game.settingsMenu.updateOptionText(0,-1)
                vol_option=game.pausedSettingsMenu.updateOptionText(0,-1)
                game.music_volume=VOLUME_DICT[vol_option]
            elif game.settingsMenu.select == 1:
                vol_option=game.settingsMenu.updateOptionText(1,-1)
                vol_option=game.pausedSettingsMenu.updateOptionText(1,-1)
                game.sfx_volume=VOLUME_DICT[vol_option]

            game.set_volume()

            if not game.settingsMenu.sound_menu_hover.isPlaying():
                game.settingsMenu.sound_menu_hover.rewind()
                game.settingsMenu.sound_menu_hover.play()

        elif keyCode==RIGHT:
            game.settingsMenu.select = game.settingsMenu.choice

            if game.settingsMenu.select == 0:
                vol_option=game.settingsMenu.updateOptionText(0,+1)
                vol_option=game.pausedSettingsMenu.updateOptionText(0,+1)
                game.music_volume=VOLUME_DICT[vol_option]
            elif game.settingsMenu.select == 1:
                vol_option=game.settingsMenu.updateOptionText(1,+1)
                vol_option=game.pausedSettingsMenu.updateOptionText(1,+1)
                game.sfx_volume=VOLUME_DICT[vol_option]

            game.set_volume()

            if not game.settingsMenu.sound_menu_hover.isPlaying():
                game.settingsMenu.sound_menu_hover.rewind()
                game.settingsMenu.sound_menu_hover.play()

        if keyCode == 27 or keyCode == 10:
            game.mode='menu'

    elif game.mode == 'pausedSettingsMenu' :
        if keyCode == UP and not game.pausedSettingsMenu.updateOptionByMouse():
            game.pausedSettingsMenu.choice -=1
            game.pausedSettingsMenu.choice = game.pausedSettingsMenu.choice%len(game.pausedSettingsMenu.options)

            if not game.pausedSettingsMenu.sound_menu_hover.isPlaying():
                game.pausedSettingsMenu.sound_menu_hover.rewind()
                game.pausedSettingsMenu.sound_menu_hover.play()
        elif keyCode == DOWN and not game.pausedSettingsMenu.updateOptionByMouse():
            game.pausedSettingsMenu.choice +=1
            game.pausedSettingsMenu.choice = game.pausedSettingsMenu.choice%len(game.pausedSettingsMenu.options)

            if not game.pausedSettingsMenu.sound_menu_hover.isPlaying():
                game.pausedSettingsMenu.sound_menu_hover.rewind()
                game.pausedSettingsMenu.sound_menu_hover.play()
        elif keyCode==LEFT:


            game.pausedSettingsMenu.select = game.pausedSettingsMenu.choice

            if game.pausedSettingsMenu.select == 0:
                vol_option=game.pausedSettingsMenu.updateOptionText(0,-1)
                vol_option=game.settingsMenu.updateOptionText(0,-1)
                game.music_volume=VOLUME_DICT[vol_option]
            elif game.pausedSettingsMenu.select == 1:
                vol_option=game.pausedSettingsMenu.updateOptionText(1,-1)
                vol_option=game.settingsMenu.updateOptionText(1,-1)
                game.sfx_volume=VOLUME_DICT[vol_option]

            game.set_volume()

            if not game.pausedSettingsMenu.sound_menu_hover.isPlaying():
                game.pausedSettingsMenu.sound_menu_hover.rewind()
                game.pausedSettingsMenu.sound_menu_hover.play()

        elif keyCode==RIGHT:
            game.pausedSettingsMenu.select = game.pausedSettingsMenu.choice

            if game.pausedSettingsMenu.select == 0:
                vol_option=game.pausedSettingsMenu.updateOptionText(0,+1)
                vol_option=game.settingsMenu.updateOptionText(0,+1)
                game.music_volume=VOLUME_DICT[vol_option]
            elif game.pausedSettingsMenu.select == 1:
                vol_option=game.pausedSettingsMenu.updateOptionText(1,+1)
                vol_option=game.settingsMenu.updateOptionText(1,+1)
                game.sfx_volume=VOLUME_DICT[vol_option]

            game.set_volume()

            if not game.pausedSettingsMenu.sound_menu_hover.isPlaying():
                game.pausedSettingsMenu.sound_menu_hover.rewind()
                game.pausedSettingsMenu.sound_menu_hover.play()

        if keyCode == 27 or keyCode == 10: # ESC OR ENTER
            game.mode='pause'

    elif game.mode == 'pause':
        if keyCode == UP and not game.pauseMenu.updateOptionByMouse():
            game.pauseMenu.choice -=1
            game.pauseMenu.choice = game.pauseMenu.choice%len(game.pauseMenu.options)

            if not game.pauseMenu.sound_menu_hover.isPlaying():
                game.pauseMenu.sound_menu_hover.rewind()
                game.pauseMenu.sound_menu_hover.play()
        if keyCode == DOWN and not game.pauseMenu.updateOptionByMouse():
            game.pauseMenu.choice +=1
            game.pauseMenu.choice = game.pauseMenu.choice%len(game.pauseMenu.options)

            if not game.pauseMenu.sound_menu_hover.isPlaying():
                game.pauseMenu.sound_menu_hover.rewind()
                game.pauseMenu.sound_menu_hover.play()
        if keyCode==10:
            game.pauseMenu.select = game.pauseMenu.choice
            if game.pauseMenu.select == 0:



                # UNPAUSE
                # RESUME BGM
                if game.sound_intro_flag == 'start':
                    game.sound_intro_start.play()
                elif game.sound_intro_flag == 'loop':
                    game.sound_intro_loop.play()
                game.sound_intro_flag = "non-pause"

                game.mode='game'
            elif game.pauseMenu.select == 1:
                game.mode='pausedSettingsMenu'
            elif game.pauseMenu.select == 2:
                game.mode='pausedControlMenu'
            elif game.pauseMenu.select == 3:
                game.mode='confirmationMessageMainMenu'
            elif game.pauseMenu.select == 4:
                game.mode='confirmationMessage'



    elif game.mode == 'pausedControlMenu':
        if keyCode == 27 or keyCode == 10:
            game.mode='pause'

    elif game.mode == 'highscore':
        if keyCode == 27 or keyCode == 10:
            game.creditsMenu.set_start()
            game.mode='highscoreCredits'



    elif game.mode == 'confirmationMessageMainMenu':
        if keyCode == UP and not game.confirmationMessageMainMenu.updateOptionByMouse():
            game.confirmationMessageMainMenu.choice -=1
            game.confirmationMessageMainMenu.choice = game.confirmationMessageMainMenu.choice%len(game.confirmationMessageMainMenu.options)

            if not game.confirmationMessageMainMenu.sound_menu_hover.isPlaying():
                game.confirmationMessageMainMenu.sound_menu_hover.rewind()
                game.confirmationMessageMainMenu.sound_menu_hover.play()
        if keyCode == DOWN and not game.confirmationMessageMainMenu.updateOptionByMouse():
            game.confirmationMessageMainMenu.choice +=1
            game.confirmationMessageMainMenu.choice = game.confirmationMessageMainMenu.choice%len(game.confirmationMessageMainMenu.options)

            if not game.confirmationMessageMainMenu.sound_menu_hover.isPlaying():
                game.confirmationMessageMainMenu.sound_menu_hover.rewind()
                game.confirmationMessageMainMenu.sound_menu_hover.play()
        if keyCode==10:
            game.confirmationMessageMainMenu.select = game.confirmationMessageMainMenu.choice
            if game.confirmationMessageMainMenu.select == 0:
                if game.sound_intro_loop.isPlaying():
                    game.sound_intro_loop.pause()
                    game.sound_intro_loop.rewind()
                elif game.sound_intro_start.isPlaying():
                    game.sound_intro_start.pause()
                    game.sound_intro_start.rewind()
                elif game.sound_boss_music.isPlaying():
                    game.sound_boss_music.pause()

                # MAKING SURE WHEN THE GAME RE INITIATES, THE CHANGES MAADE IN THE SETTINGS (VOLUME) STAY CHANGED
                game_music_vol = game.music_volume # PREV VOLUMES
                game_sfx_vol = game.sfx_volume


                game.__init__() # NEW GAME

                music_vol_change =  VOLUME_DICT.index(game_music_vol) - VOLUME_DICT.index(game.music_volume) # CHANGE OF DEFAULT VOLUME VS PREV VOLUME
                sfx_vol_change =  VOLUME_DICT.index(game_sfx_vol) - VOLUME_DICT.index(game.sfx_volume)

                game.music_volume = game_music_vol # SET GAME VOLUME TO PREV VOLUME
                game.sfx_volume = game_sfx_vol
                game.set_volume()

                game.settingsMenu.updateOptionText(0,music_vol_change) # GOOD, NOW UPDATE THE TEXTS OF THE TWO SETTINGS MENU TO NOT HAVE THE DEFAULT TEXTS, RATHER TO HAVE THE PREV VOL TEXTS
                game.settingsMenu.updateOptionText(1,sfx_vol_change)
                game.pausedSettingsMenu.updateOptionText(0,music_vol_change)
                game.pausedSettingsMenu.updateOptionText(1,sfx_vol_change)

                game.mode='menu'
            elif game.confirmationMessageMainMenu.select == 1:
                game.confirmationMessageMainMenu.choice=1
                game.mode='pause'
        if keyCode == 27:
            game.confirmationMessageMainMenu.choice=1
            game.mode='pause'

    elif game.mode == 'confirmationMessage':
        if keyCode == UP and not game.confirmationMessage.updateOptionByMouse():
            game.confirmationMessage.choice -=1
            game.confirmationMessage.choice = game.confirmationMessage.choice%len(game.confirmationMessage.options)

            if not game.confirmationMessage.sound_menu_hover.isPlaying():
                game.confirmationMessage.sound_menu_hover.rewind()
                game.confirmationMessage.sound_menu_hover.play()
        if keyCode == DOWN and not game.confirmationMessage.updateOptionByMouse():
            game.confirmationMessage.choice +=1
            game.confirmationMessage.choice = game.confirmationMessage.choice%len(game.confirmationMessage.options)

            if not game.confirmationMessage.sound_menu_hover.isPlaying():
                game.confirmationMessage.sound_menu_hover.rewind()
                game.confirmationMessage.sound_menu_hover.play()
        if keyCode==10:
            game.confirmationMessage.select = game.confirmationMessage.choice
            if game.confirmationMessage.select == 0:
                exit()
            elif game.confirmationMessage.select == 1:
                game.confirmationMessage.choice=1
                game.mode='pause'
        if keyCode == 27:
            game.confirmationMessage.choice=1
            game.mode='pause'
    elif game.mode == 'confirmationMessageMenu':
        if keyCode == UP and not game.confirmationMessageMenu.updateOptionByMouse():
            game.confirmationMessageMenu.choice -=1
            game.confirmationMessageMenu.choice = game.confirmationMessageMenu.choice%len(game.confirmationMessageMenu.options)

            if not game.confirmationMessageMenu.sound_menu_hover.isPlaying():
                game.confirmationMessageMenu.sound_menu_hover.rewind()
                game.confirmationMessageMenu.sound_menu_hover.play()
        if keyCode == DOWN and not game.confirmationMessageMenu.updateOptionByMouse():
            game.confirmationMessageMenu.choice +=1
            game.confirmationMessageMenu.choice = game.confirmationMessageMenu.choice%len(game.confirmationMessageMenu.options)

            if not game.confirmationMessageMenu.sound_menu_hover.isPlaying():
                game.confirmationMessageMenu.sound_menu_hover.rewind()
                game.confirmationMessageMenu.sound_menu_hover.play()
        if keyCode==10:
            game.confirmationMessageMenu.select = game.confirmationMessageMenu.choice
            if game.confirmationMessageMenu.select == 0:
                exit()
            elif game.confirmationMessageMenu.select == 1:
                game.confirmationMessageMenu.choice=1
                game.mode='menu'
        if keyCode == 27:
            game.confirmationMessageMenu.choice=1
            game.mode='menu'


    elif game.mode=='controls':
        if keyCode == 27 or keyCode == 10:
            game.mode='menu'

    elif game.mode=='credits':
        if keyCode == 27 or keyCode == 10 :
            game.mode='menu'
    elif game.mode=='highscoreCredits':
        if keyCode == 27 or keyCode == 10 :
            if game.sound_game_over.isPlaying():
                game.sound_game_over.pause()

            elif game.sound_win_start.isPlaying():
                game.sound_win_start.pause()
            elif game.sound_win_loop.isPlaying():
                game.sound_win_loop.pause()

            # MAKING SURE WHEN THE GAME RE INITIATES, THE CHANGES MAADE IN THE SETTINGS (VOLUME) STAY CHANGED
            game_music_vol = game.music_volume # PREV VOLUMES
            game_sfx_vol = game.sfx_volume


            game.__init__() # NEW GAME


            music_vol_change =  VOLUME_DICT.index(game_music_vol) - VOLUME_DICT.index(game.music_volume) # CHANGE OF DEFAULT VOLUME VS PREV VOLUME
            sfx_vol_change =  VOLUME_DICT.index(game_sfx_vol) - VOLUME_DICT.index(game.sfx_volume)

            game.music_volume = game_music_vol # SET GAME VOLUME TO PREV VOLUME
            game.sfx_volume = game_sfx_vol
            game.set_volume()

            game.settingsMenu.updateOptionText(0,music_vol_change) # GOOD, NOW UPDATE THE TEXTS OF THE TWO SETTINGS MENU TO NOT HAVE THE DEFAULT TEXTS, RATHER TO HAVE THE PREV VOL TEXTS
            game.settingsMenu.updateOptionText(1,sfx_vol_change)
            game.pausedSettingsMenu.updateOptionText(0,music_vol_change)
            game.pausedSettingsMenu.updateOptionText(1,sfx_vol_change)

            game.mode='menu'



    elif game.mode=='game':
        if keyCode == 10:
            game.catto.keyHandler[LEFT] = False
            game.catto.keyHandler[RIGHT] = False
            game.catto.keyHandler[UP] = False
            game.catto.keyHandler[DOWN] = False

            # PAUSE THE SOUND WHILE PAUSED
            if game.sound_intro_start.isPlaying():
                game.sound_intro_flag = "start"
                game.sound_intro_start.pause()
            else:
                game.sound_intro_flag = "loop"
                game.sound_intro_loop.pause()

            for enemy in game.enemies:
                if enemy.type=='doggo':
                    enemy.pause_sound()

            game.mode='pause'
        if keyCode==32: # IF SPACE BAR IS PRESSED
            if game.catto.touchingPlatform:
                game.catto.aX=0.01*game.dt/float(30)
                game.display_speed_bar = True
            else:
                game.catto.aX=0
                game.display_speed_bar = False



        if keyCode==77: # IF M IS PRESSED
            if not game.catto.respawning and not game.catto.sound_mew.isPlaying():
                game.catto.sound_mew=game.catto.sound_mew_list[random.randint(0,len(game.catto.sound_mew_list)-1)]
                game.catto.sound_mew.rewind()
                game.catto.sound_mew.play()

        if keyCode==88: # IF 'X' IS PRESSED
            if not game.catto.attackKeyPressed:
                game.catto.keyHandler['X']=True
                game.catto.attack=True
                game.catto.f = 8
                game.catto.attackKeyPressed = True

                if not game.catto.respawning:
                    game.catto.sound_claw.rewind()
                    game.catto.sound_claw.play()
            else:
                game.catto.keyHandler['X']=False

        if keyCode==LEFT:
            game.catto.keyHandler[LEFT]=True
        if keyCode==RIGHT:
            game.catto.keyHandler[RIGHT]=True
        if keyCode==UP:
            game.catto.keyHandler[UP]=True
        if keyCode==DOWN:
            game.catto.keyHandler[DOWN]=True

        # CHEAT CODES
        if 48<=keyCode<=57 or 65<=keyCode<=90:
            if len(game.cheatCode)<CHEAT_CODE_MAX_LEN:
                game.cheatCode+=chr(keyCode)
            else:
                game.cheatCode+=chr(keyCode)
                game.cheatCode=game.cheatCode[1:]
            if CHEAT_CODES.get(game.cheatCode,-1)== 'HEALTH':
                game.catto.lives=9
                game.cheatCode=""
                game.cheatCodeTimer = 1000
            if CHEAT_CODES.get(game.cheatCode,-1) == 'STAMINA':
                game.catto.stamina=100
                game.cheatCode=""
                game.cheatCodeTimer = 1000
            if CHEAT_CODES.get(game.cheatCode,-1) == 'STAGE CLEAR':
                if game.safePointsIndex+2 < len(game.safePointsList):
                    game.catto.posX=game.safePointsList[game.safePointsIndex+1]
                    game.gameX = game.catto.posX - game.w//2

                    game.safePointsIndex+=1
                    game.cheatCode=""
                    game.cheatCodeTimer = 1000

def keyReleased():


    if game.mode == 'game':
        if keyCode==32: # IF SPACEBAR IS RELEASED
            game.catto.aX=0
            game.display_speed_bar = False



        if keyCode==88:
            game.catto.keyHandler['X']=False
            game.catto.attackKeyPressed = False

        if keyCode==LEFT:
            game.catto.keyHandler[LEFT]=False
        if keyCode==RIGHT:
            game.catto.keyHandler[RIGHT]=False
        if keyCode==UP:
            game.catto.keyHandler[UP]=False
        if keyCode==DOWN:
            game.catto.keyHandler[DOWN]=False
