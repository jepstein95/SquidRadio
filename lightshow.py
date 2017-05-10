#!/usr/bin/env python

import argparse
import atexit
import csv
import fcntl
import json
import logging
import os
import random
import subprocess
import sys
import wave
import time
import threading
import serial

import alsaaudio as aa
import fft
import decoder
import numpy as np

from configobj import ConfigObj

CHANNEL_LEN = 5
CHANNEL_MAX = 1
NUM_LEDS = 56
LED_DELAY = 50
CHANNEL_DELAY = 200

CHUNK_SIZE = 1024
AUDIO_IN_SAMPLE_RATE = 44100
AUDIO_IN_CHANNELS = 2
AUDIO_IN_CARD  = 'hw:1'

preferred_channels = [False] * CHANNEL_LEN

def listen():
    while True:
        inp = raw_input()
        if inp == 'kill':
            os._exit(0)

def init():
    global serial_port, light_lock, channel_lock
    serial_port = serial.Serial('/dev/ttyACM0', 115200)
    light_lock = False
    channel_lock = False
    send_list([(0, 0, 0)] * NUM_LEDS)
    threading.Thread(target=listen, args=()).start()
    atexit.register(clean_up)

def clean_up():
    send_list([(0, 0, 0)] * NUM_LEDS)
    os._exit(0)

def get_config():
    dir = os.path.dirname(__file__)
    if not os.path.exists(os.path.join(dir, 'config/temp.ini')):
        if not os.path.exists(os.path.join(dir, 'config/overrides.ini')):
            if not os.path.exists(os.path.join(dir, 'config/defaults.ini')):
                print 'No config files found'
                sys.exit()
            else:
                config = ConfigObj(os.path.join(dir, 'config/defaults.ini'))
        else:
            config = ConfigObj(os.path.join(dir, 'config/overrides.ini'))
    else:
        config = ConfigObj(os.path.join(dir, 'config/temp.ini'))

    return config

def get_channel_frequencies(config):
    channel_freqs = []
    channels = [config[key] for key in config.keys()]
    for channel in channels:
        low = int(channel['min'])
        hi  = int(channel['max'])
        channel_freqs.append((low, hi))
    return channel_freqs

def schedule_lights(delay):
    global light_lock
    light_lock = True
    time.sleep(delay * (1 / 1000))
    light_lock = False

def schedule_channels(delay):
    global channel_lock
    channel_lock = True
    time.sleep(delay * (1 / 1000))
    channel_lock = False

def update_lights(matrix, mean, std, config):
    global preferred_channels
    global light_lock, channel_lock

    leds = [(0, 0, 0)] * NUM_LEDS
    channels = [config[key] for key in config.keys()]
    channels_set = [False] * CHANNEL_LEN

    # Iterate through channels. Since we can only show a limited number of channels at one time, sort by rank
    for channel in sorted(channels, key=lambda x: int(x['rank'])):
        
        # Make sure we are referencing the correct index for matrix, mean, and std
        i = channels.index(channel)
        stickiness = 0.5 if preferred_channels[i] else 1.5
        brightness = matrix[i] - mean[i]
        if brightness < 0:
            brightness = 0
        else:
            brigthness = brightness / (stickiness * std[i])
            if brightness > 1.0:
                brightness = 1.0

        if int(channel['max']) - int(channel['min']) < 10:
            continue

        # Turn on channel if brightness exceeds the given threshold   
        if brightness > float(channel['threshold']) and len([x for x in channels_set if x]) < CHANNEL_MAX:
            channels_set[i] = True
            color = tuple([int(float(x) * .2) for x in channel['color']])
            for index in channel['leds']:
                if int(index) - 1 < NUM_LEDS:
                    leds[int(index) - 1] = color

    if not channel_lock:
        preferred_channels = channels_set
        channel_thread = threading.Thread(target=schedule_channels, args=(CHANNEL_DELAY,))
        channel_thread.start()

    if not light_lock:
        send_list(leds)
        light_thread = threading.Thread(target=schedule_lights, args=(LED_DELAY,))
        light_thread.start() 

def send_list(leds):
    if len(leds) > NUM_LEDS:
        raise RuntimeError('Attempting to set pixel outside of range')

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
    global serial_port
    serial_port.write(data)
    serial_port.flush()
    serial_port.flushInput()

def audio_in():
    stream = aa.PCM(aa.PCM_CAPTURE, aa.PCM_NORMAL, AUDIO_IN_CARD)
    stream.setchannels(AUDIO_IN_CHANNELS)
    stream.setformat(aa.PCM_FORMAT_S16_LE)
    stream.setrate(AUDIO_IN_SAMPLE_RATE)
    stream.setperiodsize(CHUNK_SIZE)
         
    print "Running in audio-in mode, use Ctrl+C to stop"
    try:

        # Start with these as our initial guesses - will calculate a rolling mean / std 
        # as we get input data.
        mean = [12.0 for _ in range(CHANNEL_LEN)]
        std = [0.5 for _ in range(CHANNEL_LEN)]
        recent_samples = np.empty((250, CHANNEL_LEN))
        num_samples = 0
    
        while True:            
            l, data = stream.read()

            config = get_config()
            frequency_limits = get_channel_frequencies(config)

            if len(frequency_limits) != CHANNEL_LEN:
                continue
            
            if l:
                try:
                    matrix = fft.calculate_levels(data,
                                                  CHUNK_SIZE,
                                                  AUDIO_IN_SAMPLE_RATE,
                                                  frequency_limits,
                                                  CHANNEL_LEN,
                                                  AUDIO_IN_CHANNELS)
                    if not np.isfinite(np.sum(matrix)):
                        # Bad data --- skip it
                        continue
                except ValueError as e:
                    continue

                update_lights(matrix, mean, std, config)

                #Keep track of the last N samples to compute a running std / mean
                if num_samples >= 250:
                    no_connection_ct = 0
                    for i in range(0, CHANNEL_LEN):
                        mean[i] = np.mean([item for item in recent_samples[:, i] if item > 0])
                        std[i] = np.std([item for item in recent_samples[:, i] if item > 0])
                        
                        # Count how many channels are below 5, 
                        # if more than 1/2, assume noise (no connection)
                        if mean[i] < 5.0:
                            no_connection_ct += 1
                            
                    # If more than 1/2 of the channels appear to be not connected, turn all off
                    #if no_connection_ct > CHANNEL_LEN / 2:
                    if no_connection_ct > CHANNEL_LEN - 1:
                        mean = [20 for _ in range(CHANNEL_LEN)]

                    num_samples = 0
                else:
                    for i in range(0, CHANNEL_LEN):
                        recent_samples[num_samples][i] = matrix[i]
                    num_samples += 1
 
    except KeyboardInterrupt:
        pass
    finally:
        print "\nStopping"
        clean_up()

if __name__ == "__main__":
    init()
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help='Song to play.')
    args = parser.parse_args()
    if args.file:
        play_song(args.file)
    else:
        audio_in()
