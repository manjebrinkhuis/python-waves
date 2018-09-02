from base import Parameter
from defaults import MAJ_C, MAJ_SCALE, MAJ_INDICES
from functions import roll, cumsum, diff_single
from functions import add_single, abs_array, diff, add


class Diatonic():

    """Diatonic

    Create a diatonic scale. After setting scale parameters,
    the octave, rotate and transpose parameters are animatable.
    The alter argument contains a list of tuples with the index
    of a note in the scale and the pitch to alter that note.
    So, you can create harmonic minor, or whatever you'd like.

    """

    def __init__(self, key='C', pitch=0, octave=5,
                 rotate=0, transpose=0,
                 alter=[(0, 0)]):

        # Initial values (non-animatable)
        self.key = key
        self.pitch = pitch

        # Animatable values
        self.octave = Parameter(octave)
        self.rotate = Parameter(rotate)
        self.transpose = Parameter(transpose)
        self.alter = [(Parameter(i), Parameter(v)) for i, v in alter]

        # Internals
        self._transposed = self.transpose.get_value(0)

    def add_alter(self, alter):
        self.alter += (Parameter(alter[0]), Parameter(alter[1]))

    def get_notes(self, onset):
        """ """

        # Get values
        octave = int(self.octave.get_value(onset))
        rotate = int(self.rotate.get_value(onset))
        transpose = int(self.transpose.get_value(onset))

        ki = MAJ_C.index(self.key)

        # Root
        root = MAJ_INDICES[ki]
        root += transpose + self.pitch
        root += octave * 12

        # Distances
        distances = MAJ_SCALE
        distances = roll(distances, rotate)
        for alt in self.alter:
            index = int(alt[0].get_value(onset))
            alter = int(alt[1].get_value(onset))
            distances[index] += alter

        # Midi
        midi = cumsum(distances)
        midi = add_single(midi, root)

        # Transpose
        direction = transpose - self._transposed
        self._transposed = transpose
        maj_diff = diff_single(MAJ_INDICES, root % 12)
        min_diff = min(abs_array(maj_diff))
        min_diff *= -1 if direction > 0 else 1

        # New index
        index = maj_diff.index(min_diff)

        # Pitches
        pitch = root % 12 - MAJ_INDICES[index]
        whole_scale = roll(MAJ_SCALE, index)
        whole_indices = cumsum(whole_scale)
        whole_altered = diff(MAJ_INDICES, whole_indices)
        indices = cumsum(distances)
        pitches = diff(indices, MAJ_INDICES)
        pitches = add(whole_altered, pitches)
        pitches = add_single(pitches, pitch)

        names = roll(MAJ_C, index)
        octaves = [i // 12 for i in midi]

        return midi, (names, pitches, octaves)


class Chord():

    """Chord

    The Chord class is used to create groups of notes that are
    extracted from a Diatonic scale by their index in that scale.

    """

    def __init__(self, root=0, num_notes=1,
                 inverse=0, skip=1):

        self.root = Parameter(root)
        self.num_notes = Parameter(num_notes)
        self.inverse = Parameter(inverse)
        self.skip = Parameter(skip)

    def get_indices(self, onset):

        num_notes = int(self.num_notes.get_value(onset))
        root = int(self.root.get_value(onset))
        skip = int(self.skip.get_value(onset))
        inverse = int(self.inverse.get_value(onset))

        # Create chord
        indices = [i * (skip + 1) + root for i in range(num_notes)]

        # Inverse and lower octave of inversed notes
        for i in reversed(range(inverse)):
            index = i % num_notes
            indices[index] -= 8

        return indices

if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt
    c = Chord(root=[1,2],
              inverse=Parameter([0,5],
                                length=5))
    plt.plot(np.arange(0,10,.1),
            [c.inverse.get_value(val) for val in np.arange(0,10,.1)])

    plt.xticks(range(10))
    plt.yticks(np.arange(0,5,.5))
    plt.grid(True, linestyle='-')
