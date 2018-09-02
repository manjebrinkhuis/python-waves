from OSC import OSCClient, OSCBundle, ThreadingOSCServer
from threading import Thread
from functions import secs2time, print_note
import sys

class OSC2MidiClient(OSCClient):

    """OSC2MidiClient

    The OSC2MidiClient sends signals from the main append
    to an OSC2MidiServer, which may be running on another device.

    """

    def __init__(self, host='127.0.0.1',
                 port=2222,
                 latency=2.0):
        OSCClient.__init__(self)
        self.connect((host, port))
        self.latency = latency
    def note_on(self, note, onset):
        """Send note on message through timestamped bundle."""
        bundle = OSCBundle(address='/midi/noteon', time=onset+self.latency)
        #print 'ON:', onset+self.latency
        bundle.append(note.on_msg())
        self.send(bundle)

    def note_off(self, note, onset):
        """Send note off message through timestamped bundle."""
        bundle = OSCBundle(address='/midi/noteoff', time=onset+self.latency)
        #print 'OFF:', onset+self.latency
        bundle.append(note.off_msg())
        self.send(bundle)

    def stop(self):
        """Send stop message through timestamped bundle."""
        bundle = OSCBundle(address='/stop', time=0)
        bundle.append('stopping...')
        self.send(bundle)


class OSC2MidiServer(Thread, ThreadingOSCServer):

    """OSC2MidiServer

    The OSC2MidiServer receives input from our main app and sends
    midi signals to some midi device on the current device.

    """

    def __init__(self,
                 address='127.0.0.1',
                 port=2222,
                 dev_id=3,
                 _midi=None,
                 **kwargs):

        # Initialize midi
        self.midi = _midi
        self.midi.init()
        self.start_time = self.midi.time()
        
        self.midi_out = self.midi.Output(dev_id)

        # OSC server stuff
        ThreadingOSCServer.__init__(self, (address, port))
        self.addDefaultHandlers()
        self.addMsgHandler("/midi/noteon", self.note_on)
        self.addMsgHandler("/midi/noteoff", self.note_off)
        self.addMsgHandler("/stop", self.stop)
        self.addMsgHandler("/printed", self.msgPrinter_handler)
        self.addMsgHandler("/serverinfo", self.msgPrinter_handler)
        print "Registered Callback-functions:"
        for addr in self.getOSCAddressSpace():
            print '-', addr
        print "\nStarting OSCServer. Use ctrl-C to quit."
        super(OSC2MidiServer, self).__init__(target=self.serve_forever)

    def note_on(self, addr, tags, stuff, src):
        """Send note on signal to midi stream."""
        # Unpack information
        midi, velocity, channel, name, onset = stuff[0].split('_')
        elapsed = (self.midi.time() - self.start_time) / 1000.0
        print_note(secs2time(elapsed),
                   name, velocity, 'ON',
                   channel)
        # Turn on midi note.
        self.midi_out.note_on(int(midi), int(velocity), int(channel))

    def note_off(self, addr, tags, stuff, src):
        """Send note off signal to midi stream."""
        # Unpack information
        midi, velocity, channel, name, onset = stuff[0].split('_')
        elapsed = (self.midi.time() - self.start_time) / 1000.0
        print_note(secs2time(elapsed),
                   name, velocity, 'OFF',
                   channel)
        
        # Turn off midi note.
        self.midi_out.note_off(int(midi), int(velocity), int(channel))

    def stop(self, addr, tags, stuff, src):
        """Stop midi and terminate the server."""

        # Give user output
        print 'Closing midi device...'

        # Stop all playing notes.
        for chan in range(16):
            for note in range(128):
                self.midi_out.note_off(note, 0, chan)

        # Close things.
        print 'Closing connection...'
        self.close()
        print 'Wrapping up...'
        self.join()
        print 'Done.'

class OutputPrint():

    """Used for debugging.

    """

    def __init__(self):
        pass

    def note_on(self, note, real_onset):
        """Print note on."""
        print real_onset
        print note.to_string()
        print '---'

    def note_off(self, note, real_offset):
        """Print note off."""
        print real_offset
        print note.to_string()
        print '---'
