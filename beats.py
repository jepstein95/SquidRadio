import blinkytile

bt = blinkytile.BlinkyTile("/dev/ttyACM0", 56)
bt.send_list([(0, 0, 0)]*56)
bt.show()

import fft
import alsaaudio as aa

from numpy import sum as npsum
from numpy import abs as npabs
from numpy import roll as nproll
from numpy import log10, frombuffer, empty, hanning, fft, delete, int16, zeros

MIN_FREQUENCY = 0
MAX_FREQUENCY = 15000

CHANNEL_LEN = 5
CHANNEL_MAX = 1
NUM_LEDS = 56
LED_DELAY = 50
CHANNEL_DELAY = 200

CHUNK_SIZE = 1024
NUM_SUB_BANDS = 32
LEN_SUB_BANDS = CHUNK_SIZE / NUM_SUB_BANDS
LEN_HIST_BUF = 43
C = 250

AUDIO_IN_SAMPLE_RATE = 44100
AUDIO_IN_CHANNELS = 1
AUDIO_IN_CARD  = 'hw:2'

def detect_beat(data, chunk_size, sample_rate, input_channels, E):
    """Calculate frequency response for each channel defined in frequency_limits

    :param data: decoder.frames(), audio data for fft calculations
    :type data: decoder.frames

    :param chunk_size: chunk size of audio data
    :type chunk_size: int

    :param sample_rate: audio file sample rate
    :type sample_rate: int

    :param frequency_limits: list of frequency_limits
    :type frequency_limits: list

    :param num_bins: length of gpio to process
    :type num_bins: int

    :param input_channels: number of audio input channels to process for (default=2)
    :type input_channels: int

    :return:
    :rtype: numpy.array
    """

    # create a numpy array, taking just the left channel if stereo
    data_stereo = frombuffer(data, dtype=int16)
    if input_channels == 2:
        # data has 2 bytes per channel
        data = empty(len(data) / (2 * input_channels))

        # pull out the even values, just using left channel
        data[:] = data_stereo[::2]
    elif input_channels == 1:
        data = data_stereo

    # if you take an FFT of a chunk of audio, the edges will look like
    # super high frequency cutoffs. Applying a window tapers the edges
    # of each end of the chunk down to zero.
    data = data * hanning(len(data))

    #fourier = fft.fft(data)

    # Apply FFT - real data
    fourier = fft.rfft(data)

    # Remove last element in array to make it the same size as chunk_size
    fourier = delete(fourier, len(fourier) - 1)

    # Calculate the power spectrum
    power = npabs(fourier) ** 2

    Es = zeros(NUM_SUB_BANDS, dtype='float64')

    for i in range(NUM_SUB_BANDS):
    	sum = 0
    	for k in range(LEN_SUB_BANDS):
    		sum = sum + power[i * k]
    	Es[i] = float(NUM_SUB_BANDS) / CHUNK_SIZE * sum

    	hist_buf = E[i]
    	nproll(hist_buf, 1)
    	hist_buf[0] = Es[i]
    	E[i] = hist_buf

   	for i in range(NUM_SUB_BANDS):
   		avg_en = 0
   		for k in range(1,LEN_HIST_BUF):
   			avg_en = avg_en + E[i][k]
   		avg_en = float(1) / LEN_HIST_BUF * avg_en
   		if E[i][0] < (C * avg_en):
   			return False
    return True

def audio_in():
    stream = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, AUDIO_IN_CARD)
    stream.setchannels(AUDIO_IN_CHANNELS)
    stream.setformat(aa.PCM_FORMAT_S16_LE)
    stream.setrate(AUDIO_IN_SAMPLE_RATE)
    stream.setperiodsize(CHUNK_SIZE)
         
    print "Running in audio-in mode, use Ctrl+C to stop"
    try:
    	E = zeros((NUM_SUB_BANDS, LEN_HIST_BUF), dtype='float64')
    
        while True:            
            l, data = stream.read()
            
            if l:
            	try:
                    list = [(0, 0, 0)] * 56

                    if detect_beat(data, CHUNK_SIZE, AUDIO_IN_SAMPLE_RATE, AUDIO_IN_CHANNELS, E):
                        list[55] = (100,100,100)
                        print '#'
                    else:
                        print 'poop'

                    bt.send_list(list)
                    bt.show()	

                except ValueError as e:
                	continue
 
    except KeyboardInterrupt:
        pass
    finally:
        print "\nStopping"

if __name__ == "__main__":
  audio_in()