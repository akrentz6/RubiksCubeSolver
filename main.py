# https://builtin.com/data-science/recurrent-neural-networks-and-lstm
# https://medium.com/@benjamin.botto/implementing-an-optimal-rubiks-cube-solver-using-korf-s-algorithm-bf750b332cf9
# https://github.com/jasonrute/puzzle_cube#list-of-neural-network-puzzle-cube-solvers
# https://github.com/nicodjimenez/lstm/blob/master/lstm.py

from rubikscube import Cube

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, PathPatch
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D
from mpl_toolkits.mplot3d.art3d import pathpatch_2d_to_3d

class InteractiveCube:

	edge_colour = "#000000"  # black
	
	face_colours = [
		"#ff5800", # orange
		"#009b48", # green
		"#ffffff", # white
		"#0046ad", # blue
		"#ffd500", # yellow
		"#b71234"  # red
	]

	keys = [
		"U", "L", "F", "R", "B", "D", 
		"u", "l", "f", "r", "b", "d",
		"ctrl+u", "ctrl+l", "ctrl+f",
		"ctrl+r", "ctrl+b", "ctrl+d"]

	def __init__(self, cube = None, debug = False):

		self.cube = Cube(str_repr = cube) if cube else Cube()
		self.debug = debug
		
		plt.ion()

		self.fig = plt.figure()
		self.fig.canvas.manager.set_window_title("Rubik's Cube")
		self.fig.canvas.mpl_disconnect(self.fig.canvas.manager.key_press_handler_id)
		self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)

		self.ax = plt.axes(projection = "3d", azim = 110, elev = 20)
		self.ax.grid(False)
		self.ax.axis("off")
		
		self.ax.set_xlim(0, 3)
		self.ax.set_ylim(0, 3)
		self.ax.set_zlim(0, 3)

		self.draw()

	def on_key_press(self, event):
		
		if event.key == "t":
			self.cube.take_back()
			self.draw()
		
		elif event.key in self.keys:

			key = event.key.upper()[-1]

			if event.key.startswith("ctrl+"):
				key += "2"

			elif event.key.isupper():
				key += "'"

			self.cube.parse_move(key.encode("utf8"))
			self.draw()
	
	# Indices:
	# 0 1 2
	# 7   3
	# 6 5 4
	_face_inds = [(0,0), (0,1), (0,2), (1,2), (2,2), (2,1), (2,0), (1,0)]

	# Face index offsets:
	#  U    6
	# LFRB  0224
	#  D    4
	_face_offsets = [6, 2, 4, 4, 2, 4]

	# Faces that need text to be flipped:
	#  U    0
	# LFRB  0110
	#  D    1
	_mirror_faces = [2, 3, 5]

	# Directions:
	#  U    z
	# LFRB  xyxy
	#  D    z
	_face_dirs = ["z", "x", "y", "x", "y", "z"]

	# Flip text vertically:
	mirror = Affine2D().scale(-1, 1)

	def draw(self):

		self.ax.patches = []
		
		for i in range(6):
			
			zdir = self._face_dirs[i]
			z = 3 if i < 3 else 0
			offset = self._face_offsets[i]

			for j in range(8):

				index = (i * 8) + j

				x, y = self._face_inds[(j + offset) % 8]

				if i in [2, 3, 5]:
					x, y = y, x

				self.draw_facelet(x, y, z, zdir, self.cube.get_colour(index), index)

				if self.debug:
					
					self.draw_text(i, x, y, z, zdir, index)
			
			self.draw_facelet(1, 1, z, zdir, i, -1)

	def draw_facelet(self, x, y, z, zdir, colour, index):

		rect = Rectangle((x, y), 1, 1, facecolor=self.face_colours[colour], edgecolor=self.edge_colour)

		self.ax.add_patch(rect)
		pathpatch_2d_to_3d(rect, z = z, zdir = zdir)

	def draw_text(self, face, x, y, z, zdir, index):
		
		x += 0.25; y += 0.25
		
		if face in self._mirror_faces:

			x *= -1; x -= 0.5

		text = TextPath((x, y), str(index), size = 0.5)

		if face == 0:

			text = Affine2D().rotate_deg_around(x + 0.25, y + 0.25, 180).transform_path(text)
		
		if face in self._mirror_faces:
			
			text = self.mirror.transform_path(text)
		
		path = PathPatch(text)
		self.ax.add_patch(path)
		pathpatch_2d_to_3d(path, z = 3.1 if z else -0.1, zdir = zdir)

if __name__ == "__main__":

	mpl.rcParams["toolbar"] = "None"
	cube = InteractiveCube(cube = "".encode("utf-8"), debug = True)

	input()
	
