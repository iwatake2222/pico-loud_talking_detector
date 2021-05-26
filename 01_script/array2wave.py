#-- coding: utf-8 --
import os
import numpy as np
import matplotlib.pyplot as plt
import wave
import librosa
import soundfile
from wave_array import wave_array_yes
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert wave to array")
    parser.add_argument("-o", "--output_filename", help="output wav filename", type=str, required=False, default="out.wav")
    parser.add_argument("-s", "--sampling_rate", help="sampling rate[Hz]", type=int, required=False, default=16000)
    args = parser.parse_args()
    output_filename = args.output_filename
    sampling_rate = args.sampling_rate
    print(f"output_filename = {output_filename}, sampling_rate = {sampling_rate}")

    data = np.array(wave_array_yes)

    data = data / 2**15
    soundfile.write(output_filename, data, samplerate=sampling_rate, subtype="PCM_16")

    plt.plot(data)
    plt.show()
