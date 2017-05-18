#!/usr/bin/env python
"""
Send random notes to the output port.
"""
from __future__ import print_function
import sys
import time
import random
import mido
import threading

from OSC import OSCServer
from mido import Message

server = OSCServer( ("0.0.0.0", 7002) )
period = 1.0
note_offset = 0

def mod_handler(addr, tags, stuff, source):
    print("mod: ", stuff, " len=",len(stuff))
    global note_offset
    note_offset = stuff[0]
    print("offset = ", note_offset) 
    

def message_handler(addr, tags, stuff, source):
    print("message: ", addr)  

def tempo_handler(addr, tags, stuff, source):
    global period
    print("tempo: ", stuff[0])
    period = stuff[0]

if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

# A pentatonic scale
notes = [60, 62, 64, 67, 69, 72]

server.addMsgHandler("/test", message_handler)
server.addMsgHandler("/tempo", tempo_handler)
server.addMsgHandler("/mod", mod_handler)

print( "Registered Callback-functions:")
for addr in server.getOSCAddressSpace():
    print( addr)

st = threading.Thread( target = server.serve_forever )
st.start()

def setTone():
   #bank 0x2000 (keyboards etc)
    cchange = Message('control_change', channel=0, control=0, value = 2) #bank select MSB
    port.send(cchange)
    cchange = Message('control_change', channel=0, control=32, value = 0) #bank select LSB
    port.send(cchange)
    pgchange = Message('program_change', channel=0, program=0)
    port.send(pgchange)

try:
    with mido.open_output(portname, autoreset=True) as port:
        print('Using {}'.format(port))
        setTone()
        while True:
            note = random.choice(notes) + note_offset

            on = Message('note_on', note=note)
            print('Sending {}'.format(on), 'period = ', period)
            port.send(on)
            time.sleep(period)

            off = Message('note_off', note=note)
            #print('Sending {}'.format(off))
            port.send(off)
            time.sleep(0.1)

except KeyboardInterrupt:
    print("shutting down...")
    server.close()
    print("waiting for server thread")
    st.join()
    print("bye!")
    pass

print()
