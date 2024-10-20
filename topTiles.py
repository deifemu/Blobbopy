import pygame
import pygame.locals
import copy
import json
import sys
import time



class TopTile:
	def __init__(self, id):
		self.id = id
		self.level = None
		self.floor_tile = None
		self.is_moved = None

	def set_level(self, level):
		self.level = level

	def standing_on(self, tile):
		self.floor_tile = tile

	def slope_right(self):
		return False
	def slope_left(self):
		return False

	def is_blobbo(self):
		return False
	def is_smilie(self):
		return False
	
	def is_teleport_target(self):
		return False

	def enter(self, mycoord, coord):
		return False
	
	# return true to move the top
	def leave(self, mycoord, coord):
		return True

	def touch(self, mycoord):
		return False

	def loop(self, mycoord):
		return False
	
	def move_sprite(self):
		pass
	
	def get_coord(self):
		return self.floor_tile.get_coord()


	def render(self):
		self.level.renderTile128(self.get_coord(), self.id)

	def __str__(self):
		return(f"{self.__class__.__name__}")



class BlobboTile(TopTile):
	def __init__(self):
		super().__init__(112)
		self.glasses_count = 30
	def enter(self, mycoord, coord):
		b = self.floor_tile.leave()
	def is_blobbo(self):
		return True
	
	def render(self):
		if self.level.item == "glasses":
			self.level.renderTile128(self.get_coord(), 114)
		else:
			self.level.renderTile128(self.get_coord(), self.id)


	def move_sprite(self):
		if self.level.item == "glasses":
			self.glasses_count -= 1
			if self.glasses_count == 0:
				self.level.item = ""
				self.render()


class ChestTile(TopTile):
	def __init__(self):
		super().__init__(128)
	def enter(self, mycoord, coord):
		self.floor_tile.remove_top()
		self.level.open_chest()
		self.level.switch_top(mycoord, coord)
		return True
	




class BallTile(TopTile):
	def __init__(self):
		super().__init__(192)
		self.is_active = True
		self.is_initial = True
		self.dropping = False

	def slope_right(self):
		return True
	def slope_left(self):
		return True

	def touch(self, coord):
		# print("touch")
		self.is_active = True

	def enter(self, mycoord, coord):
		# push the ball horizontally
		if self.level.push(coord, mycoord, xOnly=True):
			self.level.switch_top(mycoord, coord)
			return True
		return False

	def loop(self, cordi):
		if not self.is_active:
			return False
		
		moreLoop = True
		while moreLoop:
			moreLoop = False

			mycoord = self.get_coord()
			coord0 = mycoord[0]   , mycoord[1] + 1
			coord1 = mycoord[0] -1, mycoord[1] + 1
			coord1C = mycoord[0] -1, mycoord[1]
			coord2 = mycoord[0] +1, mycoord[1] + 1
			coord2C = mycoord[0] +1, mycoord[1]

			# balls do not drop on the initial screen until they have been touched
			if self.is_initial:
				self.is_initial = False
				if self.level.tiles[*coord0].is_free() or (
						self.level.tiles[*coord0].slope_right() and self.level.tiles[*coord1].is_free() and self.level.tiles[*coord1C].is_free()) or (
						self.level.tiles[*coord0].slope_left() and self.level.tiles[*coord2].is_free() and self.level.tiles[*coord2C].is_free()):
					self.is_active = False
					return

			if self.level.tiles[*coord0].is_blobbo():
				if self.dropping:
					self.level.die()
			elif self.level.tiles[*coord0].is_free():
				# print(f"drop 1, {mycoord}")
				self.level.switch_top(coord0, mycoord)
				self.dropping = True
				moreLoop =  True
			elif self.level.tiles[*coord0].slope_right() and self.level.tiles[*coord1].is_free() and self.level.tiles[*coord1C].is_free():
				# print("drop 2")
				self.level.switch_top(coord1, mycoord)
				self.dropping = True
				moreLoop =  True
			elif self.level.tiles[*coord0].slope_left() and self.level.tiles[*coord2].is_free() and self.level.tiles[*coord2C].is_free():
				# print("drop 3")
				self.level.switch_top(coord2, mycoord)
				self.dropping = True
				moreLoop =  True
			else:
				self.dropping = False
			
			if moreLoop:
				self.level.game.updateScreen()
				time.sleep(0.02)



class AxTile(TopTile):
	def enter(self, mycoord, coord):
		self.level.collect_item("ax")
		self.floor_tile.remove_top()
		self.level.switch_top(mycoord, coord)
		return True


class ArrowTile(TopTile):
	def __init__(self, left):
		self.left = left
		if left:
			id = 195
		else:
			id = 194
		self.fireing = False
		super().__init__(id)

	def move_sprite(self):
		more_move = True
		fireing = False
		while more_move:
			more_move = False
			mycoord = self.get_coord()
			if self.left:
				coord = mycoord[0] + 1, mycoord[1]
				coord_slope = mycoord[0] + 1, mycoord[1] + 1
			else:
				coord = mycoord[0] - 1, mycoord[1]
				coord_slope = mycoord[0] - 1, mycoord[1] - 1

			
			if self.level.getTile(coord).is_blobbo():
				if fireing:
					self.level.die()
			elif self.level.getTile(coord).is_free():
				self.level.switch_top(coord, mycoord)
				# print(f"{self.left} {self.level.getTile(coord).slope_right()} { self.level.getTile(coord_slope).is_free()}")
				more_move = True
				fireing = True
			elif self.left and self.level.getTile(coord).slope_right() and self.level.getTile(coord_slope).is_free():
				self.level.switch_top(coord_slope, mycoord)
				more_move = True
				fireing = True
			elif not self.left and self.level.getTile(coord).slope_left() and self.level.getTile(coord_slope).is_free():
				self.level.switch_top(coord_slope, mycoord)
				more_move = True
				fireing = True

			if more_move:
				self.level.game.updateScreen()
				time.sleep(0.02)









class TreeTile(TopTile):
	def enter(self, mycoord, coord):
		if self.level.item == "ax":
			# self.level.replaceTile(mycoord, RaftTile())
			tile = self.floor_tile
			tile.remove_top()
			tile.put_top(RaftTile())

			return True
		return False

class WeedTile(TopTile):
	def __init__(self, id, dir):
		self.dir = dir
		super().__init__(id)
	

	def loop(self, mycoord):
		pass

	def move_sprite(self):
		if self.level.item == "glasses":
			return
		coord = self.get_coord()
		blobbo = self.level.blobbo.get_coord()
		if coord[0] == blobbo[0]:
			movedir = -1 if coord[1]> blobbo[1] else 1
			# print("weeed", movedir, self.dir)
			if ((movedir == 1) and (self.dir == 8)) or ((movedir == -1) and (self.dir == 2)):
				for i in range(coord[1] + movedir, blobbo[1], movedir ):
					target = self.level.getTile((coord[0], i))
					if not target.is_free():
						return
				for i in range(coord[1] + movedir, blobbo[1], movedir ):
					target = self.level.getTile((coord[0], i))
					# print(target, (coord[0], i-movedir))
					target.put_top(copy.copy(self))
					target.render()
					self.level.game.updateScreen()
					time.sleep(0.02)

		if coord[1] == blobbo[1]:
			movedir = -1 if coord[0]> blobbo[0] else 1
			if ((movedir == 1) and (self.dir == 6)) or ((movedir == -1) and (self.dir == 4)):
				for i in range(coord[0] + movedir, blobbo[0], movedir ):
					target = self.level.getTile((i, coord[1]))
					if not target.is_free():
						return
				for i in range(coord[0] + movedir, blobbo[0], movedir ):
					target = self.level.getTile((i, coord[1]))
					# print(target, (i-movedir, coord[1]))
					target.put_top(copy.copy(self))
					target.render()
					self.level.game.updateScreen()
					time.sleep(0.02)
		

class PushStoneTile(TopTile):
	def enter(self, mycoord, coord):
		if self.level.push(coord, mycoord):
			self.level.switch_top(mycoord, coord)

class SmileTile(TopTile):
	def is_smilie(self):
		return True
	def move_sprite(self):
		coord = self.get_coord()
		blobbo = self.level.blobbo.get_coord()
		if coord[0] == blobbo[0]:
			movedir = -1 if coord[1]> blobbo[1] else 1
			for i in range(coord[1] + movedir, blobbo[1], movedir ):
				target = self.level.getTile((coord[0], i))
				if (not target.is_free() and not target.is_smilie()) or target.is_water():
					return
			for i in range(coord[1] + movedir, blobbo[1], movedir ):
				target = self.level.getTile((coord[0], i))
				source = self.level.getTile((coord[0], i-movedir))
				if target.is_free():
					# print(target, (coord[0], i-movedir))
					self.level.switch_top((coord[0], i-movedir), (coord[0], i))
					target.render()
					source.render()
					self.level.game.updateScreen()
					time.sleep(0.02)

		if coord[1] == blobbo[1]:
			movedir = -1 if coord[0]> blobbo[0] else 1
			for i in range(coord[0] + movedir, blobbo[0], movedir ):
				target = self.level.getTile((i, coord[1]))
				if (not target.is_free() and not target.is_smilie()) or target.is_water():
					return
			for i in range(coord[0] + movedir, blobbo[0], movedir ):
				target = self.level.getTile((i, coord[1]))
				source = self.level.getTile((i-movedir, coord[1]))
				if target.is_free():
					# print(target, (i-movedir, coord[1]))
					self.level.switch_top((i-movedir, coord[1]), (i, coord[1]))
					target.render()
					source.render()
					self.level.game.updateScreen()
					time.sleep(0.02)

class RaftTile(TopTile):
	def __init__(self):
		super().__init__(87)
		self.blobbo = None
		self.active = False
		self.ignoreFirst = True
		self.is_moved = False

	def enter(self, mycoord, coord):
		nexttile = self.level.getTile(coord)
		# print(nexttile,  self.level.getTile(mycoord))
		if self.floor_tile.is_water():
			# print("on raft")
			# self.level.switch_top(mycoord, coord)
			self.blobbo = self.level.getTile(coord).remove_top()
			self.blobbo.floor_tile = self
			self.render()
			self.active = True

		else:
			# self.level.push(coord, mycoord)
			coord3 = 2*mycoord[0] - coord[0], 2*mycoord[1] - coord[1]
			# print("raft", coord3, mycoord, coord)
			self.level.switch_top(mycoord, coord3)
			self.level.switch_top(coord, mycoord)
			
		return True
	
	def leave(self, mycoord, coord):
		# print("leave water")
		nexttile = self.level.getTile(coord)
		nexttile.put_top(self.blobbo)
		self.blobbo = None
		self.render()
		return False
	
	def move_sprite(self):
		# print("raft",self.is_moved )
		if self.is_moved:
			return
		if not self.floor_tile.is_water():
			return
		if not self.active:
			return
		if self.ignoreFirst:
			self.ignoreFirst = False
			return
		dir =  self.floor_tile.get_dir()
		# print("raft dir ", dir, self.floor_tile)
		if dir > 0:
			coord = self.level.move_coord(dir, self.get_coord())
			self.level.switch_top(self.get_coord(), coord)
		if self.floor_tile.is_sink():
			print("byebye")
			if self.blobbo:
				self.level.die()
			self.floor_tile.remove_top()
		self.is_moved = True

	
	def render(self):
		if self.blobbo:
			self.level.renderTile128(self.get_coord(), 113)
		elif self.floor_tile.is_water():
			self.level.renderTile128(self.get_coord(), 87)
		else:
			self.level.renderTile128(self.get_coord(), 199)

class TeleportTargetTile(TopTile):
	def __init__(self):
		super().__init__(57)
	def is_teleport_target(self):
		return True

class TeleportTile(TopTile):
	def __init__(self):
		super().__init__(41)
	def enter(self, mycoord, coord):
		for coordi, tile in self.level.tiles.items():
			if tile.is_teleport_target():
				tile.remove_top()
				self.level.getTile(mycoord).remove_top()
				self.level.switch_top(coord, tile.coord)
		return True
	

class spiderTile(TopTile):
	def __init__(self, id):
		super().__init__(id)
		self.dir = 8
		self.is_moved = False

	def move_sprite(self):
		if self.is_moved: # move me only once each round
			return
		nextDir={6:2, 2:4, 4:8, 8:6}
		dir = self.dir
		coord = None
		while True:
			coord = self.level.move_coord(dir, self.get_coord())
			tile = self.level.getTile(coord)
			if tile.topTile and tile.topTile.__class__.__name__ == "spiderWebTile":
				tile.remove_top()
				self.floor_tile.remove_top()
				self.floor_tile.put_top(ChestTile())
				return
			if tile.is_free():
				self.dir = dir
				break
			dir = nextDir[dir]
			if dir == self.dir:
				return
		self.level.switch_top(self.get_coord(), coord)
		self.is_moved = True

	# def touch(self, coord):
	# 	self.level.die()
	
class spiderWebTile(TopTile):
	def enter(self, mycoord, coord):
		return False
	
class sunTile(TopTile):
	def __init__(self, id):
		super().__init__(id)
		self.is_moved = False

	def move_sprite(self):
		if self.level.item == "glasses":
			return
		if self.is_moved: # move me only once each round
			return
		coord = self.get_coord()
		blobbo = self.level.blobbo.get_coord()
		if blobbo[0] > coord[0]:
			coord = (coord[0] + 1, coord[1])
		elif blobbo[0] < coord[0]:
			coord = (coord[0] - 1, coord[1])
		if blobbo[1] > coord[1]:
			coord = (coord[0], coord[1] + 1)
		elif blobbo[1] < coord[1]:
			coord = (coord[0], coord[1] - 1)
		# print(self.get_coord(), coord, blobbo)
		coord1 = (coord[0], self.get_coord()[1])
		coord2 = (self.get_coord()[0], coord[1])

		for coord in [coord, coord1, coord2]:
			tile = self.level.getTile(coord)
			if tile.is_blobbo():
				self.level.die()
			if tile.__class__.__name__ == "holeTile":
				self.floor_tile.remove_top()
				return
			if tile.is_free():
				self.level.switch_top(self.get_coord(), coord)
				self.is_moved = True
				return

	# def touch(self, coord):
	# 	self.level.die()


	
class rollerScateTile(TopTile):
	def enter(self, mycoord, coord):
		ofs = mycoord[0] - coord[0], mycoord[1] - coord[1]
		print(mycoord, coord, ofs)

		coord = mycoord
		while True:
			coord = (coord[0] + ofs[0], coord[1] + ofs[1])
			tile = self.level.getTile(coord)
			print(tile)
			if tile.is_free():
				print(self.get_coord(), coord)
				self.level.switch_top(self.get_coord(), coord)
				self.level.game.updateScreen()
				time.sleep(0.02)
			else:
				break
		return True
	
class glassesTile(TopTile):
	def enter(self, mycoord, coord):
		self.level.collect_item("glasses")
		self.floor_tile.remove_top()
		self.level.switch_top(mycoord, coord)
		return True
	
class halveChestTile(TopTile):
	def __init__(self, id, left):
		super().__init__(id)
		self.left = left
	
	def enter(self, mycoord, coord):
		coord3 = 2*mycoord[0] - coord[0], 2*mycoord[1] - coord[1]
		print(mycoord, coord, coord3)
		tile = self.level.getTile(coord3)
		
		if tile.is_free():
			self.level.switch_top(coord3, mycoord)
			self.level.switch_top(mycoord, coord)
		if tile.topTile and tile.topTile.__class__.__name__ == "halveChestTile":
			if self.left != tile.topTile.left:
				tile.remove_top()
				self.level.getTile(mycoord).remove_top()
				tile.put_top(ChestTile())
				self.level.switch_top(mycoord, coord)




	