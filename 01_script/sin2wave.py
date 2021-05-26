#-- coding: utf-8 --
import os
import numpy as np
import matplotlib.pyplot as plt
import wave
import librosa
import soundfile
import argparse
import math



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create wave file using sin wav")
    parser.add_argument("-f", "--freq", help="frequency[Hz]", type=int, required=False, default=1000)
    parser.add_argument("-d", "--duration", help="duration[ms]", type=int, required=False, default=1000)
    parser.add_argument("-v", "--volume", help="volume", type=float, required=False, default=1.0)
    parser.add_argument("-s", "--sampling_rate", help="sampling rate[Hz]", type=int, required=False, default=16000)
    parser.add_argument("-o", "--output_directory", help="output_directory", type=str, required=False, default="./")
    args = parser.parse_args()
    freq = args.freq
    duration = args.duration
    volume = args.volume
    sampling_rate = args.sampling_rate
    output_directory = args.output_directory
    sample_num = int(duration * sampling_rate / 1000)
    print(f"Create {freq} Hz, {duration} ms, volume = {volume}, sampling_rate = {sampling_rate}")
    output_filename = f"sin_{freq}Hz_{duration}ms.wav"
    print(f"output_filename = {output_filename}")

    wave_array = []
    for t in range(sample_num):
        wave_array.append((volume * 2**15) * math.sin(math.radians(t / sampling_rate * 360 * freq)))
    data = np.array(wave_array)
    data = data / 2**15
    soundfile.write(output_directory + "/" + output_filename, data, samplerate=sampling_rate, subtype="PCM_16")
    
    plt.plot(data)
    plt.show()
