from turtle import Turtle, Screen
import random
import time
import os
import winsound 

# ================== CONSTANTS ==================
COLORS = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "white", "gray"]
START_Y = -370
FINISH_Y = 380
LANES = [-250, -150, -50, 50, 150, 250]
HIGHSCORE_FILE = "highscore.txt"

# ================== PLAYER ==================
class TurtleCross(Turtle):
    def __init__(self):
        super().__init__()
        self.shape("turtle")
        self.color("white")
        self.penup()
        self.setheading(90)
        self.reset_position()

    def move_up(self):
        if self.ycor() < FINISH_Y:
            self.forward(20)

    def move_down(self):
        if self.ycor() > START_Y:
            self.backward(20)

    def reset_position(self):
        self.goto(0, START_Y)

    def reach_finish(self):
        return self.ycor() > FINISH_Y

# ================== VEHICLE MANAGER ==================
class VehicleManager:
    def __init__(self):
        self.vehicles = []
        self.speed = 10

    def create_vehicle(self, level=1):
        chance = max(6 - level, 1)
        if random.randint(1, chance) != 1:
            return
        car = Turtle("square")
        car.shapesize(stretch_wid=1, stretch_len=2)
        car.penup()
        car.color(random.choice(COLORS))
        lane = random.choice(LANES)
        direction = random.choice([0, 1])
        if direction == 0:
            car.goto(520, lane)
            car.direction = "left"
        else:
            car.goto(-520, lane)
            car.direction = "right"
        self.vehicles.append(car)

    def move_vehicles(self):
        for car in self.vehicles:
            if car.direction == "left":
                car.backward(self.speed)
            else:
                car.forward(self.speed)

        for car in self.vehicles[:]:
            if abs(car.xcor()) > 540:
                car.hideturtle()
                self.vehicles.remove(car)

    def increase_speed(self):
        self.speed += 5

    def reset(self):
        for car in self.vehicles:
            car.hideturtle()
        self.vehicles.clear()
        self.speed = 10

# ================== SCOREBOARD ==================
class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.level = 1
        self.lives = 3
        self.highscore = self.load_highscore()
        self.color("white")
        self.penup()
        self.hideturtle()
        self.update_display()

    def load_highscore(self):
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read())
        return 0

    def save_highscore(self):
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(self.highscore))

    def update_display(self):
        self.clear()
        self.goto(-480, 360)
        hearts = "♥ " * self.lives
        self.write(f"Level: {self.level}  {hearts} Highscore: {self.highscore}",
                   align="left", font=("Courier", 16, "normal"))

    def next_level(self):
        self.level += 1
        self.update_display()
        flash_screen("green")  # flash xanh khi qua level
        play_sound("level")

    def lose_life(self):
        self.lives -= 1
        flash_screen("red")  # flash đỏ khi mất mạng
        play_sound("hit")     # âm thanh khi mất mạng
        if self.lives <= 0:
            self.game_over()
            return True
        self.update_display()
        return False

    def game_over(self):
        self.goto(0, 0)
        self.color("red")
        self.write("Con Gà", align="center", font=("Courier", 36, "bold"))
        if self.level > self.highscore:
            self.highscore = self.level
            self.save_highscore()

    def reset(self):
        self.level = 1
        self.lives = 3
        self.color("white")
        self.update_display()

# ================== FLASH EFFECT ==================
def flash_screen(color, duration=0.1):
    screen.bgcolor(color)
    screen.update()
    time.sleep(duration)
    screen.bgcolor("black")
    screen.update()

# ================== SOUND EFFECT ==================
def play_sound(effect):
    if effect == "hit":  # mất mạng
        winsound.Beep(500, 200)
    elif effect == "level":  # qua level
        winsound.Beep(800, 200)

# ================== FINISH LINE ==================
def draw_finish_line():
    finish = Turtle()
    finish.hideturtle()
    finish.penup()
    finish.goto(-500, FINISH_Y)
    finish.pendown()
    finish.color("white")
    finish.width(3)
    finish.forward(1000)
draw_finish_line()

# ================== BACKGROUND ANIMALS (Gây hại) ==================
background_animals = []
def create_background_animals():
    for _ in range(5):
        a = Turtle("circle")
        a.penup()
        a.color(random.choice(["yellow", "cyan", "magenta"]))
        a.goto(random.randint(-480,480), random.randint(-350,350))
        a.speed(0)
        a.direction = random.choice(["left", "right"])
        background_animals.append(a)

def move_background_animals():
    for a in background_animals:
        if a.direction == "left":
            a.backward(2)
        else:
            a.forward(2)
        if a.xcor() > 500:
            a.goto(-500, a.ycor())
        elif a.xcor() < -500:
            a.goto(500, a.ycor())

create_background_animals()

# ================== SCREEN ==================
screen = Screen()
screen.setup(width=1000, height=800)
screen.bgcolor("black")
screen.title("Turtle Crossing Game")
screen.tracer(0)

player = TurtleCross()
vehicles = VehicleManager()
scoreboard = Scoreboard()

game_on = True

# ================== CONTROLS ==================
screen.listen()
screen.onkey(player.move_up, "Up")
screen.onkey(player.move_down, "Down")

def reset_game():
    global game_on
    game_on = True
    player.reset_position()
    vehicles.reset()
    scoreboard.reset()
    scoreboard.update_display()
screen.onkey(reset_game, "r")

# ================== GAME LOOP ==================
while True:
    time.sleep(0.1)
    screen.update()

    move_background_animals()  # di chuyển background animals

    if game_on:
        vehicles.create_vehicle(scoreboard.level)
        vehicles.move_vehicles()

        # Collision detection với xe
        for car in vehicles.vehicles:
            if car.distance(player) < 20:
                if scoreboard.lose_life():
                    game_on = False
                player.reset_position()

        # Collision detection với background animals
        for a in background_animals:
            if a.distance(player) < 20:
                if scoreboard.lose_life():
                    game_on = False
                player.reset_position()

        # Finish line
        if player.reach_finish():
            player.reset_position()
            vehicles.increase_speed()
            scoreboard.next_level()

screen.exitonclick()
