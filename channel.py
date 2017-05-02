#!/usr/bin/python

from ttk import *
from Tkinter import *


class Channel(Frame):
  
    def __init__(self, parent, name, rank, threshold, color, leds):
        Frame.__init__(self, parent)

        self.parent = parent

        self.name = StringVar()
        self.rgb_text = StringVar()
        self.threshold = DoubleVar()
        self.rank = IntVar()
        self.color = tuple(color)
        self.leds = StringVar()
        
        self.name.set(name)
        self.rgb_text.set(self.to_string())
        self.threshold.set(threshold)
        self.rank.set(rank)
        self.leds.set(', '.join(leds))
        self.render()
        
    def render(self):
        self.style = Style()
        self.style.theme_use('default')
        self.pack(fill=BOTH, expand=1, side=LEFT)
        self.config(borderwidth=2)
        self.label = Label(self, text=self.name.get().capitalize())
        self.label.place(x=5, y=5)

        self.rgb = (
            self.scale(5,  25, self.color[0]),
            self.scale(25, 25, self.color[1]),
            self.scale(45, 25, self.color[2])
        )

        self.rgb_label = Label(self, textvariable=self.rgb_text)
        self.rgb_label.place(x=5, y=230)

        self.threshold_entry = Entry(self, width=8, justify='center', textvariable=self.threshold)
        self.threshold_label = Label(self, width=8, justify='center', text='Threshold')
        self.threshold_entry.bind('<Return>', self.update_threshold)
        self.threshold_label.place(x=65, y=30)
        self.threshold_entry.place(x=65, y=50)

        self.canvas = Canvas(self, width=70, height=70)
        self.canvas.place(x=65, y=80)

        self.rank_entry = Spinbox(self, width=7, from_=1, to=5, justify='center', textvariable=self.rank, command=self.update_rank)
        self.rank_label = Label(self, width=8, justify='center', text='Rank')
        self.rank_label.place(x=65, y=160)
        self.rank_entry.place(x=65, y=180)

        self.leds_entry = Entry(self, width=18, justify='center', textvariable=self.leds)
        self.leds_label = Label(self, width=8, justify='left', text='Leds')
        self.leds_entry.bind('<Return>', self.update_leds)
        self.leds_label.place(x=5, y=250)
        self.leds_entry.place(x=5, y=270)

        self.update_color(0)
        self.update_threshold(0)

    def scale(self, x, y, val):
        scale = Scale(self, from_=0, to=255, orient=VERTICAL, length=200, showvalue=0, command=self.update_color)
        scale.set(val)
        scale.place(x=x, y=y)
        return scale

    def update_color(self, val):
        self.color = tuple(x.get() for x in self.rgb)
        self.rgb_text.set(self.to_string())
        self.canvas.create_oval(10, 10, 60, 60, outline='black', width=3, fill=self.to_color())
        self.parent.notify(self.name.get(), 'color', tuple(int(x.get()) for x in self.rgb))

    def update_threshold(self, val):
        val = float(self.threshold_entry.get())
        if val > 1:
            val = 1
        if val < 0:
            val = 0
        self.threshold.set(val)
        self.parent.notify(self.name.get(), 'threshold', self.threshold.get())

    def update_rank(self):
        self.parent.notify(self.name.get(), 'rank', self.rank.get())

    def update_leds(self, val):
        self.parent.notify(self.name.get(), 'leds', self.leds.get().split(', '))

    def to_color(self):
        return '#%02x%02x%02x' % self.color

    def to_string(self):
        return '(' + ', '.join(str(x) for x in self.color) + ')'