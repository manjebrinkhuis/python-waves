from melody import Diatonic, Chord
from rhythm import Rhythm
from base import Parameter, Pattern, Clock, Player
from output import OSC2MidiClient, OSC2MidiServer
from pygame import midi
import time

if __name__ == '__main__':

    # Create a test song
    dia = Diatonic(key='C',
                   transpose=Parameter([0, 1], length=8, interp='nearest'),
                   rotate=Parameter([0, 5], length=16, interp='nearest'))
    
    notes = Chord(root=Parameter([1, 4, 5], length=4, interp='nearest'),
                  num_notes=1, skip=1)

    rh1 = Rhythm(steps=[8], pulses=[4, 6, 8], shift=0, bar_length=1, num_notes=3)
    rh2 = Rhythm(steps=8, pulses=Parameter([5], interp='linear'),
                 shift=0, num_notes=1)

    vel = Parameter([80, 80, 100],
                    length=2, shift=0,
                    bounds=(80, 100))
    dur = Parameter([.2, .2, .3, .4],
                    quantize=.1, length=1,
                    shift=1, bounds=None)

    clock = Clock(timer=time.time,
                  cycle=Parameter([2.0], quantize=.01, length=2))

    pat3 = Pattern(channel=3,
                   diatonic=dia,
                   notes=Chord(root=Parameter([1, 4, 5, 7], length=8, interp='nearest'),
                               num_notes=3),
                   rhythm=Rhythm(pulses=Parameter([4], length=1),
                                 steps=16,
                                 index=Parameter([1,2,3,4], length=2),
                                 skip_note=Parameter([0,1], length=4, interp='nearest'),
                                 skip_step=Parameter([1, 2], length=4),
                                 num_notes=4),
                   velocity=Parameter([80, 80, 30, 100], length=4),
                   duration=Parameter([.1, .1, .1, .1], length=1, quantize=.1))

    # Rhythm
    drum_notes = Chord(root=0, num_notes=8, skip=0)
    kick = Rhythm(steps=16, pulses=Parameter([4, 4, 5, 5], length=4, interp='nearest'), index=0, num_notes=1)
    hihat = Rhythm(steps=16, pulses=4, shift=2, index=3, num_notes=1)
    snare = Rhythm(steps=16, pulses=2, shift=4, index=1, num_notes=1)
    pat0 = Pattern(channel=0,
                   diatonic=Diatonic(octave=3),
                   notes=drum_notes,
                   rhythm=[kick, hihat, snare],
                   velocity=vel,
                   duration=dur)

    
    # Bassline
    bass_notes = Chord(root=Parameter([4,5,1,6]))
    pat1 = Pattern(channel=1,
                   diatonic=dia,
                   notes=bass_notes,
                   rhythm=[rh2],
                   velocity=vel,
                   duration=dur)

    # Chords
    chord_notes = Chord(num_notes=3, root=Parameter([4,5,1,6], length=8, interp='nearest'))
    pat2 = Pattern(channel=2,
                   diatonic=dia,
                   notes=chord_notes,
                   rhythm=[rh1],
                   velocity=vel,
                   duration=dur)

    output = OSC2MidiClient()
    player = Player(patterns=[pat0, pat1, pat2, pat3],
                    clock=clock, output=output)
    server = OSC2MidiServer(_midi=midi, dev_id=2)
    server.start()
    player.run()
