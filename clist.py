import numpy as np

class CircularList:
	
	def __init__(self, length):
		self.length = length
		self.values = np.zeros(length)
		self.start = 0

		self.avg = 0.0
		self.std = 0.0
		self.m2n = 0.0

	def add(self, value):
		oldValue = self.values[self.start]

		self.values[self.start] = value
		self.start = (self.start + 1) % self.length

		# Welford's algorthim (new value)
		delta = value - self.avg
		self.avg += delta / (self.length + 1)
		delta2 = value - self.avg
		self.m2n += delta * delta2

		# Welford's algorithm (old value)
		delta = oldValue - self.avg
		self.avg -= delta / self.length
		delta2 = oldValue - self.avg
		self.m2n -= delta * delta2

		self.std = np.sqrt(self.m2n / self.length)

	def get(self, index):
		return self.values[(self.start + index) % self.length]

	def get_avg(self):
		return self.avg

	def get_std(self):
		return self.std
