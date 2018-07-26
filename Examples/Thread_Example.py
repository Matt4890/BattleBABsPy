from threading import Thread
import time

class ButtThread(Thread):
	def __init__(self):
		Thread.__init__(self)

	def run(self):
		while True:
			print("HaHa...")
			time.sleep(2)
			print("Butts.")
			time.sleep(5)

class CounterThread(Thread):
	def __init__(self, startCount):
		Thread.__init__(self)
		self.count = startCount

	def run(self):
		while True:
			print(self.count)
			self.count += 1
			time.sleep(1)

buttBoi = ButtThread()
buttBoi.start()
countBoi = CounterThread(0)
countBoi.start()