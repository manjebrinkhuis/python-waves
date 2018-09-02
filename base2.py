from functions import linear, rescale, nearest
from timeit import default_timer
import time
from math import floor

def test(time):
    time.sleep(1)
    return 0

class Parameter():

    """Parameter.

    A parameter makes an attribute animatable. It does require
    an object to be able to retrieve its value with a given onset,
    using the "get_value" method.

    """

    def __init__(self, arr, shift=0, length=1, quantize=1,
                 bounds=None, interp='linear'):

        if isinstance(arr, Parameter):
            self.arr = arr.arr
            shift = arr.shift
            length = arr.length
            bounds = arr.bounds
            quantize = arr.quantize
        elif hasattr(arr, '__iter__'):
            self.arr = list(arr)
        else:
            self.arr = [arr]

        self.shift = shift
        self.length = length
        self.quantize = float(quantize)
        self.bounds = bounds
        self.interp = interp

    def get_value(self, onset):

        elapsed = (float(onset) + self.shift) % self.length

        if self.interp == 'linear':
            val = float(linear(elapsed / self.length, self.arr))
        elif self.interp == 'nearest':
            val = float(nearest(elapsed / self.length, self.arr))

        if self.bounds:
            ymin, ymax = self.bounds
            s, y, n = rescale(self.arr, ymin, ymax)
            val = (val - y) * s + n

        inv_qnt = 1.0 / self.quantize
        val = floor(val * inv_qnt) / inv_qnt

        return val


class Pattern(object):
    """docstring for Pattern"""
    def __init__(self, diatonic, notes, rhythm,
                 duration=4, velocity=80, channel=0):

        self.diatonic = diatonic
        self.notes = notes
        self.rhythm = rhythm if hasattr(rhythm, '__iter__') else [rhythm]
        self.channel = Parameter(channel)
        self.duration = Parameter(duration)
        self.velocity = Parameter(velocity)
        self._prev_time = 0

    def get_notes(self, song_time):

        onsets, indices = [], []
        for rhythm in self.rhythm:
            ons, ind = rhythm.get_onsets(self._prev_time, song_time)
            if ons:
                print ons
            onsets += ons
            indices += ind

        self._prev_time = song_time

        out = []
        for i, onset in enumerate(onsets):

            # Create parameters for Note
            index = indices[i]
            notes = self.notes.get_indices(onset)

            midis, (names, pitches, octaves) = self.diatonic.get_notes(onset)
            index_in_notes = index % len(notes)
            index_in_midi = notes[index_in_notes] % 7
            extra_octaves = index // len(notes) + notes[index_in_notes] // 7
            midi = midis[index_in_midi] + extra_octaves * 12
            name = names[index_in_midi]
            pitch = pitches[index_in_midi]
            sign = '#'*pitch if pitch > 0 else 'b'*abs(pitch)
            octave = octaves[index_in_midi] + extra_octaves
            full_name = name + sign + str(octave)

            # Note
            note = Note(midi=midi,
                        name=full_name,
                        onset=onset,
                        channel=self.channel.get_value(onset),
                        duration=self.duration.get_value(onset),
                        velocity=self.velocity.get_value(onset))

            out.append(note)

        return out


class Note():

    """Note

    The note class contains all the information of a note.
    The onset and duration values are relative to bar_duration.

    """

    def __init__(self,
                 midi=64,
                 name='C5',
                 onset=0,
                 start=0,
                 channel=0,
                 duration=0,
                 velocity=80):

        # Attributes
        self.channel = channel
        self.onset = onset
        self.start = start
        self.duration = duration
        self.velocity = velocity
        self.midi = midi
        self.name = name

    def __eq__(self, other):
        """ Compare two notes """

        # The channel and midi note need to be equal
        # for a Note instance to be equal.
        midi_eq = (self.midi == other.midi)
        chan_eq = (self.channel == other.channel)

        return midi_eq and chan_eq

    def __str__(self):
        return self.name

    def on_msg(self):
        vals = [int(self.midi),
                int(self.velocity),
                int(self.channel),
                self.name,
                self.onset]
        return '_'.join([str(val) for val in vals])

    def off_msg(self):
        vals = [int(self.midi),
                int(self.velocity),
                int(self.channel),
                self.name,
                self.onset + self.duration]
        return '_'.join([str(val) for val in vals])


class Clock():

    """Songtime

    """

    def __init__(self, cycle=2.0, timer=None):

        self.cycle = Parameter(cycle)
        self.timer = timer if timer else default_timer
        self.the_bar = 0
        self.song_onset = self.timer()
        self.the_time = 0
        self.onset = self.song_onset
        self.offset = self.onset + self.cycle.get_value(0)
        self.elapsed = 0

    def reset(self):

        self.song_onset = self.timer()
        self.the_time = 0
        self.onset = self.the_time
        self.offset = self.onset + self.cycle.get_value(0)

    def update(self):

        cycle = self.cycle.get_value(self.get_songtime())

        self.onset = self.the_time - self.elapsed * cycle
        self.offset = self.onset + cycle
        self.the_time = self.timer() - self.song_onset

        if self.the_time > self.offset:
            self.the_bar += 1
            self.onset = self.offset
            print 'cycle ----------- ', self.the_bar

        self.elapsed = (self.the_time - self.onset) / cycle

    def get_songtime(self):
        return self.the_bar + self.elapsed


class Player():

    """Player

    Player instance. The main loop. Every iteration the
    instances in pipeline and patterns are updated. Then,
    the list of notes is updated. Notes are played at note
    onset, using output instance, and turned off after
    note offset.

    """

    def __init__(self,
                 clock,
                 output,
                 patterns=[]):

        self.clock = clock
        self.output = output
        self.patterns = patterns

        self.is_running = False
        self._notes = []
        self._played = []

    def run(self):
        """ Cycle and play notes. """

        self.is_running = True
        self.clock.reset()

        try:
            while self.is_running:
                song_time = self.clock.get_songtime()
                # Get notes from patterns.
                self._notes = []
                for pat in self.patterns:
                    self._notes += pat.get_notes(song_time)
                self.eval_notes()
                # Update clock.
                self.clock.update()
                # Dont hog cpu.
                time.sleep(1.0001)

        except KeyboardInterrupt:
            print 'Aborted.'
            self.output.stop()

    def eval_notes(self):
        """ Play and turn off notes. """

        bar = self.clock.the_bar
        bar_onset = self.clock.onset
        
        song_time = self.clock.get_songtime()
        cycle = self.clock.cycle.get_value(song_time)

        # Turn them on.
        for note in self._notes:
            # If the note is already played
            # remove previous instance, so it
            # is not turned off at the offset
            # of previous instance.
            if note in self._played:
                self._played.remove(note)
                
            # Play the note
            real_onset = bar_onset + (note.onset - bar) * cycle
            
            self.output.note_on(note, real_onset)

            # And store in played list.
            self._played.append(note)

        # Turn them off.
        to_remove = []
        for note in self._played:

            offset = note.onset + note.duration
            
            # If offset has passed,
            # turn the note off.
            if song_time > offset:
                # Just like with onset, we pass the real onset time
                real_offset = bar_onset + (note.onset + note.duration) * cycle
                self.output.note_off(note, real_offset)

                # And remove from played list.
                to_remove.append(note)

        for note in to_remove:
            self._played.remove(note)
