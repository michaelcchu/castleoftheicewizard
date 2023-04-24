# main program

import pygame as pg
import asyncio
from settings import *
from sprites import *

class Game:
    
    # Main Functions

    def __init__(self):
        '''initializes game window, etc'''
        pg.init()
        
        self.screen = pg.display.set_mode((WIDTH,HEIGHT))
        pg.display.set_caption(TITLE)

        self.message_display('Loading ...',40,306,224,center=True, color=WHITE)
        pg.display.flip()

        self.clock = pg.time.Clock()
        pg.key.set_repeat(25,50) # if key is held, repeat action

        # Initialize Variables
        self.running = True
        self.intro = True
        self.levels = False
        self.instructions = False
        self.playing = False
        self.win = False
        self.lose = False
        
        self.fires = 0
        
        self.level = ''
        
        self.click = False

        # Initialize Music
        self.intro_audio = pg.mixer.Sound('intro_audio.ogg')
        self.game_audio = pg.mixer.Sound('game_audio.ogg')
        
        self.intro_audio.play(-1)
        
    def new(self):
        '''start a new game'''
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.ice = pg.sprite.Group()
        self.iceWalls = pg.sprite.Group()
        self.secure = pg.sprite.Group()
        self.fire = pg.sprite.Group()
        
        self.load_data()

        self.fires = 0        
        rowNum = 0 # draw blocks
        for row in self.map_data:
            colNum = 0
            ice = False
            length = 1
            wall = False
            secure = ''
            
            for item in row:
                if item == '*': # walls
                    Wall(self,colNum,rowNum)
                    length = 1
                    wall = True
                    
                elif item == 'P': # player
                    length = 1
                    self.player = Player(self,colNum*TILESIZE,rowNum*TILESIZE)
                    wall = False

                elif item == '#': # 1 secure
                    secure = 1
                    colNum = colNum - 1
                elif item == '!':
                    secure = 2
                    colNum = colNum - 1 # 2 secure

                elif item == '$': # fire
                    Fire(self,colNum*TILESIZE,rowNum*TILESIZE)
                    self.fires = self.fires + 1
                    
                    wall = False
                    
                elif not item in ['\n','-','.']: # ice
                    i = Ice(self,colNum*TILESIZE,rowNum*TILESIZE,\
                                int(item,25)-9)

                    if item == item.upper():
                        if wall == True:
                            s = Secure(self,i,'left')
                            i.image.blit(s.image,(0,0))
                            s.rect.x, s.rect.y = i.rect.x, i.rect.y
                            
                            if secure == 2:
                                s = Secure(self,i,'right')
                                i.image.blit(s.image,(i.width-s.width,0))
                                s.rect.x, s.rect.y = i.rect.right-s.width, \
                                                     i.rect.y
                        else:            
                            s = Secure(self,i,'right')
                            i.image.blit(s.image,(i.width-s.width,0))
                            s.rect.x, s.rect.y = i.rect.right-s.width, i.rect.y

                    wall = False

                else:
                    wall = False
                    
                colNum = colNum + 1

            rowNum = rowNum + 1

        # Change Music
        self.intro_audio.fadeout(1000)
        pg.time.delay(1000)
        self.game_audio.play(-1)
        
    def run(self):
        '''game loop'''
        while self.playing == True:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        
    def update(self):
        '''game loop - update'''
        self.all_sprites.update()
        if self.fires == 0:
            self.playing = False
            self.win = True
            
    def events(self):
        '''game loop - events'''
        for event in pg.event.get():
            self.mouse_quit_check(event)
                
            # check for user pressing arrow keys
            if event.type == pg.KEYDOWN:

                if self.player.onGround == True:
                    dx = 7
                else:
                    dx = 1
                                        
                if event.key == pg.K_UP:
                    if self.player.onGround == True:
                        self.player.jump(firstCall=True)
                elif event.key == pg.K_LEFT:
                    self.player.move('LEFT',-dx)
                elif event.key == pg.K_RIGHT:
                    self.player.move('RIGHT',dx)
                elif event.key == pg.K_x:
                    self.player.fall_check()
                    if self.player.onGround == True:
                        self.player.push()

            elif event.type == pg.KEYUP:
                if event.key == pg.K_z:
                    self.player.fall_check()
                    if self.player.onGround == True:
                        new_ice = True
                        for fire in self.fire:
                            if fire.onGround == False:
                                new_ice = False

                        if new_ice == True:
                            self.player.iceblock()
            
    def draw(self):
        '''game loop - draw'''
        self.screen.fill(BGCOLOR)
        self.draw_grid()
        self.all_sprites.draw(self.screen)

        levels = self.button('Levels',525,10,80,40,BLUE,LIGHTBLUE,16)
        self.click = False
        
        # after drawing everything, flip the display
        pg.display.flip()

        if levels == True:
            self.playing = False
            self.levels = True

            # Change Music
            self.game_audio.fadeout(1000)
            pg.time.delay(1000)
            self.intro_audio.play(-1)
            
    def show_intro_screen(self):
        '''game start screen'''
        # Draw Start Screen
        self.screen.fill(CYAN)
        self.message_display('Castle of the Ice Wizard',36,25,25)   
        self.message_display('Developer: Michael Chu',16,30,75)   
        wiz = pg.image.load('wizard_left.png')
        wiz = pg.transform.scale(wiz,(200,240))
        self.screen.blit(wiz,(350,150))
        
        # Loop through Intro
        while self.intro == True:
            for event in pg.event.get():
                self.mouse_quit_check(event)

            # Create/Update Buttons
            play = self.button('Play',100,150,130,40,BLUE,LIGHTBLUE,16)
            instructions = self.button('Instructions',100,250,130,40,\
                                       BLUE,LIGHTBLUE,16)
            exitB = self.button('Exit',100,350,130,40,BLUE,LIGHTBLUE,16)

            self.click = False
            
            pg.display.flip()       

            if play == True:
                self.intro = False
                self.levels = True
            elif instructions == True:
                self.intro = False
                self.instructions = True
            elif exitB == True:
                self.intro = False
                self.running = False
                
    def show_instructions_screen(self):
        '''instructions screen'''
        # Draw Instructions Screen and Display Messages
        self.screen.fill(CYAN)
        messageList = [('Instructions',36,25,25),('Goal: Extinguish all the '\
                        'fires in the level by pushing or dropping ' \
                        'ice blocks into the fires',16,25,75),('Note: You ' \
                        'cannot place an ice block in the same location as a fire, '\
                        'and if you step on a fire,',16,25,105),('you lose!',16,500,135),('Controls',\
                        16,25,155), ('Right Arrow Key: right',16,25,195),\
                       ('Left Arrow Key: left',16,25,235),('Up Arrow Key: '\
                        'jump',16,300,195),('Z Key: *create/destroy ice block',\
                        16,25,295),('X Key: push ice block',16,25,375),('*Ice '\
                        'blocks are created/destroyed',16,375,295),('diagonally '\
                        'below the wizard in',16,375,320),('the direction the '\
                        'wizard is facing',16,375,345)]
        for m in messageList:
            self.message_display(m[0],m[1],m[2],m[3])

        wizRight = pg.image.load('wizard_right.png')
        wizLeft = pg.image.load('wizard_left.png')
        arrowRight = pg.image.load('right_arrow.jpeg')
        arrowLeft = pg.image.load('left_arrow.jpeg')
        arrowUp = pg.image.load('up_arrow.jpeg')
        
        wizRight = pg.transform.scale(wizRight,(20,30))
        wizLeft = pg.transform.scale(wizLeft,(20,30))
        arrowRight = pg.transform.scale(arrowRight,(20,8))
        arrowLeft = pg.transform.scale(arrowLeft,(20,8))
        arrowUp = pg.transform.scale(arrowUp,(8,20))
        
        wList = [(wizRight,175,195),(wizLeft,195,235),(wizLeft,245,295),\
                 (wizRight,275,295),(wizLeft,225,375),(wizRight,255,375),\
                 (wizRight,435,195)]
        aList = [(arrowRight,200,200),(arrowLeft,170,240),(arrowLeft,170,385),\
                 (arrowRight,310,385),(arrowUp,440,170)]
        iList = [(220,320),(300,320),(285,380),(200,380)]
        
        for wizard in wList:
            self.screen.blit(wizard[0],(wizard[1],wizard[2]))
        for arrow in aList:
            self.screen.blit(arrow[0],(arrow[1],arrow[2]))
        for ice in iList:
            pg.draw.rect(self.screen,WHITE,(ice[0],ice[1],20,20))
            
        # Loop through Instructions Screen
        while self.instructions == True:
            for event in pg.event.get():
                self.mouse_quit_check(event)

            # Create/Update Buttons
            back = self.button('Back',525,10,80,40,BLUE,LIGHTBLUE,16)
            self.click = False
            
            pg.display.flip()

            if back == True:
                self.instructions = False
                self.intro = True
                
    def show_levels_screen(self):
        '''levels screen'''
        # Draw Levels Screen
        self.screen.fill(CYAN)
        self.message_display('Levels',36,25,25)   

        # Loop Through Levels Screen
        while self.levels == True:
            for event in pg.event.get():
                self.mouse_quit_check(event)
                    
            # Create/Update Buttons
            level1 = self.button('Level 1',100,100,130,40,BLUE,LIGHTBLUE,16,\
                                 'playing')
            level2 = self.button('Level 2',100,150,130,40,BLUE,LIGHTBLUE,16,\
                                 'playing')
            level3 = self.button('Level 3',100,200,130,40,BLUE,LIGHTBLUE,16,\
                                 'playing')
            level4 = self.button('Level 4',100,250,130,40,BLUE,LIGHTBLUE,16,\
                                 'playing')
            level5 = self.button('Level 5',100,300,130,40,BLUE,LIGHTBLUE,16,\
                                 'playing')
            level6 = self.button('Level 6',100,350,130,40,BLUE,LIGHTBLUE,16,\
                                 'playing')
            level7 = self.button('Level 7',250,100,130,40,BLUE,LIGHTBLUE,16,\
                                 'playing')
            level8 = self.button('Level 8',250,150,130,40,BLUE,LIGHTBLUE,16,\
                                 'playing')
            level9 = self.button('Level 9',250,200,130,40,BLUE,LIGHTBLUE,16,\
                                 'playing')
            level10 = self.button('Level 10',250,250,130,40,BLUE,LIGHTBLUE,16,\
                                 'playing')
            back = self.button('Back',525,10,80,40,BLUE,LIGHTBLUE,16)
            self.click = False
            
            pg.display.flip()
          
            if level1 or level2 or level3 or level4 or level5 or level6 \
               or level7 or level8 or level9 or level10 == True:
                self.levels = False
                self.playing = True

            elif back == True:
                self.levels = False
                self.intro = True

    def show_exit_screen(self):
        '''exit screen'''
        # Draw Levels Screen
        self.screen.fill(CYAN)
        messageList = [('Thank you for playing!',60,50,100),('Credits:',24,110\
                        ,220),('Developer: Michael Chu',24,110,250),('(Click '\
                        'anywhere to exit)',16,200,360)]
        for m in messageList:
            self.message_display(m[0],m[1],m[2],m[3])

        pg.display.flip()

        close = False
        while close == False:
            events = pg.event.get()
            for e in events:
                if e.type == pg.MOUSEBUTTONDOWN or e.type == pg.QUIT:
                    close = True

    def show_win_screen(self):
        '''win screen'''
        # Draw Win Screen
        self.screen.fill(CYAN)
        messageList = [('You Win!',60,50,100),('Do you want to try another '\
                        'level?',24,110,220)]
        for m in messageList:
            self.message_display(m[0],m[1],m[2],m[3])

        # Loop through Win Screen
        while self.win == True:
            for event in pg.event.get():
                self.mouse_quit_check(event)

            # Create/Update Buttons
            back = self.button('Click this button to continue',300,300,200,40,BLUE,LIGHTBLUE,16)
            self.click = False
            
            pg.display.flip()

            if back == True:
                self.win = False
                self.levels = True

                # Change Music
                self.game_audio.fadeout(1000)
                pg.time.delay(1000)
                self.intro_audio.play(-1)

    def show_lose_screen(self):
        '''lose screen'''
        # Draw Lose Screen
        self.screen.fill(CYAN)
        messageList = [('Sorry, You Lost :(',60,50,100),('Do you want to try '\
                        'again?',24,110,220)]
        for m in messageList:
            self.message_display(m[0],m[1],m[2],m[3])

        # Loop through Win Screen
        while self.lose == True:
            for event in pg.event.get():
                self.mouse_quit_check(event)

            # Create/Update Buttons
            back = self.button('Click this button to continue',300,300,200,40,BLUE,LIGHTBLUE,16)
            self.click = False
            
            pg.display.flip()

            if back == True:
                self.lose = False
                self.levels = True

                # Change Music
                self.game_audio.fadeout(1000)
                pg.time.delay(1000)
                self.intro_audio.play(-1)
            
    # Auxilary Functions

    def button(self,msg,x,y,w,h,c1,c2,fsize,nscreen=''):
        '''creates a button'''
        mouse = pg.mouse.get_pos()

        # Creates the button (change color if hovering) 
        if x + w > mouse[0] > x and y + h > mouse[1] > y:
            pg.draw.rect(self.screen,c2,(x,y,w,h))

            # Change screens if button is clicked  
            if self.click == True:
                self.click = False
                if nscreen == 'playing':
                    if msg == 'Level 1':
                        self.level = 'map1.txt'
                    elif msg == 'Level 2':
                        self.level = 'map2.txt'
                    elif msg == 'Level 3':
                        self.level = 'map3.txt'
                    elif msg == 'Level 4':
                        self.level = 'map4.txt'
                    elif msg == 'Level 5':
                        self.level = 'map5.txt'
                    elif msg == 'Level 6':
                        self.level = 'map6.txt'
                    elif msg == 'Level 7':
                        self.level = 'map7.txt'
                    elif msg == 'Level 8':
                        self.level = 'map8.txt'
                    elif msg == 'Level 9':
                        self.level = 'map9.txt'
                    elif msg == 'Level 10':
                        self.level = 'map10.txt'
                        
                return True
        else:
            pg.draw.rect(self.screen,c1,(x,y,w,h))

        # Adds text to button    
        self.message_display(msg,fsize,x+(w/2),y+(h/2),center=True,color=WHITE)

        return False
    
    def draw_grid(self):
        '''draws grid'''
        # draw vertical lines
        for x in range(0,WIDTH-MARGIN+1,TILESIZE):
            pg.draw.line(self.screen,LIGHTGREY,(x,0),(x,HEIGHT))
        # draw horizontal lines
        for y in range(0,HEIGHT,TILESIZE):
            pg.draw.line(self.screen,LIGHTGREY,(0,y),(WIDTH-MARGIN,y))
            
    def load_data(self):
        '''input map data'''
        self.map_data = []
        f = open(self.level,'r')
        for line in f: # read map
            self.map_data.append(line) # creates list of rows

    def message_display(self,text,size,x,y,center=False, color=BLACK):
        '''displays a text message'''
        #pygame.font.match_font(name,bold=0,italic=0)
        font = pg.font.Font('ARIALN.TTF',size)

        textSurf = font.render(text,True,color) # creates surface
                                                # with text rendered on it
        textRect = textSurf.get_rect()
        if center == True:
            textRect.center = (x,y)
        else:
            textRect.topleft = (x,y)

        self.screen.blit(textSurf, textRect)

    def mouse_quit_check(self,event):
        '''checks if user closes window or clicks the mouse'''
        if event.type == pg.QUIT:
            self.running = False
            self.intro = False
            self.levels = False
            self.instructions = False
            self.playing = False
            self.lose = False
            self.win = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.click = True

# Main Program
async def main():
    g = Game()

    while g.running == True:
        # change screens if necessary
        if g.intro == True:
            g.show_intro_screen()
        elif g.levels == True:
            g.show_levels_screen()
        elif g.instructions == True:
            g.show_instructions_screen()
        elif g.playing == True:
            g.new()
            g.run()
            
        elif g.win == True:
            g.show_win_screen()
        elif g.lose == True:
            g.show_lose_screen()

        await asyncio.sleep(0)
            
    g.show_exit_screen()

    pg.quit()

asyncio.run(main())
