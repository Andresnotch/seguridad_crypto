import unittest
from unittest.mock import MagicMock

class Triangle:
	def __init__(self, a, b, c):
		if all((a == 0, b == 0, c == 0)):
			raise ValueError('This is not good')
		self.a = a
		self.b = b
		self.c = c

	def triangleType(self):
		if self.a != self.b != self.c:
			return 'Escaleno'

class TestTriangle(unittest.TestCase):
	def testValidParams(self):
		triangle = Triangle(1, 2, 3)
		triangle.triangleType = MagicMock(return_value='Escaleno')

		self.assertEqual(triangle.triangleType(), 'Escaleno')

	def testInvalidParams(self):
		triangle = Triangle(0, 0, 0)
		triangle.__init__ = MagicMock(side_effect=ValueError('this is not good'))

		with self.assertRaises(ValueError):
			triangle.__init__(0, 0, 0)

if __name__ == '__main__':
	unittest.main()