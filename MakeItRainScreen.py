import urllib.request
import time
import pygame
import os
import socket
import threading
import random
import argparse
from pythonosc import osc_message_builder
from pythonosc import udp_client

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50006              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
print("started")
s.listen(1)
conn, addr = s.accept()
print('Connected by', addr)



parser = argparse.ArgumentParser()
parser.add_argument("--ip", default="127.0.0.1",help="The ip of the OSC server")
parser.add_argument("--port", type=int, default=5005,help="The port the OSC server is listening on")
args = parser.parse_args()

client = udp_client.SimpleUDPClient(args.ip, args.port)



game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "images")


def loadImages(*args):
	imageList = []
	for arg in args:
		img = pygame.image.load	(os.path.join(img_folder, arg) + ".jpg")
		imageList.append(img)
	return imageList


IPOSITION = loadImages("pos-02", "pos-03", "pos-04","pos-05","pos-06", "pos-07", "pos-08","pos-09")

#colors
WHITE 		= 	(255,255,255)
BLACK 		= 	(0,0,0)
LIGHT_BLUE 	= 	(180,233,255)
GREEN		=	(0,255,0)

#GAME CONSTANTS
TITLE 	= 	"Home Destroyinator 2000"
WIDTH 	= 	800
HEIGHT 	= 	500

#Lists and constants for modules and IP
modules = []
currentIP = []
port = 80

#Interface Values
moduleList_x = 200
moduleList_y = 200
title_x = 50
title_y = 50
refresh_x = WIDTH-(2*moduleList_x)-50
refresh_y = moduleList_y-50


playerlist = []
positionlist = []

class Position():
	def __init__(self, img, handl, handr, legl, legr):
		self.img = IPOSITION[img]
		
		self.handl = handl
		self.handr = handr
		self.legl = legl
		self.legr = legr
		positionlist.append(self)

positionlist.append(Position(0,0,0,0,0))

positionlist.append(Position(1,2,2,0,0))

positionlist.append(Position(2,2,2,0,1))

positionlist.append(Position(3,0,2,0,2))

positionlist.append(Position(4,0,0,0,0))

positionlist.append(Position(5,0,2,0,0))

positionlist.append(Position(6,1,1,0,0))

positionlist.append(Position(7,2,2,1,1))

currentPositionA= random.choice(positionlist)
currentPositionB= random.choice(positionlist)
class Player():

	def __init__(self,num):
		self.num	= num
		self.handl = (0,0)
		self.handr = (0,0)
		self.spine = (0,0)
		self.legl = (0,0)
		self.legr = (0,0)
		self.shoulder = (0,0)

	def setPos(self, handl_x, handl_y, handr_x,handr_y, spine_x,spine_y, legl_x, legl_y, legr_x,legr_y,shoulder_x,shoulder_y):
		self.handl = (handl_x, handl_y)
		self.handr = (handr_x, handr_y)
		self.spine = (spine_x, spine_y)
		self.legl = (legl_x,legl_y)
		self.legr = (legr_x, legr_y)
		self.shoulder = (shoulder_x,shoulder_y) 

		
	def checkPos(self, cp):
		if (cp.handl == 0 and self.handl[1] <= self.spine[1]):
			return False
		if (cp.handl == 1 and (self.handl[1] >= self.spine[1] or self.handl[1] < self.shoulder[1])):
			return False
		if (cp.handl == 2 and self.handl[1] >= self.shoulder[1]):
			return False
		if (cp.handr == 0 and self.handr[1] <= self.spine[1]):
			return False
		if (cp.handr == 1 and (self.handr[1] >= self.spine[1] or self.handr[1] < self.shoulder[1])):
			return False
		if (cp.handr == 2 and self.handr[1] >= self.shoulder[1]):
			return False
		if (cp.legr == 1 and abs(self.legl[1] - self.legr[1]) < 0.1) and (self.legl[1] < self.legr[1]):
			return False
		if (cp.legl == 2 and abs(self.handl[0] - self.legl[0]) > 0.1):
			return False
		print (self.handl[1])
		print (self.shoulder[1])
		print(self.spine[1])
		print(self.handr[1])
		print(cp.handl)
		return True

		


#Pygame font Init
pygame.font.init()
def text_to_screen(screen, text, x, y, size = 20,
            color = (200, 000, 000), font_type = 'Comic Sans MS'):
    text = str(text)
    font = pygame.font.SysFont(font_type, size)
    text = font.render(text, True, color)
    screen.blit(text, (x, y))

def newPosition():
	newPos = random.choice(positionlist)
	return newPos

def getData():
	while True:
		data = conn.recv(1024)
		if not data: break
		# if (data[2] > len(playerlist)-1):
		d = []
		data = str(data)
		pnum = int(data[2])
		spc = data.find(" ")
		nxtspc = data.find(" ", spc+1)
		a = True
		while (a):

			d.append(float(data[spc+1:nxtspc]))
			if (nxtspc == -1): 
				a = False
			spc = nxtspc
			nxtspc = data.find(" ", spc+1)


		
		if (pnum > len(playerlist)-1):
			p = Player(pnum)
			playerlist.append(p)
		else:
			playerlist[0].setPos(d[0],d[1],d[2],d[3],d[4],d[5],d[6],d[7],d[8],d[9], d[10], d[11])
#TRHEAD THE SHIT OUT OF IT
threads = []


def refresh():
	threads[:] = []
	t = threading.Thread(target=getData)
	threads.append(t)
	t.start()
	

def checkButton(a,b,c,d):
	click = pygame.mouse.get_pressed()
	if  click[0] == 1: 
		mouse = pygame.mouse.get_pos()
		x = mouse[0]
		y = mouse[1]
		if (x>=a and x < c and y >= b and y < d):
			return True
def win():
	client.send_message("/layer4/clip1/connect", 1)
	


#Pygame initializing things
pygame.init()
window = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
gameLoop = True


playernumA = 0
playernumB = 0

rain = 0

refresh()
while gameLoop:
	for event in pygame.event.get():
		if (event.type==pygame.QUIT):
			gameLoop = False
#INTERFACE YES YES
	window.fill(BLACK)
	
	i = 0
	

	playernumA = 0
	playernumB = 0


	for myplayer in playerlist:
		if i == 1 and myplayer.handl[0] != 0.0:
			i  += 1
			playernumB = myplayer
		if i == 0 and myplayer.handl[0] != 0.0:
			playernumA = myplayer
			i  += 1
			

	
	if playernumA != 0 and playernumB == 0:
		window.blit(currentPositionA.img,(0,0))
		if (playernumA.checkPos(currentPositionA)):
			currentPositionA = newPosition()
			win()
			rain += 0.2
			
	if playernumA != 0 and playernumB !=0:
		window.blit(currentPositionA.img,(0,0))
		window.blit(currentPositionB.img,(400,0))
		if (playernumA.checkPos(currentPositionA)) and (playernumB.checkPos(currentPositionB)):
			currentPositionA = newPosition()
			currentPositionB = newPosition()
			win()
			rain += 0.2

	rain -= 0.01
	if rain <= 0:
		rain = 0
	if rain > 1:
		rain = 1
	print(rain)
	client.send_message("/layer3/video/opacity/values", rain)

	pygame.display.flip()
#PENCILS DOWN, QUIT DRAWING
	clock.tick (10)
conn.close()
pygame.quit()



