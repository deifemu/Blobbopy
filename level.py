import pygame
import pygame.locals
import copy
import json
import sys

from tile import *


class Level:
	tileWidth = 16
	tileHeight = 16




	def __init__(self, game):
		self.game = game
		self.x = game.x
		self.y = game.y
		self.screen = game.screen
		self.tiles = {}
		self.blobbo = None
		self.chests = 0
		self.item = ""

	


	def render(self):
		for tile in self.tiles.values():
			tile.render()

	def collect_item(self, item):
		if not self.item:
			self.item = item
			return True
		return False
	
	def drop_item(self):
		if not self.item:
			return
		
		coord = self.blobbo.get_coord()
		ncoord = self.move_coord(self.last_dir, coord)
		target_tile = self.getTile(ncoord)

		if not target_tile.is_free() or target_tile.topTile != None:
			return
		
		if self.item == "glasses":
			# lvl.put_top(glassesTile())
			return

		if self.item == "ax":
			target_tile.put_top(AxTile())
		elif self.item == "key":
			target_tile.put_top(keyTile())
		elif self.item == "remote":
			target_tile.put_top(RemoteTile())
			target_tile.topTile.activate(self.last_dir)
		elif self.item == "stone":
			target_tile.put_top(StoneTile())
			

		self.item = ""
		self.move_sprite()
		




	def renderTile(self, coord, pixCoord, pixmap):
		self.screen.blit(self.game.tilepixlist[pixmap], (coord[0]*16, coord[1] * 16), (pixCoord[0]*16, pixCoord[1]*16, 16, 16))

	def renderTile128(self, coord, id):
		pixCoord = id >> 4, id & 0x0F
		self.renderTile(coord, pixCoord, "tiles")
		# self.screen.blit(self.game.tilepixlist["tiles"], (coord[0]*16, coord[1] * 16), (pixCoord[0]*16, pixCoord[1]*16, 16, 16))

	def renderLine(self, coord, vertical):
		if vertical:
			pygame.draw.rect(self.game.screen, (255,0,0), pygame.Rect(coord[0]*16+7, coord[1]*16, 2, 16),  2)
		else:
			pygame.draw.rect(self.game.screen, (255,0,0), pygame.Rect(coord[0]*16, coord[1]*16+7, 16, 2),  2)

	def animateSingle(self, coord, pixmap, maxx, y, sleep=0.1):
		for x in range(0, maxx):
			self.renderTile(coord, (x,y), pixmap)
			self.game.updateScreen()
			time.sleep(sleep)
		self.getTile(coord).render()
		self.game.updateScreen()


	def load_level(self, path):
		self.chests = 0
		self.item = ""
		self.path = path
		with open(path, "rb") as f:
			data = f.read()
		raw = Level.unpack(data)
		for n,t in enumerate(raw):
			x = n // self.y
			y = n % self.y
			self.tiles[x,y] = makeTile(self, (x, y), t)
		self.render()

	def set_blobbo(self, b):
		self.blobbo = b

	def add_chest(self):
		self.chests += 1
	def open_chest(self):
		self.chests -= 1
		if self.chests == 0:
			self.game.play_sound("rsrc2_snd_155_All")



	def unpack(data):
		# unencrypt
		source = []
		for i in range(16, len(data)):
			source.append(data[i] ^ data[i-1])

		i = 0
		dest = []
		while i < len(source):
			if source[i] >= 128:
				# Sequence of packed bytes
				runLength = 256 - source[i] + 1
				i += 1
				for ii in range(0, runLength):
					dest.append(source[i])
				i += 1

			else:
				# Sequence of unpacked bytes
				runLength = source[i] + 1
				i += 1
				for ii in range(0, runLength):
					dest.append(source[i])
					i += 1
		return dest

	def move(self, dir):
		coord = self.blobbo.get_coord()
		ncoord = self.move_coord(dir, coord)
		target_tile = self.getTile(ncoord)
		self.last_dir = dir

		if target_tile.enter(coord):
			# self.blobbo.animate_move(coord, ncoord)
			self.touch_neibours(coord)
			self.touch_neibours(ncoord)
		self.move_sprite()
			

	def switch_top(self, coord1, coord2):
		tile1 = self.getTile(coord1)
		tile2 = self.getTile(coord2)
		a = tile1.remove_top()
		b = tile2.remove_top()
		if b:
			tile1.put_top(b)
		if a:
			tile2.put_top(a)
			

	def get_dir(self, source, target):
		if target[0] > source[0]:
			return 4
		if target[0] < source[0]:
			return 6
		if target[1] > source[1]:
			return 2
		if target[1] < source[1]:
			return 8
		return 0


	def move_coord(self, dir, coord):
		if dir == 1:
			return coord[0] - 1, coord[1] - 1
		elif dir == 2:  #
			return coord[0],     coord[1] - 1
		elif dir == 3:
			return coord[0] + 1, coord[1] - 1
		
		elif dir == 4: #
			return coord[0] - 1, coord[1]
		elif dir == 5:
			return coord[0]    , coord[1]
		elif dir == 6: #
			return coord[0] + 1, coord[1]
		
		elif dir == 7:
			return coord[0] - 1, coord[1] + 1
		elif dir == 8: #
			return coord[0],     coord[1] + 1
		elif dir == 9:
			return coord[0] + 1, coord[1] + 1
		else:
			return None

	def touch_neibours(self, coord):
		self.tiles[coord[0] - 1, coord[1]    ].touch(coord)
		self.tiles[coord[0] + 1, coord[1]    ].touch(coord)
		

		self.tiles[coord[0] - 1, coord[1] - 1].touch(coord)
		self.tiles[coord[0]    , coord[1] - 1].touch(coord)
		self.tiles[coord[0] + 1, coord[1] - 1].touch(coord)
		
		self.tiles[coord[0] + 1, coord[1] + 1].touch(coord)
		self.tiles[coord[0]    , coord[1] + 1].touch(coord)
		self.tiles[coord[0] - 1, coord[1] + 1].touch(coord)

		


	def getTile(self, coord):
		try:
			return self.tiles[coord]
		except:
			return None


	def push(self, coordBlobbo, coordObject, xOnly = False):
		# push the ball horizontally
		if xOnly and (coordBlobbo[1] != coordObject[1]):
			return False
		coord3 = 2*coordObject[0] - coordBlobbo[0], 2*coordObject[1] - coordBlobbo[1]
		#print(f"move c:{coordBlobbo} t:{coordObject} => {coord3} {self.getTile(coord3)}")
		if self.getTile(coord3).is_free():
			self.switch_top(coord3, coordObject)
			return True
		return False




	def die(self):
		self.load_level(self.path)

	def loop(self):
		# for tile in self.tiles.values():
			# tile.loop()
		
		for y in range(0, self.game.y):
			
			more = True
			while more:
				more = False
				for x in range(0, self.game.x):
					tile = self.getTile((x,y))
					more = tile.loop() or more

	def move_sprite(self):
		for tile in self.tiles.values():
			if tile.topTile:
				tile.topTile.is_moved = False # make sure we only move once
		#for tile in self.tiles.values():
			#tile.move_sprite()
		
		for y in reversed(range(0, self.game.y)):
			for x in reversed(range(0, self.game.x)):
				tile = self.getTile((x,y))
				tile.move_sprite()






# def print_data(data):
# 	txt = ""
# 	i = 0
# 	for d in data:
# 		txt += f"{d:02x} "
# 		i += 1
# 		if i > 31:
# 			print(txt)
# 			txt = ""
# 			i = 0
# 	print(txt)