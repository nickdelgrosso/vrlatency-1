import pyglet
import serial
import numpy as np
# import pandas as pd
import ratcave as rc
import VRLatency as vrl
from struct import unpack

# from Stimulus import *

class Device(object):
    """ Handles attributes and methods related to stimulation/recording device

    Attributes:
        channel:
        is_connected (bool):

    """
    def __init__(self):
        self.channel = None
        self.is_connected = False

    def find_device(self):
        """ Display a list of connected devices to the machine

        Returns:
            list of the ports and the connected devices to this machine

        """
        raise NotImplementedError()

    def connect(self, port=None, baudrate=None):
        """ Connect to recording device

        Args:
            port: the port that the stimulation/recording device is connected to
            baudrate: the baudrate set on the recording device

        Return:

        """

        if (port is None) or (baudrate is None):
            raise ValueError("Specify both port and baudrate for the communication channel.")

        print('Connecting...')
        self.channel = serial.Serial(port, baudrate=baudrate, timeout=2.)
        self.channel.readline()
        print('Connection successful!')
        self.is_connected = True

    def disconnect(self):
        """ disconnect the device

        """
        self.channel.close()
        self.is_connected = False


class Window(pyglet.window.Window):
    """ Window object for the experiment

    Attributes:

    """

    def __init__(self, screen_ind=0, resizable=False, fullscreen=False, *args, **kwargs):
        """ initialize window object

        Args:
            screen_ind: inidicate which screen must contain the created window (if you have more than one screen)
            resizable: in case a resizable window is required, set this to True (default is False)
            fullscreen: for a fullscreen window, set this to True (default is False)
            args and kwargs: all other inputs that pyglet window objects can accept (look into pyglet documentaion)

        """
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_screens()[screen_ind]
        super().__init__(screen=screen, resizable=resizable, fullscreen=fullscreen, *args, **kwargs)


class Stim():
    """ initialize an stimulation object

    Attributes:
        mesh: the object appearing on the screen

    """
    def __init__(self, type='Plane'):
        self.mesh = rc.WavefrontReader(rc.resources.obj_primitives).get_mesh(type, drawmode=rc.POINTS)


class Data(object):
    """ Data object handling data-related matters

    Attributes:
        _array: stores the recorded data during the experiment (if record is set to True, and there exist a recording device)

    """

    def __init__(self):

        self._array = []

    @property
    def array(self):
        return self._array

    def record(self):
        raise NotImplementedError()

    def store(self):
        raise NotImplementedError()

        # dd = np.array(data).reshape(-1, 3)
        # df = pd.DataFrame(data=dd, columns=['Time', "Chan1", 'Trial'])
        # df.to_csv('../Measurements/' + filename + '.csv', index=False)

    def analyze(self):
        raise NotImplementedError()


class Experiment(object):
    """ Experiment object integrates other components and let's use to run, record and store experiment data

    """
    def __init__(self, window=None, stim=None, trials=20):
        """ Initialize an experiment object

        Args:
                - trials: number of trials
                - filename: name for the recorded data
                - path: path for saving the recorded data (if not given it will be saved in current directory)
        """

        # create window
        self._mywin = window

        self._stim = stim

        # create Data object
        self.data = Data()


        self.trials = trials
        self._trial = 0
        self.__last_trial = 0


    @property
    def trial(self):
        return self._trial


    def run(self, record=False, device=None):
        """ runs the experiment in the passed application window

        Input:

        return:

        """

        if record and (self.device is None):
            self._mywin.close()
            raise ValueError("No recording device attached.")

        self._paradigm()

    def _paradigm(self):
        pass


class display_latency(Experiment):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, on_width=.5, off_width=.5, record=False, device=None):
        self._paradigm(self, on_width=on_width, off_width=off_width)


    def _paradigm(self, on_width=None, off_width=None):

        if type(on_width) == float:
            on_width = [on_width] * 2
        elif len(on_width) > 2:
            raise ValueError("on_width must have either on or two values!")

        if type(off_width) == float:
            off_width = [off_width] * 2
        elif len(off_width) > 2:
            raise ValueError("off_width must have either on or two values!")

        self.__last_trial = self.__trial

        @self._mywin.event
        def on_draw():
            self._mywin.clear()
            with rc.default_shader:
                self.stim.draw()
                if self.__last_trial != self.__trial:
                    self.__last_trial = self.__trial
                    self.device.write(b'S')
            if self.has_fps_display:
                self._fr.draw()

        def start_next_trial(dt):
            self.__trial += 1
            self.stim.visible = True
            pyglet.clock.schedule_once(end_trial, np.random.uniform(low=on_width[0], high=on_width[1]))
        pyglet.clock.schedule_once(start_next_trial, 0)


        def end_trial(dt):
            POINTS = 240
            self.stim.visible = False
            dd = unpack('<' + 'I2H' * POINTS, self.device.read(8 * POINTS))
            self.data.extend(dd)
            if self.__trial > self.trials:
                pyglet.app.exit()  # exit the pyglet app
                self.device.close()  # close the serial communication channel
            pyglet.clock.schedule_once(start_next_trial, np.random.uniform(low=off_width[0], high=off_width[1]))


        def update(dt):
            pass
        pyglet.clock.schedule(update)

        pyglet.app.run()


class tracking_latency(Experiment):

    def _init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _paradigm(self):
        raise NotImplementedError()


class total_latency(Experiment):

    def _init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _paradigm(self):
        vrl.Stim_without_tracking(window=self._mywin, mesh=self._stim.mesh)
        # while len(self.data) < TOTAL_POINTS * 11:
        #     self.data.extend(unpack('<' + 'I3H?' * POINTS, device.read(11 * POINTS)))
