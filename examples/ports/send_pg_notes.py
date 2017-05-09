#!/usr/bin/env python
"""
Send random notes to the output port.
"""
from __future__ import print_function
import sys
import time
import random
import mido
import thread
from mido import Message

def proc_input(L):
   inkey = raw_input()
   print( 'input' )
   if inkey == '1':
      period-= 0.02
   if inkey == '2':
      period+= 0.02
   L.append(inkey)
   

if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

# A pentatonic scale
notes = [60, 62, 64, 67, 69, 72]

period = 0.1

def setTone():
   #bank 0x2000 (keyboards etc)
    cchange = Message('control_change', channel=0, control=0, value = 2) #bank select MSB
    port.send(cchange)
    cchange = Message('control_change', channel=0, control=32, value = 0) #bank select LSB
    port.send(cchange)
    pgchange = Message('program_change', channel=0, program=0)
    port.send(pgchange)

L = []
thread.start_new_thread(proc_input, (L,))
try:
    with mido.open_output(portname, autoreset=True) as port:
        print('Using {}'.format(port))
        setTone()
        while True:
            note = random.choice(notes)

            on = Message('note_on', note=note)
            print('Sending {}'.format(on))
            port.send(on)
            time.sleep(period)

            off = Message('note_off', note=note)
            print('Sending {}'.format(off))
            port.send(off)
            time.sleep(0.1)

            if L:
                print (L[0], L[0])
                del L[0]
except KeyboardInterrupt:
    pass

print()
