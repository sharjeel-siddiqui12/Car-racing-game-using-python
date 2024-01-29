import pygame
import time
import tkinter
import random
import os
from PIL import Image, ImageTk
import tkinter.simpledialog  # Import the simpledialog module



VRM_WIDTH = 32
VRM_HEIGHT = 24

GAMESTATUS_TITLE = 0
GAMESTATUS_START = 1
GAMESTATUS_MAIN = 2
GAMESTATUS_MISS = 3
GAMESTATUS_OVER = 4

ENEMY_MAX = 5

gameStatus = GAMESTATUS_TITLE

gameTime = 0

KEY_LEFT = "Left"
KEY_RIGHT = "Right"
KEY_SPACE = "space"

basePath = os.path.abspath(os.path.dirname(__file__))

blankRow = [0] * VRM_WIDTH
vrm = [blankRow] * VRM_HEIGHT

indexOffset = 0

roadWidth = 12

roadX = 10

mx = 16
my = 20

ex = [0] * ENEMY_MAX
ey = [0] * ENEMY_MAX
ev = [0] * ENEMY_MAX
es = [0] * ENEMY_MAX


enemy_count = 0

score = 0
player_name = ""


key = ""
keyOff = False
pygame.mixer.init()

def play_background_music():
    pygame.mixer.music.load("start.wav")
    pygame.mixer.music.play(-1)  # -1 means play indefinitely

def play_game_over_sound():
    game_over_sound = pygame.mixer.Sound("lose.wav")
    game_over_sound.play()

def pressKey(e):
	global key, keyOff
	key = e.keysym
	keyOff = False


def releaseKey(e):
	global keyOff
	keyOff = True

# Function to get player name
def get_player_name():
    global player_name
    while True:
        player_name = tkinter.simpledialog.askstring("Player Name", "Enter your name:")
        if player_name:
            filename = f"{player_name}_scores.txt"
            if os.path.exists(filename):
                with open(filename, "r") as file:
                    past_scores = [int(line.strip()) for line in file.readlines()]
                past_scores_str = ", ".join(map(str, past_scores))
                response = tkinter.messagebox.askyesno(
                    "Player Exists",
                    f"Welcome back, {player_name}!\n"
                    f"Your past scores: {past_scores_str}\n"
                    "Do you want to continue?",
                )
                if response:
                    return player_name
            else:
                return player_name

# Function to save the player's scores to a text file
def save_scores_to_file(player_name, score):
    filename = f"{player_name}_scores.txt"
    with open(filename, "w") as file:  # Use "w" mode to clear the existing content
        file.write(f"{score}\n") 


def title():
    global player_name,gameStatus, gameTime, score, mx, my, roadWidth, roadX, enemy_count, vrm

    if key == KEY_SPACE:
        player_name = get_player_name()
        score = 0
        mx = 16
        my = 20
        for i in range(0, ENEMY_MAX):
            es[i] = 0
        play_background_music()
        enemy_count = 0
        roadWidth = 12
        roadX = 10
        vrm = [blankRow] * VRM_HEIGHT
        indexOffset = 0
        gameStatus = GAMESTATUS_START
        gameTime = 0


def gameStart():
	global gameStatus, gameTime
	

	if gameTime < 24:
		generateRoad(False)

	if gameTime == 50:
		
		gameStatus = GAMESTATUS_MAIN
		gameTime = 0



def gameMain():
	global score

	generateRoad()

	movePlayer()

	moveEnemy()


	score = score + 1

# Function to load the game state from a file
def load_game_state():
    global score, mx, my, roadWidth, roadX, enemy_count
    try:
        with open("game_state.txt", "w") as file:
            score = int(file.readline())
            mx = int(file.readline())
            my = int(file.readline())
            roadWidth = int(file.readline())
            roadX = int(file.readline())
            enemy_count = int(file.readline())
          # Write data to the file
    except Exception as e:
        print(f"Error: {e}")
    
        

def generateRoad(isMove=True):
	global roadX, indexOffset

	if isMove == True:

		v = random.randint(0, 2) - 1
		if (roadX + v > 0 and roadX + v < VRM_WIDTH - roadWidth - 1):
			roadX = roadX + v

	newRow = [2] * VRM_WIDTH
	for w in range(roadWidth):
		newRow[roadX + w] = 0
	newRow[roadX - 1] = 1
	newRow[roadX + roadWidth] = 1

	indexOffset -= 1
	if indexOffset < 0:
		indexOffset = VRM_HEIGHT - 1
	
	vrm[indexOffset] = newRow


def movePlayer():
	global gameStatus, gameTime, mx

	if key == KEY_LEFT and mx > 0:
		mx -= 1

	if key == KEY_RIGHT and mx < VRM_WIDTH:
		mx += 1

	ty = indexOffset + my
	if ty > VRM_HEIGHT - 1:
		ty = ty - VRM_HEIGHT

	if vrm[ty][mx] > 0:
		gameStatus = GAMESTATUS_MISS
		play_game_over_sound() 
		gameTime = 0


def moveEnemy():
	global gameStatus, gameTime, enemy_count

	if enemy_count < ENEMY_MAX and gameTime % 150 == 0:
		enemy_count += 1

	for e in range(enemy_count):
	
		if es[e] > 0:
			
			if es[e] == 2 and ey[e] < 15:
				if ex[e] > mx:
					ex[e] -= 1
				if ex[e] < mx:
					ex[e] += 1
			ey[e] = ey[e] + 1
			if ey[e] > 23:
				es[e] = 0
			if abs(ex[e] - mx) < 2 and abs(ey[e] - my) < 2:
				
				gameStatus = GAMESTATUS_MISS
				gameTime = 0

	
		else:
			
			if gameTime > 100 and random.randint(0, 10) > 8:
				ex[e] = roadX + random.randint(0, roadWidth)
				ey[e] = 0
				ev[e] = 0
				es[e] = random.randint(1, 2)


def miss():
	global gameStatus, gameTime

	if gameTime > 25:
		pygame.mixer.music.stop()
	
		gameStatus = GAMESTATUS_OVER
		gameTime = 0


def gameover():
    global gameStatus, gameTime
    # save_game_state()
    if (gameTime > 10 and key == KEY_SPACE) or gameTime > 50:
        # Save the game state before going back to the title
        gameStatus = GAMESTATUS_TITLE
        gameTime = 0


def drawScreen():
	global gameTime


	canvas.delete("TEXT1")
	canvas.delete("BG1")
	canvas.delete("PLAYER")
	canvas.delete("ENEMY")


	if gameStatus == GAMESTATUS_START or gameStatus == GAMESTATUS_MAIN or gameStatus == GAMESTATUS_MISS:

		for row in range(VRM_HEIGHT):
			vrow = row + indexOffset
			if vrow > VRM_HEIGHT - 1:
				vrow = vrow - VRM_HEIGHT
			for col in range(VRM_WIDTH):
				canvas.create_image(gPos(col), gPos(row), image = img_chr[vrm[vrow][col]], tag = "BG1")

    
	if gameStatus == GAMESTATUS_MAIN:
		
		canvas.create_image(gPos(mx), gPos(my), image = img_mycar, tag = "PLAYER")
		
		for e in range(enemy_count):
			if es[e] > 0:
				canvas.create_image(gPos(ex[e]), gPos(ey[e]), image = img_othercar, tag = "ENEMY")
	if gameStatus == GAMESTATUS_MISS:
		
		canvas.create_image(gPos(mx), gPos(my), image = img_bang, tag = "PLAYER")


	if gameStatus == GAMESTATUS_TITLE:
		canvas.create_rectangle(0, 0, gPos(VRM_WIDTH), gPos(VRM_HEIGHT), fill = "Black")
		writeText(9, 6, "TINY CAR RACE", "TEXT1")
		
		if gameTime < 25:
			writeText(9, 13, "PUSH SPACE KEY", "TEXT1")
		if gameTime == 50:
			gameTime = 0
	if gameStatus == GAMESTATUS_START:
		if gameTime > 30 and gameTime < 50:
			writeText(14, 13, f"START ({player_name})", "TEXT1")
	if gameStatus == GAMESTATUS_OVER:
            save_scores_to_file(player_name, score)
            writeText(12, 11, "GAME OVER", "TEXT1")
            gameover()

	writeText(0, 0, "SCORE " + "{:06}".format(score)+ f"({player_name})" , "TEXT1")

 
def writeText(x, y, str, tag="text1"):


	str = str.upper()

	
	for i in range(len(str)):
		o = ord(str[i])
		if o >= 48 and o <= 57:
			canvas.create_image(gPos(x + i), gPos(y), image = img_font[o - 48], tag = tag)
		if o >= 65 and o <= 90:
			canvas.create_image(gPos(x + i), gPos(y), image = img_font[o - 55], tag = tag)


def loadImage(filePath):

	img = Image.open(filePath).convert("RGBA")
	return img.resize((img.width * 2, img.height * 2), Image.NEAREST)


def gPos(value):

	return value * 8 * 2 + 8


def main():
    global gameTime, roadWidth, roadX, mx, key, keyOff

    gameTime += 1


    if gameStatus == GAMESTATUS_TITLE:
        title()

    if gameStatus == GAMESTATUS_START:
        gameStart()

    if gameStatus == GAMESTATUS_MAIN:
        gameMain()

    if gameStatus == GAMESTATUS_MISS:
        miss()
        play_game_over_sound()

    if gameStatus == GAMESTATUS_OVER:
        gameover()

    drawScreen()

    if keyOff == True:
        key = ""
        keyOff = False

    root.after(50, main)

root = tkinter.Tk()
root.geometry(str(gPos(VRM_WIDTH) - 8) + "x" + str(gPos(VRM_HEIGHT) - 8))
root.title("Tiny Car Race")
root.bind("<KeyPress>", pressKey)
root.bind("<KeyRelease>", releaseKey)


canvas = tkinter.Canvas(width = gPos(VRM_WIDTH) - 8, height = gPos(VRM_HEIGHT) - 8)
canvas.pack()

img_mycar = ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "mycar.png"))
img_othercar = ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "othercar.png"))
img_bang = ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "bang.png"))
img_chr = [
	ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "road.png")),
	ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "block.png")),
	ImageTk.PhotoImage(loadImage(basePath + os.sep + "Images" + os.sep + "green.png"))
]

img_allfont = loadImage(basePath + os.sep + "Images" + os.sep + "font.png")
img_font = []
for w in range(0, img_allfont.width, 16):
	img = ImageTk.PhotoImage(img_allfont.crop((w , 0, w + 16, 16)))
	img_font.append(img)

main()

root.mainloop()
