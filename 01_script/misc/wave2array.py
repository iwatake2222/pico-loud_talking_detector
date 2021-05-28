#-- coding: utf-8 --
import os
import numpy as np
import matplotlib.pyplot as plt
import wave
import librosa
import soundfile
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert wave to array")
    parser.add_argument("-i", "--input_filename", help="input wav filename", type=str, required=False, default="1-100032-A-0.wav")
    parser.add_argument("-o", "--output_directory", help="output_directory", type=str, required=False, default="./")
    parser.add_argument("-s", "--sampling_rate", help="sampling rate[Hz]", type=int, required=False, default=16000)
    args = parser.parse_args()
    input_filename = args.input_filename
    output_directory = args.output_directory
    sampling_rate = args.sampling_rate
    print(f"input_filename = {input_filename}, output_directory = {output_directory}, sampling_rate = {sampling_rate}")
    os.makedirs(output_directory, exist_ok=True)

    basename, ext = os.path.splitext(os.path.basename(input_filename))
    data, sr = librosa.core.load(input_filename, sr=sampling_rate, mono=True)
    data = data * 2**15

    with open(output_directory + "/" + basename + ".txt", "w") as f:
        for d in data:
            f.write(str(int(d)) + ", ")

    plt.plot(data)
    plt.show()

    # data = data / 2**15
    # soundfile.write("a.wav", data, samplerate=16000, subtype="PCM_16")

