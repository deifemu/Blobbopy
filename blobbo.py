import pygame
import pygame.locals
import copy
import json
import sys

from level import *

class Game:
	x = 32
	y = 20
	


	def __init__(self, editLevel=""):
		pygame.init()
		self.oldClick = False
		self.levelnr = 128 + 15

		self.realscreen = pygame.display.set_mode((512*2, 320*2), flags=pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
		self.screen = pygame.Surface((self.x*16, self.y*16))

		self.tilepixlist = {}
		self.tilepixlist["tiles"] = pygame.image.load("data/blobbo.rsrc2_PMP8_128.bin.bmp").convert_alpha()
		self.tilepixlist["blobbomove"] = pygame.image.load("data/blobbo.rsrc2_PMP8_129_Move.bin.bmp").convert_alpha()
		self.tilepixlist["blobboNoPush"] = pygame.image.load("data/blobbo.rsrc2_PMP8_131_NoPush.bin.bmp").convert_alpha()
		self.tilepixlist["blobboPush"] = pygame.image.load("data/blobbo.rsrc2_PMP8_130_Push.bin.bmp").convert_alpha()
		self.tilepixlist["tree"] = pygame.image.load("data/blobbo.rsrc2_PMP8_151.bin.bmp").convert_alpha()
		self.tilepixlist["blobbosquash"] = pygame.image.load("data/blobbo.rsrc2_PMP8_201.bin.bmp").convert_alpha()
		self.tilepixlist["blobboburn"] = pygame.image.load("data/blobbo.rsrc2_PMP8_202.bin.bmp").convert_alpha()
		self.tilepixlist["blobbopierce"] = pygame.image.load("data/blobbo.rsrc2_PMP8_204.bin.bmp").convert_alpha()
		self.tilepixlist["stairs"] = pygame.image.load("data/blobbo.rsrc2_PMP8_200_Down Stairs.bin.bmp").convert_alpha()
		self.tilepixlist["drown"] = pygame.image.load("data/blobbo.rsrc2_PMP8_206.bin.bmp").convert_alpha()
		self.tilepixlist["sunhole"] = pygame.image.load("data/blobbo.rsrc2_PMP8_153.bin.bmp").convert_alpha()
		self.tilepixlist["drill"] = pygame.image.load("data/blobbo.rsrc2_PMP8_150.bin.bmp").convert_alpha()

		
		self.soundlist = {}

		self.level = Level(self)
		self.level.load_level(f"levels/00{self.levelnr}.blev")
		

	def screensize(self):
		return  self.realscreen.get_rect().size
	
	def next_level(self):
		if self.levelnr < 128 + 26:
			self.levelnr += 1
			self.level.load_level(f"levels/00{self.levelnr}.blev")

	def last_level(self):
		if self.levelnr > 128:
			self.levelnr -= 1
			self.level.load_level(f"levels/00{self.levelnr}.blev")
		
	def updateScreen(self):
		self.realscreen.blit(pygame.transform.scale(self.screen, self.screensize()), (0, 0))
		pygame.display.flip()

	def play_sound(self, name):
		if name not in self.soundlist:
			self.soundlist[name] = pygame.mixer.Sound(f"data/blobbo.{name}.wav")
		self.soundlist[name].play()


	def play(self):
		clock = pygame.time.Clock()

		self.updateScreen()
		exitGame = False
		while not exitGame:

			key = 0
			self.level.loop()
			self.updateScreen()
			clock.tick(15)
			
			for event in pygame.event.get():
				move = 0
				key = ''
				if event.type == pygame.locals.QUIT:
					exitGame = True
				elif event.type == pygame.VIDEORESIZE:
					self.realscreen = pygame.display.set_mode(event.size, pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
				elif event.type == pygame.locals.KEYDOWN:
					pressed_key = event.key
					if (pressed_key == 1073741906):
						move = 2
					elif (pressed_key == 1073741905):
						move = 8
					elif (pressed_key == 1073741903):
						move = 6
					elif (pressed_key == 1073741904):
						move = 4
					elif (pressed_key == 113):
						exitGame = True
					elif (pressed_key == 13): #enter
						key = "enter"
					elif (pressed_key == 32): #space
						key = "space"
						self.level.move_sprite()
					elif (pressed_key == 27): #esc
						key = "esc"
						self.level.die()
					elif (pressed_key == 110): #n
						self.next_level()
					elif (pressed_key == 98): #b
						self.last_level()
					elif (pressed_key == 100): #d
						self.level.drop_item()
					else:
						print(f"key {pressed_key}")
					
					# if key:
						# print(f"key {key}")
					if move > 0:
						self.level.move(move)

			click = pygame.mouse.get_pressed()[0]
			if click and not self.oldClick:
				p = pygame.mouse.get_pos()
				# fix scaling!
				x = p[0] * self.screen.get_size()[0] / self.screensize()[0]
				y = p[1] * self.screen.get_size()[1] / self.screensize()[1]
				self.level.tiles[x // self.level.tileWidth, y // self.level.tileHeight].click()
			self.oldClick = click

	pygame.quit()




if __name__ == "__main__":
	if len(sys.argv) > 1:
		mygame = Game(sys.argv[1])
	else:
		mygame = Game()
	mygame.play()