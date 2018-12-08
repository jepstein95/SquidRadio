import serial
import pyaudio
import numpy as np

from clist import CircularList

CHUNK = 1024
FORMAT = pyaudio.paInt16
RATE = 44100
DEVICE = 2

MIN_FREQ = 0
MAX_FREQ = 20000
CHANNELS = 4

NUM_LEDS = 120

CHANNEL_LEDS = [
	range(0, 12),
	list(reversed(range(16, 28))),
	range(32, 44),
	list(reversed(range(48, 60))),
	range(60, 72),
	list(reversed(range(76, 88))),
	range(92, 104),
	list(reversed(range(108, 120)))
]

CHANNEL_COLORS = [
	(0, 150, 255),
	(255, 100, 0),
	(150, 0, 200),
	(0, 255, 50)
]

serial_port = serial.Serial("/dev/cu.usbmodem1441")

def audio_in():
	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
					channels=2,
					rate=RATE,
					input=True,
					frames_per_buffer=CHUNK,
					input_device_index=DEVICE)

	frequency_limits = [(0, 1000), (1000, 3000), (3000, 5000), (5000, 20000)]

	samples = [CircularList(250) for i in range(CHANNELS)]

	while True:
		data = stream.read(CHUNK)

		if data != "":
			try:
				matrix = calculate_levels(data, frequency_limits)

				if not np.isfinite(np.sum(matrix)):
					continue
			
			except ValueError as e:
				continue

			for i in range(CHANNELS):
				samples[i].add(matrix[i])

			equalizer(samples, matrix)

def equalizer(samples, matrix):
	leds = [(0, 0, 0)] * NUM_LEDS

	for i in range(CHANNELS):
		channel_len = len(CHANNEL_LEDS[i])
		channel_color = CHANNEL_COLORS[i]

		val = matrix[i]
		avg = samples[i].get_avg()
		std = samples[i].get_std()

		if std == 0:
			continue

		diff = val - avg + (2 * std)
		percent = diff / (6 * std)

		if percent > 1:
			percent = 1
		elif percent < 0:
			percent = 0

		amp = int(percent * channel_len)

		for j in range(amp):
			leds[CHANNEL_LEDS[i * 2][j]] = channel_color
			leds[CHANNEL_LEDS[i * 2 + 1][j]] = channel_color

	send_list(leds)

def send_list(leds):
	if len(leds) > NUM_LEDS:
		return

	data = ""
	for r, g, b in leds:
		if r >= 255:
			r = 254
		if g >= 255:
			g = 254
		if b >= 255:
			b = 254
		data += chr(r) + chr(g) + chr(b)
	data += chr(255)

	serial_port.write(data)
	serial_port.flush()
	serial_port.flushInput()

def calculate_levels(data, frequency_limits):
	data_stereo = np.frombuffer(data, dtype=np.int16)
	data = np.empty(len(data) / CHANNELS)
	data[:] = data_stereo[::2]

	data = data * np.hanning(len(data))
	fourier = np.fft.rfft(data)
	fourier = np.delete(fourier, len(fourier) - 1)
	power = np.abs(fourier) ** 2

	matrix = np.zeros(CHANNELS, dtype='float64')

	for pin in range(CHANNELS):
		idx1 = int(CHUNK * frequency_limits[pin][0] / RATE)
		idx2 = int(CHUNK * frequency_limits[pin][1] / RATE)

		if idx1 == idx2:
			idx2 += 1

		npsums = np.sum(power[idx1:idx2:1])

		if npsums == 0:
			matrix[pin] = 0
		else:
			matrix[pin] = np.log10(npsums)

	return matrix

if __name__ == "__main__":
	audio_in()