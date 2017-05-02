#!/usr/bin/python

from Tkinter import *
from channel import Channel

from configobj import ConfigObj

import os
import shutil
import filecmp
import tkMessageBox

def init():
	if not os.path.exists('config/overrides.ini'):
		if not os.path.exists('config/default.ini'):
			print 'No config files found'
			sys.exit()
		shutil.copy('config/default.ini', 'config/overrides.ini')
	shutil.copy('config/overrides.ini', 'config/temp.ini')
	global config
	config = ConfigObj('config/temp.ini')

def main():
	if not config:
		print 'Cannot open config'
		sys.exit()
	global root
	root = Tk()
	root.notify = notify
	for c in config.keys():
		channel = Channel(root, c, config[c]['rank'], config[c]['threshold'], config[c]['color'], config[c]['leds'])
	root.geometry('800x300+200+200')
	root.title('SquidRadio Config')
	menu = Menu(root)
	menu.add_command(label='Save', command=save)
	menu.add_command(label='Quit', command=exit)
	root.config(menu=menu)
	root.protocol('WM_DELETE_WINDOW', exit)
	root.mainloop()

def notify(channel, attr, val):
	config[channel][attr] = val
	config.write()

def save():
	shutil.copy('config/temp.ini', 'config/overrides.ini')

def exit():
	if not filecmp.cmp('config/temp.ini', 'config/overrides.ini'):
		result = tkMessageBox.askyesno('Quit', 'Save changes?', icon='warning')
		if result:
			save()
	os.remove('config/temp.ini')
	root.destroy()

if __name__ == '__main__':
    init()
    main()