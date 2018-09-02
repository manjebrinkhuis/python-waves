from base import Parameter
from functions import euclidean_rhythm
from math import floor


class Rhythm(object):

    """Rhythm class.

    The Rhythm class relies on euclidean rhythms. A given number of pulses
    are distributed equally over a given number of steps.

    """

    def __init__(self,
                 steps=16,
                 pulses=4,
                 shift=0,
                 num_notes=3,
                 skip_step=0,
                 skip_note=0,
                 index=0,
                 order=0,
                 bar_length=1,
                 bar_shift=0):

        self.steps = Parameter(steps)
        self.pulses = Parameter(pulses)
        self.shift = Parameter(shift)
        self.num_notes = Parameter(num_notes)
        self.skip_step = Parameter(skip_step)
        self.skip_note = Parameter(skip_note)
        self.index = Parameter(index)
        self.bar_length = Parameter(bar_length)
        self.bar_shift = Parameter(bar_shift)

    def get_onsets(self, start, stop):

        # Get values at beginning of segment
        steps = int(self.steps.get_value(start))
        pulses = int(self.pulses.get_value(start))
        shift = int(self.shift.get_value(start))
        bar_length = self.bar_length.get_value(start)
        bar_shift = self.bar_shift.get_value(start)
        
        _, onsets = euclidean_rhythm(steps, pulses, shift,
                                     length=bar_length,
                                     onset=True)
        
        # shift start and stop to select onsets
        _start = (start + bar_shift) % bar_length
        _stop = (stop + bar_shift) % bar_length
        if _start > _stop:
            _start -= bar_length

        onsets = [on for on in onsets if (on >= _start) and (on < _stop)]
                
        # reshift
        bar = floor(start)
        _bar = floor(_start)
        onsets = [on-_bar+bar for on in onsets]

        # Go through onsets and make strike,
        # or arpeggio, or chord.
        out_on = []
        out_ind = []
        for i, on in enumerate(onsets):
            num = int(self.num_notes.get_value(on))
            index = int(self.index.get_value(on))
            skip_step = self.skip_step.get_value(on)
            ss = bar_length / steps * skip_step
            sn = int(self.skip_note.get_value(on))+1

            for n in range(num):
                out_on += [on+n*ss for on in onsets if (on+n*ss) >= _start]
                out_ind += [index+n*sn for on in onsets if (on+n*ss) >= _start]

        return out_on, out_ind
