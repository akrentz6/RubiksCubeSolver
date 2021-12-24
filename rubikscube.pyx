# cython: language_level=3
# distutils: define_macros=NPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION
# cython: boundscheck=False, wraparound=False, nonecheck=False

from libc.stdlib cimport rand
from libc.string cimport memset, strcmp, memcpy

"""
======================

   Global Variables

======================
"""

ctypedef unsigned long long U64

cdef enum:
	up, left, front, right, back, down

cdef enum:
	U, L, F, R, B, D, u, l, f, r, b, d, U2, L2, F2, R2, B2, D2

cdef:
	char* solved_cube = "OOOOOOOOGGGGGGGGWWWWWWWWBBBBBBBBYYYYYYYYRRRRRRRR"
	char* moves[18]
	char colours[6]
	char indices[8]

# lists of moves and colours for when the cube or move is inputted
colours[:] = [ord("O"), ord("G"), ord("W"), ord("B"), ord("Y"), ord("R")]
moves[:] = ["U", "L", "F", "R", "B", "D", # clockwise
			"U'", "L'", "F'", "R'", "B'", "D'", # anti-clockwise
			"U2", "L2", "F2", "R2", "B2", "D2" # rotate twice
]
indices[:] = [0, 1, 2, 7, 3, 6, 5, 4]

# Represents a list of moves made
cdef struct MoveStack:

	int moves[10000]
	int count

"""
======================

   Bit Manipulation

======================
"""

# http://graphics.stanford.edu/~seander/bithacks.html

cdef U64 set_bit(U64 bitboard, char offset):
	return bitboard | <U64> 1 << offset

cdef U64 get_bit(U64 bitboard, char offset):
	return bitboard & <U64> 1 << offset

cdef U64 get_bits(U64 bitboard, char offset, char len):
	return <U64> (bitboard & <U64> ((2 ** len) - 1) << offset) >> offset
	
cdef U64 set_bits(U64 bitboard, char offset, U64 new, char len):
	cdef U64 mask = (<U64> 2 ** len - 1) << offset
	return (bitboard & ~mask) | (new << offset)

cdef U64 swap_bits(U64 bitboard, char i0, char i1):
	cdef U64 temp = ((bitboard >> i0) ^ (bitboard >> i1)) & 1
	return bitboard ^ ((temp << i0) | (temp << i1))

cdef U64 rotate_bits(U64 bitboard, char i0, char i1, char i2, char i3):
	cdef char temp = i0
	bitboard = swap_bits(bitboard, i0, i3)
	bitboard = swap_bits(bitboard, i3, i2)
	bitboard = swap_bits(bitboard, i2, i1)
	bitboard = swap_bits(bitboard, i0, temp)
	return bitboard

cdef U64 rotate_bits_twice(U64 bitboard, char i0, char i1, char i2, char i3, char i4, char i5):
	bitboard = swap_bits(bitboard, i0, i3)
	bitboard = swap_bits(bitboard, i1, i4)
	bitboard = swap_bits(bitboard, i2, i5)
	return bitboard

"""
======================

    Representation

======================
"""

# Sides:
#   U                W
# L F R B    ->    G R B O
#   D                Y

# Indices:
#           0  1  2
#           7     3
#           6  5  4
# 8  9  10  16 17 18  24 25 26 32 33 34
# 15    11  23    19  31    27 39    35
# 14 13 12  22 21 20  30 29 28 38 37 36
# 			40 41 42
# 			47    43
# 			46 45 44

cdef class Cube:
	
	cdef:
		U64 bitboard[6]
		MoveStack stack

	def __init__(self, char* str_repr = solved_cube, blank = False):
		
		memset(self.stack.moves, 0, 40000)
		self.stack.count = 0

		if not blank:
			self.parse_str(str_repr)
	
	cdef parse_str(self, char* str_repr):

		cdef:
			int i, j, k

		memset(self.bitboard, 0, 48)

		for i in range(6):

			for j in range(8):

				for k in range(6):

					if str_repr[(i * 8) + j] == colours[k]:

						self.bitboard[k] = set_bit(self.bitboard[k], (i * 8) + indices[j])
						break
	
	cpdef void take_back(self):

		if not self.stack.count:
			return

		cdef char last = self.stack.moves[self.stack.count - 1]
		self.parse_int_move(self.reverse(last))
		
		self.stack.moves[self.stack.count - 1] = 0
		self.stack.moves[self.stack.count - 2] = 0
		self.stack.count -= 2

	cpdef void parse_move(self, char* inp):

		self.parse_int_move(moves.index(inp))
	
	cpdef void parse_int_move(self, int inp):

		if inp == U:
			self.U()
		elif inp == L:
			self.L()
		elif inp == F:
			self.F()
		elif inp == R:
			self.R()
		elif inp == B:
			self.B()
		elif inp == D:
			self.D()
		elif inp == u:
			self.u()
		elif inp == l:
			self.l()
		elif inp == f:
			self.f()
		elif inp == r:
			self.r()
		elif inp == b:
			self.b()
		elif inp == d:
			self.d()
		elif inp == U2:
			self.U2()
		elif inp == L2:
			self.L2()
		elif inp == F2:
			self.F2()
		elif inp == R2:
			self.R2()
		elif inp == B2:
			self.B2()
		elif inp == D2:
			self.D2()
	
	cpdef char get_colour(self, char index):

		cdef int i

		for i in range(6):

			if get_bit(self.bitboard[i], index):
			
				return i
	
	cpdef bint is_solved(self):

		return not strcmp(self.as_str().encode("utf-8"), solved_cube)

	cpdef str as_str(self):

		cdef:
			int i, j, k
			str cube = ""

		for i in range(6):

			for j in range(8):

				for k in range(6):
					
					if get_bit(self.bitboard[k], (i * 8) + indices[j]):

						cube += chr(colours[k])
		
		return cube
	
	cdef int reverse(self, int move):

		if move >= 12:
			return move
		
		elif move >= 6:
			return move - 6
		
		else:
			return move + 6
	
	cpdef int randomise(self, int depth):

		cdef:
			int i, new
			int prev = -1
		
		for i in range(depth):

			while True:

				new = rand() % 18

				if prev == -1 or new != self.reverse(prev):

					self.parse_int_move(new)

					prev = new
					break

		return self.reverse(new)
	
	cpdef hot_encode(self):

		cdef:
			int i
			int encoded[1][288]

		memset(encoded, 0, 1152)
		
		for i in range(48):

			encoded[i * 6 + self.get_colour(i)] = 1
		
		return encoded
	
	cpdef Cube copy(self):

		cdef Cube cube_copy = Cube(blank = True)

		memcpy(cube_copy.bitboard, self.bitboard, 48)
		memcpy(cube_copy.stack.moves, self.stack.moves, 40000)
		cube_copy.stack.count = self.stack.count

		return cube_copy


	cdef rotate(
		self, char move, char face, bint clockwise, 
		int l0, int l1, int l2, int l3, 
		int c0, int c1, int c2, int c3,
		int r0, int r1, int r2, int r3):

		cdef:
			int i
			unsigned char n
		
		for i in range(6):

			# rotate face:

			n = <unsigned char> (get_bits(self.bitboard[i], face * 8, 8))

			if clockwise:
				n = (n << 2) | (n >> (8 - 2))
			else:
				n = (n >> 2) | (n << (8 - 2)) & 0xff

			self.bitboard[i] = set_bits(self.bitboard[i], face * 8, <U64> n, 8)

			# Rotate sides:

			self.bitboard[i] = rotate_bits(self.bitboard[i], l0, l1, l2, l3)
			self.bitboard[i] = rotate_bits(self.bitboard[i], c0, c1, c2, c3)
			self.bitboard[i] = rotate_bits(self.bitboard[i], r0, r1, r2, r3)

		# add move to stack:

		self.stack.moves[self.stack.count] = move
		self.stack.count += 1

	cdef void rotate_twice(
		self, char move, char face, 
		int i0, int i1, int i2, int i3, int i4, int i5,
		int j0, int j1, int j2,	int j3, int j4, int j5):
		
		cdef:
			int i
			unsigned char n
			U64 mask, a, b
		
		for i in range(6):

			# rotate face:

			n = <unsigned char> (get_bits(self.bitboard[i], face * 8, 8))
			n = (n << 4) | (n >> (8 - 4))

			self.bitboard[i] = set_bits(self.bitboard[i], face * 8, <U64> n, 8)

			# swap 1st/3rd and 2nd/4th faces:

			self.bitboard[i] = rotate_bits_twice(self.bitboard[i], i0, i1, i2, i3, i4, i5)
			self.bitboard[i] = rotate_bits_twice(self.bitboard[i], j0, j1, j2, j3, j4, j5)

		# add move to stack:

		self.stack.moves[self.stack.count] = move
		self.stack.count += 1

	cdef void U(self):

		self.rotate(U, up, True, 8, 32, 24, 16, 9, 33, 25, 17, 10, 34, 26, 18)

	cdef void u(self):

		self.rotate(u, up, False, 8, 16, 24, 32, 9, 17, 25, 33, 10, 18, 26, 34)
	
	cdef void U2(self):
		self.rotate_twice(U2, up, 8, 9, 10, 24, 25, 26, 16, 17, 18, 32, 33, 34)

	cdef void L(self):

		self.rotate(L, left, True, 0, 16, 40, 36, 7, 23, 47, 35, 6, 22, 46, 34)

	cdef void l(self):

		self.rotate(l, left, False, 0, 36, 40, 16, 7, 35, 47, 23, 6, 34, 46, 22)
	
	cdef void L2(self):
		self.rotate_twice(L2, left, 0, 7, 6, 40, 47, 46, 16, 23, 22, 36, 35, 34)

	cdef void F(self):

		self.rotate(F, front, True, 6, 24, 42, 12, 5, 31, 41, 11, 4, 30, 40, 10)
	
	cdef void f(self):

		self.rotate(f, front, False, 6, 12, 42, 24, 5, 11, 41, 31, 4, 10, 40, 30)
	
	cdef void F2(self):
		self.rotate_twice(F2, front, 6, 5, 4, 42, 41, 40, 24, 31, 30, 12, 11, 10)

	cdef void R(self):

		self.rotate(R, right, True, 2, 38, 42, 18, 3, 39, 43, 19, 4, 32, 44, 20)

	cdef void r(self):

		self.rotate(r, right, False, 2, 18, 42, 38, 3, 19, 43, 39, 4, 20, 44, 32)
	
	cdef void R2(self):
		self.rotate_twice(R2, right, 2, 3, 4, 42, 43, 44, 18, 19, 20, 38, 39, 32)

	cdef void B(self):

		self.rotate(B, back, True, 0, 14, 44, 26, 1, 15, 45, 27, 2, 8, 46, 28)

	cdef void b(self):

		self.rotate(b, back, False, 0, 26, 44, 14, 1, 27, 45, 15, 2, 28, 46, 8)
	
	cdef void B2(self):
		self.rotate_twice(B2, back, 2, 1, 0, 46, 45, 44, 28, 27, 26, 8, 15, 14)

	cdef void D(self):

		self.rotate(D, down, True, 12, 20, 28, 36, 13, 21, 29, 37, 14, 22, 30, 38)

	cdef void d(self):

		self.rotate(d, down, False, 12, 36, 28, 20, 13, 37, 29, 21, 14, 38, 30, 22)
	
	cdef void D2(self):
		self.rotate_twice(D2, down, 14, 13, 12, 30, 29, 28, 22, 21, 20, 38, 37, 36)
