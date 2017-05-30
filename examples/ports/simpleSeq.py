#!/usr/bin/env python
"""
Based on midi output example from mido:
Send random notes to the output port.

added:

- OSC hooks for adjusting parameters
- major/minor/penta scale modes
- tempo (note-duration)
- upward/downward/random note progression

"""
from __future__ import print_function
import sys
import time
import random
import mido
import threading

from OSC import OSCServer
from mido import Message

#constants
ARP_UP = 1
ARP_DOWN = 2
ARP_RAND = 3

#globals
server = OSCServer( ("0.0.0.0", 7002) )
period = 1.0
note_offset = 0
arp_type = ARP_RAND
curr_note = 0

def arp_handler(addr, tags, stuff, source):
    global arp_type
    print("arp: ", stuff)
    if stuff[0] == 'up':
        arp_type = ARP_UP
    elif stuff[0] == 'down':
        arp_type = ARP_DOWN
    elif stuff[0] == 'rand':
        arp_type = ARP_RAND

def mod_handler(addr, tags, stuff, source):
    print("mod: ", stuff, " len=",len(stuff))
    global note_offset
    note_offset = stuff[0]
    print("offset = ", note_offset) 

def key_handler(addr, tags, stuff, source):
    print("key: ", stuff)
    global notes
    if (stuff[0]== 'major'):
        notes = [60, 62, 64, 65, 67, 69]
        print("MAJOR")
    elif (stuff[0] == 'penta'):
        notes = [60, 62, 64, 67, 69, 72]
        print("PENTA")
    else:
        notes = [60, 62, 63, 65, 67, 68]
        print("MINOR")

def message_handler(addr, tags, stuff, source):
    print("message: ", addr)  

def tempo_handler(addr, tags, stuff, source):
    global period
    print("tempo: ", stuff[0])
    period = stuff[0]

def get_next_note():
    global arp_type
    global curr_note
    if (arp_type == ARP_RAND):
        return random.choice(notes) + note_offset
    elif (arp_type == ARP_UP):
        curr_note =curr_note + 1;
        curr_note = curr_note%len(notes)
        return notes[curr_note] + note_offset
    elif (arp_type == ARP_DOWN):
        curr_note = curr_note - 1;
        curr_note = curr_note%len(notes)
        return notes[curr_note] + note_offset


if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

# A pentatonic scale
notes = [60, 62, 64, 67, 69, 72]

server.addMsgHandler("/test", message_handler)
server.addMsgHandler("/tempo", tempo_handler)
server.addMsgHandler("/mod", mod_handler)
server.addMsgHandler("/key", key_handler)
server.addMsgHandler("/arp", arp_handler)

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
            note = get_next_note()
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
