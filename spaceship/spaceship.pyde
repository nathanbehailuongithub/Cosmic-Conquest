
import os
import random
import csv
import time

# Used to load sound
add_library('minim')
player = Minim(this)


path = os.getcwd()
WIDTH = 1280
HEIGHT = 720

# spaceship class
class Spaceship:
    def __init__(self,x,y,img,img_w,img_h):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.img = loadImage(path + "/images/" + img)
        self.img_w = img_w
        self.img_h = img_h

# Mariner / player class
class Mariner(Spaceship):
    def __init__(self,x,y,img_w,img_h):
        Spaceship.__init__(self,x,y,"sp.png",100,100)
        self.score = 0
        self.health = 10
        self.firing = False
        self.fire_rate = 1
        self.fire_start = 0
        self.fire_end = 5000
        self.shielded = True
        self.shield_start = 0
        self.shield_end = 5000
        self.key_handler = {RIGHT:False, LEFT:False, UP:False, DOWN:False}
        self.color = 245
        self.r = 50
        
        # sounds
        self.death_sound = player.loadFile(path + "/sounds/death.mp3")
        self.shoot_sound = player.loadFile(path + "/sounds/shoot.mp3")
        self.damage_sound = player.loadFile(path + "/sounds/damage.mp3")
        
        #player's bullets
        self.bullet = []
    
    # displays player's bullet
    def display(self):
        self.update()
        for bullet in self.bullet:
            bullet.display()
        if self.shielded == True:
            tint(30,160,204)
        else:
            noTint()
        image(self.img,self.x - self.img_w//2,self.y - self.img_h//2 + game.y_shift)
        noTint()
    
    #checks distance between player spaceship and other objects
    def distance(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5
    
    # checks if player spaceship and other objects have disatance smaller than their radius
    def collision(self, other):
        if self.distance(other) < self.img_w / 2 + other.img_w / 2 :
            self.health = 0
    
    # controls movement of spaceship
    def update(self):
        if game.loss == False and game.win == False:
            # Horizontal movement and velocity
            if self.key_handler[RIGHT] == True and self.x + (self.r + 5) < game.w:
                self.vx = 7
            elif self.key_handler[LEFT] == True and self.x - (self.r + 5) > 0 :
                self.vx = -7
            else:
                self.vx = 0
        
            # Vertical movement and velocity
            if self.key_handler[UP] == True  and self.y - self.r >= game.p1.y:
                self.vy = -5
            elif self.key_handler[DOWN] == True and self.y + (self.r + 5) < game.h - game.y_shift : 
                self.vy = 5
            else:
                self.vy = 0
            
            # increments speed of player's spaceship
            self.x += self.vx
            self.y += self.vy

        
       # checks collison between player and obstacles
        for obstacle in game.obstacles:
            self.collision(obstacle)
        

        if len(game.enemies) > 0:
            for enemy in game.enemies:    # checks if there is an enemy in screen 
                if -500 <= enemy.y - self.y <= 500:
                    self.firing = True
                    break
                
                if enemy.y > game.h - game.y_shift:  # deletes enemies which are out of screen and below the player
                    game.player.score += 3 
                    game.enemies.remove(enemy)
                    
                elif -game.y_shift <= enemy.y <= game.h - game.y_shift:
                    self.firing = True
                    break
                
                self.planetoids = [] + game.comets + game.asteroids
                for planetoid in self.planetoids:
                    if self.y - planetoid.y < -500:# deletes comet/asteroids which are out of screen and below the player
                        if isinstance(planetoid, Comet):
                            game.comets.remove(planetoid)
                        elif isinstance(planetoid, Asteroid):
                            game.asteroids.remove(planetoid)
        else:
            self.firing = False
        
        
        # appends bullet for player's spaceship
        if frameCount % (60*self.fire_rate) == 0 and self.firing == True:
                self.bullet.append(Bullet(self))
                self.shoot_sound.rewind()
                self.shoot_sound.play()
        
        # condiition implemented once player's spaceship is destroyed
        if self.health == 0:
            game.loss = True
            game.bgm.pause()
            self.shoot_sound.pause()
            # self.death_sound.rewind()
            self.death_sound.play()
            self.vx = 0
            self.vy = 0
            game.save_score()
            game.bullets = []
            game.powerups = []
            game.obstacles = []
            game.enemies = []
            
            
class Enemy(Spaceship):
        def __init__(self,x,y,img_w,img_h,x_lim_left, x_lim_right):
            Spaceship.__init__(self,x,y,"enemyss.png",100,100)
            self.x_lim_left = x_lim_left
            self.x_lim_right = x_lim_right
            self.r = self.img_w // 2
            self.health = 3
            self.fire_rate = 1
            self.firing = False
            self.vx = random.randint(1,5)
            self.bullet = []
        
        # displays enemy spaceship
        def display(self):
            self.update()
            image(self.img,self.x - self.img_w//2,self.y - self.img_h//2 + game.y_shift,100,100) # resize image
        
        # controls speed of enemy spaceship
        def update(self):
            if self.x - self.r <= self.x_lim_left:
                self.vx = self.vx * -1
                
            elif self.x + self.r >= self.x_lim_right:
                self.vx *= -1
            
            self.x += self.vx
        
            # checks if there is an enemy in screen
            if len(game.enemies) > 0:
                for enemy in game.enemies:
                    if enemy.y > game.h - game.y_shift:  # deletes enemies which are out of screen and below the player
                        game.score += 3 
                        game.enemies.remove(enemy)
                    elif -game.y_shift <= enemy.y <= game.h - game.y_shift:
                        self.firing = True
                        break
            else:
                self.firing = False
            
            # appends bullet for enemy spaceship
            for enemy in game.enemies:
                if frameCount % (60*self.fire_rate) == 0 and enemy.firing :
                    self.bullet.append(Bullet(self))
                
                            
class Planetoid:
    def __init__(self,x,y,vy,img,img_w,img_h):
            self.x = x
            self.y = y
            self.vy = 0 
            self.img = loadImage(path + "/images/" + img)
            self.img_w = img_w
            self.img_h = img_h
    
    # controls movement of planetoid
    def move_down(self):
        if game.current_scene in game.scenes[6:]:
            self.y += random.randint(0,5)
        else:
            self.y += 1.5
    
    # displays object
    def display(self):
        self.move_down()
        image(self.img,self.x - self.img_w//2,self.y - self.img_h//2 + game.y_shift)


class Asteroid(Planetoid):
    def __init__ (self,x,y,vy,img,img_w,img_h):
        Planetoid.__init__(self,x,y,vy,img,img_w,img_h)
        self.r = self.img_w // 2


class Comet(Planetoid):
    def __init__ (self,x,y,vy,img,img_w,img_h):
        Planetoid.__init__(self,x,y,vy,img,img_w,img_h)
        self.r = self.img_w // 2
    
    # controls movement 
    def move_down(self):
        if game.current_scene in game.scenes[6:]:
            rand = random.randint(0,5)
        else:
            rand = 3
        self.y += rand
        self.x += rand


class Powerup:
    def __init__(self,ind):
        self.x = random.randint(20,game.w-20)
        if game.player.y >= game.h//2:
            self.y = random.randint(0,game.player.y-game.h//2)
        elif game.player.y < game.h//2:
            self.y = -random.randint(-(game.player.y-100),game.y_shift)
        self.r = 20
        self.ind = ind
        self.duration = 0
        self.type = ["shield","weapon"][ind]
        if self.type == "shield":
            self.img = loadImage(path + "/images/" + "powerup.png")
        if self.type == "weapon":
            self.img = loadImage(path + "/images/" + "weapon.png")
    
    # displays powerup object
    def display(self):
        self.update(game.player)
        image(self.img,self.x,self.y + game.y_shift)
    
    
    # Function contrlling collison between player and powerups and powers given
    def update(self,player):
        if ((self.x-player.x)**2 + (self.y-player.y)**2)**0.5 <= player.r:
            game.powerup_sound.rewind()
            game.powerup_sound.play()
            start = game.check_time()
            if self.type == "shield": #player spaceship health will be not affected
                game.player.shield_start = start
                game.player.shielded = True
                game.player.health += 3
            elif self.type == "weapon": #player's shooting speed increases
                game.player.fire_start = start
                game.player.fire_rate = 0.5
                game.player.health += 3
            del game.powerups[game.powerups.index(self)]
        if frameCount % 150 == 0 and self.y > (game.h - game.y_shift): #deletes powerups left behind by player
            del game.powerups[game.powerups.index(self)]

class Bullet:
    def __init__(self, spaceship):
        self.x = 0
        self.y = 0
        self.r = 10
        self.fired = False
        self.spent = False
        self.holder = spaceship
        if isinstance(self.holder, Enemy):
            self.img = loadImage(path + "/images/" + "b1.png")
        if isinstance(self.holder, Mariner):
            self.img = loadImage(path + "/images/" + "playerbullet.png")
   
    # displays bullet object
    def display(self):
        self.update()
        image(self.img,self.x - self.r,self.y + game.y_shift)      
 
           
    def update(self):
        # Upon initialization, creates bullet at bow of player's spaceship
        if self.fired == False:
            if isinstance(self.holder, Enemy):
                self.x = self.holder.x 
                self.y = self.holder.y + self.holder.r
                self.fired = True
            elif isinstance(self.holder, Mariner):
                self.x = self.holder.x 
                self.y = self.holder.y - self.holder.r
                self.fired = True
        else:
            if isinstance(self.holder, Enemy):
                self.y += 2
            if isinstance(self.holder, Mariner):
                self.y -= 2
    
    #checks collision between bullets and other objects 
    def check_collision(self,other):
        if ((self.x-other.x)**2 + (self.y-other.y)**2)**0.5 <= other.r:
            if isinstance(other, Comet) or  isinstance(other, Asteroid):
                return "CometOrAsteroid"
            elif isinstance(other, Enemy):
                return "Enemy"
            elif isinstance(other, Mariner):
                return "Mariner"
        elif self.y < -10 - game.y_shift and frameCount % 300 == 0:
            self.spent = True  


class Portal():
    def __init__ (self,x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.img = loadImage(path + "/images/" + "portal.png")
    
    # displays portal class
    def display(self):
        self.collision(game.player)
        image(self.img,self.x,self.y + game.y_shift,self.w,self.h)
    
    # checks distance between portal and other objects
    def distance(self, other):
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5
        
    # checks if distance between portal and other objects is less than sum of their radius
    def collision(self, other):
        if self.distance(other) < self.w // 2 + other.img_w //2:
            fill(255)
            textSize(30)
            text("Great Job Captain! \nPress E to continue", WIDTH //2 - 130, 100)
            game.bgm.pause()
            game.win = True
            # game.save_score()
            game.win_sound.play()
            
            # Continue to next level
            if game.key_handler["E"] == True:
                level_completed = game.current_scene
                player_name = game.player_name
                player_score = game.score
                game_volume = game.sound_volume[1]
                
                game.__init__() # reinisatantiates game
                game.player_name = player_name
                game.score = player_score
                game.sound_volume[1] = game_volume
                game.bgm.loop()
                game.name_saved = True
                if level_completed == "level0":
                    game.set_scene(6)
                    game.start_time = game.check_time()
                elif level_completed == "level1":
                    game.set_scene(7)
                    game.start_time = game.check_time()
                else:
                    game.save_score()
               
            
               
            
class Game():
    def __init__(self):
        self.w = WIDTH
        self.h = HEIGHT
        self.y_shift = 0
        self.player = Mariner(575,650,100,100)
        
        # Scenes and scene selection
        self.scenes = ["home","newgame","levels","leaderboard","settings","level0","level1","level2","play"]
        self.current_scene = self.scenes[0]

        # Image files + fonts
        self.fpbkg_img = loadImage(path + "/images/" + "fpbkg.png")
        self.levels_img = loadImage(path + "/images/" + "Levels.png")
        self.scores_img = loadImage(path + "/images/" + "scores.png")
        self.font1 = loadFont(path + "/data/" + "LucidaSansUnicode-48.vlw")
        # self.font2 = loadFont(path + "/data/" + "GoudyStout-48.vlw")
        self.settings_img = loadImage(path + "/images/" + "settingsbkg.png")
        self.lvl0_img = loadImage(path+"/images/lvl2.png")
        self.lvl1_img = loadImage(path+"/images/lvl0.png")
        self.lvl2_img = loadImage(path+"/images/lvl0.png")
        self.lvlimgs = [self.lvl0_img,self.lvl1_img,self.lvl2_img]

        # Audio files
        self.bgm = player.loadFile(path + "/sounds/background.mp3")
        # self.bgm.loop()       <-- delete
        self.shoot_sound = player.loadFile(path + "/sounds/shoot.mp3")
        self.damage_sound = player.loadFile(path + "/sounds/damage.mp3")
        self.death_sound = player.loadFile(path + "/sounds/death.mp3")
        self.win_sound = player.loadFile(path + "/sounds/win.mp3")
        self.powerup_sound = player.loadFile (path + "/sounds/powerup.mp3")

        # Lists for objects
        self.asteroids = []
        self.comets = []
        self.enemies = []
        self.powerups = []
        self.obstacles = []
        self.portals = []
        self.num = 0    
        self.create_objects(10)
    
        # Volume control
        self.sound_volume = [False, 2]
        self.key_handler = {RIGHT:False, LEFT:False, UP:False, DOWN:False, "E":False, "P": False}
        
        # Attributes for runtime
        self.obstacles = [] + self.asteroids + self.comets + self.enemies
        self.score = 0
        self.start_time = 0
        self.time = 0
        self.score_saved = False
        self.loss = False
        self.win = False
        self.player_name = "_"
        self.name_saved = False
        self.clicked = False
    
    # Function to create enemies and obstacles between the player and the portal
    def create_objects(self, num):
        self.portal_y = -5000
        rand_y = []
        for i in range(400,self.portal_y, -100):
            rand_y.append(i)
        rand_e = random.randint(1,50)
        
        # Create enemies with random starting positions and random limits on their horizontal movement
        for i in range(num):
            rand_x = random.randint(100,700)
            x_lim_right = random.randint(640,1150)
            x_lim_left = random.randint(0,320)
            rand_idx = random.randint(0,len(rand_y)-1)
            self.enemies.append (Enemy(rand_x, rand_y[rand_idx], 100,100, x_lim_left, x_lim_right))
            rand_y.pop(rand_idx)
        
        # Create a portal at the end of the level
        self.p1 = Portal(self.w//2, self.portal_y,100,100)
        self.portals.append(self.p1)

        # Create asteroids
        for i in range(num):
            rand_x = random.randint(0,720)
            rand_idx = random.randint(0,len(rand_y)-1)
            asteroid = Asteroid(rand_x,rand_y[rand_idx],0,"asteroid.png",80,80)
            self.asteroids.append(asteroid)
        # Create comets
        for i in range(num):
            rand_x = random.randint(0,720)
            rand_idx = random.randint(0,len(rand_y)-1)
            comet = Comet(rand_x,rand_y[rand_idx],10,"comet.png",150,150)
            self.comets.append(comet)
        
        self.obstacles = [] + self.asteroids + self.comets + self.enemies

    def check_time(self):
        return millis() 
    
    def save_score(self):
        if self.score_saved == False:
            with open('highscores.csv','a') as table:
                w = csv.writer(table,lineterminator='\n')
                w.writerow(["{}".format(self.player_name).upper(),self.score])
                self.score_saved = True
    
    # Functions for simplifying button presses
    def set_scene(self,scene):
        self.current_scene = self.scenes[scene]
        
    def button_clicked(self,x,y,w,h):
        if x <= mouseX <= x + w and y <= mouseY <= y + h:
            return True
    
    # Handle volume in settings page
    def update(self):
        # Input for changing volume
        if self.button_clicked(87,430,72,72):
            s_x, s_y, s_w,s_h = 87,430,72,72
            if self.key_handler[RIGHT] == True:
                self.sound_volume[1] += 1
                # stroke(180)
                # rect(169,430,72,72)
            elif self.key_handler[LEFT] == True:
                self.sound_volume[1] -= 1
            # Restrict values
            if self.sound_volume[1] < 0:
                self.sound_volume[1] = 0
            elif self.sound_volume[1] > 40:
                self.sound_volume[1] = 40
            # Volume display
            for n in range(self.sound_volume[1] // 4):
                fill(255)
                stroke(180)
                rect(s_x + s_w + 30 *n , s_y + s_h//2 , 30, 30)
            
            # Apply volume to each mp3, turn the shooting sound down more
            for mp3 in [self.bgm,self.shoot_sound,self.damage_sound,self.death_sound,self.win_sound,self.powerup_sound]:
                if self.sound_volume[1] > 0:
                    mp3.setGain(float(self.sound_volume[1] - 39))
                    if mp3 == self.shoot_sound:
                        mp3.setGain(float(self.sound_volume[1] - 49))
                else:
                    mp3.setGain(-80.0)
                
    def levels(self, level):
        y_shift = self.y_shift
        height_up = -1 * y_shift % self.h
        height_down = self.h - height_up
        
        image(self.lvlimgs[self.scenes.index(self.current_scene)-5],0,0,self.w,height_down,0,height_up,self.w,self.h)
        image(self.lvlimgs[self.scenes.index(self.current_scene)-5],0,height_down,self.w,height_up,0,0,self.w,height_up)
        
        # Scroll background as player progresses
        if self.player.y <= self.h//2 - self.y_shift and self.player.vy < 0: 
            game.y_shift += -1 * self.player.vy
                    
        # Spawn a powerup every 5 seconds if there are less than 3 already present
        if frameCount % 300 == 0 and game.loss == False == game.win and len(self.powerups) < 3:
                self.powerups.append(Powerup(random.randint(0,1)))

        
        # Display current level in top right
        fill(255)
        textSize(20)
        if level == "level0":
            text("Level O" ,1175, 85)
        elif level == "level1":
            text("Level 1" ,1175, 85)
        elif level == "level2":
            text("Level 2" ,1175, 85)
        
        # Object display
        for enemy in self.enemies:
            enemy.display()
        for comet in self.comets:
            comet.display()
        for asteroid in self.asteroids:
            asteroid.display()
        for bullet in self.player.bullet:
            bullet.display()
        for enemy in self.enemies:
            for bullets in enemy.bullet:
                bullets.display()
        for powerup in self.powerups:
            powerup.display()
        self.player.display()
        
        self.p1.display()
        
        if game.loss == False:
            self.time = self.check_time() - self.start_time
            # Sync powerup timers
            self.player.shield_end = self.player.shield_start + 5000
            self.player.fire_end = self.player.fire_start + 5000
            # Check powerup timers
            if self.check_time() > self.player.shield_end:
                self.player.shielded = False
            if self.check_time() > self.player.fire_end:
                self.player.fire_rate = 1
        
   
        # Check if bullets hit a valid target
        for bullet in self.player.bullet:
            for obstacle in self.obstacles:
                if bullet.check_collision(obstacle) == "CometOrAsteroid":
                    self.player.bullet.remove(bullet)
                elif bullet.check_collision(obstacle) == "Enemy":
                    obstacle.health -= 1
                    self.player.bullet.remove(bullet)
                    if obstacle.health == 0 and obstacle in self.enemies and obstacle in self.obstacles:
                        self.enemies.remove(obstacle)
                        self.obstacles.remove(obstacle)
                        self.score += 5
                        
        for enemy in self.enemies:
            for bullet in enemy.bullet:
                if bullet.check_collision(self.player) == "Mariner":
                    enemy.bullet.remove(bullet)
                    if self.player.shielded == False:
                        self.player.health -= .1
                        self.damage_sound.rewind()
                        self.damage_sound.play()
                    if self.player.health <= 0:
                        break
                        
        # Name and Scoreboard display
        fill(255)
        textSize(20)
        if self.win == False:
            text("Player: " + "{}".format(self.player_name).upper(),10,self.h//30)
            text("Health: {}".format(int(self.player.health)),10,50)
            text('Score: {}'.format(self.score),self.w*0.92,self.h//30)
            text("Time: {}".format(self.time//1000),self.w*0.924,50)
    
        if self.player.health <= 0:
            self.loss = True
            self.save_score()
            self.bgm.pause()
            #self.player.shoot_sound.pause()
            self.death_sound.play()
            self.player.img =  loadImage(path + "/images/" + "explosion.png")
            self.obstacles = []
            self.asteroids = []
            self.comets = []
            self.enemies = []
            self.powerups = []
            self.player.bullet = []
        
            # Restart by pressing E after death
            fill(255)
            textSize(30)
            text("Game Over *  \n Press E restart" ,WIDTH //2 , HEIGHT//2)
            if self.key_handler["E"] == True:
                level_completed = game.current_scene
                player_name = game.player_name
                player_score = game.score
                game_volume = self.sound_volume[1]
                if game.current_scene == "level0":
                    game.__init__()
                    game.set_scene(1)
                if game.current_scene == "level1":
                    game.__init__()
                    game.set_scene(1)           
                elif game.current_scene == "level2" and self.score > 30:
                    game.__init__()
                    game.set_scene(7)
                else:
                    game.__init__()
                    game.set_scene(1)

                # Carry volume level and player's name over and skip the screen to enter a name
                game.player_name = player_name
                game.name_saved = True
                self.sound_volume[1] = game_volume
                game.bgm.loop()
                game.start_time = game.check_time()
                game.player.shield_start = game.check_time()
            
    def display(self):
        self.update()
    
# Main menu
        if self.current_scene == "home":
            image(self.fpbkg_img,0,0)
            textSize(32)
            fill(0, 408, 612, 204)
            noFill()
            noStroke()
            rect(550,400,178,50) # start
            rect(520,478,244,50) # leaderboard
            rect(565,550,150,50) # settings
            rect(600,618,72,50)  # exit
        
# Input for Player name
        elif self.current_scene == "newgame":
            if self.name_saved == False:
                if key != ENTER and key != RETURN:
                    strokeWeight(0)
                    fill(20)
                    rect(0, 0, self.w, self.h)
                    fill(200)
                    rect((self.w-400)/2,(self.h-50)/2,400,50)
                    textSize(20)
                    text("Enter a name:",(self.w-400)/2,(self.h-80)/2)
                    fill(100)
                    textSize(40)
                    text("{}".format(self.player_name[1:]).upper(),(self.w*0.7)/2,(self.h+30)/2)
                    if keyPressed == True and type(key) == unicode and len(self.player_name) <= 12:
                        if len(self.player_name) == 0:
                            self.player_name = "_"
                        if key != self.player_name[-1]:
                            self.player_name += key
                    elif key == BACKSPACE: # needs fix    <-- delete
                        self.player_name = self.player_name[0:-1]
                else:
                    self.player_name = self.player_name[1:]
                    self.name_saved = True
            else:
                image(self.levels_img,0,0)
                noFill()
                rect(550,350,150,67) # Beginner
                rect(550,475,150,67) # Advanced
                    
                    
# Level Select screen
        elif self.current_scene == "levels":
            pass

# Scoreboard screen
        elif self.current_scene == "leaderboard":
            image(self.scores_img,0,0)
            fill(240)
            textFont(game.blanka,60)
            
            # Create and sort list of scores from csv
            scores_temp = []
            scores = []
            file = open('highscores.csv','r')
            for line in file:
                line_list = line.strip().split(",")
                if line_list[0] == "":
                    line_list[0] = "-"
                scores_temp.append([line_list[0],int(line_list[1])])
            file.close()
            scores_temp.sort()
            
            # Remove entries with matching names, save the higher score
            invalid = []
            for i in range(len(scores_temp)-1):
                if scores_temp[i][0] == scores_temp[i+1][0]:
                    invalid.append(i)
            invalid.sort(reverse=True)
            for index in invalid:
                del scores_temp[index]
                
            # Sort to show the highest score at the top
            for line in scores_temp:
                scores.append([line[1],line[0]])
            scores.sort(reverse=True)
            
            # Display top 10 scores as text on screen
            space = 0
            for score in scores[:5]:
                text("{}".format(score[1]),90, 200 + space)
                textAlign(RIGHT)
                text("{}".format(score[0]),590, 200 + space)
                textAlign(LEFT)
                space += 100
            space = 0
            for score in scores[5:10]:
                text("{}".format(score[1]),690, 200 + space)
                textAlign(RIGHT)
                text("{}".format(score[0]),1190, 200 + space)
                textAlign(LEFT)
                space += 100
            textFont(self.font1)
            
# Settings 
        elif self.current_scene == "settings":
            image(self.settings_img,0,0)
            noFill()
            noStroke()
            rect(0,0, 125,65) #back
            rect(87,430,72,72) #sound
            if self.button_clicked(0,0, 125,65):
                self.current_scene == self.scenes[0]
            elif self.sound_volume[0]:
                 self.update()
            fill(255)
            textSize(20)
            text("Welcome to the single player space shooting game! Here are the rules: \n 1. There are two levels in the game: Beginner (level 0) and Advanced (levels 1 and 2). \n 2. The player can either start at the Beginner level or Advanced level. \n 3. To unlock level 2, the player must successfully complete level 1. \n 4. To replay level 2, the player must successfully complete level 1 and achieve a minimum score of 30." , 20 , 550)
     
# Levels
        elif self.current_scene in self.scenes[5]:
            self.levels("level0")
        elif self.current_scene in self.scenes[6]:
            self.levels("level1")
        elif self.current_scene in self.scenes[7]:
            self.levels("level2")
        

def setup():
    size(WIDTH, HEIGHT)
    background(20)
    game.blanka = createFont(path + "/data/" + "Blanka-Regular.otf",48)
    game.bgm.loop()

    
def draw():
    background(255,255,255)
    game.display()
    
game = Game()

def keyPressed():
    # Player movement
    if game.player.health > 0 and game.current_scene in game.scenes[5:]:
        if keyCode == RIGHT:
            game.player.key_handler[RIGHT] = True
        elif keyCode == LEFT:    
            game.player.key_handler[LEFT] = True
        elif keyCode == UP:    
            game.player.key_handler[UP] = True
        elif keyCode == DOWN:    
            game.player.key_handler[DOWN] = True

    # Audio input
    elif game.current_scene == "settings":
        if game.button_clicked(87,430,72,72) or game.button_clicked(87,603,75,75):
            if keyCode == RIGHT:
                game.key_handler[RIGHT] = True
            elif keyCode == LEFT:    
                game.key_handler[LEFT] = True
                
    # Restart/Continue or Pause    
    if key == "E" or key == "e":
        game.key_handler["E"] = True
    if key == "P" or key == "p":
        game.key_handler["P"] = True
        game.set_scene(1)
        
def keyReleased():
    if game.player.health > 0 and game.current_scene in game.scenes[5:]:
        if keyCode == RIGHT:
            game.player.key_handler[RIGHT] = False
        elif keyCode == LEFT:    
            game.player.key_handler[LEFT] = False
        elif keyCode == UP:    
            game.player.key_handler[UP] = False
        elif keyCode == DOWN:    
            game.player.key_handler[DOWN] = False
    
    elif game.current_scene == "settings":
        if game.button_clicked(87,430,72,72) or game.button_clicked(87,603,75,75):
            if keyCode == RIGHT:
                game.key_handler[RIGHT] = False
            elif keyCode == LEFT:    
                game.key_handler[LEFT] = False
                
    if key == "E" or key == "e":
        game.key_handler["E"] = False
    if key == "P" or key == "p":
        game.key_handler["P"] = False
    
def mousePressed():
    #Check if the mouse is inside the button
    if game.current_scene == "home":
        if game.button_clicked(550,400,178,50): #Start clicked
            game.set_scene(1)
        elif game.button_clicked(565,550,150,50) : #Settings clicked
            game.set_scene(4)
        elif game.button_clicked(520,478,244,50): # Leaderboard clicked
            game.set_scene(3)    
        elif game.button_clicked(600,618,72,50): # Exit clicked
            exit()
    else:            
        if game.current_scene == "newgame":
            if game.button_clicked(550, 350,150,67): # Beginner clicked
                game.set_scene(5)
                game.start_time = game.check_time()
                game.player.shield_start = game.check_time()
            elif game.button_clicked(550, 475,150,67): # Advanced clicked
                game.set_scene(6)
                game.start_time = game.check_time()
                game.player.shield_start = game.check_time()
                
        elif game.current_scene == "leaderboard":
            pass
            
        elif game.current_scene == "settings":
            if game.button_clicked(87,430,72,72): # Sound 
                game.sound_volume[0] = True
                
        if game.button_clicked(0,0, 125, 55) and game.current_scene not in game.scenes[5:]: #Back clicked
            game.set_scene(0)
