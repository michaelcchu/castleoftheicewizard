# sprite classes for platform game

import pygame as pg
import math
from settings import *

class SpriteFunctions(pg.sprite.Sprite):
    def __init__(self):
        '''initializes sprite'''
        pass
    
    def move(self, x, y, dx=0, dy=0):
        '''moves sprite'''
        # change xy position
        x = x + dx
        y = y + dy
        return x,y

    def fall_check(self,game,width,left,right,top,bottom):
        '''checks if sprite should fall'''
        for block in game.iceWalls: # check if ice is on top of a block
            if block.rect.left - width < left and \
               block.rect.right + width > right and \
               abs(block.rect.top - bottom) <= 0 and block.rect.bottom > top:
                    return True
        return False

    def collide_check(self,sprite,game,direction):
        '''checks if sprite overlaps with a block
        if so, sprite is moved'''
        for wall in game.walls: # check walls
            if sprite.rect.colliderect(wall.rect):
                if direction == "RIGHT":
                    sprite.rect.right = wall.rect.left
                    return wall
                elif direction == "LEFT":
                    sprite.rect.left = wall.rect.right
                    return wall
                elif direction == "UP":
                    sprite.rect.top = wall.rect.bottom
                    return True
                elif direction == "DOWN":
                    sprite.rect.bottom = wall.rect.top
                    return wall

        for ice in game.ice: # check ice blocks
            if sprite.rect.colliderect(ice.rect):
                if sprite != ice:
                    if direction == "RIGHT":
                        sprite.rect.right = ice.rect.left
                        return ice
                    elif direction == "LEFT":
                        sprite.rect.left = ice.rect.right
                        return ice
                    elif direction == "UP":
                        sprite.rect.top = ice.rect.bottom
                        return True 
                    elif direction == "DOWN":
                        sprite.rect.bottom = ice.rect.top
                        return ice

        for fire in game.fire: # check fires
            if sprite.rect.colliderect(fire.rect):
                if direction == "RIGHT":
                    sprite.rect.right = fire.rect.left
                    return fire
                elif direction == "LEFT":
                    sprite.rect.left = fire.rect.right
                    return fire
                elif direction == "UP":
                    sprite.rect.top = fire.rect.bottom
                    return fire 
                elif direction == "DOWN":
                    sprite.rect.bottom = fire.rect.top
                    return fire
        return False
        
class Player(pg.sprite.Sprite):
    def __init__(self,game,x,y):
        '''initializes player sprite'''
        # Add player to all_sprites group
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game # tells python what game player is part of

        # Add Sprite Functions
        self.fgroup = SpriteFunctions()
        
        # Create Player Image
        self.width = TILESIZE - 14
        self.height = TILESIZE - 6
        self.imageRight = pg.image.load('wizard_right.png')
        self.imageLeft = pg.image.load('wizard_left.png')
        self.imageRight = pg.transform.scale\
                          (self.imageRight,(self.width,self.height))
        self.imageLeft = pg.transform.scale\
                          (self.imageLeft,(self.width,self.height))

        self.image = self.imageRight
        
        # Give Player XY Values
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Define Player Attributes
        self.onGround = True
        self.jumping = False
        self.moveWhileJump = True
        self.jumpVel = 0
        self.jumpMovement = 0
        self.fallRate = 2

        # Define Sound Effects
        self.jump_audio = pg.mixer.Sound('jump.wav')
        self.push_audio = pg.mixer.Sound('push.wav')
        self.place_audio = pg.mixer.Sound('place_iceblock.wav')
        self.destroy_audio = pg.mixer.Sound('remove_iceblock.wav')

        for audio in [self.jump_audio,self.place_audio,\
                      self.destroy_audio]:
            audio.set_volume(0.25)

        self.push_audio.set_volume(0.20)
        
    def move(self, direction, dx=0, dy=0):
        '''moves player'''
        # change xy position
        self.rect.x,self.rect.y = self.fgroup.move(self.rect.x,self.rect.y,dx,dy)

        # change direction player image is facing
        if direction == 'RIGHT' or direction == 'LEFT':
            self.image_direction(direction)
            
        check = self.collide_check(direction) # check collisions
        if check == True:   # check if player can jump (is there a block above?)
            self.jumping = False
        if check in self.game.fire:
            self.game.lose = True
            self.game.playing = False

    def image_direction(self,direction):
        '''changes player image'''
        if direction == 'RIGHT':
                self.image = self.imageRight
        else:
                self.image = self.imageLeft
                
    def collide_check(self,direction):
        '''checks if player sprite overlaps with a block
        if so, player is moved'''
        return self.fgroup.collide_check(self,self.game,direction)
        
    def update(self):
        '''updates player'''
        if self.jumping == True: # if player is jumping, continue jumping
            self.jump(firstCall=False)

        self.fall_check() # check if player should fall
        
    def fall_check(self):
        '''checks if player should fall'''
        self.onGround = self.fgroup.fall_check(self.game,self.width,self.rect.left,self.rect.right,self.rect.top,self.rect.bottom)        
                
        # if player is not on top of a block, make player fall
        if self.onGround == False:
            self.move("DOWN",dy=self.fallRate)
            
    def jump(self,firstCall):
        '''makes player jump'''
        if firstCall == True: # if it is the beginning of a jump,
                              # reset variables
            self.jumpVel = -10
            self.jumpMovement = 0
            self.jumping = True
            
            self.jump_audio.play()

        # set a limit to player's jump            
        if self.jumpMovement <= -28: #* TILESIZE:
            self.jumping = False

        # keep track of how much player has moved
        self.jumpMovement = self.jumpMovement + self.jumpVel + self.fallRate
    
        self.move("UP",dy=self.jumpVel) # move the player up        
        self.jumpVel = self.jumpVel * 0.9 # update jumpVel

    def supportCheck(self):
        '''checks if left or right foot is supported'''
        if self.image == self.imageRight: # check left foot
            for block in self.game.iceWalls:
                if block.rect.left <= self.rect.left and \
                   block.rect.right > self.rect.left:
                    if abs(block.rect.top - self.rect.bottom) <= 0 and \
                       block.rect.bottom > self.rect.top:
                        return True
        else:
            for block in self.game.iceWalls: # check right foot
                if block.rect.right >= self.rect.right and \
                   block.rect.left < self.rect.right:
                    if abs(block.rect.top - self.rect.bottom) <= 0 and \
                       block.rect.bottom > self.rect.top:
                        return True
        return False
    
    def iceblock(self):
        '''creates/destroys ice blocks'''
        distance = TILESIZE - self.width

        if self.image == self.imageRight: # where should iceblock be created/destroyed?
            x = math.floor((self.rect.right+distance)/32) * 32
        else:
            x = math.floor((self.rect.left-distance)/32) * 32

        y = self.rect.bottom

        # check if an ice block should be removed
        create = True
        for ice in self.game.ice:
            xList = [] # create list of x values within iceblock
            for num in range(int(ice.width/TILESIZE)): 
                xList.append(ice.rect.x + TILESIZE * num)
                
            for element in xList:
                if element == x and ice.rect.y == y:
                    if self.supportCheck() == True:
                        '''remove ice block'''# but first record its secureness                        
                        create = False

                        # Play Sound
                        self.destroy_audio.play()
                        
                        secureList = []
                        for element in ice.secure:
                            if element != False:
                                secureList = secureList + [True]
                            else:
                                secureList = secureList + [False]
                        
                        if ice.secure[0] != False:
                            for group in ice.secure[0].groups:
                                group.remove(ice.secure[0])
                        if ice.secure[1] != False:
                            for group in ice.secure[1].groups:
                                group.remove(ice.secure[1])
                        for group in ice.groups:
                            group.remove(ice)

                        if len(xList) > 1:
                            # split iceblock into two smaller iceblocks
                            left = 0
                            right = 0
                            for xPosition in xList:
                                if xPosition < x:
                                    left = left + 1
                                elif xPosition > x:
                                    right = right + 1
                            if left > 0:
                                i = Ice(self.game,ice.rect.x,y,left)
                                if secureList[0] != False:
                                    s = Secure(self.game,i,'left')
                                    i.image.blit(s.image,(0,0))
                                    s.rect.x, s.rect.y = i.rect.x, i.rect.y
                            if right > 0:
                                i2 = Ice(self.game,x+TILESIZE,y,right)
                                if secureList[1] != False:
                                    s2 = Secure(self.game,i2,'right')
                                    i2.image.blit(s2.image,(i2.width-s2.width,0))
                                    s2.rect.x, s2.rect.y = i2.rect.right-s2.width, i2.rect.y

        for wall in self.game.walls:
            if wall.rect.x == x and wall.rect.y == y:
                # there is a wall there, don't create ice block
                create = False

        for fire in self.game.fire:
            if fire.rect.x == x and fire.rect.y == y:
                # there is a fire there, don't create ice block
                create = False

        for ice in self.game.ice:
            # do not create ice block if an ice block is falling
            if ice.falling == True:
                create = False
                
        if create == True:
            '''create ice block'''
            # play sound
            self.place_audio.play()
            
            # check for merging
            length = 0
            rightIce = False
            leftIce = False
            wallCheck = True
            rightCheck = True
            leftCheck = True
            
            for ice in self.game.ice:
                if ice.rect.y == y:
                    if ice.rect.left == x+TILESIZE:
                        rightIce = ice
                    elif ice.rect.right == x:
                        leftIce = ice

            if rightIce != False and leftIce == False:
                # merge right
                merge = True
                secureList = []
                for element in rightIce.secure:
                    secureList = secureList + [element]
                if rightIce.secure[1] != False:
                    for group in rightIce.secure[1].groups:
                        group.remove(rightIce.secure[1])
                        
                length = int(rightIce.width/32 + 1)

                # remove the old ice block
                for group in rightIce.groups:
                    group.remove(rightIce)
                    
                # create the merged ice block
                i = Ice(self.game,x,y,length)
                if secureList[1] != False: # add back old secures
                    s = Secure(self.game,i,'right')
                    i.image.blit(s.image,(i.width-s.width,0))
                    s.rect.x, s.rect.y = i.rect.right-s.width, i.rect.y

                rightCheck = False

            elif leftIce != False and rightIce == False:
                # merge left
                merge = True
                secureList = []
                for element in leftIce.secure:
                    secureList = secureList + [element]
                        
                if leftIce.secure[0] != False:
                    for group in leftIce.secure[0].groups:
                        group.remove(leftIce.secure[0])
                        
                length = int(leftIce.width/32 + 1)
                x = leftIce.rect.x

                for group in leftIce.groups:
                    group.remove(leftIce)

                i = Ice(self.game,x,y,length)
                if secureList[0] != False:
                    s = Secure(self.game,i,'left')
                    i.image.blit(s.image,(0,0))
                    s.rect.x, s.rect.y = i.rect.x, i.rect.y

                leftCheck = False

            elif leftIce != False and rightIce != False:
                # merge right and left
                secureList = [leftIce.secure[0],rightIce.secure[1]]
                    
                if leftIce.secure[0] != False:
                    for group in leftIce.secure[0].groups:
                        group.remove(leftIce.secure[0])
                if rightIce.secure[1] != False:
                    for group in rightIce.secure[1].groups:
                        group.remove(rightIce.secure[1])
                        
                length = int(leftIce.width/32 + 1 + rightIce.width/32)
                x = leftIce.rect.x

                for group in leftIce.groups:
                    group.remove(leftIce)

                for group in rightIce.groups:
                    group.remove(rightIce)
                    
                i = Ice(self.game,x,y,length)
                
                if secureList[0] != False:
                    s = Secure(self.game,i,'left')
                    i.image.blit(s.image,(0,0))
                    s.rect.x, s.rect.y = i.rect.x, i.rect.y
                if secureList[1] != False:
                    s2 = Secure(self.game,i,'right')
                    i.image.blit(s2.image,(i.width-s2.width,0))
                    s2.rect.x, s2.rect.y = i.rect.right-s2.width, i.rect.y

                wallCheck = False
                
            else:
                # create an iceblock with length 1 (no merge)
                i = Ice(self.game,x,y,1)

            if wallCheck == True:
                for wall in self.game.walls:
                    if wall.rect.y == i.rect.y:
                        # if connected to a wall, add a secure
                        #(make sure there is not already one there)
                        if rightCheck == True:
                            if wall.rect.left == i.rect.right:
                                if i.secure[1] == False:
                                    s2 = Secure(self.game,i,'right')
                                    i.image.blit(s2.image,(i.width-s2.width,0))
                                    s2.rect.x, s2.rect.y = i.rect.right-s2.width, i.rect.y
                            
                        if leftCheck == True:
                            if wall.rect.right == i.rect.left:
                                if i.secure[0] == False:
                                    s3 = Secure(self.game,i,'left')                        
                                    i.image.blit(s3.image,(0,0))
                                    s3.rect.x, s3.rect.y = i.rect.x, i.rect.y
                        
    def secureCheck(self,i):
        '''checks if iceblock is secure'''
        for block in self.game.iceWalls:
            if block.rect.topright == i.rect.topleft or \
               block.rect.topleft == i.rect.topright:
                return True
        return False

    def push(self):
        '''pushes iceblock'''
        if self.image == self.imageRight:
            for ice in self.game.ice:
                if ice.rect.bottom == self.rect.bottom:
                    if ice.rect.left == self.rect.right:
                        if ice.secure == [False,False]:
                            if ice.width == TILESIZE:
                                ice.push = "RIGHT"
                                self.push_audio.play()
        else:
            for ice in self.game.ice:
                if ice.rect.bottom == self.rect.bottom:
                    if ice.rect.right == self.rect.left:
                        if ice.secure == [False,False]:
                            if ice.width == TILESIZE:
                                ice.push = "LEFT"
                                self.push_audio.play()

class Wall(pg.sprite.Sprite):
    def __init__(self,game,x,y):
        '''initializes Wall sprites'''
        # Add wall to groups
        self.groups = game.all_sprites, game.walls, game.iceWalls
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game

        # Create Wall Image
        self.image = pg.Surface((TILESIZE,TILESIZE))
        self.image.fill(MAGENTA)
        
        # Give Wall XY Values
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE # puts wall on grid
        self.rect.y = y * TILESIZE

class Ice(pg.sprite.Sprite):
    def __init__(self,game,x,y,length):
        '''initializes Ice sprites'''
        # Add ice to groups
        self.groups = game.all_sprites, game.ice, game.iceWalls
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        
        # Create Ice Image
        self.image = pg.image.load('iceblock_'+str(length)+'.png')
        self.image = pg.transform.scale(self.image,\
                            (TILESIZE*length,TILESIZE))
                
        # Give Ice XY Values
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = TILESIZE * length
        self.height = TILESIZE
        self.onGround = True
        self.fallRate = 2
        self.pushRate = 4
        self.secure = [False,False]
        self.fgroup = SpriteFunctions()
        self.push = False
        self.falling = False

        # Sound Effects
        self.fire_audio = pg.mixer.Sound('fire.wav')

        self.fire_audio.set_volume(0.35)

    def update(self):
        '''updates iceblock'''
        if self.secure[0] == False and self.secure[1] == False:
           self.fall_check()
        if self.push == "RIGHT":
            self.move("RIGHT",dx=self.pushRate)
        elif self.push == "LEFT":
            self.move("LEFT",dx=self.pushRate * -1)

    def fall_check(self):
        '''checks if ice should fall'''
        self.onGround = self.fgroup.fall_check(self.game,self.width,self.rect.left,self.rect.right,self.rect.top,self.rect.bottom)
           
        # if ice is not on top of a block, make ice fall
        if self.onGround == False and self.playerCheck() == False:
            self.falling = True
            self.push = False
            self.move("DOWN",dy=self.fallRate)
        else:
            self.falling = False

    def playerCheck(self):
        '''checks if player is under the ice'''
        if self.game.player.rect.left - self.width < self.rect.left and \
           self.game.player.rect.right + self.width > self.rect.right and \
           abs(self.game.player.rect.top - self.rect.bottom) <= 0 and self.game.player.rect.bottom > self.rect.top:
                return True
        return False

    def move(self, direction, dx=0, dy=0):
        '''change xy position'''
        self.rect.x,self.rect.y = self.fgroup.move(self.rect.x,self.rect.y,dx,dy)

        if self.push != False:
            check = self.fgroup.collide_check(self,self.game,self.push) # check collisions
        if self.falling == True:
            check = self.fgroup.collide_check(self,self.game,"DOWN")
            
        if check != False:  
            self.push = False
            
        if check in self.game.fire:
            self.fire_audio.play()
            
            self.game.fires = self.game.fires - 1
            for group in self.groups:
                group.remove(self)
            for group in check.groups:
                group.remove(check)

class Secure(pg.sprite.Sprite):
    def __init__(self,game,iceblock,side):
        self.groups = game.all_sprites, game.secure
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        self.iceblock = iceblock

        if side == 'left':
            iceblock.secure[0] = self
        elif side == 'right':
            iceblock.secure[1] = self

        self.width = 5
        self.height = TILESIZE
        self.image = pg.Surface((self.width,self.height))
        self.image.fill(CYAN)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0

class Fire(pg.sprite.Sprite):
    def __init__(self,game,x,y):
        '''initializes Fire sprites'''
        # Add ice to groups
        self.groups = game.all_sprites, game.fire
        pg.sprite.Sprite.__init__(self,self.groups)
        self.game = game
        
        # Create Ice Image
        self.image = pg.image.load('flame.png')
        self.image = pg.transform.scale(self.image,\
                            (TILESIZE,TILESIZE))

        # Give Ice XY Values
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = TILESIZE
        self.height = TILESIZE
        self.onGround = True
        self.fallRate = 2
        self.fgroup = SpriteFunctions()

    def update(self):
        '''updates fire'''
        self.fall_check()

    def fall_check(self):
        '''checks if fire should fall'''
        self.onGround = self.fgroup.fall_check(self.game,self.width,self.rect.left,self.rect.right,self.rect.top,self.rect.bottom)
           
        # if fire is not on top of a block, make fire fall
        if self.onGround == False:
            self.move("DOWN",dy=self.fallRate)

    def move(self, direction, dx=0, dy=0):
        '''change xy position'''
        self.rect.x,self.rect.y = self.fgroup.move(self.rect.x,self.rect.y,dx,dy)
