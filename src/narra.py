

import json
from enum import Enum
import os
import inspect
import wave
import yaml                          # pip3 install pyyaml
from pyOptional import Optional      # pip3 install pyOptional
import numpy as np
import numpy.ma as ma
import scipy.fftpack as fft

"""
The actual thing-of-interest here is the YAML formatted data
Python classes and methods are essentially helpers/wrappers for this format:

---
meta:
  audio_file: psalm_133_drb_64kb.wav
  audio_samples_sec: 22050
  content_start_sec: 13.74
  content_end_sec: 44.38
  duration_sec: 49.66
  word_count: 67
  wpm: 27.44
  central_hz: 333.42
  loudness_rms: 2000.0
script:
- word: behold start=13.74
- word: how start=14.5
- word: good start=14.83
- word: and start=15.48
- word: how start=15.64
- word: pleasant start=15.8
...

Possible elements under script are:
  word (Label.WORD)
  pause (Label.PAUSE)
  punc (Label.PUNC)
  breath (Label.BREATH)

TODO: per-word: rate, volume, central_hz
"""

# Names under meta
AUDIO_FILE        = "audio_file"
AUDIO_SAMPLES_SEC = "audio_samples_sec"
CONTENT_START_SEC = "content_start_sec"
CONTENT_END_SEC   = "content_end_sec"
DURATION_SEC      = "duration_sec"
WORD_COUNT        = "word_count"
WPM               = "wpm"
CENTRAL_HZ        = "central_hz"
LOUDNESS_RMS      = "loudness_rms"

#Names under script
START             = "start"


class Dynamics:
    class Inflection(Enum):
        RISING = 1
        STEADY = 0
        FALLING = -1

    class Label(Enum):
        WORD = 1
        PAUSE = 2
        PUNC = 3
        BREATH = 4


class Narra:
    """An entire audio work for analysis or recording to audio"""

    def __init__(self, file):
        self.dbfile = os.path.splitext(file)[0] + ".yaml"
        try:
            f = open(self.dbfile, 'r')
            self.yaml = yaml.safe_load(f)
        except FileNotFoundError:
            self.yaml = { "meta": {}, "script": {} }

        self.samples = None  # NumPy Array
        meta = self.yaml["meta"]
        meta[AUDIO_FILE] = file
        self.load_audio()
        self.checkpoint()

    def load_audio(self):
        MAX_WAVE_SIZE = 100 * 1024 * 1024
        meta = self.yaml['meta']
        fp = wave.open(meta[AUDIO_FILE], "rb")
        audio_params = fp.getparams()
        print(audio_params)
        meta[AUDIO_SAMPLES_SEC] = audio_params.framerate
        meta[DURATION_SEC] = audio_params.nframes / audio_params.framerate
        if not audio_params.sampwidth == 2:
            print("Warning: this WAV file isn't 16-bit")
        if audio_params.nchannels > 1:
            print("Warning: this WAV file isn't mono")
        samps = fp.readframes(MAX_WAVE_SIZE)
        dt = np.dtype('int16')
        #dt = dt.newbyteorder('>')
        samples = np.frombuffer(samps,dtype=dt)
        self.samples = samples
        meta[LOUDNESS_RMS] = self.average_vol()
        meta[CENTRAL_HZ] = self.average_tone()

    def average_vol(self):
        """ RMS of values, omitting quiet samples"""
        NOISE_GATE = 10 # of -32,768 ...
        s = self.samples
        valid_samples = np.ma.masked_inside(s,-1 * NOISE_GATE, NOISE_GATE)
        return float(np.sqrt(np.mean(valid_samples.astype(float)**2)))

    def average_tone(self):
        """ determine rincipal frequency component"""
        # see https://medium.com/@neurodatalab/pitch-tracking-or-how-to-estimate-the-fundamental-frequency-in-speech-on-the-examples-of-praat-fe0ca50f61fd
        # see https://rileyjshaw.com/blog/taking-the-average-tone/
        # maybe even https://gist.github.com/endolith/255291
        #fourier = np.fft.fft(self.samples)
        #frequencies = np.fft.fftfreq(len(fourier))
        meta = self.yaml['meta']
        sample_length = len(self.samples)
        rate = meta[AUDIO_SAMPLES_SEC]
        k = np.arange(sample_length)
        period = sample_length / rate
        freqs = (k / period)[range(sample_length // 2)]  # right-side frequency range
        fourier = abs(fft.fft(self.samples * np.hanning(sample_length)) / sample_length)  # normalized, not clipped
        fourier = fourier[range(sample_length // 2)]  # clip to right-side
        print(fourier)
        power = np.power(fourier, 2.0)
        print(sum(power * freqs))
        print(sum(power))
        return float(sum(power * freqs) / sum(power))

    def process(self, transcription_file):
        """ Given a JSON file with words & timing, separate out and process audio for the whole work
        """
        with open(transcription_file, "r") as f:
            f.close()
        s = self.yaml["script"]
        self.serialize()

    def checkpoint(self):
        """serialize to disk"""
        with open(self.dbfile, "w") as f:
            print("saved checkpoint")
            yaml.safe_dump(self.yaml, f)
            f.close()

class Vocable:
    """
    a Vocable is any individual unit that can serve as an input to a text-to-speech engine
    """

    def __init__(self, label: str):
        self.label = Optional(label)      # primary key for serialization
        self.start_ms = Optional(0)       # msec
        self.duration_ms = Optional(0)    # msec
        if type(self) is Vocable:
            print("Why are you instantiating this directly?")

    def dump(self):
        print("XXX")
        print(type(self.label))
        print(self.label.get_or_else("?"))
        props = [prop for prop in dir(self) if not prop.startswith('__') if not inspect.ismethod(getattr(self, prop))]
        for prop in props:
            print("%s %s" % (prop, type(getattr(self, prop))))
        #print(" ".join(props))

def test_optional():
    i = Optional(3)
    print(i)
    print(i.map(lambda x: x+4))
    print(i.get_or_else(5))

    n = Optional.empty()
    print(n)
    print(n.get_or_else(2))

    s = Optional("foo")
    print(s)
    print(s.get_or_else("foo"))

