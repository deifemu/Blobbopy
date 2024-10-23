import pygame
import pygame.locals
import copy
import json
import sys
import time

from topTiles import *


def makeTile(level, coord, id):
	if id == 0:
		lvl = FreeTile()
	elif id == 112:
		lvl =  FreeTile() # blobbo
		b = BlobboTile()
		lvl.put_top(b)
		level.set_blobbo(b)
	elif id == 128:
		level.add_chest()
		lvl =  FreeTile()
		lvl.put_top(ChestTile())
	elif id == 192:
		lvl =  FreeTile()
		lvl.put_top(BallTile())
	elif id == 194:
		lvl =  FreeTile()
		lvl.put_top(ArrowTile(False))
	elif id == 195:
		lvl =  FreeTile()
		lvl.put_top(ArrowTile(True))
	elif id == 40:
		lvl =  FireTile(id)
	elif id == 41:
		lvl =  FreeTile()
		lvl.put_top(TeleportTile())
	elif id == 47:
		lvl =  EndTile(id)
	elif id == 63:
		lvl =  EndTile(id, hidden=True)
	elif id == 57:
		lvl =  FreeTile()
		lvl.put_top(TeleportTargetTile())
	elif id in list(range(1,33)) + list(range(224, 241)):
		lvl =  WallTile(id)
	elif id in [38, 39]:
		lvl =  WallTile(id, slope_left=(id==38), slope_right=(id==39))
	elif id == 132:
		lvl =  FreeTile()
		lvl.put_top(AxTile(id))
	elif id == 51:
		lvl =  FreeTile()
		lvl.put_top(TreeTile(id))

	elif id == 199:
		lvl =  FreeTile()
		lvl.put_top(RaftTile())

	elif id == 89:
		lvl =  FreeTile()
		lvl.put_top(WeedTile(id, 8))
	elif id == 90:
		lvl =  FreeTile()
		lvl.put_top(WeedTile(id, 6))
	elif id == 91:
		lvl =  FreeTile()
		lvl.put_top(WeedTile(id, 2))
	elif id == 92:
		lvl =  FreeTile()
		lvl.put_top(WeedTile(id, 4))
	elif id == 209:
		lvl =  FreeTile()
		lvl.put_top(PushStoneTile(id))
	elif id == 197: # hidden 
		lvl =  FreeTile()
		lvl.put_top(PushStoneTile(id))
	elif id == 104:
		lvl =  FreeTile()
		lvl.put_top(SmileTile(id))
	elif id == 80:
		lvl =  WaterTile(id, 0)
	elif id == 81:
		lvl =  WaterTile(id, 6) # right
	elif id == 82:
		lvl =  WaterTile(id, 2) # up
	elif id == 83:
		lvl =  WaterTile(id, 4) # left
	elif id == 84:
		lvl =  WaterTile(id, 8)  # down
	elif id == 85:
		lvl =  WaterTile(id, 99)  # sink

	elif id == 126:
		lvl =  FreeTile()
		lvl.put_top(spiderTile(id))
	elif id == 60:
		lvl =  FreeTile()
		lvl.put_top(spiderWebTile(id))
		level.add_chest()
	elif id == 196:
		lvl =  FreeTile()
		lvl.put_top(rollerScateTile(id))
	elif id == 127:
		lvl =  FreeTile()
		lvl.put_top(sunTile(id))
	elif id == 133:
		lvl =  FreeTile()
		lvl.put_top(glassesTile(id))
	elif id == 33:
		lvl =  oneWayTile(id, 6)
	elif id == 34:
		lvl =  oneWayTile(id, 2)
	elif id == 35:
		lvl =  oneWayTile(id, 4)
	elif id == 36:
		lvl =  oneWayTile(id, 8)
	elif id == 58:
		lvl =  FreeTile()
		lvl.put_top(holeTile(id))
	elif id == 86:
		lvl =  iceTile(id)
	elif id == 207:
		lvl =  FreeTile()
		lvl.put_top(halveChestTile(id, True))
		level.add_chest()
	elif id == 223:
		lvl =  FreeTile()
		lvl.put_top(halveChestTile(id, False))
	elif id in [117, 118, 119, 120, 121, 122, 123, 124]:
		lvl =  FreeTile()
		lvl.put_top(snailTile(id))
		level.add_chest()
	elif id == 50:
		lvl =  FreeTile()
		lvl.put_top(tvTile(id))
	elif id == 103:
		lvl =  FreeTile()
		lvl.put_top(multyArrowTile(id))
	elif id == 210:
		lvl =  FreeTile()
		lvl.put_top(plugTile(id))
	elif id == 129:
		lvl =  FreeTile()
		lvl.put_top(keyTile(id))
	elif id == 37:
		lvl =  FreeTile()
		lvl.put_top(DoorTile(id))
	elif id == 193:
		lvl =  FreeTile()
		lvl.put_top(bloonTile(id))

	else:
		print(f"unknown tile {id}")
		lvl =  Tile(id)
	lvl.set_level(level)
	lvl.coord = coord
	return lvl


class Tile:
	def __init__(self, id):
		self.coord = None
		self.set_id(id)
		self.level = None
		self.topTile = None
		self.can_enter = False

	def set_id(self, id):
		self.id = id

	def set_level(self, level):
		self.level = level
		if self.topTile:
			self.topTile.set_level(level)

	def put_top(self, top):
		if self.topTile:
			print("error top already full")
		top.level = self.level
		self.topTile = top
		self.topTile.standing_on(self)
		if self.level:
			self.render()

	def remove_top(self):
		top = self.topTile
		self.topTile = None
		self.render()
		return top
	
	def get_coord(self):
		return self.coord

	def is_free(self):
		return self.can_enter and not self.topTile
	
	def is_blobbo(self):
		if not self.topTile:
			return False
		else:
			return self.topTile.is_blobbo()
		
	def is_smilie(self):
		if not self.topTile:
			return False
		else:
			return self.topTile.is_smilie()
		
	def slope_right(self):
		if not self.topTile:
			return self.can_enter
		else:
			return self.topTile.slope_right()
	def slope_left(self):
		if not self.topTile:
			return self.can_enter
		else:
			return self.topTile.slope_left()
	def is_teleport_target(self):
		if not self.topTile:
			return False
		else:
			return self.topTile.is_teleport_target()
	def is_water(self):
		return False
	
	def is_hole(self):
		if not self.topTile:
			return False
		else:
			return self.topTile.__class__.__name__ == "holeTile"


	def enter(self, coord):
		if not self.topTile:
			if self.can_enter:
				if self.level.getTile(coord).leave(self.coord):
					self.level.switch_top(self.coord, coord)
				return True
		else:
			if self.topTile.enter(self.coord, coord):
				if self.level.getTile(coord).leave(self.coord):
					self.level.switch_top(self.coord, coord)
		return False
	
	def leave(self, coord):
		# print(f"lili {self}")
		if not self.topTile:
			return True
		else:
			return self.topTile.leave(self.coord, coord)

	def touch(self, coord):
		if not self.topTile:
			return False
		else:
			return self.topTile.touch(self.coord)

	def loop(self):
		if not self.topTile:
			return False
		else:
			return self.topTile.loop(self.coord)
		
	def move_sprite(self):
		if self.topTile:
			self.topTile.move_sprite()

	def render(self):
		if not self.topTile:
			self.level.renderTile128(self.coord, self.id)
		else:
			self.topTile.render()

	def set_coord(self, level, coord):
		self.level = level
		self.coord = coord


	def __str__(self):
		if self.topTile:
			return(f"{self.__class__.__name__} {self.id} at {self.coord} with {self.topTile}")
		return(f"{self.__class__.__name__} {self.id} at {self.coord}")


	def click(self):
		print(self)




class FreeTile(Tile):
	def __init__(self):
		# self.blobbo = blobbo
		super().__init__(0)
		self.can_enter = True


class WallTile(Tile):
	def __init__(self, id, slope_left=False, slope_right=False):
		super().__init__(id)
		self._slope_left = slope_left
		self._slope_right = slope_right
	def slope_right(self):
		return self._slope_right
	def slope_left(self):
		return self._slope_left





class FireTile(Tile):
	def enter(self, coord):
		self.level.die()
		return False





class EndTile(Tile):
	def __init__(self, id, hidden=False):
		if hidden:
			super().__init__(0)
		else:
			super().__init__(id)
		self.can_enter = True
		self.hidden = hidden


	def enter(self, coord):
		if self.hidden:
			self.level.getTile(coord).leave(self.coord)
			self.level.switch_top(self.coord, coord)
			return True
		if self.level.chests == 0:
			self.level.game.next_level()
			return True
		return False
	
	def move_sprite(self):
		if self.level.chests == 0 and self.hidden:
			self.hidden = False
			self.id = 47
			self.render()

		return super().move_sprite()
		





class WaterTile(Tile):
	def __init__(self, id=80, dir=0):
		super().__init__(id)
		self.dir = dir
		self.can_enter = False
		self.debug = False
	def is_water(self):
		return True
	def enter(self, coord):
		if not self.topTile:
			print("die in water")
			self.level.die()
			return False
		super().enter(coord)

	def render(self):
		if not self.topTile:
			if self.id > 80 and self.debug:
				self.level.renderTile128(self.coord, self.id + 80)
			else:
				self.level.renderTile128(self.coord, self.id)
				
		else:
			self.topTile.render()

	def get_dir(self):
		if self.dir > 0 and self.dir < 10:
			return self.dir
		return 0

	def is_sink(self):
		return self.dir == 99
	



class oneWayTile(Tile):
	def __init__(self, id, dir):
		super().__init__(id)
		self.dir = dir

	def enter(self, coord):
		print(coord, self.get_coord())
		if ((self.dir == 4) and (coord[0] >= self.get_coord()[0])) or (
			(self.dir == 6) and (coord[0] <= self.get_coord()[0])) or (
			(self.dir == 2) and (coord[1] >= self.get_coord()[1])) or (
			(self.dir == 8) and (coord[1] <= self.get_coord()[1])):

			self.level.getTile(coord).leave(self.coord)
			self.level.switch_top(self.coord, coord)
			return True
		return False
	
	
class iceTile(Tile):
	def __init__(self, id):
		super().__init__(id)
		self.can_enter = True

	def enter(self, coord):
		ofs = self.coord[0] - coord[0], self.coord[1] - coord[1]
		print(self.coord, coord, ofs)
		self.level.switch_top(self.coord, coord)
		self.level.game.updateScreen()
		time.sleep(0.02)

		ncoord = (self.coord[0] + ofs[0], self.coord[1] + ofs[1])
		tile = self.level.getTile(ncoord)
		tile.enter(self.coord)
		return True
	


