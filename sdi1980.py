'''
sdi1980.py

This program uses turtle graphics to simulate the old Missile Command game. The purpose of this program
is to allow me to get practice subclassing objects, and so I'm probably not using turtles as intended, 
but I am able to piggyback over the built-in updating that turtles do.



author: James P. Burke
'''

import turtle as trtl
import random as rand
import math

# ------------------------------
# Game Data Setup
# ------------------------------

# lists to keep track of the falling missiles and the things that have exploded
explosions = []
missiles = []

# constants that govern the paremeters of the game, like the speed of updates
# the size of explosions and how the score is calculated
TICK_INTERVAL = 50
EXPLOSION_DEATH_SIZE = 85
ZAP_COST = 55
LANDED_PENALTY = 300
MISSILE_BONUS = 100

# global variables used to keep track of the running score, the countdown timer
# that ends the game, and how many milliseconds have accumulated since the last second passed
score = 0
timer = 60
subsecond = 0

# get a reference to the screen and use it to turn off automatic updates
wn = trtl.Screen()
wn.tracer(0)

# set the size of the play area and store it for use later
wn.screensize(400,300)
gamesize = wn.screensize()
screenwidth = gamesize[0]
screenheight = gamesize[1]

# create two turtles used to draw the border, messages to the player, and the score/timer
pen = trtl.Turtle()
scorepen = trtl.Turtle()
scorepen.hideturtle()


# ------------------------------
# Utility/Setup functions 
# ------------------------------

def draw_border():
    """Use the screen parameters from before to
    draw a border around the play area.
    """
    pen.speed(0)
    pen.hideturtle()
    pen.penup()
    n=1
    pen.goto(screenwidth/n,screenheight/n)
    pen.pendown()
    pen.goto(screenwidth/n,-screenheight/n)
    pen.goto(-screenwidth/n,-screenheight/n)
    pen.goto(-screenwidth/n,screenheight/n)
    pen.goto(screenwidth/n,screenheight/n)

def write_begin_message():
    """Use the pen turtle to tell the user
    to start the game by hitting the a key
    """
    pen.speed(0)
    pen.hideturtle()
    pen.penup()
    pen.goto(0,0)
    pen.write("Hit the a key to begin",align="center", font=("Arial", 45, "bold"))

def setup_score_turtle():
    """Set the initial position of the turtle that draws the score
    """
    scorepen.hideturtle()
    scorepen.penup()
    scorepen.goto(-screenwidth, -screenheight)

#
# Call the "begin game" utility functions and make sure the screen updates
#
draw_border()
write_begin_message()
wn.update()

# ------------------------------
# Game Object Classes
# ------------------------------

class MissileTurtle(trtl.Turtle):
    """MissileTurtle is a subclass of Turtle and it's used to draw
    and keep track of a single missile
    """
    was_split = False
    fall_speed = 0

    def __init__(self, *args, **kwargs):
        """Part of the initialization is setting the position 
        and heading of the missile. These are random.
        """
        super(MissileTurtle,self).__init__(*args, **kwargs)
        self.hideturtle()
        self.speed(0)
        self.penup()
        self.pencolor("red")
        randloc = rand.randint(int(screenwidth*4/7),screenwidth)
        if (rand.randint(1,2)==2):
            randloc = -randloc
            self.setheading(rand.randint(-90,-45))
        else:
            self.setheading(rand.randint(-125,-90))
        self.goto(randloc,screenheight)
        #print(randloc)
        #print(self.heading())
        self.pendown()
        self.fall_speed = rand.randint(3,8)

    def advance(self):
        """Having a custom advance functin allows me to have different missile speeds
        """
        self.forward(self.fall_speed)
    
    def split(self, alist):
        """The game has a feature where missiles can split in two.
        This is triggered randomly in the game loop.
        The split function creates a second missile and sends the two
        missiles off in different directions.
        """
        if (not self.was_split):
            self.was_split = True
            headmod = rand.randint(20,40)
            self.setheading(self.heading()+headmod)
            warhead = MissileTurtle()
            warhead.penup()
            warhead.goto(self.pos())
            warhead.setheading(self.heading()-headmod)
            warhead.pendown()
            warhead.was_split = True
            alist.append(warhead)


class ExplosionTurtle(trtl.Turtle):
    """ExplosionTurtle keeps track of currently active explosions. It's
    a subclass of Turtle.
    """
    radius = 20
    # I need to note the size of the turtle's circular shape because set shape size
    # scales the shape, and I need the original size to be able to set the size of
    # the explosion in pixels. This isn't working perfectly, and I suspect the
    # stampsize I've assumed is incorrect, but I haven't had time to fix it.
    stampsize = 20

    def __init__(self, *args, **kwargs):
        super(ExplosionTurtle,self).__init__(*args, **kwargs)
        self.speed(0)
        self.hideturtle()
        self.color("gray")
        self.penup()
        self.shape("circle")
        self.shapesize(self.radius/self.stampsize)
        self.showturtle()

    def fire(self, x,y):
        """Firing the zaps sets the new locaton of the explosion
        """
        self.hideturtle()
        self.goto(x,y)
        self.showturtle()

    def grow(self):
        """This routine controls the growth of the explosion.
        The three should probably have been a class constant.
        """
        self.radius += 3
        self.shapesize(self.radius/self.stampsize)
        colorval = self.radius/(EXPLOSION_DEATH_SIZE+15)
        self.color((colorval,colorval,colorval))
    
    def get_radius(self):
        return self.radius

    def checkCollision(self,inTurtle):
        """Check whether this explosion has collided with the given
        turtle (which is presumably a missile)
        """
        if (self.distance(inTurtle) < self.radius*.7):
            return True
        else:
            return False

# Game Functions

def begin_game():
    """Used to turn the screen click events on and the timer events on."""
    pen.clear()
    draw_border()
    setup_score_turtle()
    wn.onclick(zapfired)
    wn.ontimer(gametick, TICK_INTERVAL) 

def zapfired(x,y):
    """Handles the screen clicks, which are the player firing the zaps to cause an
    explosion. Zaps cost energy, which comes out of your score.
    """
    global score
    tempturt = ExplosionTurtle()
    tempturt.fire(x,y)
    explosions.append(tempturt)
    #explosions.append(trtl.Turtle())
    print("zap!!!!!")
    score = score - ZAP_COST

def draw_score():
    """This draws the timer and score on the screen using a formatted string
    which is the first time I've used this functionality.
    """
    scorepen.clear()
    scorepen.write("{0}{1:03d}{2}{3}".format("Time: ", timer, " / Score: ", score), font=('Arial', 20, 'bold'))

def end_game():
    """When the game needs to end, this is called. It mainlt writes the message to the user."""
    pen.penup()
    pen.goto(0,0)
    pen.write("Game Over",align="center", font=("Arial", 65, "bold"))   

# ------------------------------
# Game Loop Tick Handler
# ------------------------------
def gametick():
    """This is the main game loop. A lot is happening in here.
    This one function has several phases:
    -- COLLISION CHECK
    -- GAME STATE UPDATE
    -- DRAWING/SCREEN UPDATE
    """
    tempexplode = []
    # If I had written this in a better object oriented way, I wouldn't have needed globals.
    global score
    global timer
    global subsecond
    # ------------------------------
    # COLLISION CHECK
    # ------------------------------
    #
    # if there is a collision, a missile is removed from the missile list and an explosion is created
    # in its place. We do the collision handling here because we've just come back from a slight
    # pause in the processing, which means we're reacting to a state that the user has been able
    # to see for a tenth of a second.
    # This sort of collision is the only time the score increases.
    #
    for expl in explosions:
        for miss in missiles:
            if (expl.checkCollision(miss)):
                missposx = miss.xcor()
                missposy = miss.ycor()
                tempturt = ExplosionTurtle()
                tempturt.fire(missposx,missposy)
                tempexplode.append(tempturt)
                print("missile destroyed")
                missiles.remove(miss)
                miss.clear()
                score = score + MISSILE_BONUS
    # ------------------------------
    # UPDATE GAME STATE
    # ------------------------------
    # 
    # Once the collisions are handled, it's time to update the state of the game (positions of
    # objects, the state of objects, etc.)
    #
    # First we eliminate any explosions that have gotten to their max size
    for expl in explosions:
        if (expl.get_radius() > EXPLOSION_DEATH_SIZE):
            explosions.remove(expl)
            expl.hideturtle()
            expl.clear()
    for miss in missiles:
        if (miss.ycor() < -screenheight):
            missiles.remove(miss)
            miss.clear()
            print("missile landed")
            score = score - LANDED_PENALTY
    for expl in explosions:
        expl.grow()
    for miss in missiles:
        miss.advance()
        #expl.shapesize(rand.randint(1,10))
    for miss in missiles:
        if (rand.randint(1,200)<5):
            miss.split(missiles)
    if (rand.randint(1,200)<20):
        missiles.append(MissileTurtle())
    for newexpl in tempexplode:
        explosions.append(newexpl)
    subsecond += TICK_INTERVAL
    if (subsecond >= 1000):
        timer -= 1
        subsecond = 0
    # update drawing
    draw_score()
    wn.update()
    # register for tick
    if(timer>0):
        wn.ontimer(gametick, TICK_INTERVAL) 
    else:
        end_game()

# ------------------------------
# Event Handlers
# ------------------------------

wn.onkey(begin_game, "a")
#wn.ontimer(gametick, TICK_INTERVAL) 
wn.listen()
wn.mainloop()
