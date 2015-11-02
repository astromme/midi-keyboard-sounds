#!/usr/bin/env python

import logging
import sys
import time
import subprocess
import os

import rtmidi
from rtmidi.midiutil import open_midiport

playing = None
sounds_dir = "sounds"
sounds = [s for s in discover_sounds(sounds_dir)]
print "discovered {0} sounds".format(len(sounds))

def discover_sounds(path):
    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            sound = os.path.join(dirname, filename)
            p = subprocess.Popen(["afinfo", sound], shell=False, stdout=subprocess.PIPE)
            streamdata = p.communicate()[0]
            if p.returncode == 0:
                yield sound

def get_sound_index(key):
    print key % len(sounds)
    return key % len(sounds)

def get_sound_index_white_keys_only(key):
    notes = {
    0: 0,
    2: 1,
    4: 2,
    5: 3,
    7: 4,
    9: 5,
    11: 6}

    note = key % 12
    octave = key / 12

    if note not in notes:
        return 4 #bueller... bueller....

    index = octave * 7 + notes[note]
    print index
    return index % len(sounds)


log = logging.getLogger('test_midiin_poll')

logging.basicConfig(level=logging.DEBUG)

port = sys.argv[1] if len(sys.argv) > 1 else None
try:
    midiin, port_name = open_midiport(port)
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Entering main loop. Press Control-C to exit.")
try:
    timer = time.time()
    while True:
        msg = midiin.get_message()

        if msg:
            message, deltatime = msg
            timer += deltatime
            print("[%s] @%0.6f %r" % (port_name, timer, message))
            unknown, key, strength = message
            if strength > 0:
                if playing:
                    playing.kill()
                path = get_sound_path(get_sound_index(key))
                print path
                playing = subprocess.Popen(["afplay", path], shell=False)

        time.sleep(0.01)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin